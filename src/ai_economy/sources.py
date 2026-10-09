"""Registro explícito de las fuentes: no se generan URLs ni contenidos ficticios."""

KAGGLE_DATASET = "rounakbanik/ted-talks"
KAGGLE_URL = "https://www.kaggle.com/datasets/rounakbanik/ted-talks"
KAGGLE_DOWNLOAD = "https://www.kaggle.com/api/v1/datasets/download/rounakbanik/ted-talks"

# Criterio deliberado: tecnología, complementariedad, empleo y gobernanza.
# La selección es temática y no es representativa de todos los discursos sobre IA.
TED_SPEAKERS = {
    "Andrew McAfee", "Erik Brynjolfsson", "Anthony Goldbloom", "David Autor",
    "Garry Kasparov", "Zeynep Tufekci", "Jeremy Howard", "Nick Bostrom",
    "Stuart Russell", "Augie Picado", "Tim Leberecht",
}

TED_EXCLUDED_SLUGS = {
    "nick_bostrom_on_our_biggest_problems",  # filosofía general, no IA/trabajo
    "tim_leberecht_3_ways_to_usefully_lose_control_of_your_reputation",  # marca y marketing
    "zeynep_tufekci_how_the_internet_has_made_social_change_easy_to_organize_hard_to_win",  # organización política
}

WEB_SOURCES = [
    {"id": "ilo2025", "title": "Generative AI and Jobs: A Refined Global Index of Occupational Exposure", "authors": "Gmyrek et al. / ILO", "url": "https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure", "year": 2025, "kind": "web_report", "selector": "main", "scope": "Ficha y síntesis institucional del informe, no texto íntegro del informe"},
    {"id": "cbo2024", "title": "Artificial Intelligence and Its Potential Effects on the Economy and the Federal Budget", "authors": "Congressional Budget Office", "url": "https://www.cbo.gov/publication/61147", "year": 2024, "kind": "web_report", "selector": "main", "scope": "Informe web"},
    {"id": "gpts2023", "title": "GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models", "authors": "Eloundou, Manning, Mishkin and Rock", "url": "https://arxiv.org/abs/2303.10130", "year": 2023, "kind": "web_paper", "selector": "blockquote.abstract", "scope": "Resumen científico, no texto íntegro del paper"},
    {"id": "imf2024", "title": "AI Will Transform the Global Economy. Let's Make Sure It Benefits Humanity.", "authors": "Kristalina Georgieva / IMF", "url": "https://www.imf.org/en/blogs/articles/2024/01/14/ai-will-transform-the-global-economy-lets-make-sure-it-benefits-humanity", "year": 2024, "kind": "web_blog", "selector": "article", "scope": "Artículo institucional"},
    {"id": "nber31161", "title": "Generative AI at Work", "authors": "Erik Brynjolfsson, Danielle Li and Lindsey Raymond", "url": "https://www.nber.org/papers/w31161", "year": 2023, "kind": "web_paper", "selector": ".page-header__intro, .abstract, .paper-abstract, .page-content", "scope": "Ficha y resumen científico, no texto íntegro del paper"},
    {"id": "nber32487", "title": "The Simple Macroeconomics of AI", "authors": "Daron Acemoglu", "url": "https://www.nber.org/papers/w32487", "year": 2024, "kind": "web_paper", "selector": ".page-header__intro, .abstract, .paper-abstract, .page-content", "scope": "Ficha y resumen científico, no texto íntegro del paper"},
]
