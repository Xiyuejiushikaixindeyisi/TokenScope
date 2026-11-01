"""Real public worker/replay consumer; configured policies are synthetic, not business claims."""

import json

import pytest
from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient
from test_task_service import options, setup

from tokenscope.analysis_common.contracts import (
    DiagnosticRequest,
    DiagnosticSelection,
    SourceSelection,
)
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.plugins import EvidenceCapabilities, PluginRegistry, RunControl
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
from tokenscope.api.app import create_app
from tokenscope.domain import DEFAULT_SETTINGS, RunSubmission
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.token_content.auto_proposals import TokenProposalAdapter
from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin
from tokenscope.token_content.extraction import extract
from tokenscope.token_content.json_values import digest, dumps, loads


def test_real_same_task_recommendations_scope_counts_and_noop(service, monkeypatch, tmp_path):
    _, legacy_receipt, source = setup(service)
    original_hash = file_digest(source.directory / "requests.sqlite3")
    request = next(source.iter_requests())
    inventory = extract(
        request, EvidenceCapabilities(), RunControl(options().token_selection.budget)
    )
    identity = next(e.tool_identity for e in inventory.entries if e.tool_identity)
    selector = json.dumps(
        {
            "version": "token-result-selector-1",
            "appid": "a",
            "tool_name": "f",
            "tool_identity": identity,
            "representation": "text",
            "embedded_pointer": None,
        }
    )
    basis = Basis(
        kind="business_policy",
        ref="synthetic-test-only",
        revision="1",
        digest="a" * 64,
        scope_selector=selector,
        authority=BasisAuthority(
            source_kind="synthetic_fixture",
            source_ref="test",
            source_digest="b" * 64,
            status="verified",
        ),
        limitations=("Constructed policy, not business authorization or production benefits",),
    )
    recipes = []
    for name, kind, fields, rule, handler in [
        ("shorten", "select_lines", {"side": "first", "count": 1}, "T2", "select_result_lines"),
        ("noop", "select_lines", {"side": "first", "count": 99}, "T2", "select_result_lines"),
        (
            "retention",
            "retain_last",
            {"keep_last": 0, "replacement_json": '"omitted"'},
            "T4",
            "apply_retention_replacements",
        ),
    ]:
        recipes.append(
            Recipe(
                recipe_id=name,
                revision="1",
                primary_rule=rule,
                category_rules=(rule,),
                selector_json=selector,
                parameter_generator_json=json.dumps(
                    {
                        "version": "token-result-generator-1",
                        "kind": kind,
                        "omission_permitted": True,
                        **fields,
                    }
                ),
                handler_id=handler,
                handler_version="1",
                basis=basis,
                title=f"Synthetic {name}",
                change_summary="Configured test change",
            )
        )
    recipes.append(
        recipes[0].model_copy(
            update={
                "recipe_id": "same-execution-different-basis",
                "basis": basis.model_copy(
                    update={"ref": "synthetic-second-basis", "digest": "c" * 64}
                ),
            }
        )
    )
    recipes.append(recipes[0].model_copy(update={"recipe_id": "advice", "basis": None}))
    recipes.append(
        recipes[2].model_copy(
            update={
                "recipe_id": "negative-benefit",
                "parameter_generator_json": json.dumps(
                    {
                        "version": "token-result-generator-1",
                        "kind": "retain_last",
                        "keep_last": 0,
                        "replacement_json": json.dumps("expanded synthetic content " * 100),
                        "omission_permitted": True,
                    }
                ),
            }
        )
    )
    plugins = PluginRegistry()
    plugins.register(CurrentTokenContentPlugin())
    adapters = ProposalRegistry()
    adapters.register(TokenProposalAdapter())
    diagnostics = DiagnosticService(
        SourceResolver(service),
        plugins,
        RecommendationSettings(
            adapters, RecipeBundle(bundle_id="synthetic", revision="1", recipes=tuple(recipes))
        ),
    )
    receipt = diagnostics.submit(
        DiagnosticRequest(
            source=SourceSelection(
                source_kind="base", base_run_id=source.scope.source.base_run_id, appid="a"
            ),
            submission_key="auto-synthetic",
            selection=DiagnosticSelection(
                reason_codes=("request_length",), enable_low_hit=False, enable_token_content=True
            ),
        ),
        options(),
    )
    completed = diagnostics.process_next()
    assert completed.status == "ready", completed
    saved = diagnostics.items(receipt.task_id, "recommendation")
    assert len(saved) == 6
    by_recipe = {item["data"]["recipe"]["recipe_id"]: item["data"] for item in saved}
    for name, recommendation in by_recipe.items():
        if name == "advice":
            assert recommendation["status"] == "advice_only"
            assert recommendation["impact"]["modified_requests"] is None
            assert recommendation["evaluation_ref"] is None
            continue
        assert recommendation["status"] == "available", recommendation["reason_codes"]
        assert recommendation["impact"]["total_requests"] == "2"
        assert recommendation["impact"]["matched_requests"] == "2"
        expected = "0" if name == "noop" else "2"
        assert recommendation["impact"]["modified_requests"] == expected
        assert recommendation["evaluation"]["before"]["n"] == "2"
        assert recommendation["evaluation"]["after"]["n"] == "2"
        assert recommendation["evaluation_ref"]["task_id"] == receipt.task_id
        assert diagnostics.item(receipt.task_id, "plan", recommendation["prepared_plan_ref"]["id"])
        assert len(recommendation["example_refs"]) <= 3
        for ref in recommendation["example_refs"]:
            example = diagnostics.item(receipt.task_id, "recommendation_example", ref["id"])
            assert example["owner_id"] == recommendation["recommendation_id"]
            assert example["before"]["source"]["source_pointer"] == "/messages/3/content"
    left, right = by_recipe["shorten"], by_recipe["same-execution-different-basis"]
    assert left["recommendation_id"] != right["recommendation_id"]
    assert left["prepared_plan_ref"] != right["prepared_plan_ref"]
    assert left["execution_plan_ref"] == right["execution_plan_ref"]
    assert left["evaluation_ref"] == right["evaluation_ref"]
    assert left["evaluation_reused"] != right["evaluation_reused"]
    negative = by_recipe["negative-benefit"]
    assert int(negative["evaluation"]["after"]["p"]) > int(negative["evaluation"]["before"]["p"])
    assert negative["display_qualification"] == "token_evaluated"
    assert file_digest(source.directory / "requests.sqlite3") == original_hash
    fragments = diagnostics.items(receipt.task_id, "fragment")
    assert all(item["data"]["plugin_version"] == "token-content-2" for item in fragments)
    assert all(o["rule_id"] != "T1" for item in fragments for o in item["data"]["observations"])

    diagnostics.recommendations.budget = RecommendationBudget(max_token_evaluations=1)
    partial = diagnostics.submit(
        DiagnosticRequest(
            source=SourceSelection(
                source_kind="base", base_run_id=source.scope.source.base_run_id, appid="a"
            ),
            submission_key="auto-budget-limited",
            selection=DiagnosticSelection(
                reason_codes=("request_length",), enable_low_hit=False, enable_token_content=True
            ),
        ),
        options(),
    )
    assert diagnostics.process_next().status == "partial"
    partial_items = diagnostics.items(partial.task_id, "recommendation")
    assert any(item["data"]["status"] == "blocked" for item in partial_items)
    assert all(
        item["data"]["impact"]["modified_requests"] is None
        for item in partial_items
        if item["data"]["status"] == "blocked"
    )

    # Actual app registration reads the sealed extension; no analysis on GET.
    app = create_app(service, start_worker=False)

    def forbidden(*args, **kwargs):
        raise AssertionError("GET invoked computation")

    monkeypatch.setattr(TokenProposalAdapter, "propose", forbidden)
    monkeypatch.setattr(CurrentTokenContentPlugin, "analyze_request", forbidden)
    monkeypatch.setattr(EncodingContext, "encode", forbidden)
    with TestClient(app) as client:
        cap = client.get("/diagnostics/recommendations/capabilities")
        assert cap.status_code == 200
        assert cap.json()["token_rule_ids"] == ["T2", "T3", "T4"]
        headers = {"x-tokenscope-service-instance": cap.json()["service_instance_id"]}
        base = f"/diagnostics/tasks/{receipt.task_id}"
        response = client.get(base + "/recommendations", headers=headers)
        assert response.status_code == 200, response.text
        assert len(response.json()["items"]) == 6
        (tmp_path / "actual-http-t2-t4.json").write_text(
            json.dumps(response.json(), ensure_ascii=False, indent=2)
        )
        for item in response.json()["items"]:
            detail = client.get(base + "/recommendations/" + item["id"], headers=headers)
            assert detail.status_code == 200
            examples = client.get(
                base + "/recommendations/" + item["id"] + "/examples", headers=headers
            )
            assert examples.status_code == 200
        assert client.get(base + "/recommendations", headers=headers).json() == response.json()
        catalog = client.get("/diagnostics/discovery/catalog", headers=headers).json()
        assert any(item["task_id"] == receipt.task_id for item in catalog["defaults"])
        assert all(item["task_id"] != partial.task_id for item in catalog["defaults"])
        terminal = client.get(
            f"/diagnostics/discovery/tasks/{receipt.task_id}/terminal", headers=headers
        )
        assert terminal.status_code == 200
        old = f"/diagnostics/tasks/{legacy_receipt.task_id}"
        summary = client.get(old + "/recommendation-summary", headers=headers)
        assert summary.status_code == 200
        assert summary.json()["availability"] == "not_computed"
        old_fragments = client.get(old + "/items/fragment", headers=headers).json()["items"]
        assert any(o["rule_id"] == "T1" for f in old_fragments for o in f["data"]["observations"])
        assert (
            client.get(
                base + "/recommendations", headers={"x-tokenscope-service-instance": "wrong"}
            ).status_code
            == 409
        )


