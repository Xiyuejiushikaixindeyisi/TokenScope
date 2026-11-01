"""Synthetic business policy fixtures; no production authorization or benefit claims."""

import json

import pytest
from test_auto_config import config
from test_extraction import control, view

from tokenscope.analysis_common.plugins import EvidenceCapabilities, PluginSelection
from tokenscope.analysis_common.proposal_plugins import ProposalAdapter, validate_support
from tokenscope.analysis_common.recommendations import Basis, BasisAuthority, Recipe, RecipeBundle
from tokenscope.token_content.auto_proposals import TokenProposalAdapter
from tokenscope.token_content.extraction import extract
from tokenscope.token_content.plugin import TokenContentPlugin


def fixture(kind="project_fields", basis=True, **updates):
    body = {
        "tools": [{"type": "function", "function": {"name": "search"}}],
        "messages": [
            {"role": "function", "name": "search", "content": content}
            for content in ['{"id":1,"noise":2}', '{"id":2,"noise":3}']
        ],
    }
    request = view(body)
    evidence = EvidenceCapabilities()
    inventory = extract(request, evidence, control())
    identity = next(e.tool_identity for e in inventory.entries if e.tool_identity)
    args = config(kind)
    selector = json.loads(args[0])
    selector.update(appid=request.appid, tool_name="search", tool_identity=identity)
    selector_json = json.dumps(selector)
    recipe_basis = (
        Basis(
            kind="business_policy",
            ref="synthetic-policy-not-production",
            revision="1",
            digest="a" * 64,
            scope_selector=selector_json,
            authority=BasisAuthority(
                source_kind="synthetic_fixture",
                source_ref="test",
                source_digest="b" * 64,
                status="verified",
            ),
            limitations=("Constructed engineering fixture, not business authorization",),
        )
        if basis
        else None
    )
    recipe = Recipe(
        recipe_id="synthetic-recipe",
        revision="1",
        primary_rule=args[2],
        category_rules=(args[2],),
        handler_id=args[3],
        handler_version="1",
        selector_json=selector_json,
        parameter_generator_json=args[1],
        basis=recipe_basis,
        title="Synthetic projection",
        change_summary="Retain configured fields",
    )
    if updates:
        recipe = recipe.model_copy(update=updates)
    bundle = RecipeBundle(bundle_id="synthetic", revision="1", recipes=(recipe,))
    fragment = TokenContentPlugin().analyze_request(
        request,
        PluginSelection(rule_ids=("T2", "T4"), budget=control().budget),
        evidence,
        control(),
    )
    return request, fragment, bundle


def propose(request, fragment, bundle):
    adapter: ProposalAdapter = TokenProposalAdapter()
    return adapter.propose(
        "task", request.scope_id, request, "0", fragment, bundle, EvidenceCapabilities(), control()
    )


@pytest.mark.parametrize("kind,count", [("project_fields", 2), ("retain_last", 1)])
def test_propose_and_prepare(kind, count):
    request, fragment, bundle = fixture(kind)
    (proposal,) = propose(request, fragment, bundle)
    assert len(proposal.request_targets) == count
    validate_support(proposal, "task", "scope", "0", fragment)
    assert proposal.recipe.basis is not None
    prepared = TokenProposalAdapter().prepare_proposal(request, proposal, proposal.recipe.basis)
    assert prepared.status == "prepared", prepared.reason_codes
    assert len(prepared.operations) == count
    assert all(t.location.source_pointer.startswith("/messages/") for t in proposal.request_targets)


def test_no_basis_is_advice_without_executable_targets():
    request, fragment, bundle = fixture(basis=False)
    (proposal,) = propose(request, fragment, bundle)
    assert proposal.applicability == "advice_only"
    assert proposal.reason_codes == ("RECIPE_BASIS_MISSING",)
    assert not proposal.request_targets


def test_changed_tool_identity_and_appid_do_not_match():
    request, fragment, bundle = fixture()
    assert not propose(request.model_copy(update={"appid": "different"}), fragment, bundle)
    selector = json.loads(bundle.recipes[0].selector_json)
    selector["tool_identity"] = "f" * 64
    raw = json.dumps(selector)
    recipe = bundle.recipes[0]
    recipe = recipe.model_copy(
        update={
            "selector_json": raw,
            "basis": recipe.basis.model_copy(update={"scope_selector": raw}),
        }
    )
    assert not propose(request, fragment, bundle.model_copy(update={"recipes": (recipe,)}))


