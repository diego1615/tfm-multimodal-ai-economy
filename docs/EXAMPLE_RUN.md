# Ejecución de ejemplo

La ejecución se basa en datos reales: CSV descargados de Kaggle, cuatro páginas verificadas recuperadas como texto y dos abstracts NBER extraídos de HTML guardado. No se utilizaron datos sintéticos en la investigación.

| Componente | Resultado |
|---|---:|
| Metadatos TED originales | 2.550 |
| Filas de transcripción originales | 2.467 |
| Duplicados exactos de transcripción eliminados | 3 |
| Charlas ajenas al foco excluidas por URL | 3 |
| Transcripciones seleccionadas | 12 |
| Fuentes web utilizadas | 6 |
| Documentos totales | 18 |
| Palabras procesadas | 33.499 |
| Oraciones candidatas sin duplicación exacta | 1.202 |
| Oraciones seleccionadas por enfoque | 10 |

El manifiesto contiene hashes, fechas registradas y versiones instaladas; cada resultado agregado puede rastrearse a un ID de fuente. Las seis fuentes escritas se adquirieron correctamente. No se ejecutaron ASR, análisis visual de vídeos ni un LLM externo.

| Método | Cobertura de fuentes | Redundancia media | Relevancia media |
|---|---:|---:|---:|
| Centroide | 38,9 % | 0,01706 | 0,13950 |
| Centroide con cuota | 55,6 % | 0,01693 | 0,13532 |
| MMR con cuota | 55,6 % | 0,00587 | 0,13133 |

La cuota y la penalización de redundancia son decisiones distintas. Comparar los dos últimos métodos mantiene constante la regla de una oración por fuente. Estas métricas describen la selección léxica interna; no validan exactitud factual ni sustituyen una evaluación humana.

Se entregan el notebook ejecutado con tablas y figuras, una vista HTML, tres visualizaciones, la síntesis original española, la matriz de cumplimiento, metadatos y código. Los nueve tests verifican limpieza, claves de unión, fechas de adquisición, artefactos de interfaz y trazabilidad. La aplicación Streamlit fue comprobada con su mecanismo de prueba: inicio y filtro por autor sin excepciones.