@pytest.mark.parametrize("model", list(DEFAULT_SETTINGS))
def test_t3_real_three_model_automatic_replay(service, model, tmp_path):
    tool = {
        "type": "function",
        "function": {
            "name": "f",
            "parameters": {
                "type": "object",
                "properties": {"document": {"type": "string"}, "document_ref": {"type": "string"}},
                "required": [],
            },
        },
    }
    payload = "synthetic complete document " * 40
    body = {
        "tools": [tool],
        "enable_thinking": False,
        "messages": [
            {"role": "user", "content": "read"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "c",
                        "type": "function",
                        "function": {"name": "f", "arguments": json.dumps({"document": payload})},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "c", "content": payload},
            {"role": "user", "content": payload},
        ],
    }
    rows = [
        valid_row(
            appid=appid,
            request_input=json.dumps(body),
            hash_id=f"t3-{i}",
            model_handle_start_time=f"2026-10-27T00:00:0{i}Z",
        )
        for i, appid in enumerate(("a", "b", "a"))
    ]
    (service.inputs.root / "auto-t3.csv").write_bytes(csv_bytes(rows))
    base = service.submit(RunSubmission(file_ref="auto-t3.csv", model_id=model))
    assert service.processor.process_next().status == "completed"
    selection = SourceSelection(source_kind="base", base_run_id=base.run_id, appid="a")
    identity = digest(dumps(loads(json.dumps(tool), max_depth=32), sort_keys=True))
    recipes = []
    for kind in ("reference", "delete_message"):
        selector = {
            "version": "token-duplicate-selector-1",
            "appid": "a",
            "payload_digest": digest(dumps(payload)),
            "target_kind": "argument_field" if kind == "reference" else "ordinary_message",
        }
        selector.update(
            {"tool_identity": identity, "argument_pointer": "/document"}
            if kind == "reference"
            else {"message_role": "user"}
        )
        raw = json.dumps(selector)
        generator = {
            "version": "token-duplicate-generator-1",
            "kind": kind,
            "omission_permitted": True,
        }
        if kind == "reference":
            generator.update(
                reference_key="document_ref",
                reference_value="existing://synthetic/1",
                protocol_ref="synthetic-consumer-protocol",
            )
        basis = Basis(
            kind="explicit_authorization",
            ref=f"synthetic-{kind}",
            revision="1",
            digest="a" * 64,
            scope_selector=raw,
            authority=BasisAuthority(
                source_kind="synthetic_fixture",
                source_ref="test",
                source_digest="b" * 64,
                status="verified",
            ),
            limitations=("Constructed mapping/policy; no production authorization",),
        )
        recipes.append(
            Recipe(
                recipe_id=kind,
                revision="1",
                primary_rule="T3",
                category_rules=("T3",),
                selector_json=raw,
                parameter_generator_json=json.dumps(generator),
                basis=basis,
                handler_id="replace_payload_with_reference"
                if kind == "reference"
                else "remove_authorized_duplicate_message",
                handler_version="1",
                title=f"Synthetic {kind}",
                change_summary="Explicit configured change",
            )
        )
    plugins = PluginRegistry()
    plugins.register(CurrentTokenContentPlugin())
    adapters = ProposalRegistry()
    adapters.register(TokenProposalAdapter())
    diagnostics = DiagnosticService(
        SourceResolver(service),
        plugins,
        RecommendationSettings(
            adapters, RecipeBundle(bundle_id="synthetic-t3", revision="1", recipes=tuple(recipes))
        ),
    )
    receipt = diagnostics.submit(
        DiagnosticRequest(
            source=selection,
            submission_key="t3-auto",
            selection=DiagnosticSelection(
                reason_codes=("request_length",), enable_low_hit=False, enable_token_content=True
            ),
        ),
        options(),
    )
    completed = diagnostics.process_next()
    assert completed.status == "ready", completed
    items = diagnostics.items(receipt.task_id, "recommendation")
    assert len(items) == 2
    for item in items:
        rec = item["data"]
        assert rec["status"] == "available", rec["reason_codes"]
        assert rec["impact"]["modified_requests"] == rec["impact"]["total_requests"] == "2"
        assert int(rec["evaluation"]["after"]["p"]) < int(rec["evaluation"]["before"]["p"])
        assert rec["support_refs"] and not rec["support_refs"][0]["finding_ids"]

    app = create_app(service, start_worker=False)
    with TestClient(app) as client:
        cap = client.get("/diagnostics/recommendations/capabilities").json()
        headers = {"x-tokenscope-service-instance": cap["service_instance_id"]}
        response = client.get(
            f"/diagnostics/tasks/{receipt.task_id}/recommendations", headers=headers
        )
        assert response.status_code == 200
        assert len(response.json()["items"]) == 2
        (tmp_path / "actual-http-t3.json").write_text(
            json.dumps(response.json(), ensure_ascii=False, indent=2)
        )


