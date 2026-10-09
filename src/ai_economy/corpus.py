"""Ingesta real, caché verificable, limpieza y unión validada por URL."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .sources import KAGGLE_DATASET, KAGGLE_DOWNLOAD, KAGGLE_URL, TED_SPEAKERS, TED_EXCLUDED_SLUGS, WEB_SOURCES


def canonical_url(value: str) -> str:
    value = str(value).strip().replace("\\n", "").strip()
    parts = urlsplit(value)
    return urlunsplit(("https", parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def clean_text(value: str) -> str:
    value = re.sub(r"\[(?:Button|Input|Select)(?::[^\]]*)?\]", " ", str(value), flags=re.I)
    value = BeautifulSoup(str(value), "html.parser").get_text(" ")
    value = re.sub(r"\((?:applause|laughter|music|cheers|audience laughs)\)", " ", value, flags=re.I)
    value = value.replace("\u00a0", " ").replace("\u200b", "")
    # Preserva negación, puntuación, cifras y relaciones causales expresadas.
    return re.sub(r"\s+", " ", value).strip()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download_ted(destination: Path, timeout: int = 90) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / "ted-talks.zip"
    response = requests.get(KAGGLE_DOWNLOAD, timeout=timeout, headers={"User-Agent": "TFM-AI-Economy/1.0 (academic research)"})
    response.raise_for_status()
    archive.write_bytes(response.content)
    if not zipfile.is_zipfile(archive):
        raise RuntimeError("Kaggle no devolvió un ZIP. Descargue el dataset desde su página o use kaggle datasets download -d rounakbanik/ted-talks.")
    with zipfile.ZipFile(archive) as handle:
        for filename in ("ted_main.csv", "transcripts.csv"):
            matches = [name for name in handle.namelist() if Path(name).name == filename]
            if len(matches) != 1:
                raise RuntimeError(f"Esperado un archivo {filename}; recibidos {matches}")
            (destination / filename).write_bytes(handle.read(matches[0]))
    acquisition = {"dataset": KAGGLE_DATASET, "url": KAGGLE_URL, "archive_sha256": file_sha256(archive), "retrieved_at": datetime.now(timezone.utc).isoformat()}
    (destination / "acquisition.json").write_text(json.dumps(acquisition, indent=2), encoding="utf-8")
    return acquisition


def load_ted(path: Path) -> tuple[list[dict], dict]:
    meta_path, transcript_path = path / "ted_main.csv", path / "transcripts.csv"
    metadata, transcripts = pd.read_csv(meta_path), pd.read_csv(transcript_path)
    metadata_raw_rows, transcript_raw_rows = len(metadata), len(transcripts)
    manifest_path = path / "acquisition.json"
    acquired = json.loads(manifest_path.read_text()).get("retrieved_at") if manifest_path.exists() else None
    for frame in (metadata, transcripts):
        frame["canonical_url"] = frame.url.map(canonical_url)
        # El dataset real contiene tres transcripciones repetidas exactamente.
        # Se eliminan filas idénticas y se rechazan conflictos sobre una misma URL.
        frame.drop_duplicates(inplace=True)
        if frame.canonical_url.duplicated().any():
            raise ValueError("La URL no es única: no se admite una unión many-to-many.")
    joined = metadata.merge(transcripts[["canonical_url", "transcript"]], on="canonical_url", how="inner", validate="one_to_one")
    selected = joined[joined.main_speaker.isin(TED_SPEAKERS)].copy().sort_values(["film_date", "title"])
    speaker_selected_count = len(selected)
    selected = selected[~selected.canonical_url.map(lambda url: url.rsplit("/", 1)[-1]).isin(TED_EXCLUDED_SLUGS)]
    records = []
    for _, row in selected.iterrows():
        text = clean_text(row.transcript)
        if len(text.split()) < 100:
            continue
        slug = row.canonical_url.rsplit("/", 1)[-1]
        records.append({"id": "ted_" + slug, "title": row.title, "authors": row.main_speaker, "url": row.canonical_url, "year": datetime.fromtimestamp(row.film_date, timezone.utc).year, "kind": "video_transcript", "modality": "spoken", "language": "en", "text": text, "retrieval_method": "kaggle_official_transcript", "dataset": KAGGLE_DATASET, "scope": "Transcripción completa proporcionada por TED, recuperada del dataset; no se ejecutó ASR ni análisis visual", "retrieved_at": acquired, "processed_at": datetime.now(timezone.utc).isoformat(), "source_text_sha256": hashlib.sha256(text.encode()).hexdigest()})
    audit = {"metadata_rows": metadata_raw_rows, "transcript_rows": transcript_raw_rows, "metadata_exact_duplicate_rows_removed": metadata_raw_rows - len(metadata), "transcript_exact_duplicate_rows_removed": transcript_raw_rows - len(transcripts), "unique_transcript_rows": len(transcripts), "joined_rows": len(joined), "missing_transcript_rows": len(metadata) - len(joined), "speaker_selected_count": speaker_selected_count, "off_topic_talks_removed": speaker_selected_count - len(selected), "excluded_slugs": sorted(TED_EXCLUDED_SLUGS), "selected_talks": len(records), "metadata_sha256": file_sha256(meta_path), "transcripts_sha256": file_sha256(transcript_path), "join_key": "canonical_url", "join_validation": "one_to_one_after_exact_deduplication", "selection": sorted(TED_SPEAKERS)}
    return records, audit


def extract_html(html: str, source: dict) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.select("script, style, nav, header, footer, form, aside, noscript"):
        element.decompose()
    candidates = soup.select(source.get("selector", "main"))
    if source["id"].startswith("nber"):
        # NBER utiliza una clase específica en algunas versiones de la web.
        specific = soup.select(".page-header__intro, .abstract, .paper-abstract")
        if specific:
            candidates = specific
    if not candidates:
        candidates = soup.select("article, main") or [soup]
    text = clean_text(" ".join(x.get_text(" ", strip=True) for x in candidates))
    if len(text.split()) < 50:
        raise ValueError(f"Contenido insuficiente o página de error para {source['id']}")
    lowered = text.lower()
    if len(text.split()) < 400 and any(token in lowered for token in ("verify you are human", "access denied", "javascript is required", "checking your browser")):
        raise ValueError(f"Página de bloqueo para {source['id']}")
    return text


def load_web(path: Path, offline: bool = False) -> tuple[list[dict], list[dict]]:
    path.mkdir(parents=True, exist_ok=True)
    records, audit = [], []
    for source in WEB_SOURCES:
        html_path, json_path = path / (source["id"] + ".html"), path / (source["id"] + ".json")
        try:
            method = "cached_html_scraping"
            retrieved_at = None
            if html_path.exists():
                text = extract_html(html_path.read_text(encoding="utf-8"), source)
                sidecar = path / (source["id"] + ".metadata.json")
                if sidecar.exists():
                    retrieved_at = json.loads(sidecar.read_text()).get("retrieved_at")
            elif json_path.exists():
                cached = json.loads(json_path.read_text(encoding="utf-8"))
                cached_text = cached["text"]
                if source["id"] == "gpts2023" and "Abstract:" in cached_text:
                    cached_text = cached_text.split("Abstract:", 1)[1]
                    cached_text = re.split(r"\n(?:Comments:|Subjects:|Cite as:|Journal reference:|Submission history|## Submission)", cached_text, maxsplit=1)[0]
                elif source["id"] == "ilo2025":
                    cached_text = cached_text.split("# Generative AI and Jobs", 1)[-1]
                    cached_text = cached_text.split("## Interactive charts", 1)[0]
                elif source["id"] == "cbo2024":
                    cached_text = cached_text.split("## Summary", 1)[-1]
                elif source["id"] == "imf2024":
                    cached_text = cached_text.split("### Reshaping the Nature of Work", 1)[-1].split("### References", 1)[0]
                text = clean_text(cached_text)
                method = cached.get("retrieval_method", "cached_text")
                retrieved_at = cached.get("retrieved_at", retrieved_at)
                if len(text.split()) < 50:
                    raise ValueError("La caché está vacía o no contiene el artículo.")
            elif offline:
                raise FileNotFoundError("Fuente sin caché local; ejecución offline.")
            else:
                response = requests.get(source["url"], timeout=35, headers={"User-Agent": "TFM-AI-Economy/1.0 (academic research; respectful single-page retrieval)"})
                response.raise_for_status()
                text = extract_html(response.text, source)
                html_path.write_text(response.text, encoding="utf-8")
                method = "live_html_scraping"
                retrieved_at = datetime.now(timezone.utc).isoformat()
                (path / (source["id"] + ".metadata.json")).write_text(json.dumps({"url": source["url"], "retrieved_at": retrieved_at}, indent=2), encoding="utf-8")
            # El reader de arXiv puede contener cuerpo de paper además del abstract.
            scope = source["scope"]
            if method == "web_reader_text" and source["id"] == "gpts2023":
                scope = "Resumen científico recuperado por lector web; sin menús ni texto íntegro del paper"
            record = {**source, "scope": scope, "modality": "written", "language": "en", "text": text, "retrieval_method": method, "retrieved_at": retrieved_at, "processed_at": datetime.now(timezone.utc).isoformat(), "source_text_sha256": hashlib.sha256(text.encode()).hexdigest()}
            records.append(record)
            audit.append({"id": source["id"], "url": source["url"], "status": "ok", "words": len(text.split()), "retrieval_method": method, "source_text_sha256": record["source_text_sha256"]})
        except (requests.RequestException, OSError, ValueError, KeyError) as error:
            audit.append({"id": source["id"], "url": source["url"], "status": "failed", "error": f"{type(error).__name__}: {error}"})
    return records, audit


def sentence_split(text: str, min_words: int = 10, max_words: int = 110) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'\(])", text)
    return [sentence.strip() for sentence in sentences if min_words <= len(sentence.split()) <= max_words]