def test_tampered_target_parameters_and_basis_rejected():
    request, fragment, bundle = fixture()
    (proposal,) = propose(request, fragment, bundle)
    adapter = TokenProposalAdapter()
    basis = proposal.recipe.basis
    target = proposal.request_targets[0].model_copy(
        update={"parameters_json": '{"fields":[],"field_level":"object"}'}
    )
    bad = proposal.model_copy(update={"request_targets": (target,)})
    assert adapter.prepare_proposal(request, bad, basis).status == "blocked"
    other = basis.model_copy(update={"digest": "c" * 64})
    assert adapter.prepare_proposal(request, proposal, other).status == "blocked"


def test_unverified_basis_and_wildcard_scope_rejected():
    _, _, bundle = fixture()
    recipe = bundle.recipes[0]
    for basis in [
        recipe.basis.model_copy(update={"scope_selector": "{}"}),
        recipe.basis.model_copy(
            update={"authority": recipe.basis.authority.model_copy(update={"status": "missing"})}
        ),
    ]:
        with pytest.raises(ValueError):
            TokenProposalAdapter().validate_bundle(
                bundle.model_copy(update={"recipes": (recipe.model_copy(update={"basis": basis}),)})
            )


def test_fragment_scope_and_missing_evidence_rejected():
    request, fragment, bundle = fixture()
    with pytest.raises(ValueError):
        propose(request, fragment.model_copy(update={"observations": ()}), bundle)
    with pytest.raises(ValueError):
        propose(request, fragment.model_copy(update={"raw_sha256": "f" * 64}), bundle)


def test_current_plugin_excludes_t1_but_legacy_descriptor_unchanged():
    from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin

    plugin = CurrentTokenContentPlugin()
    assert plugin.describe().version == "token-content-2"
    assert [r.name for r in plugin.describe().rule_versions] == ["T2", "T3", "T4"]
    assert "T1" in [r.name for r in TokenContentPlugin().describe().rule_versions]
    assert TokenContentPlugin().describe().version == "token-content-1"
    with pytest.raises(ValueError):
        plugin.validate_selection(PluginSelection(rule_ids=("T1",), budget=control().budget))
    request, _, _ = fixture()
    fragment = plugin.analyze_request(
        request,
        PluginSelection(rule_ids=("T2", "T3", "T4"), budget=control().budget),
        EvidenceCapabilities(),
        control(),
    )
    assert fragment.plugin_version == "token-content-2"
    assert all(o.rule_id != "T1" for o in fragment.observations)
    assert all(c.handler_id != "replace_tool_description" for c in fragment.modification_candidates)


def test_cancel_and_target_budget_fail_without_partial_proposals():
    from tokenscope.analysis_common.plugins import ExecutionStopped

    request, fragment, bundle = fixture()
    adapter = TokenProposalAdapter()
    for ctl in (control(max_candidates=1), control()):
        if ctl.budget.max_candidates != 1:
            ctl.cancelled = lambda: True
        with pytest.raises(ExecutionStopped):
            adapter.propose(
                "task",
                request.scope_id,
                request,
                "0",
                fragment,
                bundle,
                EvidenceCapabilities(),
                ctl,
            )


def test_modern_tool_call_identity_resolves_and_unknown_call_does_not_edit():
    request, _, bundle = fixture()
    body = json.loads(request.raw_body)
    body["messages"] = [
        {
            "role": "assistant",
            "tool_calls": [
                {"id": "c", "type": "function", "function": {"name": "search", "arguments": "{}"}}
            ],
        },
        {"role": "tool", "tool_call_id": "c", "content": '{"id":1,"noise":2}'},
    ]
    request = view(body)
    fragment = TokenContentPlugin().analyze_request(
        request,
        PluginSelection(rule_ids=("T2",), budget=control().budget),
        EvidenceCapabilities(),
        control(),
    )
    (proposal,) = propose(request, fragment, bundle)
    assert len(proposal.request_targets) == 1
    assert proposal.request_targets[0].location.source_pointer == "/messages/1/content"
    body["messages"][1]["tool_call_id"] = "unknown"
    request = view(body)
    fragment = TokenContentPlugin().analyze_request(
        request,
        PluginSelection(rule_ids=("T2",), budget=control().budget),
        EvidenceCapabilities(),
        control(),
    )
    with pytest.raises(ValueError, match="EVIDENCE_LOCATION_AMBIGUOUS"):
        propose(request, fragment, bundle)
