"""Modelos sin API externa: TF-IDF, NMF, clustering y comparación de resúmenes."""

from __future__ import annotations

import re
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from .corpus import sentence_split

ORAL_FILLERS = {"like", "know", "going", "think", "just", "really", "lot", "actually", "got", "said", "say", "things", "thing", "kind", "sort", "bit", "ve", "ll", "don", "let"}
STOP_WORDS = sorted(set(ENGLISH_STOP_WORDS) | ORAL_FILLERS)


def topic_analysis(documents: list[dict], n_topics: int = 5, seed: int = 42) -> dict:
    # El vocabulario depende exclusivamente de textos adquiridos. No son embeddings
    # semánticos y las similitudes no representan acuerdo ni evidencia causal.
    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS, ngram_range=(1, 2), min_df=2, max_df=0.88, max_features=16000, sublinear_tf=True)
    matrix = vectorizer.fit_transform([document["text"] for document in documents])
    if matrix.shape[1] < 10:
        raise ValueError("El corpus no contiene vocabulario suficiente para modelar temas.")
    n_topics = min(n_topics, len(documents) - 1, matrix.shape[1] - 1)
    nmf = NMF(n_components=n_topics, init="nndsvda", random_state=seed, max_iter=1000, tol=1e-5)
    weights = nmf.fit_transform(matrix)
    denominator = weights.sum(axis=1, keepdims=True)
    profiles = np.divide(weights, denominator, out=np.zeros_like(weights), where=denominator != 0)
    words = vectorizer.get_feature_names_out()
    terms = [{"topic": f"T{i + 1}", "terms": words[np.argsort(component)[-10:][::-1]].tolist()} for i, component in enumerate(nmf.components_)]
    cluster_model = KMeans(n_clusters=min(4, len(documents) - 1), n_init=20, random_state=seed)
    clusters = cluster_model.fit_predict(matrix)
    cluster_counts = Counter(clusters.tolist())
    silhouette = float(silhouette_score(matrix, clusters, metric="cosine")) if 1 < len(cluster_counts) < len(documents) else None
    return {"vectorizer": vectorizer, "matrix": matrix, "nmf": nmf, "profiles": profiles, "terms": terms, "similarity": cosine_similarity(matrix), "clusters": clusters, "diagnostics": {"vocabulary_size": matrix.shape[1], "n_topics": n_topics, "n_clusters": len(cluster_counts), "silhouette_cosine": silhouette, "nmf_relative_reconstruction_residual": float(nmf.reconstruction_err_ / np.sqrt(matrix.multiply(matrix).sum())), "extra_oral_stopwords": sorted(ORAL_FILLERS), "interpretation": "Diagnósticos internos de un corpus pequeño y deliberado; no precisión de clasificación, no validación factual ni representatividad poblacional."}}


def sentence_corpus(documents: list[dict]) -> tuple[list[dict], TfidfVectorizer, object, np.ndarray]:
    rows = []
    # Deduplicación global exacta, antes de comparar los métodos de selección.
    seen = set()
    for document in documents:
        for ordinal, sentence in enumerate(sentence_split(document["text"]), 1):
            normalized = re.sub(r"\W+", " ", sentence.lower()).strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            rows.append({"sentence_id": f"{document['id']}:s{ordinal}", "source_id": document["id"], "title": document["title"], "url": document["url"], "text": sentence, "modality": document["modality"], "words": len(sentence.split())})
    if len(rows) < 5:
        raise ValueError("No hay suficientes oraciones para resumir.")
    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS, ngram_range=(1, 2), max_features=20000, min_df=1, sublinear_tf=True)
    matrix = vectorizer.fit_transform([row["text"] for row in rows])
    # Un voto por fuente: una charla larga no pesa más que un abstract breve.
    centroids = []
    for source_id in dict.fromkeys(row["source_id"] for row in rows):
        indices = [i for i, row in enumerate(rows) if row["source_id"] == source_id]
        centroids.append(normalize(np.asarray(matrix[indices].mean(axis=0))))
    global_centroid = normalize(np.mean(np.vstack(centroids), axis=0, keepdims=True))
    relevance = np.asarray(matrix @ global_centroid.T).ravel()
    return rows, vectorizer, matrix, relevance


