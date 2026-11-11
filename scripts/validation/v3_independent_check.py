"""Independent small-sample cache oracle; no production PrefixLedger/strategy calls."""

import argparse
import json
from fractions import Fraction
from pathlib import Path

from tokenscope.analysis_common.contracts import ModificationPlan
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.execution_v3 import WorkerSpec3
from tokenscope.analysis_common.modifications import apply_mutations
from tokenscope.analysis_common.preparation_store import PreparationStore
from tokenscope.analysis_common.sample_source import open_sample_window
from tokenscope.domain import ModelSettings
from tokenscope.monitoring.service import MonitoringService

parser = argparse.ArgumentParser()
parser.add_argument("attempt", type=Path)
args = parser.parse_args()
root = args.attempt.resolve()
results = json.loads((root / "browser-results.json").read_text())["results"]
output = root / "independent-check.json"
assert not output.exists()
checked = []
for result in results:
    job = root / "state/diagnostics-v3/jobs" / result["task"]
    spec = WorkerSpec3.model_validate_json((job / "job.json").read_bytes())
    preparation = PreparationStore(root / "state/diagnostics-v3")
    receipt = preparation.receipt(spec.sample_preparation_id)
    parent = preparation.root / "jobs" / receipt.preparation_id
    manifest = parent / preparation.execution(receipt.preparation_id).telemetry["manifest_path"]
    service = MonitoringService(
        Path(spec.input_root), Path(spec.state_root), Path(spec.asset_root), 1
    )
    report = json.loads((root / (result["appid"] + "-report.json")).read_text())
    for recommendation in report["recommendations"]:
        for window in recommendation["windows"]:
            if not window["complete"]:
                continue
            source = open_sample_window(
                service,
                manifest.parent,
                receipt.manifest_sha256,
                window["role"],
                metadata_limit=spec.profile.sample.max_metadata_bytes,
            )
            settings = ModelSettings.model_validate_json(source.scope.source.settings_json)
            context = EncodingContext(source, cpu_budget=1)
            plan = ModificationPlan.model_validate_json((job / window["plan_ref"]).read_bytes())
            operations = {}
            for operation in plan.operations:
                operations.setdefault(operation.target.location.request_key, []).append(operation)
            published = json.loads((job / window["rows_ref"]).read_text())
            histories = [[], []]
            totals = [dict(p=0, h=0, c=0), dict(p=0, h=0, c=0)]
            for index, request in enumerate(source.iter_requests()):
                raw, _ = apply_mutations(
                    request, tuple(operations.get(request.request_key, ())), settings
                )
                variants = [context.verify_baseline(request), context.encode(request, raw)]
                assert published[index]["request_key"] == request.request_key.model_dump(
                    mode="json"
                )
                for side, encoded, previous, total in zip(
                    ("before", "after"), variants, histories, totals, strict=True
                ):
                    ids = encoded.prompt_ids
                    # Compare literal token-prefix tuples rather than chained hash
                    # ledger keys. Only bounded sealed sample members are visited.
                    best = 0
                    for prior in previous:
                        common = 0
                        for a, b in zip(ids, prior, strict=False):
                            if a != b:
                                break
                            common += 1
                        best = max(best, common)
                    size = settings.effective_block_size
                    blocks = min(best // size, max(len(ids) - 1, 0) // size)
                    hit = (
                        max(blocks - int(settings.mtp), 0) * size
                        if settings.prefix_cache_enabled
                        else 0
                    )
                    expected = dict(p=len(ids), h=hit, c=len(ids) - hit)
                    assert all(published[index][side][k] == v for k, v in expected.items())
                    assert published[index][side]["ids_sha256"] == encoded.prompt_digest
                    for key, value in expected.items():
                        total[key] += value
                    previous.append(ids)
            for side, total in zip(("before", "after"), totals, strict=True):
                assert {k: int(v) for k, v in window[side].items()} == total
            before, after = totals
            pp = 100 * (Fraction(after["h"], after["p"]) - Fraction(before["h"], before["p"]))
            assert (
                Fraction(
                    int(window["improvement_pp"]["numerator"]),
                    int(window["improvement_pp"]["denominator"]),
                )
                == pp
            )
            checked.append(
                dict(
                    task=result["task"],
                    role=window["role"],
                    n=len(published),
                    before=before,
                    after=after,
                    improvement_pp=str(pp),
                )
            )
with output.open("x") as stream:
    json.dump(
        {"oracle": "literal-token-prefixes-no-production-ledger", "windows": checked},
        stream,
        indent=2,
    )
print(json.dumps(checked))
