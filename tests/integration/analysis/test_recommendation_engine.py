"""Actual Token adapter and local model replay with explicitly synthetic omission policy."""

import json

from conftest import csv_bytes, valid_row
from test_diagnostic_tasks import options

from tokenscope.analysis_common.contracts import (
    DiagnosticRequest,
    DiagnosticSelection,
    SourceSelection,
)
from tokenscope.analysis_common.plugins import PluginRegistry
from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
from tokenscope.analysis_common.recommendation_runtime import RecommendationSettings
from tokenscope.analysis_common.recommendations import (
    Basis,
    BasisAuthority,
    Recipe,
    RecipeBundle,
    RecommendationBudget,
)
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.domain import RunSubmission
from tokenscope.token_content.auto_proposals import TokenProposalAdapter
from tokenscope.token_content.json_values import digest, dumps, loads
from tokenscope.token_content.plugin import TokenContentPlugin


def configured(service, *, basis=True, budget=None, duplicate=False):
    tool = {
        "type": "function",
        "function": {
            "name": "search",
            "description": "lookup",
            "parameters": {"type": "object", "properties": {}},
        },
    }
    raw = json.dumps(
        {
            "messages": [
                {"role": "user", "content": "look up"},
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call1",
                            "type": "function",
                            "function": {"name": "search", "arguments": "{}"},
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call1",
                    "content": json.dumps({"id": 1, "noise": "padding " * 120}),
                },
            ],
            "tools": [tool],
            "enable_thinking": False,
        }
    )
    rows = [
        valid_row(appid="a", request_input=raw, model_handle_start_time=f"2026-10-27T00:00:0{i}Z")
        for i in range(3)
    ]
    (service.inputs.root / "recommend.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="recommend.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    selector = json.dumps(
        {
            "version": "token-result-selector-1",
            "appid": "a",
            "tool_name": "search",
            "tool_identity": digest(dumps(loads(json.dumps(tool), max_depth=64), sort_keys=True)),
            "representation": "structural_json",
            "embedded_pointer": "",
        }
    )
    policy = (
        Basis(
            kind="business_policy",
            ref="synthetic-only",
            revision="1",
            digest="a" * 64,
            scope_selector=selector,
            authority=BasisAuthority(
                source_kind="synthetic_fixture",
                source_ref="test-not-production",
                source_digest="b" * 64,
                status="verified",
            ),
        )
        if basis
        else None
    )
    recipe = Recipe(
        recipe_id="projection",
        revision="1",
        primary_rule="T2",
        category_rules=("T2",),
        handler_id="project_result_fields",
        handler_version="1",
        selector_json=selector,
        parameter_generator_json=json.dumps(
            {
                "version": "token-result-generator-1",
                "kind": "project_fields",
                "omission_permitted": True,
                "fields": ["id"],
                "field_level": "object",
            }
        ),
        basis=policy,
        title="Synthetic projection",
        change_summary="Synthetic policy permits noise omission",
    )
    recipes = (recipe,)
    if duplicate:
        other = recipe.model_copy(
            update={
                "recipe_id": "projection-second-basis",
                "basis": policy.model_copy(update={"ref": "synthetic-other"}),
            }
        )
        recipes = (*recipes, other)
    bundle = RecipeBundle(bundle_id="synthetic-only", revision="1", recipes=recipes)
    registry = PluginRegistry()
    registry.register(TokenContentPlugin())
    proposal_registry = ProposalRegistry()
    proposal_registry.register(TokenProposalAdapter())
    settings = RecommendationSettings(proposal_registry, bundle, budget or RecommendationBudget())
    diagnostics = DiagnosticService(SourceResolver(service), registry, settings)
    request = DiagnosticRequest(
        source=SourceSelection(source_kind="base", base_run_id=run.run_id, appid="a"),
        selection=DiagnosticSelection(
            reason_codes=("request_length",), enable_low_hit=False, enable_token_content=True
        ),
        submission_key="rec-task",
    )
    return diagnostics, request


def test_real_adapter_full_replay_and_shared_execution(service):
    diagnostics, request = configured(service, duplicate=True)
    task = diagnostics.submit(request, options(max_encoding_calls=500))
    result = diagnostics.process_next()
    assert result.status == "ready", diagnostics.report(task.task_id)
    recs = [i["data"] for i in diagnostics.items(task.task_id, "recommendation")]
    assert len(recs) == 2 and all(r["status"] == "available" for r in recs)
    assert all(r["impact"]["modified_requests"] == "3" for r in recs)
    assert len({r["evaluation_ref"]["id"] for r in recs}) == 1
    assert sum(r["evaluation_reused"] for r in recs) == 1
    assert all(
        int(r["evaluation"]["after"]["p"]) < int(r["evaluation"]["before"]["p"]) for r in recs
    )
    assert all(len(r["example_refs"]) == 3 for r in recs)


def test_missing_basis_is_complete_advice(service):
    diagnostics, request = configured(service, basis=False)
    task = diagnostics.submit(request, options())
    assert diagnostics.process_next().status == "ready"
    rec = diagnostics.items(task.task_id, "recommendation")[0]["data"]
    assert rec["status"] == "advice_only" and rec["impact"]["modified_requests"] is None
    assert rec["evaluation"] is None and "RECIPE_BASIS_MISSING" in rec["reason_codes"]
    examples = diagnostics.items(task.task_id, "recommendation_example")
    assert examples and len(examples) <= 3
    assert all(e["data"]["before"]["raw_span"] is not None for e in examples)
    assert all(e["data"]["after"] is None for e in examples)


def test_budget_partial_and_snapshot_idempotency(service):
    diagnostics, request = configured(service, budget=RecommendationBudget(max_proposals=2))
    task = diagnostics.submit(request, options())
    old = diagnostics.store.row(task.task_id)["intent"]
    diagnostics.recommendations.bundle = RecipeBundle(bundle_id="changed", revision="2", recipes=())
    assert diagnostics.submit(request, options()).task_id == task.task_id
    assert diagnostics.store.row(task.task_id)["intent"] == old
    assert diagnostics.process_next().status == "partial"
    summary = diagnostics.items(task.task_id, "recommendation_summary")[0]["data"]
    assert "RECOMMENDATION_PROPOSALS_EXHAUSTED" in summary["reason_codes"]
    assert summary["stop_location"] is not None
    assert summary["proposal_coverage"]["complete"] is False
    assert not diagnostics.items(task.task_id, "evaluation")


def test_plan_budget_leaves_no_dangling_reference(service):
    diagnostics, request = configured(service, budget=RecommendationBudget(max_plan_bytes=1))
    task = diagnostics.submit(request, options())
    assert diagnostics.process_next().status == "partial"
    rec = diagnostics.items(task.task_id, "recommendation")[0]["data"]
    assert rec["status"] == "blocked" and rec["prepared_plan_ref"] is None
    assert rec["evaluation_ref"] is None and rec["impact"]["modified_requests"] is None
    assert not diagnostics.items(task.task_id, "plan")


def test_example_budget_preserves_complete_evaluation_but_marks_partial(service):
    diagnostics, request = configured(
        service, budget=RecommendationBudget(max_example_bytes_per_group=1)
    )
    task = diagnostics.submit(request, options())
    assert diagnostics.process_next().status == "partial"
    rec = diagnostics.items(task.task_id, "recommendation")[0]["data"]
    assert rec["status"] == "available" and not rec["example_refs"]
    assert "RECOMMENDATION_EXAMPLE_BUDGET_EXHAUSTED" in rec["reason_codes"]


def test_cancel_during_adapter_does_not_publish_report(service, monkeypatch):
    diagnostics, request = configured(service)
    task = diagnostics.submit(request, options())
    adapter = diagnostics.recommendations.registry.get()
    original = adapter.propose

    def cancel(*args, **kwargs):
        diagnostics.cancel(task.task_id)
        return original(*args, **kwargs)

    monkeypatch.setattr(adapter, "propose", cancel)
    assert diagnostics.process_next().status == "interrupted"
    assert diagnostics.store.row(task.task_id)["report_digest"] is None


def test_group_budget_keeps_full_scope_and_records_unrun_group(service):
    diagnostics, request = configured(
        service, duplicate=True, budget=RecommendationBudget(max_recommendations=1)
    )
    task = diagnostics.submit(request, options(max_encoding_calls=500))
    assert diagnostics.process_next().status == "partial"
    summary = diagnostics.items(task.task_id, "recommendation_summary")[0]["data"]
    coverage = summary["evaluation_coverage"]
    assert coverage["eligible"] == "2" and coverage["checked"] == "1"
    assert coverage["completed"] == "1" and coverage["not_run"] == "1"
    assert coverage["complete"] is False and summary["stop_location"] is not None
    recs = diagnostics.items(task.task_id, "recommendation")
    assert len(recs) == 1
    assert recs[0]["data"]["impact"]["total_requests"] == "3"
    assert recs[0]["data"]["impact"]["modified_requests"] == "3"
