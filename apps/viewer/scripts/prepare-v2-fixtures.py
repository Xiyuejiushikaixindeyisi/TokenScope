"""Run from repository root. Synthetic local acceptance inputs; no production data.

Usage: .venv/bin/python apps/viewer/scripts/prepare-v2-fixtures.py [input-root]
Existing files are left intact, so reruns cannot mutate sealed input evidence.
"""
import csv
import json
import sys
from pathlib import Path

from tokenscope.monitoring.ma.ingest import COLUMNS

root = Path(sys.argv[1] if len(sys.argv) > 1 else "artifacts/validation/viewer/monitoring-v2/inputs")
root.mkdir(parents=True, exist_ok=True)


def write(name, columns, rows):
    target = root / name
    if target.exists():
        return
    with target.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


for index, model in enumerate(("GLM-5.2", "Qwen3.6-27B", "DeepSeek-V4-Flash-0731"), 1):
    rows = [dict(hash_id=f"synthetic-{j}", appid=f"synthetic-app-{index}", model_handle_start_time=f"2026-10-27T00:00:{j:02d}Z", completion_tokens=str(j + 10), request_input=json.dumps({"model": model, "messages": [{"role": "system", "content": "synthetic prefix " * 200}, {"role": "user", "content": f"question {j}"}]})) for j in range(30)]
    write(f"model-{index}.csv", rows[0].keys(), rows)
    if index == 1:
        write("multi-app.csv", rows[0].keys(), [r | {"appid": "app-a" if j < 15 else "app-b"} for j, r in enumerate(rows)])

raw = json.dumps({"model": "Qwen3.6-27B", "messages": [{"role": "user", "content": "shared synthetic prefix " * 200}]})


def row(role, uuid, **overrides):
    stamp = "2026-10-20T07:01:00Z" if role == "pre" else "2026-10-20T08:01:00Z"
    return dict(instance_uuid=uuid, hash_id=uuid, appid="tenant", request_time=stamp, model_handle_start_time=stamp, prompt_tokens="100", cached_tokens="25", completion_tokens="10", request_input=raw) | overrides


pre = [row("pre", f"uuid-{i:02d}") for i in range(8)] + [row("pre", "pre-only")]
now = [row("now", f"uuid-{i:02d}") for i in range(8)] + [row("now", "real-only", request_input="bad"), row("now", "no-pre"), row("now", "missing-real", cached_tokens=""), row("now", "zero-uncached", cached_tokens="100"), row("now", "", cached_tokens="")]
for name, rows in [("mv2-pre.csv", pre), ("mv2-now.csv", now), ("mv2-empty-pre.csv", []), ("mv2-empty-now.csv", []), ("mv2-conflict-pre.csv", [row("pre", "conflict", model_handle_start_time="2026-10-20T08:02:00Z")]), ("mv2-conflict-now.csv", [row("now", "conflict")])]:
    write(name, COLUMNS, rows)
print(f"Synthetic inputs available at {root}; existing files preserved")
