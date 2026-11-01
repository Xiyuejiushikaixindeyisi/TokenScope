"""Persist actual local reports under pytest basetemp for readonly frontend acceptance."""

import json

from conftest import csv_bytes, valid_row
from test_diagnostic_tasks import options, setup

from tokenscope.analysis_common.contracts import (
    DiagnosticRequest,
    DiagnosticSelection,
    SourceSelection,
)
from tokenscope.analysis_common.plugins import PluginRegistry
from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
from tokenscope.analysis_common.recommendation_runtime import RecommendationSettings
from tokenscope.analysis_common.recommendations import RecipeBundle
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import RunSubmission
from tokenscope.token_content.auto_proposals import TokenProposalAdapter
from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin


def test_frontend_low_hit_and_difference_reports(service, tmp_path):
    legacy, request = setup(service, low_hit=True)
    registry = PluginRegistry()
    registry.register(CurrentTokenContentPlugin())
    proposals = ProposalRegistry()
    proposals.register(TokenProposalAdapter())
    settings = RecommendationSettings(
        proposals, RecipeBundle(bundle_id="synthetic-no-token-policy", revision="1", recipes=())
    )
    diagnostics = DiagnosticService(SourceResolver(service), registry, settings)
    first = diagnostics.submit(request, options(candidate_limit=16, max_encoding_calls=500))
    assert diagnostics.process_next().status == "ready"
    recs = diagnostics.items(first.task_id, "recommendation")
    assert any(i["data"]["display_qualification"] == "low_hit_optimization" for i in recs)
    for item in recs:
        recipe = item["data"]["recipe"]
        if recipe["primary_rule"] == "L1":
            assert recipe["title"] == "请求前部动态内容影响相同指令复用"
            assert "删除/messages/0/content" in recipe["change_summary"]
            assert "评估" not in recipe["change_summary"]
            assert "前提" in recipe["change_summary"]
    examples = diagnostics.items(first.task_id, "recommendation_example")
    edits = [e["data"] for e in examples if e["data"]["after"] is not None]
    assert edits and any(e["comparison"] is not None for e in edits)
    assert all(len(e["before"]["excerpt"]) < 100 for e in edits)
    assert all(e["before"]["source"]["text_range"] is not None for e in edits)
    groups = diagnostics.items(first.task_id, "difference_group")
    assert any(g["data"]["rule_id"] == "L4" for g in groups)
    assert all(len(g["data"]["example_refs"]) <= 3 for g in groups)
    l4_ids = {g["data"]["group_id"] for g in groups if g["data"]["rule_id"] == "L4"}
    l4_examples = [e["data"] for e in examples if e["data"]["owner_id"] in l4_ids]
    assert l4_examples
    assert all(len(e["before"]["excerpt"]) < 100 for e in l4_examples)
    assert all(e["before"]["source"]["text_range"] is not None for e in l4_examples)
    rows = []
    for i in range(4):
        payload = {"id": 1, "text": "example result"}
        content = (
            json.dumps(payload, indent=2) if i % 2 else json.dumps(payload, separators=(",", ":"))
        )
        body = {
            "enable_thinking": False,
            "tools": [
                {
                    "type": "function",
                    "function": {"name": "f", "parameters": {"type": "object", "properties": {}}},
                }
            ],
            "messages": [
                {"role": "user", "content": "lookup"},
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "c",
                            "type": "function",
                            "function": {"name": "f", "arguments": "{}"},
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "c", "content": content},
            ],
        }
        rows.append(
            valid_row(
                appid="representation",
                request_input=json.dumps(body),
                model_handle_start_time=f"2026-10-27T00:00:0{i}Z",
            )
        )
    (service.inputs.root / "representations.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="representations.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    request = DiagnosticRequest(
        source=SourceSelection(source_kind="base", base_run_id=run.run_id, appid="representation"),
        selection=DiagnosticSelection(
            reason_codes=("low_hit",), enable_low_hit=True, enable_token_content=True
        ),
        submission_key="frontend-l5",
    )
    second = diagnostics.submit(request, options(candidate_limit=16, max_encoding_calls=500))
    assert diagnostics.process_next().status == "ready"
    groups = diagnostics.items(second.task_id, "difference_group")
    assert any(g["data"]["rule_id"] == "L5" for g in groups)
    manifest = {
        "nature": "actual local GLM-5.2 replay on synthetic requests; no production claims",
        "input_root": str(service.inputs.root),
        "state_root": str(service.state_root),
        "tasks": {"low_hit_l4": first.task_id, "l5_representation": second.task_id},
        "reports": [diagnostics.report(t) for t in (first.task_id, second.task_id)],
    }
    (tmp_path / "frontend-reports.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)
    )
