import json
from pathlib import Path

import pandas as pd
import pytest

from ai_economy.corpus import canonical_url, clean_text, extract_html, load_ted, load_web, sentence_split


def test_cleaning_preserves_negation_and_numbers():
    text = clean_text("<p>AI does not replace all work. (Applause) Costs fell 12.5%.</p>")
    assert "does not" in text
    assert "12.5%" in text
    assert "Applause" not in text


def test_reader_interface_tokens_are_removed_without_losing_economic_input():
    text = clean_text("[Input: Search] [Button: Submit] [Select: Language] Economic input matters; AI does not remove every task.")
    assert "Search" not in text and "Submit" not in text and "Language" not in text
    assert "Economic input matters" in text and "does not" in text


def test_url_normalization_aligns_dataset_urls():
    assert canonical_url("http://www.ted.com/talks/example/\\n") == canonical_url("https://www.ted.com/talks/example?language=en\n")


def test_html_rejects_challenge_and_removes_navigation():
    with pytest.raises(ValueError):
        extract_html("<main>Access denied</main>", {"id": "x"})
    result = extract_html("<nav>Unrelated navigation words</nav><main>" + "Economic research and employment growth. " * 20 + "</main>", {"id": "x"})
    assert "Unrelated" not in result


def test_duplicate_keys_prevent_many_to_many_join(tmp_path):
    pd.DataFrame({"url": ["https://ted.com/talks/a", "https://ted.com/talks/a"], "title": ["conflicting title A", "conflicting title B"]}).to_csv(tmp_path / "ted_main.csv", index=False)
    pd.DataFrame({"url": ["https://ted.com/talks/a"], "transcript": ["test"]}).to_csv(tmp_path / "transcripts.csv", index=False)
    with pytest.raises(ValueError, match="many-to-many"):
        load_ted(tmp_path)


def test_missing_web_sources_are_audited(tmp_path):
    records, audit = load_web(tmp_path, offline=True)
    assert not records
    assert len(audit) == 6
    assert all(row["status"] == "failed" for row in audit)


def test_cached_acquisition_date_is_not_read_date(tmp_path):
    payload = {"text": "Employment research and economic policy. " * 40, "retrieved_at": "2025-01-02", "retrieval_method": "web_reader_text"}
    (tmp_path / "ilo2025.json").write_text(json.dumps(payload))
    records, _ = load_web(tmp_path, offline=True)
    assert records[0]["retrieved_at"] == "2025-01-02"
    assert records[0]["processed_at"].startswith("20")
