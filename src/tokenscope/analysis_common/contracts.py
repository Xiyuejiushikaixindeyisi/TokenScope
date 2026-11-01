"""Shared diagnostic contract models (analysis-common-1.0)."""

import hashlib
import json
import re
from fractions import Fraction
from typing import Annotated, Any, Literal, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

CONTRACT_VERSION: Literal["analysis-common-1.0"] = "analysis-common-1.0"
Nonnegative = Annotated[int, Field(ge=0)]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Name = Annotated[str, Field(min_length=1)]


def checked_json(value: str) -> str:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in items:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = item
        return result

    def constant(value: str) -> None:
        raise ValueError("Nonfinite JSON value")

    value.encode("utf-8")
    json.loads(value, object_pairs_hook=pairs, parse_constant=constant)
    return value


JsonText = Annotated[str, AfterValidator(checked_json)]


def checked_pointer(value: str) -> str:
    if value and not value.startswith("/"):
        raise ValueError("JSON Pointer must be empty or start with slash")
    if re.search(r"~(?![01])", value):
        raise ValueError("Invalid JSON Pointer escape")
    return value


Pointer = Annotated[str, AfterValidator(checked_pointer)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


def metadata_wire(value: Any) -> Any:
    """Counts are decimal strings; embedded JsonText is not transformed."""
    if isinstance(value, BaseModel):
        return metadata_wire(value.model_dump(mode="json"))
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, (tuple, list)):
        return [metadata_wire(item) for item in value]
    if isinstance(value, dict):
        return {key: metadata_wire(item) for key, item in value.items()}
    return value


