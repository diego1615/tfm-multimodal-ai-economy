"""Explorador de resultados públicos, sin corpus completo ni credenciales."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "outputs"
st.set_page_config(page_title="IA, automatización y trabajo", page_icon="📚", layout="wide")
st.title("IA, automatización y trabajo")
st.caption("TFM · Investigación de fuentes escritas y transcripciones audiovisuales · Diego Fernández")
if not (OUTPUT / "run_manifest.json").exists():
    st.error("Ejecute primero el pipeline o incorpore los resultados públicos de ejemplo.")
    st.stop()
manifest = json.loads((OUTPUT / "run_manifest.json").read_text())
sources = pd.read_csv(OUTPUT / "sources.csv")
comparison = json.loads((OUTPUT / "summary_comparison.json").read_text())
col1, col2, col3, col4 = st.columns(4)
col1.metric("Fuentes", manifest["corpus_sources"])
col2.metric("Transcripciones de vídeo", manifest["spoken_sources"])
col3.metric("Textos web", manifest["written_sources"])
col4.metric("Palabras procesadas", f"{manifest['corpus_words']:,}")
st.info("Las dos modalidades se unifican en texto. No se procesaron imagen, prosodia ni sonido. Los temas y similitudes son patrones de vocabulario, no una validación de hechos.")
overview, corpus, topics, methods = st.tabs(["Síntesis", "Fuentes", "Temas y vínculos", "Comparación de métodos"])
with overview:
    st.markdown((OUTPUT / "resumen_global.md").read_text(encoding="utf-8"))
with corpus:
    modality = st.multiselect("Modalidad", options=sorted(sources.modality.unique()), default=sorted(sources.modality.unique()))
    query = st.text_input("Buscar por autor o título")
    filtered = sources[sources.modality.isin(modality)].copy()
    if query:
        filtered = filtered[filtered.title.str.contains(query, case=False, regex=False) | filtered.authors.str.contains(query, case=False, regex=False)]
    st.dataframe(filtered[["source_ref", "title", "authors", "year", "modality", "words", "dominant_topic", "url"]], hide_index=True, use_container_width=True, column_config={"url": st.column_config.LinkColumn("Fuente")})
    st.caption("La búsqueda filtra metadatos; no es un sistema de preguntas con LLM ni búsqueda semántica.")
with topics:
    st.image(str(OUTPUT / "figures/topic_profiles.png"), caption="NMF: peso relativo de temas dentro de cada documento.")
    st.image(str(OUTPUT / "figures/source_similarity.png"), caption="Coincidencias léxicas TF-IDF; no identifican acuerdo ni causalidad.")
with methods:
    st.image(str(OUTPUT / "figures/summary_comparison.png"))
    st.dataframe(pd.DataFrame(comparison["metrics"]).T.drop(columns="note"), use_container_width=True)
    st.markdown("Se compara centroide, centroide con cuota y MMR con la misma cuota. **Cuota** significa una oración por fuente. Esto separa la diversificación de la restricción de representación.")
    st.dataframe(pd.DataFrame(comparison["sensitivity"])[["lambda_relevance", "source_coverage_fraction", "mean_centroid_relevance", "mean_pairwise_redundancy"]], hide_index=True)
    st.caption("Sin resumen de referencia ni etiquetas humanas, estas métricas no representan ROUGE, F1 o exactitud factual.")
