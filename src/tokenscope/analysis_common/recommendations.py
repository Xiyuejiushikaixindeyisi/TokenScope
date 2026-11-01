"""Independent recommendation contract; never added to the frozen H0 schema export."""

from typing import Literal, Self

from pydantic import Field, model_validator

from tokenscope.analysis_common.contracts import (
    Contract,
    Digest,
    EvaluationResult,
    JsonText,
    Location,
    Name,
    Nonnegative,
    RequestKey,
)

VERSION: Literal["analysis-recommendations-1"] = "analysis-recommendations-1"
ADAPTER_VERSION: Literal["token-auto-proposals-1"] = "token-auto-proposals-1"
ExtensionKind = Literal[
    "recommendation", "difference_group", "recommendation_example", "recommendation_summary"
]


class BasisAuthority(Contract):
    source_kind: Name
    source_ref: Name
    source_digest: Digest
    status: Literal["verified", "missing", "invalid"]


class Basis(Contract):
    kind: Literal["business_policy", "offline_hypothesis", "explicit_authorization"]
    ref: Name
    revision: Name
    digest: Digest
    scope_selector: JsonText
    authority: BasisAuthority
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class Recipe(Contract):
    recipe_id: Name
    revision: Name
    primary_rule: Literal["L1", "L2", "L3", "T2", "T3", "T4"]
    category_rules: tuple[Literal["L1", "L2", "L3", "T2", "T3", "T4"], ...]
    handler_id: Name
    handler_version: Name
    selector_json: JsonText
    parameter_generator_json: JsonText
    basis: Basis | None
    title: Name
    change_summary: Name
    conditions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def rule_membership(self) -> Self:
        if self.primary_rule not in self.category_rules:
            raise ValueError("primary_rule must belong to category_rules")
        if len(set(self.category_rules)) != len(self.category_rules):
            raise ValueError("Duplicate category rule")
        if "T1" in self.category_rules or self.handler_id == "replace_tool_description":
            raise ValueError("RECIPE_RULE_OUT_OF_SCOPE: T1 is historical only")
        if self.primary_rule == "T3" and self.basis is not None:
            if self.basis.kind != "explicit_authorization":
                raise ValueError("T3 requires explicit authorization")
        return self


class RecipeBundle(Contract):
    version: Literal["token-auto-proposals-1"] = ADAPTER_VERSION
    bundle_id: Name
    revision: Name
    recipes: tuple[Recipe, ...]

    @model_validator(mode="after")
    def unique_recipes(self) -> Self:
        keys = [(r.recipe_id, r.revision) for r in self.recipes]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate recipe identity")
        return self


class SupportRef(Contract):
    kind: Literal["prefix_finding", "token_observation"]
    task_id: Name
    scope_id: Name
    request_key: RequestKey
    raw_sha256: Digest
    finding_ids: tuple[str, ...] = ()
    fragment_id: str | None = None
    observation_ids: tuple[str, ...] = ()
    unit_ids: tuple[str, ...] = ()
    location_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def required_evidence(self) -> Self:
        if self.kind == "prefix_finding" and not self.finding_ids:
            raise ValueError("Prefix support requires findings")
        if self.kind == "token_observation" and (not self.fragment_id or not self.observation_ids):
            raise ValueError("Token support requires fragment and observations")
        return self


class ProposalTarget(Contract):
    location: Location
    parameters_json: JsonText


class Proposal(Contract):
    adapter_version: Literal["token-auto-proposals-1"] = ADAPTER_VERSION
    recipe: Recipe
    support_refs: tuple[SupportRef, ...] = Field(min_length=1)
    request_targets: tuple[ProposalTarget, ...]
    applicability: Literal["matched", "advice_only", "not_applicable"]
    reason_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def target_binding(self) -> Self:
        identities = {(s.request_key, s.raw_sha256) for s in self.support_refs}
        scopes = {(s.task_id, s.scope_id) for s in self.support_refs}
        if len(scopes) != 1:
            raise ValueError("Proposal support crosses task/scope")
        for target in self.request_targets:
            if (target.location.request_key, target.location.raw_sha256) not in identities:
                raise ValueError("Target has no matching evidence")
        if self.applicability == "matched" and not self.request_targets:
            raise ValueError("Matched proposal requires targets")
        if self.recipe.primary_rule not in ("T2", "T3", "T4"):
            raise ValueError("Token adapter only accepts T2-T4")
        if any(r not in ("T2", "T3", "T4") for r in self.recipe.category_rules):
            raise ValueError("Token proposal cannot mix low-hit rules")
        return self


class Impact(Contract):
    total_requests: Nonnegative
    matched_requests: Nonnegative | None
    matched_checked_requests: Nonnegative
    match_complete: bool
    modified_requests: Nonnegative | None
    evaluation_complete: bool
    count_basis: Literal["raw_body_changed"] = "raw_body_changed"

    @model_validator(mode="after")
    def complete_counts(self) -> Self:
        if self.matched_checked_requests > self.total_requests:
            raise ValueError("Checked exceeds scope")
        if self.match_complete:
            if (
                self.matched_requests is None
                or self.matched_checked_requests != self.total_requests
            ):
                raise ValueError("Complete match requires full coverage")
        elif self.matched_requests is not None:
            raise ValueError("Incomplete match count must be null")
        if self.evaluation_complete != (self.modified_requests is not None):
            raise ValueError("Modified count requires complete evaluation")
        for count in (self.matched_requests, self.modified_requests):
            if count is not None and count > self.total_requests:
                raise ValueError("Count exceeds scope")
        return self


