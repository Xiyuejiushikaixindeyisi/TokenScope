"""Synthetic MA-only inputs for coordinator-owned cold HTTP/browser validation.

Run from repository root with a NEW input directory. Never overwrites inputs.
Uses the frozen examples' raw rows, not their mocked 4096-token encoding.
"""
import csv
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
root.mkdir(parents=True, exist_ok=True)
examples = json.loads(Path("docs/tasks/monitoring/v2-ma/hv2-availability/examples.json").read_text())["cases"]
columns = list(examples[0]["pre"][0])
matrix = {"pre": [], "now": []}
for index, case in enumerate(examples + examples[:4]):
    for role in matrix:
        matrix[role].extend(row | {"instance_uuid": f"{index:02d}-{case['name']}"} for row in case[role])
for role, rows in matrix.items():
    target = root / f"hv2-ma-matrix-{role}.csv"
    with target.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
print(f"Synthetic 13-UUID inputs written to {root}; real tokenizer results must be read from HTTP.")
