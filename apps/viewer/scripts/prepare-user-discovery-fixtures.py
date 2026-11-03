"""Synthetic shared-APPID Trace inputs for coordinator-owned cold E2E. Never overwrite."""
import csv
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
root.mkdir(parents=True, exist_ok=True)
for index, model in enumerate(("GLM-5.2", "Qwen3.6-27B", "DeepSeek-V4-Flash-0731"), 1):
    rows = [dict(hash_id=f"hv2-{index}-{j}", appid="hv2-shared", model_handle_start_time=f"2026-10-27T00:00:{j:02d}Z", completion_tokens="10", request_input=json.dumps({"model": model, "messages": [{"role": "system", "content": "synthetic shared prefix " * 200}, {"role": "user", "content": f"synthetic question {j}"}]})) for j in range(25)]
    with (root / f"hv2-user-{index}.csv").open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
print(f"Created three synthetic shared-APPID inputs in {root}")
