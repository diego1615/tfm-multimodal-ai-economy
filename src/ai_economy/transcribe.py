"""Ruta opcional para audio de vídeos: descarga autorizada + ASR local.

No ejecutada en el ejemplo publicado, que recupera transcripciones de TED.
No se presupone acceso a plataformas ni se eluden controles de descarga.
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def transcribe_video(url: str, destination: Path, model_size: str = "small", language: str = "en") -> Path:
    from faster_whisper import WhisperModel
    from yt_dlp import YoutubeDL

    if urlparse(url).scheme != "https":
        raise ValueError("Se requiere una URL HTTPS de contenido cuyo acceso esté autorizado.")
    destination.mkdir(parents=True, exist_ok=True)
    with YoutubeDL({"format": "bestaudio/best", "outtmpl": str(destination / "%(id)s.%(ext)s"), "noplaylist": True}) as downloader:
        info = downloader.extract_info(url, download=True)
        audio_path = downloader.prepare_filename(info)
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, language=language, vad_filter=True)
    timeline = [{"start": segment.start, "end": segment.end, "text": segment.text.strip()} for segment in segments]
    source_id = "asr_" + hashlib.sha256(url.encode()).hexdigest()[:12]
    result = {"id": source_id, "title": info.get("title", source_id), "authors": info.get("uploader", "unknown"), "url": url, "year": int(info.get("upload_date", datetime.now().strftime("%Y%m%d"))[:4]), "kind": "video_asr", "modality": "spoken", "language": language, "text": " ".join(segment["text"] for segment in timeline), "segments": timeline, "retrieval_method": "yt_dlp_faster_whisper", "retrieved_at": datetime.now(timezone.utc).isoformat(), "asr_model": model_size, "scope": "Reconocimiento automático de voz local: necesita revisión de errores y nombres propios"}
    target = destination / (source_id + ".json")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--destination", type=Path, default=Path("data/raw/audio"))
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default="en")
    args = parser.parse_args()
    print(transcribe_video(args.url, args.destination, args.model, args.language))