def canonical_metadata(value: Any) -> bytes:
    return json.dumps(
        metadata_wire(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def stable_id(prefix: str, value: Any) -> str:
    return prefix + ":" + hashlib.sha256(canonical_metadata(value)).hexdigest()


class RequestKey(Contract):
    base_run_id: str = Field(min_length=1)
    source_record_index: int = Field(ge=0)


class DiagnosticSelection(Contract):
    reason_codes: tuple[Literal["low_hit", "request_length", "qps"], ...]
    enable_low_hit: bool
    enable_token_content: bool

    @model_validator(mode="after")
    def validate_routing(self) -> Self:
        if not self.reason_codes or len(set(self.reason_codes)) != len(self.reason_codes):
            raise ValueError("reason_codes must be nonempty and unique")
        if self.enable_low_hit != ("low_hit" in self.reason_codes):
            raise ValueError("reason and low_hit switch disagree")
        if not self.enable_token_content:
            raise ValueError("selected reasons require token_content")
        return self

    @property
    def stages(self) -> tuple[str, ...]:
        return ("low_hit", "token_content") if self.enable_low_hit else ("token_content",)


class InputMetrics(Contract):
    """Internal integers; external decimal-string serialization is a separate layer."""

    p: int = Field(ge=0)
    h: int = Field(ge=0)
    c: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_conservation(self) -> Self:
        if self.p != self.h + self.c:
            raise ValueError("P must equal H+C")
        return self

    @property
    def hit_ratio(self) -> Fraction | None:
        return Fraction(self.h, self.p) if self.p else None


def gain_percentage_points(before: InputMetrics, after: InputMetrics) -> Fraction | None:
    """Exact absolute percentage-point change, never a rounded relative gain."""
    left, right = before.hit_ratio, after.hit_ratio
    if left is None or right is None:
        return None
    return 100 * (right - left)


def passes_gain_gate(before: InputMetrics, after: InputMetrics, *, complete: bool) -> bool:
    """Only a complete evaluation with gain strictly above one point qualifies."""
    gain = gain_percentage_points(before, after)
    return complete and gain is not None and gain > 1


class TimeWindow(Contract):
    start_ns: int
    end_ns: int

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.start_ns >= self.end_ns:
            raise ValueError("Window must be nonempty and half-open")
        return self


class SourceSelection(Contract):
    source_kind: Literal["base", "user_v2"]
    base_run_id: Name | None = None
    user_run_id: Name | None = None
    appid: Name
    window: TimeWindow | None = None
    expected_index_revision: Name | None = None

    @model_validator(mode="after")
    def one_source(self) -> Self:
        if self.source_kind == "base":
            if self.base_run_id is None or self.user_run_id is not None:
                raise ValueError("base source requires only base_run_id")
            if self.expected_index_revision is not None:
                raise ValueError("base source has no user index revision")
        elif self.user_run_id is None or self.base_run_id is not None:
            raise ValueError("user_v2 source requires only user_run_id")
        return self


class SourceIdentity(Contract):
    base_run_id: Name
    user_run_id: Name | None = None
    common_name: str | None = None
    model_id: Name
    manifest_sha256: Digest
    asset_identity: Name
    encoder_identity: Name
    profile_json: JsonText
    settings_json: JsonText
    algorithm_version: Name


class AnalysisScope(Contract):
    source: SourceIdentity
    appid: Name
    window: TimeWindow | None
    request_count: Nonnegative
    request_keys_digest: Digest
    baseline_origin: Literal["original_run_window", "selected_window_recomputed"]

    @property
    def scope_id(self) -> str:
        return stable_id("scope", self)


class BaselineMetrics(Contract):
    j: Nonnegative
    p: Nonnegative
    h: Nonnegative | None = None
    c: Nonnegative | None = None
    o: Nonnegative | None = None

    @model_validator(mode="after")
    def conservation(self) -> Self:
        if self.h is not None and self.c is not None and self.p != self.h + self.c:
            raise ValueError("P must equal H+C when both are available")
        return self


class RequestView(Contract):
    request_key: RequestKey
    scope_id: Name
    appid: Name
    time_ns: int
    hash_id: str
    raw_body: str
    raw_sha256: Digest
    raw_body_complete: bool
    capture_truncation: Literal["known_truncated", "known_complete", "unknown"] = "unknown"
    baseline_metrics: BaselineMetrics
    encoder_identity: Name
    asset_identity: Name
    effective_options_json: JsonText
    token_slice_json: JsonText | None = None
    light_evidence_json: JsonText = "{}"
    association_ref: str | None = None

    @model_validator(mode="after")
    def body_integrity(self) -> Self:
        if hashlib.sha256(self.raw_body.encode("utf-8")).hexdigest() != self.raw_sha256:
            raise ValueError("Raw body digest mismatch")
        return self


class TextRange(Contract):
    start: Nonnegative
    end: Nonnegative

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.end < self.start:
            raise ValueError("Invalid half-open range")
        return self


class EmbeddedLocation(Contract):
    format: Literal["json"] = "json"
    parser_version: Name
    pointer: Pointer


class Location(Contract):
    request_key: RequestKey
    raw_sha256: Digest
    source_pointer: Pointer
    embedded: EmbeddedLocation | None = None
    text_range: TextRange | None = None

    @property
    def location_id(self) -> str:
        return stable_id("loc", {"identity_schema_version": "1", **self.model_dump()})


class Participation(Contract):
    status: Literal["included", "ignored", "unknown"] = "unknown"
    evidence_method: str | None = None
    encoding_identity: str | None = None
    prompt_token_spans: tuple[TextRange, ...] | None = None

    @model_validator(mode="after")
    def evidence_required(self) -> Self:
        if self.status != "unknown" and (not self.evidence_method or not self.encoding_identity):
            raise ValueError("Participation claim requires method and encoding identity")
        if self.prompt_token_spans is not None and self.status != "included":
            raise ValueError("Exact spans require included participation")
        return self


class ContentUnit(Contract):
    location_id: Name
    representation: Name
    measurement_version: Name
    content_sha256: Digest
    facets: tuple[str, ...] = ()
    measurement_unit: Name
    measured_value: Nonnegative
    parent_unit_id: str | None = None
    container_unit_id: str | None = None
    overlap_relation: Literal["none", "contained", "overlapping", "unknown"] = "unknown"
    participation: Participation = Participation()

    @property
    def unit_id(self) -> str:
        return stable_id(
            "unit",
            {
                "location_id": self.location_id,
                "representation": self.representation,
                "measurement_version": self.measurement_version,
            },
        )


class Observation(Contract):
    rule_id: Name
    rule_version: Name
    unit_ids: tuple[str, ...]
    predicate: Name
    method: Name
    policy_digest: Digest | None = None
    condition: Literal["met", "not_met", "unknown"]
    details_json: JsonText = "{}"

    @property
    def observation_id(self) -> str:
        return stable_id(
            "obs",
            {
                "rule_id": self.rule_id,
                "rule_version": self.rule_version,
                "unit_ids": sorted(set(self.unit_ids)),
                "predicate": self.predicate,
                "method": self.method,
                "policy_digest": self.policy_digest,
            },
        )


class Coverage(Contract):
    checked: Nonnegative
    eligible: Nonnegative | None
    complete: bool
    reasons: tuple[str, ...] = ()
    stop_location: str | None = None

    @model_validator(mode="after")
    def counts(self) -> Self:
        if self.eligible is not None and self.checked > self.eligible:
            raise ValueError("Checked exceeds eligible")
        if self.complete and (self.eligible is None or self.checked != self.eligible):
            raise ValueError("Complete coverage requires exact eligible count")
        return self


class RuleResult(Contract):
    rule_id: Name
    status: Literal["completed", "not_applicable", "partial", "failed", "not_checked"]
    condition: Literal["met", "not_met", "unknown"]
    coverage: Coverage
    reason_codes: tuple[str, ...] = ()


class FindingCandidate(Contract):
    finding_id: Name
    rule_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    title: Name
    category: Literal[
        "construction_issue",
        "optimization_opportunity",
        "policy_exceeded",
        "needs_evidence",
        "difference_evidence",
    ]
    advice: str


class ModificationCandidate(Contract):
    candidate_id: Name
    finding_refs: tuple[str, ...]
    handler_id: Name
    handler_version: Name
    action_class: Literal[
        "business_information_preserving",
        "stabilization",
        "hypothetical_content_removal",
        "policy_based",
    ]
    locations: tuple[Location, ...]
    parameters_json: JsonText
    business_basis_ref: str | None = None
    missing_parameters: tuple[str, ...] = ()


class TargetLocation(Contract):
    location: Location
    original_type: Literal["object", "array", "string", "number", "boolean", "null", "absent"]
    value_guard: Digest | Literal["absent"]
    outer_string_guard: Digest | None = None

    @model_validator(mode="after")
    def guard_kind(self) -> Self:
        if (self.original_type == "absent") != (self.value_guard == "absent"):
            raise ValueError("Absent guard/type must agree")
        if self.location.embedded is not None and self.outer_string_guard is None:
            raise ValueError("Embedded location requires outer guard")
        return self


class PreparedMutation(Contract):
    operation_id: Name
    handler_id: Name
    handler_version: Name
    target: TargetLocation
    public_primitive: Literal["replace_value", "remove_value"]
    replacement_json: JsonText | None = None
    source_operations_json: JsonText = "[]"
    invariants_json: JsonText = "{}"
    business_basis_ref: str | None = None
    manifest_fragment_json: JsonText = "{}"

    @model_validator(mode="after")
    def replacement_required(self) -> Self:
        if (self.public_primitive == "replace_value") != (self.replacement_json is not None):
            raise ValueError("Replacement presence must match primitive")
        return self


class ModificationPlan(Contract):
    plan_id: Name
    version: Name
    source_scope_id: Name
    transformation_digest: Digest
    direction: Literal["low_hit", "token_content", "combined"]
    action_class: str
    finding_refs: tuple[str, ...]
    operations: tuple[PreparedMutation, ...] = Field(min_length=1)
    combination_refs: tuple[str, ...] = ()


class AnalysisFragment(Contract):
    request_key: RequestKey
    raw_sha256: Digest
    plugin_id: Name
    plugin_version: Name
    locations: tuple[Location, ...] = ()
    units: tuple[ContentUnit, ...] = ()
    observations: tuple[Observation, ...] = ()
    finding_candidates: tuple[FindingCandidate, ...] = ()
    modification_candidates: tuple[ModificationCandidate, ...] = ()
    rule_results: tuple[RuleResult, ...] = ()
    coverage: Coverage
    reason_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def references(self) -> Self:
        locs = {item.location_id for item in self.locations}
        units = {item.unit_id for item in self.units}
        observations = {item.observation_id for item in self.observations}
        for loc in self.locations:
            if loc.request_key != self.request_key or loc.raw_sha256 != self.raw_sha256:
                raise ValueError("Fragment location outside request")
        if any(unit.location_id not in locs for unit in self.units):
            raise ValueError("Dangling unit location")
        if any(not set(obs.unit_ids) <= units for obs in self.observations):
            raise ValueError("Dangling observation unit")
        if any(not set(item.observation_ids) <= observations for item in self.finding_candidates):
            raise ValueError("Dangling finding observation")
        return self


class AggregateMetrics(InputMetrics):
    n: Nonnegative
    j: Nonnegative


class EvaluationResult(Contract):
    evaluation_id: Name
    plan_id: Name
    scope_id: Name
    stage: Literal["pilot", "full", "direct_full"]
    direction: Literal["low_hit", "token_content", "combined"]
    status: Literal["available", "blocked", "failed", "not_run", "interrupted"]
    baseline_origin: Literal["original_run_window", "selected_window_recomputed"]
    coverage: Coverage
    before: AggregateMetrics | None = None
    after: AggregateMetrics | None = None
    modified_before: AggregateMetrics | None = None
    modified_after: AggregateMetrics | None = None
    manifest_ref: str | None = None
    reason_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def publication(self) -> Self:
        if self.status == "available":
            if not self.coverage.complete or self.before is None or self.after is None:
                raise ValueError("Available evaluation requires complete before/after")
            if self.before.n != self.after.n or self.before.n != self.coverage.checked:
                raise ValueError("Evaluation dropped requests")
        elif self.after is not None or self.modified_after is not None:
            raise ValueError("Incomplete evaluation cannot publish after")
        return self

    @property
    def gate_passed(self) -> bool | None:
        if self.direction != "low_hit" or self.before is None or self.after is None:
            return None
        if gain_percentage_points(self.before, self.after) is None:
            return None
        return passes_gain_gate(self.before, self.after, complete=self.coverage.complete)

    @property
    def display_eligible(self) -> bool:
        return self.stage != "pilot" and self.gate_passed is True


class RequestComparison(Contract):
    left: RequestKey
    right: RequestKey
    left_raw_sha256: Digest
    right_raw_sha256: Digest
    difference_pointers: tuple[Pointer, ...]
    association_ref: str | None = None
    lcp_tokens: Nonnegative | None = None


class DiagnosticRequest(Contract):
    source: SourceSelection
    selection: DiagnosticSelection
    reason_note: str = ""
    submission_key: Name


class TaskReceipt(Contract):
    task_id: Name
    attempt: Annotated[int, Field(ge=1)]
    status: Literal["queued", "running", "ready", "partial", "empty", "failed", "interrupted"]
    active_direction: Literal["low_hit", "token_content"] | None = None
    report_ref: str | None = None
    error_code: str | None = None