class ObjectRef(Contract):
    task_id: Name
    id: Name


class ReasonDetail(Contract):
    code: Name
    rule_id: str | None = None
    missing_requirement: (
        Literal["template", "retention_rule", "reference_or_delete_agreement", "replacement_rule"]
        | None
    ) = None
    explanation: str = ""


class Recommendation(Contract):
    version: Literal["analysis-recommendations-1"] = VERSION
    recommendation_id: Name
    task_id: Name
    scope_id: Name
    direction: Literal["low_hit", "token_content"]
    generator_identity: Name
    recipe_key: Name
    group_basis_digest: Digest
    recipe: Recipe
    support_refs: tuple[SupportRef, ...] = Field(min_length=1)
    matched_set_digest: Digest
    support_set_digest: Digest
    members_complete: bool
    impact: Impact
    proposal_status: Literal["matched", "advice_only", "not_applicable", "partial", "failed"]
    preparation_status: Literal["not_required", "not_run", "prepared", "blocked", "failed"]
    evaluation_status: Literal[
        "not_required", "not_run", "available", "blocked", "failed", "interrupted"
    ]
    status: Literal["available", "advice_only", "blocked", "not_run", "failed", "interrupted"]
    reason_codes: tuple[str, ...] = ()
    reason_details: tuple[ReasonDetail, ...] = ()
    prepared_plan_ref: ObjectRef | None = None
    execution_plan_ref: ObjectRef | None = None
    evaluation_ref: ObjectRef | None = None
    evaluation_reused: bool = False
    execution_fingerprint: Digest | None = None
    evaluation: EvaluationResult | None = None
    display_qualification: Literal[
        "low_hit_optimization", "token_evaluated", "token_advice", "not_eligible"
    ]
    example_refs: tuple[ObjectRef, ...] = Field(default=(), max_length=3)
    display_order: Nonnegative

    @model_validator(mode="after")
    def consistent_result(self) -> Self:
        expected = ("T2", "T3", "T4") if self.direction == "token_content" else ("L1", "L2", "L3")
        if any(rule not in expected for rule in self.recipe.category_rules):
            raise ValueError("Recommendation rules disagree with direction")
        for support in self.support_refs:
            if (support.task_id, support.scope_id) != (self.task_id, self.scope_id):
                raise ValueError("Foreign support")
        refs = (self.prepared_plan_ref, self.execution_plan_ref, self.evaluation_ref)
        if any(r.task_id != self.task_id for r in (*refs, *self.example_refs) if r):
            raise ValueError("Foreign object reference")
        available = self.status == "available"
        if available != (self.evaluation_status == "available"):
            raise ValueError("Evaluation and recommendation status disagree")
        if available != self.impact.evaluation_complete:
            raise ValueError("Impact and evaluation completeness disagree")
        if available:
            ev = self.evaluation
            if ev is None or ev.status != "available" or any(r is None for r in refs):
                raise ValueError("Available recommendation requires complete execution references")
            assert self.execution_plan_ref is not None
            assert self.evaluation_ref is not None
            if (
                ev.plan_id != self.execution_plan_ref.id
                or ev.direction != self.direction
                or ev.scope_id != self.scope_id
                or ev.evaluation_id != self.evaluation_ref.id
            ):
                raise ValueError("Execution identity mismatch")
            if self.preparation_status != "prepared":
                raise ValueError("Available recommendation must be prepared")
            # Low-hit discovery can be partial while its independently compiled Plan
            # still covers the complete original scope. Token requires a full proposal scan.
            if self.direction == "token_content" and not self.members_complete:
                raise ValueError(
                    "Available Token recommendation requires complete proposal members"
                )
            if ev.before is None or ev.before.n != self.impact.total_requests:
                raise ValueError("Evaluation does not cover scope")
            if ev.modified_before is None or ev.modified_after is None:
                raise ValueError("Modified counts are required")
            if not (ev.modified_before.n == ev.modified_after.n == self.impact.modified_requests):
                raise ValueError("Modified counts disagree")
        elif self.evaluation is not None and self.evaluation.after is not None:
            raise ValueError("Unavailable result cannot expose after")
        if self.display_qualification == "low_hit_optimization":
            if not available or self.direction != "low_hit" or not self.evaluation:
                raise ValueError("Low hit card requires evaluated low hit result")
            if not self.evaluation.display_eligible:
                raise ValueError("Low hit card requires full gain >1pp")
        if self.display_qualification == "token_evaluated" and (
            not available or self.direction != "token_content"
        ):
            raise ValueError("Token evaluated card requires complete Token evaluation")
        if self.display_qualification == "token_advice" and self.direction != "token_content":
            raise ValueError("Token advice cannot describe low-hit result")
        if self.evaluation_reused and (
            self.execution_fingerprint is None or self.evaluation_ref is None
        ):
            raise ValueError("Evaluation reuse requires fingerprint and execution reference")
        return self