def test_less_input_can_increase_full_block_compute(service):
    """Find a real token/block boundary, then verify the automatic path reports both metrics."""
    model = "GLM-5.2"
    block = DEFAULT_SETTINGS[model].effective_block_size
    tool = {"type": "function", "function": {"name": "f"}}
    rows = []
    for padding in range(block):
        body = {
            "enable_thinking": False,
            "tools": [tool],
            "messages": [
                {"role": "user", "content": "stable " * (padding + 3 * block)},
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "c",
                            "type": "function",
                            "function": {"name": "f", "arguments": "{}"},
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "c", "content": "a\nb\n"},
            ],
        }
        for ordinal in range(2):
            rows.append(
                valid_row(
                    appid=f"boundary-{padding}",
                    hash_id=f"{padding}-{ordinal}",
                    request_input=json.dumps(body),
                    model_handle_start_time=f"2026-10-27T00:00:0{ordinal}Z",
                )
            )
    (service.inputs.root / "block-boundary.csv").write_bytes(csv_bytes(rows))
    base = service.submit(RunSubmission(file_ref="block-boundary.csv", model_id=model))
    assert service.processor.process_next().status == "completed"
    resolver = SourceResolver(service)
    selected = None
    for padding in range(block):
        selection = SourceSelection(
            source_kind="base", base_run_id=base.run_id, appid=f"boundary-{padding}"
        )
        source = resolver.resolve_scope(selection)
        if next(source.iter_requests()).baseline_metrics.p % block == 1:
            selected = selection
            break
    assert selected is not None, "Fixture failed to locate a real token block boundary"
    selector = json.dumps(
        {
            "version": "token-result-selector-1",
            "appid": selected.appid,
            "tool_name": "f",
            "tool_identity": digest(dumps(loads(json.dumps(tool), max_depth=32), sort_keys=True)),
            "representation": "text",
            "embedded_pointer": None,
        }
    )
    basis = Basis(
        kind="business_policy",
        ref="synthetic-boundary",
        revision="1",
        digest="a" * 64,
        scope_selector=selector,
        authority=BasisAuthority(
            source_kind="synthetic_fixture",
            source_ref="test",
            source_digest="b" * 64,
            status="verified",
        ),
    )
    recipe = Recipe(
        recipe_id="boundary",
        revision="1",
        primary_rule="T2",
        category_rules=("T2",),
        selector_json=selector,
        parameter_generator_json=json.dumps(
            {
                "version": "token-result-generator-1",
                "kind": "select_lines",
                "side": "first",
                "count": 1,
                "omission_permitted": True,
            }
        ),
        basis=basis,
        handler_id="select_result_lines",
        handler_version="1",
        title="Synthetic boundary",
        change_summary="Retain the first result line",
    )
    registry = PluginRegistry()
    registry.register(CurrentTokenContentPlugin())
    proposals = ProposalRegistry()
    proposals.register(TokenProposalAdapter())
    diagnostics = DiagnosticService(
        resolver,
        registry,
        RecommendationSettings(
            proposals, RecipeBundle(bundle_id="synthetic-boundary", revision="1", recipes=(recipe,))
        ),
    )
    receipt = diagnostics.submit(
        DiagnosticRequest(
            source=selected,
            submission_key="boundary",
            selection=DiagnosticSelection(
                reason_codes=("request_length",), enable_low_hit=False, enable_token_content=True
            ),
        ),
        options(),
    )
    assert diagnostics.process_next().status == "ready"
    recommendation = diagnostics.items(receipt.task_id, "recommendation")[0]["data"]
    evaluation = recommendation["evaluation"]
    assert int(evaluation["after"]["p"]) < int(evaluation["before"]["p"])
    assert int(evaluation["after"]["c"]) > int(evaluation["before"]["c"])
    assert recommendation["impact"]["modified_requests"] == "2"
    assert recommendation["display_qualification"] == "token_evaluated"
