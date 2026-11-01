import json

from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import RunSubmission
from tokenscope.prefix_analysis.detection import collect_dynamics
from tokenscope.prefix_analysis.experiments import pilot_scope, run_experiment


def test_real_two_stage_combination_and_individual_blocking(service, tmp_path):
    rows = []
    for i in range(6):
        raw = json.dumps(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": f"Time: 2026-10-31 09:00:0{i} path: /tmp/job-{i}\n"
                        + "stable " * 700,
                    },
                    {"role": "user", "content": "query"},
                ],
                "enable_thinking": False,
            }
        )
        rows.append(
            valid_row(
                appid="a", request_input=raw, model_handle_start_time=f"2026-10-27T00:00:0{i}Z"
            )
        )
    (service.inputs.root / "experiment.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="experiment.csv", model_id="GLM-5.2"))
    service.processor.process_next()
    source = SourceResolver(service).resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run.run_id, appid="a")
    )
    report = collect_dynamics(source, tmp_path / "discover", candidate_limit=1)
    findings = tuple(
        f for f in report.findings if f.comparison.right.source_record_index == 2 and f.recipe_json
    )
    assert len(findings) == 2
    small = pilot_scope(source, findings[0], 3)
    assert [r.request_key.source_record_index for r in small.iter_requests()] == [1, 2, 3]
    assert pilot_scope(source, findings[0], 6) is None
    singles = [
        run_experiment(source, (f,), tmp_path / f"single-{i}", pilot_limit=3)
        for i, f in enumerate(findings)
    ]
    assert all(item.status == "pilot_below_gate" and item.full is None for item in singles)
    combined = run_experiment(source, findings, tmp_path / "combo", pilot_limit=3)
    assert combined.status == "full_qualified", combined
    assert combined.pilot.before.n == 3 and combined.full.before.n == 6
    assert combined.full.display_eligible
    assert not combined.pilot.display_eligible


def test_real_pilot_pass_full_below_gate_is_not_an_optimization(service, tmp_path):
    rows = []
    for i in range(6):
        content = (
            (f"time 2026-10-31 09:00:0{i}\n" + "stable " * 300)
            if i < 3
            else (f"independent-{i} " + "filler " * 30000)
        )
        raw = json.dumps(
            {
                "messages": [
                    {"role": "system", "content": content},
                    {"role": "user", "content": "query"},
                ],
                "enable_thinking": False,
            }
        )
        rows.append(
            valid_row(
                appid="a", request_input=raw, model_handle_start_time=f"2026-10-27T00:00:0{i}Z"
            )
        )
    (service.inputs.root / "diluted.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="diluted.csv", model_id="GLM-5.2"))
    service.processor.process_next()
    source = SourceResolver(service).resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run.run_id, appid="a")
    )
    report = collect_dynamics(source, tmp_path / "find", candidate_limit=1)
    finding = next(f for f in report.findings if f.recipe_json)
    result = run_experiment(source, (finding,), tmp_path / "evaluate", pilot_limit=3)
    assert result.pilot.gate_passed is True
    assert result.full.before.n == result.full.after.n == 6
    assert result.status == "full_below_gate" and not result.full.display_eligible
