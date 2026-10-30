"""Generate synthetic, schema-validated frontend examples from the actual MA pipeline."""

import csv
import json
from pathlib import Path

from tokenscope.monitoring.ma import contracts as c
from tokenscope.monitoring.ma.ingest import COLUMNS
from tokenscope.monitoring.ma.service import MaService
from tokenscope.monitoring.service import MonitoringService


def main() -> None:
    project = Path(__file__).resolve().parents[2]
    root = project / "artifacts/validation/monitoring/v2-ma/M005/frontend-examples"
    inputs = root / "inputs"
    inputs.mkdir(parents=True, exist_ok=False)
    raw = json.dumps({"messages": [{"role": "user", "content": "synthetic shared prefix " * 1800}]})
    for role, hour in (("pre", 7), ("now", 8)):
        with (inputs / f"{role}.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            for uuid in (
                ("warm", "conflict", "pre-only")
                if role == "pre"
                else ("warm", "conflict", "cold", "bad-json")
            ):
                stamp = f"2026-10-20T0{hour}:01:00Z"
                writer.writerow(
                    dict(
                        instance_uuid=uuid,
                        hash_id=f"{role}-{uuid}",
                        appid=role,
                        request_time=stamp,
                        model_handle_start_time="2026-10-20T08:02:00Z"
                        if role == "pre" and uuid == "conflict"
                        else stamp,
                        prompt_tokens="100",
                        cached_tokens="" if uuid == "cold" else "25",
                        completion_tokens="10",
                        request_input="{bad" if uuid == "bad-json" else raw,
                    )
                )
    service = MaService(MonitoringService(inputs, root / "state"))
    binding = c.Submit(
        submission_key="synthetic-frontend",
        pre_file_ref="pre.csv",
        now_file_ref="now.csv",
        model_standard_name="Qwen3.6-27B-64K",
        model_id="Qwen3.6-27B",
        pre_start="2026-10-20T07:00:00Z",
        now_start="2026-10-20T08:00:00Z",
        now_end="2026-10-20T09:00:00Z",
    )
    receipt = service.submit(binding)
    examples = [dict(case="queued", type="Receipt", payload=receipt.model_dump(mode="json"))]
    result = service.processor.process_next()
    assert result is not None and result.state == "completed", result
    examples.append(dict(case="completed", type="Receipt", payload=result.model_dump(mode="json")))
    for state in ("running", "failed", "interrupted"):
        payload = receipt.model_dump(mode="json") | {
            "state": state,
            "error_code": "WORKER_INTERRUPTED"
            if state == "interrupted"
            else "OUTSIDE_WINDOW"
            if state == "failed"
            else None,
        }
        examples.append(dict(case=f"synthetic-state-{state}", type="Receipt", payload=payload))
    examples.append(
        dict(case="catalog", type="Catalog", payload=service.catalog().model_dump(mode="json"))
    )
    examples.append(
        dict(
            case="quality",
            type="QualityPage",
            payload=service.quality(receipt.ma_run_id).model_dump(mode="json"),
        )
    )
    for uuid in ("warm", "conflict", "pre-only", "cold", "bad-json"):
        examples.append(
            dict(
                case=uuid,
                type="Snapshot",
                payload=service.snapshot(receipt.ma_run_id, uuid).model_dump(mode="json"),
            )
        )
    for code in (
        "INVALID_REQUEST",
        "SUBMISSION_CONFLICT",
        "RESULT_NOT_READY",
        "INSTANCE_NOT_FOUND",
    ):
        examples.append(
            dict(
                case=code,
                type="ErrorEnvelope",
                payload=dict(error=dict(code=code, message="Synthetic example")),
            )
        )
    for example in examples:
        getattr(c, example["type"]).model_validate(example["payload"])
    path = project / "docs/contracts/ma-monitoring-v2/frontend.examples.json"
    path.write_text(
        json.dumps(
            dict(
                origin="synthetic; not production traffic or frontend acceptance", examples=examples
            ),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )
    print(f"Validated {len(examples)} frontend examples")


if __name__ == "__main__":
    main()
