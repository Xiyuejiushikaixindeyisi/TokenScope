"""Private consumer of frozen v2; synthetic sources, no listeners."""

import inspect
from unittest.mock import patch

from test_task_service import options, setup

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.execution_v2 import RequestV2, RuntimeV2, SelectionV2
from tokenscope.analysis_common.plugins import PluginRegistry
from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
from tokenscope.analysis_common.recommendation_runtime import RecommendationSettings
from tokenscope.analysis_common.recommendations import RecipeBundle
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.token_content.auto_proposals import TokenProposalAdapter
from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin


def test_disabled_token_all_entrypoints_and_encoding_sentinels(service):
    _, _, source = setup(service)
    registry = PluginRegistry()
    registry.register(CurrentTokenContentPlugin())
    adapters = ProposalRegistry()
    adapters.register(TokenProposalAdapter())
    diagnostics = DiagnosticService(
        SourceResolver(service),
        registry,
        RecommendationSettings(adapters, RecipeBundle(bundle_id="empty", revision="1", recipes=())),
    )
    request = RequestV2(
        source=SourceSelection(
            source_kind="base", base_run_id=source.scope.source.base_run_id, appid="a"
        ),
        submission_key="hv2-private-disabled",
        selection=SelectionV2(
            reason_codes=("low_hit",), enable_low_hit=True, enable_token_content=False
        ),
    )
    opts = RuntimeV2(**(options().model_dump() | {"version": "diagnostics-runtime-2"}))
    original = EncodingContext.encode

    def guarded_encode(self, *args, **kwargs):
        assert not any(
            "/token_content/" in f.filename or f.filename.endswith("recommendation_engine.py")
            for f in inspect.stack()
        )
        return original(self, *args, **kwargs)

    with (
        patch.object(
            CurrentTokenContentPlugin,
            "analyze_request",
            side_effect=AssertionError("disabled analyze"),
        ),
        patch.object(
            TokenProposalAdapter, "propose", side_effect=AssertionError("disabled propose")
        ),
        patch.object(
            TokenProposalAdapter, "prepare_proposal", side_effect=AssertionError("disabled prepare")
        ),
        patch.object(EncodingContext, "encode", guarded_encode),
    ):
        receipt = diagnostics.submit(request, opts)
        assert diagnostics.process_next().status in ("ready", "partial")
    assert diagnostics.report(receipt.task_id)["selected_directions"] == ["low_hit"]
    assert diagnostics.items(receipt.task_id, "fragment") == []


def test_v2_missing_basis_keeps_unknown_impact(service):
    import json

    from tokenscope.analysis_common.plugins import EvidenceCapabilities, RunControl
    from tokenscope.analysis_common.recommendations import Recipe
    from tokenscope.token_content.extraction import extract

    _, _, source = setup(service)
    raw = next(source.iter_requests())
    inventory = extract(raw, EvidenceCapabilities(), RunControl(options().token_selection.budget))
    identity = next(e.tool_identity for e in inventory.entries if e.tool_identity)
    recipe = Recipe(
        recipe_id="synthetic-advice",
        revision="1",
        primary_rule="T2",
        category_rules=("T2",),
        selector_json=json.dumps(
            {
                "version": "token-result-selector-1",
                "appid": "a",
                "tool_name": "f",
                "tool_identity": identity,
                "representation": "text",
                "embedded_pointer": None,
            }
        ),
        parameter_generator_json=json.dumps(
            {
                "version": "token-result-generator-1",
                "kind": "select_lines",
                "side": "first",
                "count": 1,
                "omission_permitted": True,
            }
        ),
        handler_id="select_result_lines",
        handler_version="1",
        basis=None,
        title="Synthetic missing basis",
        change_summary="Not production authorization",
    )
    plugins = PluginRegistry()
    plugins.register(CurrentTokenContentPlugin())
    adapters = ProposalRegistry()
    adapters.register(TokenProposalAdapter())
    diagnostics = DiagnosticService(
        SourceResolver(service),
        plugins,
        RecommendationSettings(
            adapters, RecipeBundle(bundle_id="synthetic", revision="1", recipes=(recipe,))
        ),
    )
    opts = options().model_dump()
    opts["version"] = "diagnostics-runtime-2"
    opts["token_selection"]["rule_ids"] = ("T2", "T3", "T4")
    request = RequestV2(
        source=SourceSelection(
            source_kind="base", base_run_id=source.scope.source.base_run_id, appid="a"
        ),
        submission_key="hv2-advice",
        selection=SelectionV2(
            reason_codes=("request_length",), enable_low_hit=False, enable_token_content=True
        ),
    )
    receipt = diagnostics.submit(request, RuntimeV2(**opts))
    assert diagnostics.process_next().status == "ready"
    items = diagnostics.items(receipt.task_id, "recommendation")
    assert len(items) == 1
    value = items[0]["data"]
    assert value["status"] == "advice_only"
    assert value["impact"]["modified_requests"] is None
    assert value["evaluation_ref"] is None
