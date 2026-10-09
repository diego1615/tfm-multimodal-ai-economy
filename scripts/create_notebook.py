"""Construye un notebook portable con nbformat; ejecución independiente posterior."""

from pathlib import Path
import nbformat

BASE = Path(__file__).resolve().parents[1]
cells = [
    nbformat.v4.new_markdown_cell("""# IA, automatización y trabajo
**Diego Fernández · TFM — Proyecto 2**

## Resumen ejecutivo
Se analizan textos web y transcripciones de vídeos TED. El enfoque distingue exposición de tareas, adopción y resultados laborales; los temas identificados son patrones de vocabulario y no predicciones económicas. La síntesis española revisada y el detalle de fuentes están en `outputs/resumen_global.md`. Los resultados numéricos siguientes se calculan a partir de los artefactos de la ejecución, sin datos simulados.

## Contexto y métodos
TF-IDF transforma vocabulario; NMF identifica cinco temas; K-means agrupa documentos. Centroide, centroide con cuota y MMR con cuota comparan selección de evidencia. La cuota restringe cada fuente a una oración y el centroide da un voto a cada documento.

### Supuestos y límites
Corpus deliberado, inglés, capa histórica TED hasta 2017 y textos científicos/institucionales posteriores. No se ejecutaron ASR ni un LLM externo. La transcripción representa contenido hablado y omite imagen, voz y sonido. Sin resumen de referencia no se reporta ROUGE, exactitud o F1.
"""),
    nbformat.v4.new_code_cell("""from pathlib import Path
import os, sys, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown

BASE = Path.cwd()
if BASE.name == 'notebooks':
    BASE = BASE.parent
sys.path.insert(0, str(BASE / 'src'))
from ai_economy.pipeline import run
OUTPUT = BASE / 'outputs'
DATA_DIR = Path(os.environ.get('AI_ECONOMY_DATA_DIR', str(BASE / 'data/raw')))
if (DATA_DIR / 'ted_main.csv').exists() and (DATA_DIR / 'transcripts.csv').exists():
    manifest = run(DATA_DIR, OUTPUT, offline=True)
    print('Modo: nueva ejecución completa desde datos adquiridos y cachés web.')
else:
    manifest = json.loads((OUTPUT / 'run_manifest.json').read_text())
    print('Modo: auditoría de artefactos publicados; no se ejecutaron de nuevo los modelos.')
sns.set_theme(style='white', font_scale=.9)
"""),
    nbformat.v4.new_markdown_cell("""## Datos
La adquisición mantiene modalidades y alcance de texto separados en metadatos. `run_manifest.json` registra hashes, fechas documentadas, unión y fallos; los textos íntegros permanecen en caché local excluida de Git. Los tests sintéticos verifican funciones y nunca forman parte de esta investigación.
"""),
    nbformat.v4.new_code_cell("""sources = pd.read_csv(OUTPUT / 'sources.csv')
topics = json.loads((OUTPUT / 'topics.json').read_text())
comparison = json.loads((OUTPUT / 'summary_comparison.json').read_text())
summary = pd.DataFrame({
    'Fuentes': [manifest['corpus_sources']],
    'Transcripciones': [manifest['spoken_sources']],
    'Textos web': [manifest['written_sources']],
    'Palabras': [manifest['corpus_words']],
    'Oraciones candidatas': [manifest['candidate_sentences']]
})
display(summary)
display(sources[['source_ref', 'title', 'authors', 'year', 'modality', 'words', 'retrieval_method']])
assert sources.source_ref.is_unique
assert set(sources.modality) == {'spoken', 'written'}
assert int(sources.words.sum()) == manifest['corpus_words']
display(pd.DataFrame(manifest['web_audit'])[['id', 'status']])
print('Filas de transcripción duplicadas eliminadas:', manifest['ted_audit']['transcript_exact_duplicate_rows_removed'])
print('Charlas fuera del foco temático excluidas:', manifest['ted_audit']['off_topic_talks_removed'])
"""),
    nbformat.v4.new_markdown_cell("""## Resultados
### Temas por fuente
Las filas son documentos; las columnas son temas NMF. El peso se normaliza dentro de cada documento. El gráfico permite reconocer conversaciones compartidas y fuentes complementarias, sin equiparar peso léxico con relevancia social.
"""),
    nbformat.v4.new_code_cell("""profiles = pd.read_csv(OUTPUT / 'topic_profiles.csv', index_col=0)
display(pd.DataFrame([{'Tema': topic['topic'], 'Términos principales': ', '.join(topic['terms'][:6])} for topic in topics['topics']]))
labels = [f'{row.source_ref} · {row.authors[:22]} · {row.year}' for row in sources.itertuples()]
fig, ax = plt.subplots(figsize=(11, max(7, len(sources) * .38)))
sns.heatmap(profiles, yticklabels=labels, cmap='Blues', vmin=0, vmax=1,
            annot=True, fmt='.2f', linewidths=.7,
            cbar_kws={'label': 'Peso relativo por documento'}, ax=ax)
ax.set_title('Temas NMF: fuentes escritas y transcripciones TED', loc='left', pad=14)
ax.set_xlabel('Tema: términos definidos en la tabla')
ax.set_ylabel('Fuente y año')
plt.tight_layout()
plt.show()
"""),
    nbformat.v4.new_markdown_cell("""La lectura de cada celda debe combinarse con los términos y la fuente. Si un documento tiene peso alto en varios temas, conecta vocabularios; si concentra su peso en uno, no significa que sólo trate esa cuestión. Los corpus de épocas y géneros distintos pueden separarse por estilo.

### Similitud entre fuentes
La matriz TF-IDF permite encontrar puentes entre transcripciones y textos web. La diagonal corresponde a cada fuente consigo misma y no debe contarse como vínculo entre fuentes distintas.
"""),
    nbformat.v4.new_code_cell("""similarity = pd.read_csv(OUTPUT / 'source_similarity.csv', index_col=0)
assert np.allclose(similarity.values, similarity.values.T)
assert np.allclose(np.diag(similarity.values), 1)
fig, ax = plt.subplots(figsize=(10.5, 9))
sns.heatmap(similarity, cmap='YlGnBu', vmin=0, vmax=1, square=True,
            annot=True, fmt='.2f', annot_kws={'fontsize': 7},
            cbar_kws={'label': 'Similitud coseno TF-IDF'}, ax=ax)
ax.set_title('Puentes léxicos entre fuentes: IDs registrados en la tabla', loc='left', pad=14)
ax.set_xlabel('Fuente'); ax.set_ylabel('Fuente')
plt.tight_layout(); plt.show()
pairs = []
for i in range(len(sources)):
    for j in range(i + 1, len(sources)):
        pairs.append({'Fuente A': sources.iloc[i].source_ref,
                      'Fuente B': sources.iloc[j].source_ref,
                      'Modalidades distintas': sources.iloc[i].modality != sources.iloc[j].modality,
                      'Coseno': float(similarity.iloc[i, j])})
display(pd.DataFrame(pairs).query('`Modalidades distintas`').sort_values('Coseno', ascending=False).head(5))
"""),
    nbformat.v4.new_markdown_cell("""La tabla presenta los cinco puentes más próximos entre modalidades, excluyendo pares de un mismo tipo. Una relación alta señala vocabulario compartido; la validación de acuerdo o contradicción requiere lectura humana.

### Comparación de resúmenes
El control de centroide con cuota evita confundir diversificación MMR con la regla de una oración por fuente. Todas las métricas son internas y el presupuesto de selección es el mismo.
"""),
    nbformat.v4.new_code_cell("""metrics = pd.DataFrame(comparison['metrics']).T.drop(columns='note').astype(float)
display(metrics.round(4))
metrics[['source_coverage_fraction', 'mean_pairwise_redundancy', 'source_balanced_representation_cosine']].T.plot.bar(
    figsize=(11, 4.8), rot=0, color=['#7e96b5', '#4b83a3', '#176e72'])
plt.xticks(range(3), ['Cobertura de fuentes ↑', 'Redundancia ↓', 'Representación léxica ↑'])
plt.ylabel('Valor métrico'); plt.title('Centroide, control con cuota y MMR', loc='left')
plt.legend(title='Método', bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout(); plt.show()
display(pd.DataFrame(comparison['sensitivity'])[['lambda_relevance', 'mean_centroid_relevance', 'mean_pairwise_redundancy', 'source_coverage_fraction']].round(4))
evidence = json.loads((OUTPUT / 'evidence.json').read_text())
assert len({item['source_id'] for item in evidence}) == len(evidence)
display(pd.DataFrame(evidence)[['citation', 'source_id', 'sentence_id', 'relevance_score']])
"""),
    nbformat.v4.new_markdown_cell("""## Síntesis y conclusiones
La narrativa revisada siguiente distingue argumentos históricos, exposición potencial de tareas y decisiones de implementación. Cada punto indica sus fuentes; no se presenta como una predicción ni como verificación automática de hechos.
"""),
    nbformat.v4.new_code_cell("""display(Markdown((OUTPUT / 'resumen_global.md').read_text(encoding='utf-8')))
"""),
    nbformat.v4.new_markdown_cell("""## Verificación y continuidad
El notebook conserva tablas y gráficos sin corpus íntegro. Una reproducción completa requiere adquirir los CSV y páginas web; sin ellos, el modo de auditoría revisa los artefactos publicados y lo informa al inicio. Los hashes y versiones de ejecución están en el manifiesto.

La mejora prioritaria sería una evaluación humana con referencia que mida cobertura factual y legibilidad. Luego se ampliaría la capa audiovisual contemporánea, se probarían embeddings y se incorporaría audio con revisión de errores ASR y marcas temporales. Mantener alcance, fuentes fallidas y costes visibles es parte de la reproducibilidad.
""")
]
notebook = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.10"}})
target = BASE / 'notebooks/investigacion_multimodal.ipynb'
target.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(notebook, target)
print(target)
