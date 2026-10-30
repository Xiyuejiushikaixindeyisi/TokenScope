import csv
import json
from pathlib import Path

from tokenscope.monitoring.ma.contracts import Submit
from tokenscope.monitoring.ma.ingest import COLUMNS


def binding() -> Submit:
    return Submit(
        submission_key="one",
        pre_file_ref="pre.csv",
        now_file_ref="now.csv",
        model_standard_name="q-64K",
        model_id="Qwen3.6-27B",
        pre_start="2026-10-20T07:00:00Z",
        now_start="2026-10-20T08:00:00Z",
        now_end="2026-10-20T09:00:00Z",
    )


def row(role: str = "now", **changes: str) -> dict[str, str]:
    time = "2026-10-20T07:01:00Z" if role == "pre" else "2026-10-20T08:01:00Z"
    return (
        dict(
            instance_uuid="A",
            hash_id="same",
            appid="tenant",
            request_time=time,
            model_handle_start_time=time,
            prompt_tokens="100",
            cached_tokens="25",
            completion_tokens="10",
            request_input=json.dumps(
                {"model": "Qwen3.6-27B", "messages": [{"role": "user", "content": "hello"}]}
            ),
        )
        | changes
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(COLUMNS))
        writer.writeheader()
        writer.writerows(rows)
