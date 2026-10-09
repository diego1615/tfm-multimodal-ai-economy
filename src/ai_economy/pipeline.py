"""CLI de investigación con productos públicos y corpus local separado."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .analysis import compare_summaries, topic_analysis
from .corpus import download_ted, load_ted, load_web
from .sources import KAGGLE_URL


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def source_metadata(documents: list[dict], result: dict) -> pd.DataFrame:
    rows = []
    for index, document in enumerate(documents):
        row = {key: value for key, value in document.items() if key not in ("text", "selector")}
        row.update({"words": len(document["text"].split()), "dominant_topic": result["terms"][int(np.argmax(result["profiles"][index]))]["topic"], "cluster": int(result["clusters"][index])})
        rows.append(row)
    return pd.DataFrame(rows)


def make_figures(documents: list[dict], result: dict, summary: dict, output: Path) -> None:
    figure_dir = output / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="white", font_scale=0.95, rc={"axes.titleweight": "bold", "axes.labelcolor": "#172b4d", "text.color": "#172b4d"})
    labels = [f"{document['year']} · {'TED' if document['modality'] == 'spoken' else 'WEB'} · {document['title'][:49]}" for document in documents]
    topic_labels = [item["topic"] for item in result["terms"]]
    fig, ax = plt.subplots(figsize=(13.5, max(7.8, len(documents) * 0.44)))
    sns.heatmap(result["profiles"], yticklabels=labels, xticklabels=topic_labels, cmap="Blues", vmin=0, vmax=1, annot=True, fmt=".2f", linewidths=0.7, linecolor="#f0f3f7", cbar_kws={"label": "Peso temático normalizado por documento"}, ax=ax)
    ax.set_title("IA, automatización y trabajo: perfiles temáticos por fuente", loc="left", pad=18)
    ax.set_xlabel("Temas NMF · etiquetas por términos de mayor peso", labelpad=12)
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=0)
    fig.text(0.01, 0.005, "Fuente: TED/Kaggle y textos web registrados. Temas aprendidos sin etiquetas; peso ≠ veracidad ni prevalencia social.", fontsize=9)
    fig.tight_layout(rect=(0, 0.025, 1, 1))
    fig.savefig(figure_dir / "topic_profiles.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Orden por tema principal, modalidad y fecha para facilitar comparación.
    order = sorted(range(len(documents)), key=lambda index: (int(np.argmax(result["profiles"][index])), documents[index]["modality"], documents[index]["year"]))
    short_labels = [f"S{index + 1:02} · {documents[index]['authors'][:22]}" for index in order]
    fig, ax = plt.subplots(figsize=(11.8, 10.3))
    sns.heatmap(result["similarity"][np.ix_(order, order)], cmap="YlGnBu", vmin=0, vmax=1, annot=True, fmt=".2f", annot_kws={"fontsize": 7}, yticklabels=short_labels, xticklabels=short_labels, square=True, linewidths=0.4, cbar_kws={"label": "Similitud coseno TF-IDF"}, ax=ax)
    ax.set_title("Puentes y diferencias entre discursos audiovisuales y textos web", loc="left", pad=18)
    ax.tick_params(axis="x", rotation=75)
    ax.tick_params(axis="y", rotation=0)
    fig.text(0.01, 0.01, "Sxx identifica sources.csv. Orden por tema dominante. Coincidencia de vocabulario ≠ acuerdo ni causalidad.", fontsize=9)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(figure_dir / "source_similarity.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    values = summary["metrics"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.1))
    for ax, key, title in zip(axes, ("source_coverage_fraction", "mean_pairwise_redundancy", "source_balanced_representation_cosine"), ("Cobertura de fuentes ↑", "Redundancia léxica ↓", "Representación del corpus ↑")):
        metric_values = [values[method][key] for method in ("centroid", "centroid_quota", "mmr")]
        bars = ax.bar(["Centroide", "Centroide\n+ cuota", "MMR\n+ cuota"], metric_values, color=["#7e96b5", "#4b83a3", "#176e72"], width=0.6)
        ax.set_title(title, fontsize=11)
        ax.set_ylim(0, max(0.15, max(metric_values) * 1.28))
        ax.spines[["top", "right"]].set_visible(False)
        for bar, value in zip(bars, metric_values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + ax.get_ylim()[1] * 0.03, f"{value:.3f}", ha="center", fontsize=10)
    fig.suptitle("Resumen: relevancia, cuota por fuente y diversificación MMR", x=0.04, ha="left", fontsize=16, fontweight="bold")
    fig.text(0.04, 0.01, "Igual presupuesto. Cuota = máximo una oración por fuente. Comparación interna, sin validación de exactitud factual.", fontsize=9)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    fig.savefig(figure_dir / "summary_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def narrative(documents: list[dict], topics: dict, summary: dict) -> str:
    source_refs = {document["id"]: f"S{index + 1:02}" for index, document in enumerate(documents)}
    def speaker_reference(speaker: str) -> str:
        return ", ".join(source_refs[document["id"]] for document in documents if document["authors"] == speaker)
    def cite(source_id: str) -> str:
        return source_refs.get(source_id, "")
    words = sum(len(document["text"].split()) for document in documents)
    spoken = sum(document["modality"] == "spoken" for document in documents)
    years = [document["year"] for document in documents]
    lines = ["# Resumen global: IA, automatización, productividad y trabajo", "", f"La ejecución integra **{len(documents)} fuentes**: {spoken} transcripciones audiovisuales y {len(documents) - spoken} textos web, con {words:,} palabras procesadas. El corpus comprende publicaciones de {min(years)} a {max(years)} y está íntegramente en inglés. La síntesis narrativa siguiente es una interpretación revisada; la selección automática de evidencia se obtiene con TF-IDF y MMR, sin una API de LLM.", "", "## Visión general e ideas clave", ""]
    autor, brynjolfsson, goldbloom = speaker_reference("David Autor"), speaker_reference("Erik Brynjolfsson"), speaker_reference("Anthony Goldbloom")
    if autor and brynjolfsson:
        lines.append(f"La discusión sobre automatización combina sustitución de tareas, complementariedad entre personas y máquinas y capacidad de reorganizar la producción; reducirla a una predicción única de desaparición del empleo pierde esa diversidad conceptual. La lectura conjunta de Autor y Brynjolfsson permite formular esta tensión sin tratar sus charlas como estimaciones actuales del mercado laboral. [{autor}; {brynjolfsson}]")
    if goldbloom:
        lines += ["", f"Goldbloom organiza su argumento alrededor de tareas frecuentes frente a situaciones nuevas; esta distinción es una perspectiva histórica de 2016 y debe contrastarse con las capacidades posteriores de IA generativa. No constituye un límite permanente demostrado de la tecnología. [{goldbloom}]"]
    if cite("gpts2023") and cite("ilo2025"):
        lines += ["", f"Los trabajos contemporáneos distinguen exposición potencial de tareas de pérdida efectiva de puestos. El estudio de Eloundou y colaboradores analiza capacidades y exposición; el índice de la OIT describe posibilidades de transformación por ocupación. Sus porcentajes y universos de referencia no se pueden combinar como si midieran una sola tasa de desempleo futura. [{cite('gpts2023')}; {cite('ilo2025')}]"]
    if cite("nber31161"):
        lines += ["", f"El estudio de Brynjolfsson, Li y Raymond aporta evidencia de una implementación concreta de asistencia generativa en atención al cliente. Su utilidad para este corpus consiste en conectar el debate general con efectos observados en un contexto productivo delimitado; extrapolar ese resultado a todos los sectores requiere evidencia adicional. [{cite('nber31161')}]"]
    if cite("nber32487"):
        lines += ["", f"Acemoglu introduce una distinción necesaria entre mejora de tareas individuales y crecimiento agregado. La magnitud macroeconómica depende de la extensión de las tareas afectadas y de los ahorros o aumentos de productividad; una demostración llamativa no basta para cuantificar el efecto sobre el PIB. [{cite('nber32487')}]"]
    if cite("imf2024") and cite("cbo2024"):
        lines += ["", f"Los textos institucionales del FMI y la CBO amplían el análisis hacia desigualdad, adaptación de capacidades y efectos económicos y presupuestarios. La lectura para una decisión institucional es evaluar adopción, complementariedad y distribución junto con la capacidad técnica, conservando la incertidumbre sobre los efectos netos. [{cite('imf2024')}; {cite('cbo2024')}]"]
    lines += ["", "## Qué añade el aprendizaje automático", "", f"NMF identifica {len(topics['terms'])} patrones de vocabulario. Las etiquetas siguientes son términos de mayor peso, no categorías objetivas ni conclusiones causales:", ""]
    for item in topics["terms"]:
        lines.append(f"- **{item['topic']}**: {', '.join(item['terms'][:6])}.")
    centroid, mmr = summary["metrics"]["centroid"], summary["metrics"]["mmr"]
    quota = summary["metrics"]["centroid_quota"]
    lines += ["", f"Con el mismo presupuesto de {mmr['selected_sentences']} oraciones, el centroide cubre {centroid['source_coverage_fraction']:.1%} de las fuentes y MMR {mmr['source_coverage_fraction']:.1%}. La redundancia media es {centroid['mean_pairwise_redundancy']:.3f} y {mmr['mean_pairwise_redundancy']:.3f}, respectivamente. La cuota de una oración por fuente es parte explícita de MMR: explica una porción de esa diferencia y no demuestra superioridad factual.", "", "## Evidencia seleccionada automáticamente", "", "Las citas breves permiten ubicar la oración identificada en la caché local. No sustituyen la lectura de la fuente; el corpus completo y las oraciones completas permanecen fuera del repositorio público.", ""]
    lines.insert(lines.index("## Evidencia seleccionada automáticamente"), f"El control centroide con la misma cuota obtiene cobertura {quota['source_coverage_fraction']:.1%} y redundancia {quota['mean_pairwise_redundancy']:.3f}; comparar este control con MMR permite distinguir la contribución de la penalización de redundancia de la cuota por fuente.")
    for evidence in summary["evidence"]:
        ref = source_refs[evidence["source_id"]]
        lines.append(f"- **{evidence['citation']} / {ref}** · {evidence['title']} · `{evidence['sentence_id']}` · [Fuente]({evidence['url']}).")
    lines += ["", "## Interpretación de las visualizaciones", "", "El mapa de calor temático muestra cuánto peso relativo asigna NMF a cada patrón dentro de cada fuente. Permite localizar conversaciones compartidas y textos que aportan vocabulario distinto. La matriz de similitud muestra puentes léxicos entre fuentes, incluidas las dos modalidades; una similitud baja puede responder a género discursivo, extensión o época y no implica desacuerdo.", "", "## Alcance y limitaciones", "", "La muestra es deliberada y pequeña. TED aporta una capa histórica hasta 2017 y las fuentes web una capa posterior: sus diferencias no identifican una evolución causal. Las transcripciones excluyen imagen, prosodia y sonido; no se ejecutó reconocimiento de voz. Los abstracts contienen menos contexto que los informes completos. TF-IDF depende del vocabulario, NMF es sensible al número de temas y MMR puede seleccionar oraciones que necesiten contexto. No hay etiquetas ni resumen de referencia: no se reportan exactitud, F1 o ROUGE. Las conclusiones requieren revisión humana y no predicen empleo.", "", "## Registro de fuentes", "", "| ID | Año | Modalidad | Fuente |", "|---|---:|---|---|"]
    position = lines.index("## Alcance y limitaciones")
    cross_pairs = [(float(topics["similarity"][i, j]), i, j) for i in range(len(documents)) for j in range(i + 1, len(documents)) if documents[i]["modality"] != documents[j]["modality"]]
    maximum, first, second = max(cross_pairs)
    interpretation = f"El puente más próximo entre modalidades une «{documents[first]['title']}» y «{documents[second]['title']}», con coseno {maximum:.3f}. Esta relación señala un vocabulario común que merece comparación cualitativa; no demuestra acuerdo de sus conclusiones. [{source_refs[documents[first]['id']]}; {source_refs[documents[second]['id']]}]"
    lines.insert(position, interpretation)
    ilo_indices = [i for i, document in enumerate(documents) if document["id"] == "ilo2025"]
    if ilo_indices:
        index = ilo_indices[0]
        dominant = int(np.argmax(topics["profiles"][index]))
        lines.insert(position, f"En la fuente OIT predomina {topics['terms'][dominant]['topic']} con peso {topics['profiles'][index, dominant]:.2f}, cuyo vocabulario principal es {', '.join(topics['terms'][dominant]['terms'][:4])}. Es un ejemplo concreto de cómo el mapa localiza exposición de tareas y trabajo dentro de este corpus. [{source_refs['ilo2025']}]")
    for document in documents:
        title = document["title"].replace("|", " ")
        lines.append(f"| {source_refs[document['id']]} | {document['year']} | {document['modality']} | [{title}]({document['url']}) |")
    return "\n".join(lines) + "\n"


def run(data_dir: Path, output: Path, offline: bool = False) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    if not (data_dir / "ted_main.csv").exists() or not (data_dir / "transcripts.csv").exists():
        if offline:
            raise FileNotFoundError("Faltan ted_main.csv/transcripts.csv. Descargue el dataset antes de ejecutar offline.")
        download_ted(data_dir)
    ted, ted_audit = load_ted(data_dir)
    web, web_audit = load_web(data_dir / "web", offline=offline)
    if not web:
        raise RuntimeError("No se adquirió ninguna fuente escrita. Un corpus sólo TED no cumple el proyecto multimodal.")
    documents = ted + web
    if len(ted) < 2 or len(web) < 2:
        raise RuntimeError("La ejecución necesita al menos dos transcripciones y dos textos web.")
    ids = [document["id"] for document in documents]
    if len(ids) != len(set(ids)):
        raise ValueError("Identificadores de fuente duplicados.")
    topics = topic_analysis(documents)
    summary = compare_summaries(documents, count=10)
    metadata = source_metadata(documents, topics)
    metadata.insert(0, "source_ref", [f"S{i + 1:02}" for i in range(len(documents))])
    metadata.to_csv(output / "sources.csv", index=False)
    write_json(output / "sources.json", metadata.to_dict(orient="records"))
    write_json(output / "topics.json", {"topics": topics["terms"], "diagnostics": topics["diagnostics"]})
    write_json(output / "summary_comparison.json", {key: value for key, value in summary.items() if key != "evidence"})
    write_json(output / "evidence.json", summary["evidence"])
    pd.DataFrame(topics["profiles"], index=metadata.source_ref, columns=[item["topic"] for item in topics["terms"]]).to_csv(output / "topic_profiles.csv", index_label="source_ref")
    pd.DataFrame(topics["similarity"], index=metadata.source_ref, columns=metadata.source_ref).to_csv(output / "source_similarity.csv", index_label="source_ref")
    make_figures(documents, topics, summary, output)
    (output / "resumen_global.md").write_text(narrative(documents, topics, summary), encoding="utf-8")
    runtime = {package: importlib.metadata.version(package) for package in ("numpy", "pandas", "scikit-learn", "matplotlib", "seaborn", "requests", "beautifulsoup4")}
    manifest = {"executed_at": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(), "packages": runtime, "random_seed": 42, "offline": offline, "corpus_sources": len(documents), "spoken_sources": len(ted), "written_sources": len(web), "corpus_words": int(metadata.words.sum()), "candidate_sentences": summary["candidate_sentences"], "year_range": [int(metadata.year.min()), int(metadata.year.max())], "kaggle_url": KAGGLE_URL, "ted_audit": ted_audit, "web_audit": web_audit, "audio_asr_executed": False, "visual_video_analysis_executed": False, "external_llm_executed": False, "notes": ["Recuperación de transcripciones preexistentes de vídeos, no transcripción automática de audio ejecutada.", "La caché del lector web es texto de la página, puede ser parcial y no equivale a HTML original.", "Fecha de adquisición null cuando no se dispone de registro; processed_at es fecha de procesamiento.", "No se publican corpus completos ni tokens de acceso. Datos crudos/cachés quedan excluidos del repositorio."]}
    write_json(output / "run_manifest.json", manifest)
    private = output / "private"
    private.mkdir(exist_ok=True)
    with (private / "corpus.jsonl").open("w", encoding="utf-8") as handle:
        for document in documents:
            handle.write(json.dumps(document, ensure_ascii=False) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="TFM: investigación IA y trabajo con textos web y transcripciones TED")
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--offline", action="store_true", help="Utiliza solamente datos y fuentes web ya adquiridos")
    args = parser.parse_args()
    manifest = run(args.data_dir, args.output, offline=args.offline)
    print(json.dumps({"sources": manifest["corpus_sources"], "words": manifest["corpus_words"], "output": str(args.output), "failed_web_sources": sum(item["status"] == "failed" for item in manifest["web_audit"])}, indent=2))


if __name__ == "__main__":
    main()