def select_mmr(rows: list[dict], matrix: object, relevance: np.ndarray, count: int = 10, diversity_weight: float = 0.65, max_per_source: int = 1) -> list[int]:
    """MMR: λ relevancia − (1−λ) redundancia; cuota explícita por fuente."""
    if not 0 <= diversity_weight <= 1:
        raise ValueError("lambda debe estar entre 0 y 1")
    selected, source_counts = [], Counter()
    remaining = set(range(len(rows)))
    while remaining and len(selected) < count:
        eligible = sorted(i for i in remaining if source_counts[rows[i]["source_id"]] < max_per_source)
        if not eligible:
            break
        redundancy = cosine_similarity(matrix[eligible], matrix[selected]).max(axis=1) if selected else np.zeros(len(eligible))
        scores = diversity_weight * relevance[eligible] - (1 - diversity_weight) * redundancy
        chosen = eligible[int(np.argmax(scores))]
        selected.append(chosen)
        source_counts[rows[chosen]["source_id"]] += 1
        remaining.remove(chosen)
    return selected


def summary_metrics(indices: list[int], rows: list[dict], matrix: object, relevance: np.ndarray, document_ids: list[str], total_words: int) -> dict:
    if not indices:
        raise ValueError("Resumen vacío")
    within = cosine_similarity(matrix[indices])
    pairs = within[np.triu_indices(len(indices), k=1)]
    coverage = cosine_similarity(matrix, matrix[indices]).max(axis=1)
    # Misma ponderación por fuente en evaluación y objetivo de síntesis.
    source_coverage = []
    for source_id in document_ids:
        group = [i for i, row in enumerate(rows) if row["source_id"] == source_id]
        if group:
            source_coverage.append(float(coverage[group].mean()))
    selected_words = sum(rows[i]["words"] for i in indices)
    return {"selected_sentences": len(indices), "selected_words_internal": selected_words, "source_coverage_fraction": len({rows[i]["source_id"] for i in indices}) / len(document_ids), "mean_centroid_relevance": float(np.mean(relevance[indices])), "mean_pairwise_redundancy": float(pairs.mean()) if len(pairs) else 0.0, "source_balanced_representation_cosine": float(np.mean(source_coverage)), "compression_ratio_internal": selected_words / total_words, "note": "Métricas internas: no equivalen a calidad factual, ROUGE, exactitud o satisfacción de lector. No existe resumen de referencia."}


def compare_summaries(documents: list[dict], count: int = 10) -> dict:
    rows, vectorizer, matrix, relevance = sentence_corpus(documents)
    source_count = len({row["source_id"] for row in rows})
    count = min(count, source_count)
    centroid = np.argsort(-relevance, kind="stable")[:count].tolist()
    centroid_quota, seen_sources = [], set()
    for index in np.argsort(-relevance, kind="stable").tolist():
        if rows[index]["source_id"] in seen_sources:
            continue
        centroid_quota.append(index)
        seen_sources.add(rows[index]["source_id"])
        if len(centroid_quota) == count:
            break
    mmr = select_mmr(rows, matrix, relevance, count=count, diversity_weight=0.65)
    document_ids = [document["id"] for document in documents]
    total_words = sum(len(document["text"].split()) for document in documents)
    metrics = {method: summary_metrics(indices, rows, matrix, relevance, document_ids, total_words) for method, indices in (("centroid", centroid), ("centroid_quota", centroid_quota), ("mmr", mmr))}
    sensitivity = [{"lambda_relevance": value, **summary_metrics(select_mmr(rows, matrix, relevance, count=count, diversity_weight=value), rows, matrix, relevance, document_ids, total_words)} for value in (0.50, 0.65, 0.80)]
    # Sólo citas breves del método elegido. Baseline conserva IDs y puntuaciones,
    # evitando duplicar citas de la misma fuente en archivos públicos.
    evidence = []
    for ordinal, index in enumerate(mmr, 1):
        row = rows[index]
        evidence.append({"citation": f"E{ordinal:02}", "sentence_id": row["sentence_id"], "source_id": row["source_id"], "title": row["title"], "url": row["url"], "modality": row["modality"], "relevance_score": round(float(relevance[index]), 6), "character_length_internal": len(row["text"]), "excerpt": " ".join(row["text"].split()[:14]) + (" …" if row["words"] > 14 else ""), "excerpt_scope": "Cita breve para trazabilidad; oraciones completas sólo en caché privada"})
    return {"metrics": metrics, "sensitivity": sensitivity, "evidence": evidence, "centroid_sentence_ids": [rows[index]["sentence_id"] for index in centroid], "centroid_quota_sentence_ids": [rows[index]["sentence_id"] for index in centroid_quota], "mmr_sentence_ids": [rows[index]["sentence_id"] for index in mmr], "candidate_sentences": len(rows)}
