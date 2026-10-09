# Resumen global: IA, automatización, productividad y trabajo

La ejecución integra **18 fuentes**: 12 transcripciones audiovisuales y 6 textos web, con 33,499 palabras procesadas. El corpus comprende publicaciones de 2012 a 2025 y está íntegramente en inglés. La síntesis narrativa siguiente es una interpretación revisada; la selección automática de evidencia se obtiene con TF-IDF y MMR, sin una API de LLM.

## Visión general e ideas clave

La discusión sobre automatización combina sustitución de tareas, complementariedad entre personas y máquinas y capacidad de reorganizar la producción; reducirla a una predicción única de desaparición del empleo pierde esa diversidad conceptual. La lectura conjunta de Autor y Brynjolfsson permite formular esta tensión sin tratar sus charlas como estimaciones actuales del mercado laboral. [S09; S02]

Goldbloom organiza su argumento alrededor de tareas frecuentes frente a situaciones nuevas; esta distinción es una perspectiva histórica de 2016 y debe contrastarse con las capacidades posteriores de IA generativa. No constituye un límite permanente demostrado de la tecnología. [S06]

Los trabajos contemporáneos distinguen exposición potencial de tareas de pérdida efectiva de puestos. El estudio de Eloundou y colaboradores analiza capacidades y exposición; el índice de la OIT describe posibilidades de transformación por ocupación. Sus porcentajes y universos de referencia no se pueden combinar como si midieran una sola tasa de desempleo futura. [S15; S13]

El estudio de Brynjolfsson, Li y Raymond aporta evidencia de una implementación concreta de asistencia generativa en atención al cliente. Su utilidad para este corpus consiste en conectar el debate general con efectos observados en un contexto productivo delimitado; extrapolar ese resultado a todos los sectores requiere evidencia adicional. [S17]

Acemoglu introduce una distinción necesaria entre mejora de tareas individuales y crecimiento agregado. La magnitud macroeconómica depende de la extensión de las tareas afectadas y de los ahorros o aumentos de productividad; una demostración llamativa no basta para cuantificar el efecto sobre el PIB. [S18]

Los textos institucionales del FMI y la CBO amplían el análisis hacia desigualdad, adaptación de capacidades y efectos económicos y presupuestarios. La lectura para una decisión institucional es evaluar adopción, complementariedad y distribución junto con la capacidad técnica, conservando la incertidumbre sobre los efectos netos. [S16; S14]

## Qué añade el aprendizaje automático

NMF identifica 5 patrones de vocabulario. Las etiquetas siguientes son términos de mayor peso, no categorías objetivas ni conclusiones causales:

- **T1**: humans, machine, human, machines, intelligence, learning.
- **T2**: ai, workers, generative ai, task, exposure, effects.
- **T3**: great, economy, work, time, jobs, look.
- **T4**: chess, deep blue, played, champion, grandmaster, deep.
- **T5**: powered, capabilities, models, significantly, impacts, software.

Con el mismo presupuesto de 10 oraciones, el centroide cubre 38.9% de las fuentes y MMR 55.6%. La redundancia media es 0.017 y 0.006, respectivamente. La cuota de una oración por fuente es parte explícita de MMR: explica una porción de esa diferencia y no demuestra superioridad factual.

El control centroide con la misma cuota obtiene cobertura 55.6% y redundancia 0.017; comparar este control con MMR permite distinguir la contribución de la penalización de redundancia de la cuota por fuente.
## Evidencia seleccionada automáticamente

Las citas breves permiten ubicar la oración identificada en la caché local. No sustituyen la lectura de la fuente; el corpus completo y las oraciones completas permanecen fuera del repositorio público.

