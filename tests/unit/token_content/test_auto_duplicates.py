"""All policies/references here are explicitly synthetic engineering fixtures."""

import json

import pytest
from test_authorizations import evidence
from test_extraction import control, view

from tokenscope.analysis_common.plugins import EvidenceCapabilities
from tokenscope.analysis_common.recommendations import Basis, BasisAuthority, Recipe, RecipeBundle
from tokenscope.token_content.auto_proposals import TokenProposalAdapter


def fixture(kind="reference", mapping=True, authorized=True):
    request, fragment, _, argument, message, reference = evidence()
    parameters = json.loads(reference)
    selector = {
        "version": "token-duplicate-selector-1",
        "appid": "a",
        "payload_digest": argument.content_sha256,
        "target_kind": "argument_field" if kind == "reference" else "ordinary_message",
    }
    if kind == "reference":
        selector.update(tool_identity=parameters["tool_identity"], argument_pointer="/document")
    else:
        selector.update(message_role="user")
    raw = json.dumps(selector)
    generator = {"version": "token-duplicate-generator-1", "kind": kind, "omission_permitted": True}
    if kind == "reference":
        generator.update(
            reference_key=parameters["reference_key"],
            protocol_ref=parameters["protocol_ref"],
            reference_value=parameters["reference_value"] if mapping else None,
        )
    basis = (
        Basis(
            kind="explicit_authorization",
            ref="synthetic-auth",
            revision="1",
            digest="a" * 64,
            scope_selector=raw,
            authority=BasisAuthority(
                source_kind="synthetic_fixture",
                source_ref="test",
                source_digest="b" * 64,
                status="verified",
            ),
            limitations=("Synthetic, not production authorization",),
        )
        if authorized
        else None
    )
    recipe = Recipe(
        recipe_id="synthetic-t3",
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
        title="Synthetic duplicate",
        change_summary="Configured reference or deletion",
    )
    bundle = RecipeBundle(bundle_id="synthetic", revision="1", recipes=(recipe,))
    return request, fragment, bundle


def run(request, fragment, bundle):
    return TokenProposalAdapter().propose(
        "task", "scope", request, "0", fragment, bundle, EvidenceCapabilities(), control()
    )


@pytest.mark.parametrize("kind", ["reference", "delete_message"])
def test_no_finding_required_and_real_source_rechecked(kind):
    request, fragment, bundle = fixture(kind)
    fragment = fragment.model_copy(update={"finding_candidates": ()})
    (proposal,) = run(request, fragment, bundle)
    assert proposal.applicability == "matched"
    assert not proposal.support_refs[0].finding_ids
    prepared = TokenProposalAdapter().prepare_proposal(request, proposal, proposal.recipe.basis)
    assert prepared.status == "prepared", prepared.reason_codes
    assert len(prepared.operations) == 1


@pytest.mark.parametrize(
    "mapping,authorized,reason",
    [
        (False, True, "REFERENCE_MAPPING_MISSING"),
        (True, False, "RECIPE_BASIS_MISSING"),
    ],
)
def test_missing_mapping_or_authorization_is_advice(mapping, authorized, reason):
    request, fragment, bundle = fixture(mapping=mapping, authorized=authorized)
    (proposal,) = run(request, fragment, bundle)
    assert proposal.applicability == "advice_only"
    assert reason in proposal.reason_codes
    assert not proposal.request_targets


def test_changed_source_rejected_even_with_old_claimed_digest():
    request, fragment, bundle = fixture()
    (proposal,) = run(request, fragment, bundle)
    bad = request.model_copy(update={"raw_body": request.raw_body.replace("payload", "changed")})
    result = TokenProposalAdapter().prepare_proposal(bad, proposal, proposal.recipe.basis)
    assert result.status == "blocked"


def test_reference_schema_is_checked_and_not_rewritten():
    request, fragment, bundle = fixture()
    body = json.loads(request.raw_body)
    body["tools"][0]["function"]["parameters"]["required"] = ["document"]
    changed = view(body)
    # Identity changed: the previous authorization cannot match the modified tool schema.
    from tokenscope.analysis_common.plugins import PluginSelection
    from tokenscope.token_content.plugin import TokenContentPlugin

    actual = TokenContentPlugin().analyze_request(
        changed,
        PluginSelection(rule_ids=("T3",), budget=control().budget),
        EvidenceCapabilities(),
        control(),
    )
    assert not run(changed, actual, bundle)


def test_deletion_does_not_target_tool_messages_or_different_roles():
    request, fragment, bundle = fixture("delete_message")
    (proposal,) = run(request, fragment, bundle)
    assert [t.location.source_pointer for t in proposal.request_targets] == ["/messages/3/content"]
    raw = json.loads(bundle.recipes[0].selector_json)
    raw["message_role"] = "assistant"
    raw = json.dumps(raw)
    recipe = bundle.recipes[0]
    recipe = recipe.model_copy(
        update={
            "selector_json": raw,
            "basis": recipe.basis.model_copy(update={"scope_selector": raw}),
        }
    )
    assert not run(request, fragment, bundle.model_copy(update={"recipes": (recipe,)}))
