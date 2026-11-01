import json

from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.evaluation import evaluate_plan
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import RunSubmission
from tokenscope.prefix_analysis.service import collect_l2, compile_l2_plan


def test_tool_permutation_actual_replay(service, tmp_path):
    tools = [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": name * 300,
                "parameters": {"type": "object", "properties": {}},
            },
        }
        for name in ("a", "b")
    ]
    rows = []
    for i in range(6):
        raw = json.dumps(
            {
                "messages": [{"role": "user", "content": "stable " * 500}],
                "tools": tools if i % 2 else list(reversed(tools)),
                "enable_thinking": False,
            }
        )
        rows.append(
            valid_row(
                appid="a", request_input=raw, model_handle_start_time=f"2026-10-27T00:00:0{i}Z"
            )
        )
    (service.inputs.root / "tools.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="tools.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    source = SourceResolver(service).resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run.run_id, appid="a")
    )
    report = collect_l2(source, tmp_path / "discovery", candidate_limit=2)
    assert report.findings and report.checked_requests == 6 and report.candidate_coverage_partial
    assert all(f.comparison.left != f.comparison.right for f in report.findings)
    plan = compile_l2_plan(source, report.findings[0])
    assert len(plan.operations) == 3
    result = evaluate_plan(source, plan, tmp_path / "evaluation")
    assert result.status == "available", result
    assert result.after.h > result.before.h
