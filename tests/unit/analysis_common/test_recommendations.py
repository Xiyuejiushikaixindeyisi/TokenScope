import pytest
from pydantic import ValidationError

from tokenscope.analysis_common.contracts import Location, RequestKey
from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
from tokenscope.analysis_common.recommendations import (
    Impact,
    Proposal,
    ProposalTarget,
    Recipe,
    RecipeBundle,
    RecommendationBudget,
    SupportRef,
)
from tokenscope.analysis_common.wire import from_wire, to_wire


def recipe() -> Recipe:
    return Recipe(
        recipe_id="t2",
        revision="1",
        primary_rule="T2",
        category_rules=("T2",),
        handler_id="project",
        handler_version="1",
        selector_json="{}",
        parameter_generator_json="{}",
        basis=None,
        title="Project fields",
        change_summary="Keep x",
    )


def test_actual_fragment_support_checked() -> None:
    from tokenscope.analysis_common.contracts import AnalysisFragment, Coverage, Observation
    from tokenscope.analysis_common.proposal_plugins import validate_support

    key = RequestKey(base_run_id="r", source_record_index=1)
    obs = Observation(
        rule_id="T3",
        rule_version="1",
        unit_ids=(),
        predicate="duplicate",
        method="exact",
        condition="met",
    )
    fragment = AnalysisFragment(
        request_key=key,
        raw_sha256="a" * 64,
        plugin_id="token_content",
        plugin_version="1",
        observations=(obs,),
        coverage=Coverage(checked=1, eligible=1, complete=True),
    )
    support = SupportRef(
        kind="token_observation",
        task_id="t",
        scope_id="s",
        request_key=key,
        raw_sha256="a" * 64,
        fragment_id="f",
        observation_ids=(obs.observation_id,),
    )
    proposal = Proposal(
        recipe=recipe(), support_refs=(support,), request_targets=(), applicability="advice_only"
    )
    validate_support(proposal, "t", "s", "f", fragment)
    with pytest.raises(ValueError, match="Foreign"):
        validate_support(proposal, "other", "s", "f", fragment)
    bad = proposal.model_copy(
        update={"support_refs": (support.model_copy(update={"observation_ids": ("missing",)}),)}
    )
    with pytest.raises(ValueError, match="Unknown observation"):
        validate_support(bad, "t", "s", "f", fragment)


def test_legacy_summary_and_atomic_writer(tmp_path) -> None:
    from tokenscope.analysis_common.recommendation_store import write_extension
    from tokenscope.analysis_common.recommendations import RecommendationSummary
    from tokenscope.analysis_common.storage import ResultWriter, read_items

    summary = RecommendationSummary(
        task_id="t",
        scope_id="s",
        availability="not_computed",
        configured_recipe_count=None,
        recommendation_count=0,
        difference_group_count=0,
        proposal_coverage=None,
        evaluation_coverage=None,
        budget=None,
        budget_digest=None,
        consumed=None,
    )
    writer = ResultWriter(tmp_path)
    with pytest.raises(ValueError, match="foreign"):
        write_extension(writer, "other", "s", summary)
    write_extension(writer, "t", "s", summary)
    writer.close()
    assert read_items(tmp_path, "recommendation_summary", None, 0, 10)[0]["data"] == to_wire(
        summary
    )
    with pytest.raises(ValidationError):
        RecommendationSummary.model_validate_json(
            summary.model_copy(update={"recommendation_count": 1}).model_dump_json()
        )


def test_wire_bundle_and_budget() -> None:
    bundle = RecipeBundle(bundle_id="b", revision="1", recipes=(recipe(),))
    assert from_wire(RecipeBundle, to_wire(bundle)) == bundle
    budget = RecommendationBudget()
    assert from_wire(RecommendationBudget, to_wire(budget)) == budget
    assert ProposalRegistry().capabilities() == ()
    with pytest.raises(ValidationError):
        RecipeBundle(bundle_id="b", revision="1", recipes=(recipe(), recipe()))
    with pytest.raises(ValidationError):
        RecommendationBudget(version="future")


@pytest.mark.parametrize(
    "changes",
    [
        {"modified_requests": 0},
        {"matched_requests": 0},
        {"matched_checked_requests": 7},
        {"evaluation_complete": True},
        {"match_complete": True},
    ],
)
def test_partial_count_cannot_look_complete(changes: dict) -> None:
    values = dict(
        total_requests=6,
        matched_requests=None,
        matched_checked_requests=2,
        match_complete=False,
        modified_requests=None,
        evaluation_complete=False,
    )
    values.update(changes)
    with pytest.raises(ValidationError):
        Impact(**values)


def test_t3_observation_without_finding_and_foreign_target() -> None:
    key = RequestKey(base_run_id="r", source_record_index=1)
    support = SupportRef(
        kind="token_observation",
        task_id="t",
        scope_id="s",
        request_key=key,
        raw_sha256="a" * 64,
        fragment_id="f",
        observation_ids=("o",),
    )
    target = ProposalTarget(
        location=Location(request_key=key, raw_sha256="a" * 64, source_pointer="/messages/0"),
        parameters_json="{}",
    )
    proposal = Proposal(
        recipe=recipe(), support_refs=(support,), request_targets=(target,), applicability="matched"
    )
    assert from_wire(Proposal, to_wire(proposal)) == proposal
    foreign = support.model_copy(update={"task_id": "other"})
    with pytest.raises(ValidationError):
        Proposal(
            recipe=recipe(),
            support_refs=(support, foreign),
            request_targets=(target,),
            applicability="matched",
        )
    target = target.model_copy(
        update={"location": target.location.model_copy(update={"raw_sha256": "b" * 64})}
    )
    with pytest.raises(ValidationError):
        Proposal(
            recipe=recipe(),
            support_refs=(support,),
            request_targets=(target,),
            applicability="matched",
        )
