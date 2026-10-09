"""Reconstruye resúmenes extractivos completos sólo en la carpeta privada local."""

import argparse
import json
from pathlib import Path

from .analysis import sentence_corpus


def export(output: Path, method: str = "mmr") -> Path:
    documents = [json.loads(line) for line in (output / "private/corpus.jsonl").read_text(encoding="utf-8").splitlines() if line]
    comparison = json.loads((output / "summary_comparison.json").read_text())
    sentence_ids = comparison[f"{method}_sentence_ids"]
    rows, _, _, _ = sentence_corpus(documents)
    lookup = {row["sentence_id"]: row for row in rows}
    target = output / "private" / f"summary_{method}_full.md"
    lines = [f"# Resumen extractivo local: {method}", "", "Oraciones completas del corpus privado. No incorporar este archivo al repositorio público.", ""]
    for sentence_id in sentence_ids:
        row = lookup[sentence_id]
        lines += [f"{row['text']} [{row['title']}]({row['url']}) · `{sentence_id}`", ""]
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--method", choices=["centroid", "centroid_quota", "mmr"], default="mmr")
    arguments = parser.parse_args()
    print(export(arguments.output, arguments.method))
