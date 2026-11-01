"""Synthetic transport fixtures, not business policies or measured savings."""

import copy

from tokenscope.analysis_common.contracts import Location, RequestKey
from tokenscope.analysis_common.proposal_plugins import ProposalDescriptor
from tokenscope.analysis_common.recommendations import (
    Basis,
    BasisAuthority,
    Impact,
    Proposal,
    ProposalTarget,
    Recipe,
    RecipeBundle,
    SupportRef,
)
from tokenscope.analysis_common.wire import to_wire


def examples() -> dict:
    key = RequestKey(base_run_id="synthetic-run", source_record_index=10**20)
    basis = Basis(
        kind="business_policy",
        ref="fixture-only",
        revision="1",
        digest="a" * 64,
        scope_selector="{}",
        authority=BasisAuthority(
            source_kind="test_fixture",
            source_ref="not-production",
            source_digest="a" * 64,
            status="verified",
        ),
    )
    recipe = Recipe(
        recipe_id="fixture-project",
        revision="1",
        primary_rule="T2",
        category_rules=("T2",),
        handler_id="project_result_fields",
        handler_version="1",
        selector_json='{"version":"fixture-selector-1","tool":"example"}',
        parameter_generator_json='{"version":"fixture-generator-1","fields":["value"]}',
        basis=basis,
        title="Synthetic field projection",
        change_summary="Keep value (fixture only)",
    )
    support = SupportRef(
        kind="token_observation",
        task_id="fixture-task",
        scope_id="fixture-scope",
        request_key=key,
        raw_sha256="b" * 64,
        fragment_id="fixture-fragment",
        observation_ids=("fixture-observation",),
    )
    proposal = Proposal(
        recipe=recipe,
        support_refs=(support,),
        request_targets=(
            ProposalTarget(
                location=Location(
                    request_key=key, raw_sha256="b" * 64, source_pointer="/messages/1/content"
                ),
                parameters_json='{"fields":["value"]}',
            ),
        ),
        applicability="matched",
    )
    valid = [
        {
            "model": "RecipeBundle",
            "wire": to_wire(RecipeBundle(bundle_id="fixture", revision="1", recipes=(recipe,))),
        },
        {"model": "Proposal", "wire": to_wire(proposal)},
        {
            "model": "ProposalDescriptor",
            "wire": to_wire(
                ProposalDescriptor(
                    generator_identity="fixture-1",
                    rule_ids=("T2", "T3", "T4"),
                    basis_kinds=("business_policy", "explicit_authorization"),
                )
            ),
        },
        {
            "model": "Impact",
            "wire": to_wire(
                Impact(
                    total_requests=6,
                    matched_requests=6,
                    matched_checked_requests=6,
                    match_complete=True,
                    modified_requests=0,
                    evaluation_complete=True,
                )
            ),
        },
    ]
    invalid = []
    for name, mutate in [
        ("T1 rejected", lambda v: v["recipe"].update(primary_rule="T1", category_rules=["T1"])),
        (
            "foreign target",
            lambda v: v["request_targets"][0]["location"].update(raw_sha256="c" * 64),
        ),
        ("unknown adapter", lambda v: v.update(adapter_version="unknown")),
        ("missing observations", lambda v: v["support_refs"][0].update(observation_ids=[])),
    ]:
        value = copy.deepcopy(valid[1]["wire"])
        mutate(value)
        invalid.append({"model": "Proposal", "case": name, "wire": value})
    value = copy.deepcopy(valid[3]["wire"])
    value["evaluation_complete"] = False
    invalid.append(
        {"model": "Impact", "case": "partial cannot publish modified count", "wire": value}
    )
    return {
        "nature": "synthetic transport fixtures; private DSL must be validated by Token adapter",
        "valid": valid,
        "invalid": invalid,
    }