class EvidenceSpan(Contract):
    start: Nonnegative
    end: Nonnegative

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.end < self.start:
            raise ValueError("Reversed span")
        return self


class LocalEvidence(Contract):
    locator_version: Literal["evidence-locator-1"] = "evidence-locator-1"
    source: Location
    offset_unit: Literal["unicode_codepoint"] = "unicode_codepoint"
    raw_span: EvidenceSpan | None
    decoded_span: EvidenceSpan | None = None
    excerpt: str
    context_before: str = ""
    context_after: str = ""
    omitted_before: bool = False
    omitted_after: bool = False
    reason_codes: tuple[str, ...] = ()


class RecommendationExample(Contract):
    version: Literal["analysis-recommendations-1"] = VERSION
    example_id: Name
    task_id: Name
    scope_id: Name
    owner_id: Name
    before: LocalEvidence
    after: LocalEvidence | None = None
    comparison: LocalEvidence | None = None


class DifferenceGroup(Contract):
    version: Literal["recommendation-group-1"] = "recommendation-group-1"
    group_id: Name
    task_id: Name
    scope_id: Name
    rule_id: Literal["L4", "L5"]
    title: Name
    change_summary: str
    group_basis_digest: Digest
    finding_ids: tuple[Name, ...] = Field(min_length=1)
    member_requests: tuple[RequestKey, ...] = Field(min_length=1)
    members_complete: bool
    example_refs: tuple[ObjectRef, ...] = Field(default=(), max_length=3)
    reason_codes: tuple[str, ...] = ()
    display_order: Nonnegative

    @model_validator(mode="after")
    def unique_members(self) -> Self:
        if len(self.member_requests) != len(set(self.member_requests)):
            raise ValueError("Repeated request member")
        if any(ref.task_id != self.task_id for ref in self.example_refs):
            raise ValueError("Foreign example")
        return self


class RecommendationBudget(Contract):
    version: Literal["recommendation-budget-1"] = "recommendation-budget-1"
    max_proposals: int = Field(default=256, ge=1)
    max_recommendations: int = Field(default=32, ge=1)
    max_prepared_operations: int = Field(default=10000, ge=1)
    max_proposal_bytes: int = Field(default=1024 * 1024, ge=1)
    max_plan_bytes: int = Field(default=16 * 1024 * 1024, ge=1)
    max_total_plan_bytes: int = Field(default=64 * 1024 * 1024, ge=1)
    max_token_evaluations: int = Field(default=8, ge=1)
    max_examples_per_group: int = Field(default=3, ge=1, le=3)
    max_excerpt_codepoints: int = Field(default=1024, ge=1)
    max_context_codepoints: int = Field(default=128, ge=0)
    max_example_bytes_per_group: int = Field(default=24 * 1024, ge=1)


class StageCoverage(Contract):
    eligible: Nonnegative | None
    checked: Nonnegative
    completed: Nonnegative
    advice_only: Nonnegative
    blocked: Nonnegative
    not_run: Nonnegative
    failed: Nonnegative
    complete: bool
    reason_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_coverage(self) -> Self:
        if self.eligible is not None and self.checked > self.eligible:
            raise ValueError("Stage checked exceeds eligible")
        if self.completed + self.advice_only + self.blocked + self.failed > self.checked:
            raise ValueError("Stage outcomes exceed checked")
        if self.complete and (
            self.eligible != self.checked or self.blocked or self.failed or self.not_run
        ):
            raise ValueError("Incomplete stage cannot claim complete")
        return self


class BudgetConsumption(Contract):
    proposals: Nonnegative = 0
    recommendations: Nonnegative = 0
    prepared_operations: Nonnegative = 0
    total_plan_bytes: Nonnegative = 0
    token_evaluations: Nonnegative = 0
    encoding_calls: Nonnegative = 0


class RecommendationSummary(Contract):
    version: Literal["analysis-recommendations-1"] = VERSION
    task_id: Name
    scope_id: Name
    availability: Literal["computed", "not_computed"]
    configured_recipe_count: Nonnegative | None
    recommendation_count: Nonnegative
    difference_group_count: Nonnegative
    proposal_coverage: StageCoverage | None
    evaluation_coverage: StageCoverage | None
    budget: RecommendationBudget | None
    budget_digest: Digest | None
    consumed: BudgetConsumption | None
    reason_codes: tuple[str, ...] = ()
    stop_location: str | None = None

    @model_validator(mode="after")
    def legacy_has_no_computation(self) -> Self:
        if self.availability == "not_computed" and (
            self.recommendation_count
            or self.difference_group_count
            or self.proposal_coverage is not None
            or self.evaluation_coverage is not None
            or self.budget is not None
            or self.budget_digest is not None
            or self.consumed is not None
        ):
            raise ValueError("Legacy report cannot claim extension computation")
        return self
