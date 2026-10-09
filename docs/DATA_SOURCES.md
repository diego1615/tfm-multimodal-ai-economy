# Registro y alcance de las fuentes

La procedencia ejecutada está en `outputs/sources.csv`, `outputs/sources.json` y `outputs/run_manifest.json`. Cada documento conserva URL, autores, año, modalidad, alcance de extracción, método real y hash del texto procesado.

El dataset Kaggle [TED Talks, de Rounak Banik](https://www.kaggle.com/datasets/rounakbanik/ted-talks) contiene metadatos y transcripciones obtenidos de TED. Se utiliza la descarga pública, con atribución al autor del dataset y a TED. Los contenidos de las charlas tienen condiciones de uso propias de TED; una etiqueta de licencia del dataset no elimina derechos de las obras subyacentes. Consulte la [política de uso de TED](https://www.ted.com/about/our-organization/our-policies-terms/ted-talks-usage-policy).

Las páginas web pertenecen a sus autores e instituciones. OIT y CBO aportan informes, FMI un artículo y arXiv/NBER textos científicos o sus abstracts; el alcance de cada extracción es explícito. La caché de lector web usada en el ejemplo es texto de página recuperado mediante una herramienta de lectura, no HTML original, y puede ser parcial. Los scrapers HTML se incluyen para la reproducción con acceso a las páginas.

La fecha de adquisición se conserva cuando está documentada. Cuando falta, `retrieved_at` es nulo; `processed_at` registra la lectura y limpieza local, no una nueva descarga. Las fuentes sin caché o fallidas se listan con motivo en la auditoría.

El repositorio excluye mediante `.gitignore` el corpus completo, HTML y audio, así como los resúmenes extractivos completos de `outputs/private`. La síntesis española es original y los extractos públicos seleccionados tienen un máximo de 14 palabras y una sola selección por fuente. Los tests usan textos sintéticos aislados para validar funciones; no forman parte del corpus analizado.
