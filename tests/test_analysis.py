import numpy as np
from scipy.sparse import csr_matrix

from ai_economy.analysis import compare_summaries, select_mmr, sentence_corpus


def toy_documents():
    # Textos sintéticos sólo para verificar lógica; nunca usados como datos de investigación.
    return [
        {"id": "a", "title": "A", "url": "https://example.org/a", "modality": "spoken", "text": "Machines can help people complete routine tasks while employment changes across firms. Training allows workers to adapt their skills to new tools and responsibilities."},
        {"id": "b", "title": "B", "url": "https://example.org/b", "modality": "written", "text": "Economic growth depends on productivity gains and on the distribution of income. Public institutions can assess economic benefits while protecting vulnerable workers from displacement."},
        {"id": "c", "title": "C", "url": "https://example.org/c", "modality": "written", "text": "Reliable measurement requires clear definitions of tasks, exposure, adoption, and observed outcomes. Occupational exposure does not automatically predict realized employment losses or aggregate productivity improvements."},
    ]


def test_mmr_enforces_source_quota_and_diversity():
    rows = [{"source_id": "a"}, {"source_id": "a"}, {"source_id": "b"}]
    matrix = csr_matrix([[1., 0.], [1., 0.], [0., 1.]])
    chosen = select_mmr(rows, matrix, np.array([1., .99, .7]), count=3, diversity_weight=.6)
    assert chosen == [0, 2]


def test_sentence_ids_and_evidence_are_traceable_and_bounded():
    documents = toy_documents()
    result = compare_summaries(documents, count=3)
    rows, _, _, _ = sentence_corpus(documents)
    ids = {row["sentence_id"] for row in rows}
    assert set(result["mmr_sentence_ids"]).issubset(ids)
    assert len({item["source_id"] for item in result["evidence"]}) == len(result["evidence"])
    assert all(len(item["excerpt"].replace(" …", "").split()) <= 14 for item in result["evidence"])
    for method in ("centroid", "centroid_quota", "mmr"):
        assert 0 <= result["metrics"][method]["source_coverage_fraction"] <= 1
        assert 0 <= result["metrics"][method]["mean_pairwise_redundancy"] <= 1
