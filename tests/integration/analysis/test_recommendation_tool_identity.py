import json

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.evaluation import evaluate_plan
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import RunSubmission
from tokenscope.prefix_analysis.detection import collect_dynamics, compile_dynamic_plan


@pytest.mark.parametrize("reordered", [False, True])
def test_dynamic_tool_comparison_preserves_identity(service, tmp_path, reordered):
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
        if reordered and i % 2:
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
        ("/tools/0/function/description", "/tools/1/function/description")
        if reordered
        else ("/tools/0/function/description",)
    )
    plan = compile_dynamic_plan(source, finding)
    assert len(plan.operations) == 6
    assert {op.target.location.source_pointer for op in plan.operations} == set(
        finding.comparison.difference_pointers
    )
    result = evaluate_plan(source, plan, tmp_path / "eval-tools")
    assert result.status == "available" and result.gate_passed is True

    from tokenscope.analysis_common.recommendation_evidence import edit_examples
    from tokenscope.analysis_common.recommendations import RecommendationBudget
    from tokenscope.prefix_analysis.recommendation_projection import project_low_hit

    rec = project_low_hit(
        [finding],
        [result],
        [plan],
        task_id="review",
        scope_id=source.scope.scope_id,
        total_requests=6,
    )[0]
    examples = edit_examples(
        rec, plan, source, RecommendationBudget(), {finding.finding_id: finding}
    )
    (tmp_path / "review-examples.json").write_text(
        json.dumps([e.model_dump(mode="json") for e in examples], ensure_ascii=False, indent=2)
    )
    paired = [e for e in examples if e.comparison]
    assert len(paired) == 2, "Both original pair members need a reliable comparison"
    for e in paired:
        other = source.read_request(e.comparison.source.request_key)
        ptr = e.comparison.source.source_pointer
        tool = json.loads(other.raw_body)["tools"][int(ptr.split("/")[2])]
        assert tool["function"]["name"] == "a", (ptr, tool, e.model_dump())

    for e in paired:
        assert e.after is not None and e.after.source.request_key == e.before.source.request_key
        for evidence in (e.before, e.comparison):
            original = source.read_request(evidence.source.request_key)
            assert evidence.source.raw_sha256 == original.raw_sha256
            assert (
                original.raw_body[evidence.raw_span.start : evidence.raw_span.end]
                == evidence.excerpt
            )
