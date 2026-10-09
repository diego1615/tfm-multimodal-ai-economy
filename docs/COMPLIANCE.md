# Matriz de cumplimiento de la consigna · Proyecto 2

Esta revisión contrasta el proyecto con **todas las obligaciones y preguntas de la opción «Resumen multimodal de investigación»**, páginas 7–9 de `enunciado_TFM_MDATA2-.pdf`, y con las condiciones comunes de las páginas 1–4. El documento `Fuentes-de-datos-TFM.pdf` incluye Kaggle entre las fuentes propuestas, sin exigir utilizar todas las fuentes enumeradas.

La explicación principal es el relato continuo de [README.md](../README.md). La matriz localiza las respuestas y sus evidencias; no sustituye la narrativa ni asigna una calificación.

**Estado:** requisitos técnicos y documentales comprobados el 9 de octubre de 2026. Código, resultados, visualizaciones y notebook publicados y verificados en el repositorio público [diego1615/tfm-multimodal-ai-economy](https://github.com/diego1615/tfm-multimodal-ai-economy); los archivos remotos coinciden con las versiones revisadas. Compartir posteriormente el enlace en el campus, dentro del plazo institucional, corresponde al alumno.

## Alcance de la elección

El enunciado permite elegir entre resumen multimodal y asistente RAG. Este repositorio desarrolla **resumen multimodal**: 12 transcripciones de vídeos TED y seis documentos web, unificados en texto. Los requisitos de cinco formatos, vector store, asistente RAG y mejora de recuperación pertenecen a la otra opción y no son obligaciones de este proyecto.

Se recuperan transcripciones preexistentes de vídeos; no se afirma haber ejecutado reconocimiento de voz ni análisis de imagen. La consigna admite expresamente trabajar con transcripciones de contenido hablado. La extensión de audio incluida es opcional y no participa en los resultados publicados.

## Obligaciones comunes y entregables

| ID | Requisito | Cumplimiento y evidencia publicada |
|---|---|---|
| C01 | Repositorio independiente en el GitHub personal | Repositorio público independiente indicado arriba, con código, resultados, visualizaciones, documentación y notebook publicados |
| C02 | Código fuente completo | [Módulos](../src/ai_economy/), [script del notebook](../scripts/create_notebook.py), [cuaderno](../notebooks/investigacion_multimodal.ipynb), [app](../app.py), [configuración/dependencias](../pyproject.toml) y [pruebas](../tests/) |
| C03 | Resultados obtenidos, outputs, métricas y ejemplos | [Manifiesto real](../outputs/run_manifest.json), [fuentes](../outputs/sources.csv), [temas](../outputs/topics.json), [comparación de resúmenes](../outputs/summary_comparison.json), [evidencias](../outputs/evidence.json) y outputs del cuaderno |
| C04 | Visualizaciones realizadas | Tres PNG calculados en [outputs/figures](../outputs/figures/) y gráficos del notebook; se muestran también en el README |
| C05 | Markdown narrativo con problema, datos, modelos, resultados y conclusiones | README: «De la pregunta a los datos», «Limpieza y unificación», «Modelos y resumen global», «Qué muestran las visualizaciones» y «Límites y siguientes mejoras» |
| C06 | Describir proceso y justificar decisiones técnicas | Las secciones citadas explican selección temática, modalidades, adquisición, limpieza, TF-IDF/NMF/K-means y alternativas de resumen |
| C07 | Responder las preguntas de manera integrada | Las seis preguntas y todas sus dimensiones se localizan en la matriz siguiente dentro del README principal |
| C08 | Ejemplos, métricas y visualizaciones relevantes | Notebook ejecutado, tres enfoques comparados, sensibilidad de MMR, síntesis con referencias y figuras derivadas del corpus |
| C09 | Dificultades encontradas y resolución | README: duplicados de transcripciones, conflictos de URL, marcas de interfaz, charlas fuera del foco, diferencias de adquisición, antigüedad y alcance |
| C10 | Esquema visual o textual completo | README: «Módulos y flujo completo», con diagrama y explicación de extracción, procesamiento, modelado, insights y visualización |
| E01 | Código de recolección de artículos/páginas y transcripciones de audio/vídeo | [corpus.py](../src/ai_economy/corpus.py): descarga Kaggle, carga de transcripciones, scraping HTML, lectura de cachés y auditoría; [sources.py](../src/ai_economy/sources.py): fuentes/alcance. Dos abstracts NBER se extrajeron de HTML real; cuatro páginas se adquirieron como texto de lector web |
| E02 | Procesado, limpieza y unificación de los textos | Normalización de URL, deduplicación, validación uno a uno, eliminación de interfaz/navegación y marcas orales, conservación de cifras/negaciones, esquema documental uniforme e IDs de oración |
| E03 | Resumen e insights con ML y/o LLM | [analysis.py](../src/ai_economy/analysis.py): TF-IDF, NMF, K-means y resumen extractivo con centroide/MMR; [resumen global](../outputs/resumen_global.md): síntesis narrativa original con IDs de fuente. No se requiere utilizar un LLM si se emplean algoritmos de ML |
| E04 | Dos visualizaciones basadas en el contenido | [Perfiles NMF](../outputs/figures/topic_profiles.png) y [similitud TF-IDF](../outputs/figures/source_similarity.png). [Comparación de resúmenes](../outputs/figures/summary_comparison.png) es una ampliación adicional |
| E05 | Ejemplo de ejecución | [Notebook ejecutado](../notebooks/investigacion_multimodal.ipynb): seis celdas de código con outputs reales; [manifiesto](../outputs/run_manifest.json) y comandos reproducibles en «Reproducir» |
| E06 | Markdown con respuestas y esquema de módulos, relaciones y técnicas | README narrativo, seis respuestas localizadas abajo y diagrama con módulos/herramientas; [registro de fuentes](DATA_SOURCES.md) amplía procedencia y alcance |

## Todas las preguntas de la opción de resumen multimodal

La ubicación remite al README principal. Las respuestas no quedan limitadas a esta tabla ni a un documento secundario.

| ID | Pregunta y dimensiones de la consigna | Respuesta explícita en el README y evidencia |
|---|---|---|
| Q01 | ¿Qué técnica empleaste para extraer la información de las fuentes? ¿Usaste APIs, web scraping o una herramienta específica? ¿Qué ventajas y limitaciones encontraste con cada método? | «De la pregunta a los datos» y «Limpieza y unificación»: API de descarga de Kaggle y transcripciones TED; scraping con `requests`/BeautifulSoup; cuatro cachés de lector web y dos HTML NBER diferenciados. Se explican trazabilidad/calidad, antigüedad/cobertura, pérdida audiovisual, cambios de páginas/acceso y alcance parcial de lector/abstracts |
| Q02 | ¿Cómo procesaste y limpiaste los datos? | «Limpieza y unificación»: URL normalizada, unión uno a uno, tres duplicados exactos de transcripción eliminados, rechazo de conflictos, marcas orales/interfaz/menús, esquema común, cifras/negaciones, oraciones deduplicadas e IDs; decisiones sobre tres charlas fuera del foco |
| Q03 | ¿Cómo generaste el resumen y los insights? ¿Probaste distintos prompts o enfoques? | «Modelos y resumen global»: TF-IDF/NMF/K-means, centroide equilibrado por fuente, centroide con cuota y MMR con la misma cuota; sensibilidad `λ=0,50/0,65/0,80`. No se ejecutó un LLM: la comparación es entre enfoques algorítmicos. Se distinguen extracción automática y narrativa interpretativa revisada |
| Q04 | ¿Qué muestran tus visualizaciones y por qué son relevantes? | «Qué muestran las visualizaciones»: perfiles relativos de temas por fuente para localizar vocabularios compartidos/complementarios; similitud para puentes entre modalidades; tercera figura para cobertura, redundancia y representación. Se advierte que vocabulario no equivale a acuerdo, verdad o prevalencia social |
| Q05 | Crea un esquema del sistema. Describe extracción, procesamiento, modelado, generación de insights y visualización, sus interacciones y técnicas | «Módulos y flujo completo»: Kaggle/fuentes web → `corpus.py` → TF-IDF → NMF/K-means y centroide/cuota/MMR → `pipeline.py` → gráficos, notebook, síntesis y explorador. Se explican además exportación local y extensión opcional de audio |
| Q06 | ¿Qué mejorarías si tuvieras más tiempo o recursos? | «Límites y siguientes mejoras»: referencias y evaluación humana de factualidad/legibilidad, nuevas charlas contemporáneas, comparación de embeddings y revisión de ASR/marcas temporales, conservando auditoría de fallos y costes |

## Evidencia de resultados, interpretación y límites

La ejecución final contiene **18 fuentes: 12 transcripciones y seis textos web**, **33.499 palabras** y **1.202 oraciones candidatas**, con publicaciones entre 2012 y 2025. El manifiesto registra la adquisición, transformación, versiones, semilla y hashes; las fuentes fallidas se auditan en lugar de inventar contenido.

Se calculan cinco temas NMF y cuatro grupos K-means. Son patrones exploratorios de un corpus pequeño y seleccionado, sin etiquetas. La similitud coseno no identifica acuerdo ni causalidad; el silhouette bajo no acredita una taxonomía sólida. Tampoco hay un resumen humano de referencia que permita declarar exactitud factual o ROUGE.

Con diez oraciones seleccionadas, la cobertura del centroide sin cuota es **38,89%**. Centroide con cuota y MMR cubren ambos **55,56%**: esa mejora de cobertura responde a la cuota. Al mantener la misma cuota, la redundancia léxica media pasa de **0,01693** a **0,00587** con MMR; su relevancia media disminuye ligeramente. Es un compromiso medido entre relevancia y diversidad, no una demostración de superioridad factual.

La síntesis global identifica la diferencia entre exposición potencial, adopción y resultados laborales, y relaciona argumentos históricos con textos científicos/institucionales posteriores. Los puntos incluyen referencias `Sxx` resolubles en las fuentes. Los extractos públicos tienen hasta 14 palabras por fuente; las oraciones completas pueden reconstruirse localmente desde sus IDs mediante [export_summary.py](../src/ai_economy/export_summary.py).

El corpus completo, HTML y audio no se redistribuyen. Los enlaces y el código permiten nueva adquisición; sin la misma captura, nuevas páginas o versiones pueden cambiar resultados. Se diferencia reproducción completa desde datos adquiridos de auditoría de outputs publicados sin datos crudos. La capa TED anterior a 2018 y la capa web posterior limitan cualquier inferencia temporal.

## Las cinco categorías de evaluación

| Categoría | Peso indicado por la consigna | Evidencia para su evaluación |
|---|---:|---|
| Investigación y justificación técnica | 3 puntos | Selección de fuentes, distinción de modalidades/fechas/alcance, elección de técnicas y comparación de tres enfoques con control de cuota |
| Resultados y visualizaciones | 2,5 puntos | Síntesis trazable, métricas calculadas, tres figuras, tablas y notebook ejecutado |
| Calidad del código y estructura | 2 puntos | Extracción/análisis/pipeline/exportación separados, configuración de dependencias, nueve pruebas y registros de procedencia |
| Innovación, creatividad y originalidad | 1,5 puntos | Centroide con igual peso por fuente, control de cuota para interpretar MMR, trazabilidad de oraciones y explorador interactivo |
| Documentación y storytelling | 1 punto | README narrativo completo, resumen español con fuentes, cuaderno explicado y matriz de localización |

El Proyecto 2 representa el **40%** de la nota final; el Proyecto 1 representa el **60%**. Estas correspondencias documentan evidencias, sin garantizar una nota.

## Verificaciones realizadas

- **Nueve pruebas superadas** con Python 3.13.9: limpieza semántica y de interfaz, normalización, contenido HTML, conflictos de unión, fallos de adquisición, fecha de captura, cuota y trazabilidad.
- **6/6 celdas de código ejecutadas** en el notebook, con cero outputs de error.
- Los 18 documentos locales coinciden en orden, modalidad, número de palabras y SHA-256 con `sources.csv` y el manifiesto; ambos tipos están presentes.
- Perfiles NMF y matriz de similitud reproducidos independientemente desde el corpus; coincidencia numérica, perfiles no negativos con suma uno, matriz simétrica y diagonal uno.
- Métricas de los tres enfoques de resumen reproducidas independientemente. IDs, fuentes, URLs, cuotas, extractos de hasta 14 palabras y presencia de las dos modalidades comprobados.
- Las tres figuras finales se inspeccionaron visualmente y resultaron legibles.
- La exportación del resumen completo local funcionó; su destino permanece dentro de la carpeta excluida de publicación.
- El explorador Streamlit se probó con el corpus final: muestra 18/12/6 fuentes, inicia sin excepciones y filtra autores/títulos correctamente.

No se afirma ejecución de ASR, análisis visual de vídeos, evaluación factual automática, representatividad poblacional o predicción de empleo. Las ampliaciones opcionales quedan separadas de las evidencias ejecutadas.
