"""Generate this candidate's schema/examples from project root with .venv/bin/python."""

import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import cast

from fastapi import FastAPI

from tokenscope.api.ma import router
from tokenscope.monitoring.ma import contracts
from tokenscope.monitoring.ma.availability import AvailabilityResponse
from tokenscope.monitoring.ma.service import MaService

root = Path.cwd()
sys.path.insert(0, str(root / "tests/unit"))
from ma.helpers import binding, row  # noqa: E402
from ma.test_availability import synthetic  # noqa: E402

destination = Path(__file__).resolve().parent
output = root / "artifacts/validation/monitoring/v2-ma/HV2-R1"
output.mkdir(parents=True, exist_ok=True)
cases = [
    ("source_cached_missing", [row("pre")], [row(cached_tokens="")]),
    (
        "warmup_order_conflict",
        [row("pre", model_handle_start_time="2026-10-20T08:02:00Z")],
        [row()],
    ),
    ("no_valid_prompt", [row("pre")], [row(prompt_tokens="", request_input="bad")]),
    ("valid_zero_cached", [row("pre")], [row(cached_tokens="0")]),
    ("zero_denominator", [row("pre")], [row(prompt_tokens="0", cached_tokens="0")]),
    ("bad_json_real_valid", [row("pre")], [row(request_input="bad", completion_tokens="bad")]),
    ("empty_now", [row("pre")], []),
    ("no_valid_prewarm", [], [row()]),
    (
        "partial_observations",
        [row("pre")],
        [row(), row(cached_tokens="", request_time="2026-10-20T08:05:00Z")],
    ),
]
examples = []
app = FastAPI(title="MA monitoring design contract", version="1.0.0")
app.include_router(router(cast(MaService, None)))
openapi = app.openapi()
openapi["x-status"] = "runtime-route-signatures; no service execution during generation"
old = json.loads((root / "docs/contracts/ma-monitoring-v2/design.openapi.json").read_text())
for path, operations in old["paths"].items():
    assert openapi["paths"][path] == operations, path
for name, schema in old["components"]["schemas"].items():
    assert openapi["components"]["schemas"][name] == schema, name
frozen = json.loads((root / "docs/contracts/ma-monitoring-v2/schema.json").read_text())
for name, schema in frozen.items():
    assert getattr(contracts, name).model_json_schema() == schema, name
with tempfile.TemporaryDirectory(dir=output) as temp:
    for name, pre, now in cases:
        snapshot, explanation = synthetic(Path(temp) / name, pre, now)
        response = AvailabilityResponse(
            service_instance_id="synthetic-service",
            ma_run_id=f"synthetic-{name}",
            binding=binding(),
            availability=explanation,
        )
        examples.append(
            dict(
                name=name,
                synthetic=True,
                pre=pre,
                now=now,
                response=response.model_dump(mode="json"),
                snapshot_excerpt=snapshot.model_dump(
                    mode="json", exclude={"input_histograms", "uncached_histograms"}
                ),
            )
        )
for filename, value in (
    ("schema.json", AvailabilityResponse.model_json_schema()),
    ("candidate.openapi.json", openapi),
    (
        "examples.json",
        dict(
            provenance="Synthetic 4096-token identical shards; not Huawei evidence", cases=examples
        ),
    ),
):
    (destination / filename).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
print(f"Validated {len(examples)} synthetic availability responses; generated schema and examples")
paths = [
    "src/tokenscope/monitoring/ma/availability.py",
    "src/tokenscope/monitoring/ma/ingest.py",
    "src/tokenscope/monitoring/ma/statistics.py",
    "src/tokenscope/monitoring/ma/service.py",
    "src/tokenscope/api/ma.py",
    "tests/unit/ma/test_availability.py",
]
hashes = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sorted(paths)}
identity = hashlib.sha256(
    json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
(destination / "source-manifest.json").write_text(
    json.dumps(
        dict(
            baseline_head="7cbe28621f4e46083bf47f9aa14b011b3cb250c4",
            status="candidate_not_frozen",
            identity_algorithm="sha256(canonical sorted path-to-sha256 JSON, compact separators)",
            source_and_test_identity=identity,
            files=hashes,
        ),
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
