"""Versioned explicit-direction submission; v1 models and sealed payloads stay intact."""

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from tokenscope.analysis_common.contracts import Contract, Name, Nonnegative, SourceSelection
from tokenscope.analysis_common.discovery_contracts import CatalogEntry, DefaultReference
from tokenscope.analysis_common.runtime import RuntimeOptions


class SelectionV2(Contract):
    reason_codes: tuple[Literal["low_hit", "request_length", "qps"], ...]
    enable_low_hit: bool
    enable_token_content: bool

    @model_validator(mode="after")
    def selected(self) -> Self:
        if not self.reason_codes or len(set(self.reason_codes)) != len(self.reason_codes):
            raise ValueError("Reasons must be nonempty and unique")
        if not (self.enable_low_hit or self.enable_token_content):
            raise ValueError("At least one direction is required")
        return self


class RequestV2(Contract):
    source: SourceSelection
    selection: SelectionV2
    reason_note: str = ""
    submission_key: Name


class RuntimeV2(RuntimeOptions):
    version: Literal["diagnostics-runtime-2"] = "diagnostics-runtime-2"
    max_findings: int = Field(ge=5)
    max_retained_bytes: int = Field(default=4 * 1024 * 1024, ge=5)
    max_comparisons: int = Field(default=100000, ge=1)
    max_fragment_bytes: int = Field(default=8 * 1024 * 1024, ge=1)
    max_total_fragment_bytes: int = Field(default=64 * 1024 * 1024, ge=1)


class SubmissionV2(Contract):
    version: Literal["diagnostics-execution-2"] = "diagnostics-execution-2"
    request: RequestV2
    options: RuntimeV2


def runtime_from_json(raw: str) -> RuntimeOptions:
    import json

    return (
        RuntimeV2 if json.loads(raw).get("version") == "diagnostics-runtime-2" else RuntimeOptions
    ).model_validate_json(raw)


# These response models document new views, without changing the frozen v1 rows.


class SelectedReport(Contract):
    binding_id: str
    direction: Literal["low_hit", "token_content"]
    task_id: str
    sequence: str
    status: Literal["ready", "partial"]
    selection_kind: Literal["ready", "published_partial_fallback"]


class CatalogV2(Contract):
    version: Literal["diagnostics-discovery-2"]
    service_instance_id: str
    snapshot: str
    event_cursor: str
    items: list[CatalogEntry]
    defaults: list[DefaultReference]
    next_after: str | None
    selected_reports: list[SelectedReport]


# Explicit decimal-string maps: the frozen v1 codec does not restore additionalProperties.
DecimalCount = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)$")]


class MetricsV2(Contract):
    version: Literal["diagnostics-telemetry-2"]
    clock: Literal["perf_counter_ns"]
    elapsed_ns: dict[str, DecimalCount]
    counts: dict[str, DecimalCount]


class StageV2(Contract):
    direction: Literal["low_hit", "token_content"]
    status: Literal["completed", "partial"]
    stage: str | None = None
    reason: str | None = None
    reason_codes: list[str] = []
    checked_requests: Nonnegative | None = None
    eligible_requests: Nonnegative | None = None
    scan_complete: bool | None = None
    comparison_complete: bool | None = None
    retention_complete: bool | None = None
    fragments_complete: bool | None = None
    retained_requests: Nonnegative | None = None
    retained_bytes: Nonnegative | None = None
    detected_by_rule: dict[str, DecimalCount] | None = None
    retained_by_rule: dict[str, DecimalCount] | None = None
    rule_status_counts: dict[str, dict[str, DecimalCount]] | None = None
    ruleset_version: str | None = None
    candidate_coverage_partial: bool | None = None
    rule_scope: str | None = None


class ExecutionViewV2(Contract):
    version: Literal["diagnostics-execution-2"]
    task_id: str
    scope_id: str
    status: Literal["ready", "partial", "empty"]
    availability: Literal["computed", "not_computed"]
    selected_directions: list[Literal["low_hit", "token_content"]] | None
    stages: list[StageV2]
    telemetry: MetricsV2 | None
