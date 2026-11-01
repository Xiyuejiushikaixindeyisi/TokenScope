import json

from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.evaluation import evaluate_plan
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import RunSubmission
from tokenscope.prefix_analysis.comparison import read_comparison
from tokenscope.prefix_analysis.detection import collect_dynamics, compile_dynamic_plan


def test_dynamic_prompt_actual_deletion_and_gain(service, tmp_path):
    rows = []
    for i in range(4):
        raw = json.dumps(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": f"Time: 2026-10-31 09:00:0{i}\n" + "stable " * 2000,
                    },
                    {"role": "user", "content": "hello"},
                ],
                "enable_thinking": False,
            }
        )
        rows.append(
            valid_row(
                appid="a", request_input=raw, model_handle_start_time=f"2026-10-27T00:00:0{i}Z"
            )
        )
    (service.inputs.root / "dynamic.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="dynamic.csv", model_id="GLM-5.2"))
    service.processor.process_next()
    source = SourceResolver(service).resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run.run_id, appid="a")
    )
    report = collect_dynamics(
        source, tmp_path / "discovery", candidate_limit=2, include_history=True
    )
    history = next(f for f in report.findings if f.rule_id == "L4")
    assert history.evidence_status == "needs_association" and history.recipe_json is None
    left, right = read_comparison(source, history.comparison)
    assert left == source.read_request(history.comparison.left).raw_body
    assert right == source.read_request(history.comparison.right).raw_body
    assert len(json.loads(left)["messages"]) == 2
    finding = next(f for f in report.findings if f.rule_id == "L1")
    plan = compile_dynamic_plan(source, finding)
    assert plan.action_class == "hypothetical_content_removal"
    assert len(plan.operations) == 4
    result = evaluate_plan(source, plan, tmp_path / "eval", stage="full")
    assert result.status == "available" and result.gate_passed is True


def test_reordered_dynamic_tool_has_both_paths_and_real_gain(service, tmp_path):
    rows = []
    for i in range(6):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "a",
                    "description": f"workspace /tmp/job-{i}\n" + "stable " * 700,
                },
            },
            {"type": "function", "function": {"name": "b", "description": "other"}},
        ]
        if i % 2:
            tools.reverse()
        raw = json.dumps(
            {
                "messages": [{"role": "user", "content": "query"}],
                "tools": tools,
                "enable_thinking": False,
            }
        )
        rows.append(
            valid_row(
                appid="a", request_input=raw, model_handle_start_time=f"2026-10-27T00:00:0{i}Z"
            )
        )
    (service.inputs.root / "tools-dynamic.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="tools-dynamic.csv", model_id="GLM-5.2"))
    service.processor.process_next()
    source = SourceResolver(service).resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run.run_id, appid="a")
    )
    report = collect_dynamics(source, tmp_path / "discover-tools", candidate_limit=1)
    finding = next(f for f in report.findings if f.recipe_json)
    assert finding.rule_id == "L3"
    assert finding.comparison.difference_pointers == (
        "/tools/0/function/description",
        "/tools/1/function/description",
    )
    plan = compile_dynamic_plan(source, finding)
    assert len(plan.operations) == 6
    assert {op.target.location.source_pointer for op in plan.operations} == set(
        finding.comparison.difference_pointers
    )
    result = evaluate_plan(source, plan, tmp_path / "eval-tools")
    assert result.status == "available" and result.gate_passed is True