- **E01 / S16** · AI Will Transform the Global Economy. Let's Make Sure It Benefits Humanity. · `imf2024:s1` · [Fuente](https://www.imf.org/en/blogs/articles/2024/01/14/ai-will-transform-the-global-economy-lets-make-sure-it-benefits-humanity).
- **E02 / S17** · Generative AI at Work · `nber31161:s1` · [Fuente](https://www.nber.org/papers/w31161).
- **E03 / S18** · The Simple Macroeconomics of AI · `nber32487:s4` · [Fuente](https://www.nber.org/papers/w32487).
- **E04 / S06** · The jobs we'll lose to machines -- and the ones we won't · `ted_anthony_goldbloom_the_jobs_we_ll_lose_to_machines_and_the_ones_we_won_t:s25` · [Fuente](https://www.ted.com/talks/anthony_goldbloom_the_jobs_we_ll_lose_to_machines_and_the_ones_we_won_t).
- **E05 / S02** · The key to growth? Race with the machines · `ted_erik_brynjolfsson_the_key_to_growth_race_em_with_em_the_machines:s54` · [Fuente](https://www.ted.com/talks/erik_brynjolfsson_the_key_to_growth_race_em_with_em_the_machines).
- **E06 / S05** · What happens when our computers get smarter than we are? · `ted_nick_bostrom_what_happens_when_our_computers_get_smarter_than_we_are:s87` · [Fuente](https://www.ted.com/talks/nick_bostrom_what_happens_when_our_computers_get_smarter_than_we_are).
- **E07 / S07** · 4 ways to build a human company in the age of machines · `ted_tim_leberecht_4_ways_to_build_a_human_company_in_the_age_of_machines:s66` · [Fuente](https://www.ted.com/talks/tim_leberecht_4_ways_to_build_a_human_company_in_the_age_of_machines).
- **E08 / S10** · 3 principles for creating safer AI · `ted_stuart_russell_how_ai_might_make_us_better_people:s7` · [Fuente](https://www.ted.com/talks/stuart_russell_how_ai_might_make_us_better_people).
- **E09 / S13** · Generative AI and Jobs: A Refined Global Index of Occupational Exposure · `ilo2025:s11` · [Fuente](https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure).
- **E10 / S15** · GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models · `gpts2023:s1` · [Fuente](https://arxiv.org/abs/2303.10130).

## Interpretación de las visualizaciones

El mapa de calor temático muestra cuánto peso relativo asigna NMF a cada patrón dentro de cada fuente. Permite localizar conversaciones compartidas y textos que aportan vocabulario distinto. La matriz de similitud muestra puentes léxicos entre fuentes, incluidas las dos modalidades; una similitud baja puede responder a género discursivo, extensión o época y no implica desacuerdo.

En la fuente OIT predomina T2 con peso 1.00, cuyo vocabulario principal es ai, workers, generative ai, task. Es un ejemplo concreto de cómo el mapa localiza exposición de tareas y trabajo dentro de este corpus. [S13]
El puente más próximo entre modalidades une «Will automation take away all our jobs?» y «Artificial Intelligence and Its Potential Effects on the Economy and the Federal Budget», con coseno 0.252. Esta relación señala un vocabulario común que merece comparación cualitativa; no demuestra acuerdo de sus conclusiones. [S09; S14]
## Alcance y limitaciones

La muestra es deliberada y pequeña. TED aporta una capa histórica hasta 2017 y las fuentes web una capa posterior: sus diferencias no identifican una evolución causal. Las transcripciones excluyen imagen, prosodia y sonido; no se ejecutó reconocimiento de voz. Los abstracts contienen menos contexto que los informes completos. TF-IDF depende del vocabulario, NMF es sensible al número de temas y MMR puede seleccionar oraciones que necesiten contexto. No hay etiquetas ni resumen de referencia: no se reportan exactitud, F1 o ROUGE. Las conclusiones requieren revisión humana y no predicen empleo.

## Registro de fuentes

| ID | Año | Modalidad | Fuente |
|---|---:|---|---|
| S01 | 2012 | spoken | [Are droids taking our jobs?](https://www.ted.com/talks/andrew_mcafee_are_droids_taking_our_jobs) |
| S02 | 2013 | spoken | [The key to growth? Race with the machines](https://www.ted.com/talks/erik_brynjolfsson_the_key_to_growth_race_em_with_em_the_machines) |
| S03 | 2013 | spoken | [What will future jobs look like?](https://www.ted.com/talks/andrew_mcafee_what_will_future_jobs_look_like) |
| S04 | 2014 | spoken | [The wonderful and terrifying implications of computers that can learn](https://www.ted.com/talks/jeremy_howard_the_wonderful_and_terrifying_implications_of_computers_that_can_learn) |
| S05 | 2015 | spoken | [What happens when our computers get smarter than we are?](https://www.ted.com/talks/nick_bostrom_what_happens_when_our_computers_get_smarter_than_we_are) |
| S06 | 2016 | spoken | [The jobs we'll lose to machines -- and the ones we won't](https://www.ted.com/talks/anthony_goldbloom_the_jobs_we_ll_lose_to_machines_and_the_ones_we_won_t) |
| S07 | 2016 | spoken | [4 ways to build a human company in the age of machines](https://www.ted.com/talks/tim_leberecht_4_ways_to_build_a_human_company_in_the_age_of_machines) |
| S08 | 2016 | spoken | [Machine intelligence makes human morals more important](https://www.ted.com/talks/zeynep_tufekci_machine_intelligence_makes_human_morals_more_important) |
| S09 | 2016 | spoken | [Will automation take away all our jobs?](https://www.ted.com/talks/david_autor_why_are_there_still_so_many_jobs) |
| S10 | 2017 | spoken | [3 principles for creating safer AI](https://www.ted.com/talks/stuart_russell_how_ai_might_make_us_better_people) |
| S11 | 2017 | spoken | [Don't fear intelligent machines. Work with them](https://www.ted.com/talks/garry_kasparov_don_t_fear_intelligent_machines_work_with_them) |
| S12 | 2017 | spoken | [The real reason manufacturing jobs are disappearing](https://www.ted.com/talks/augie_picado_the_real_reason_manufacturing_jobs_are_disappearing) |
| S13 | 2025 | written | [Generative AI and Jobs: A Refined Global Index of Occupational Exposure](https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure) |
| S14 | 2024 | written | [Artificial Intelligence and Its Potential Effects on the Economy and the Federal Budget](https://www.cbo.gov/publication/61147) |
| S15 | 2023 | written | [GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models](https://arxiv.org/abs/2303.10130) |
| S16 | 2024 | written | [AI Will Transform the Global Economy. Let's Make Sure It Benefits Humanity.](https://www.imf.org/en/blogs/articles/2024/01/14/ai-will-transform-the-global-economy-lets-make-sure-it-benefits-humanity) |
| S17 | 2023 | written | [Generative AI at Work](https://www.nber.org/papers/w31161) |
| S18 | 2024 | written | [The Simple Macroeconomics of AI](https://www.nber.org/papers/w32487) |
