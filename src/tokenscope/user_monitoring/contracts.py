"""User monitoring contract 1.0.1. No runtime routes are installed by this module."""

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

UInt = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)$", max_length=128)]
PositiveIntText = Annotated[str, Field(pattern=r"^[1-9][0-9]*$", max_length=128)]
Text = Annotated[str, Field(min_length=1, max_length=4096)]
DecimalText = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)(\.[0-9]+)?$", max_length=128)]
Ratio = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
ModelId = Literal["GLM-5.2", "Qwen3.6-27B", "DeepSeek-V4-Flash-0731"]
Width = Literal[1000, 2000, 5000]


class DTO(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class UserState(StrEnum):
    ACCEPTED = "accepted"
    BASE_PENDING = "base_pending"
    INDEXING = "indexing"
    READY = "ready"
    EMPTY = "empty"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class Submit(DTO):
    submission_key: Text
    file_ref: Text
    common_name: Text
    model_id: ModelId


class Bind(DTO):
    submission_key: Text
    base_run_id: Text
    common_name: Text


class Receipt(DTO):
    service_instance_id: Text
    user_run_id: Text
    base_run_id: Text | None
    common_name: Text
    model_id: ModelId
    state: UserState
    index_revision: Text | None
    error_code: Text | None

    @model_validator(mode="after")
    def valid_state(self) -> Self:
        if self.state == UserState.READY and (not self.base_run_id or not self.index_revision):
            raise ValueError("ready requires base and index")
        if self.state == UserState.EMPTY and not self.base_run_id:
            raise ValueError("empty requires base")
        if self.state in (UserState.FAILED, UserState.INTERRUPTED) and not self.error_code:
            raise ValueError("terminal failure requires reason")
        return self


class Fraction(DTO):
    numerator: UInt
    denominator: PositiveIntText


class ModeBin(DTO):
    lower: UInt
    upper: PositiveIntText
    count: PositiveIntText
    sum_compute_tokens: UInt
    share: Ratio
    mean: Fraction

    @model_validator(mode="after")
    def check_bin(self) -> Self:
        if int(self.upper) <= int(self.lower):
            raise ValueError("upper must exceed lower")
        if self.mean.numerator != self.sum_compute_tokens or self.mean.denominator != self.count:
            raise ValueError("mean must match exact sum/count")
        if (
            not int(self.lower) * int(self.count)
            <= int(self.sum_compute_tokens)
            < int(self.upper) * int(self.count)
        ):
            raise ValueError("sum outside bin")
        return self


class RankRow(DTO):
    appid: Text
    request_count: PositiveIntText
    total_prompt_tokens: UInt
    total_ideal_cached_tokens: UInt
    total_ideal_compute_tokens: UInt
    ideal_hit_rate: Ratio | None
    prompt_p90: UInt
    typical_compute_tokens: Fraction
    representative_bin: ModeBin
    tie_count: PositiveIntText

    @model_validator(mode="after")
    def conservation(self) -> Self:
        p, h, c = map(
            int,
            (
                self.total_prompt_tokens,
                self.total_ideal_cached_tokens,
                self.total_ideal_compute_tokens,
            ),
        )
        if p != h + c:
            raise ValueError("P must equal H+C")
        if (p == 0) != (self.ideal_hit_rate is None):
            raise ValueError("zero denominator must be null")
        if p and self.ideal_hit_rate is not None and abs(self.ideal_hit_rate - h / p) > 1e-12:
            raise ValueError("incorrect hit ratio")
        if self.typical_compute_tokens != self.representative_bin.mean:
            raise ValueError("representative mean mismatch")
        return self


class Quality(DTO):
    read_rows: UInt
    valid_rows: UInt
    skipped_rows: UInt

    @model_validator(mode="after")
    def conserve(self) -> Self:
        if int(self.read_rows) != int(self.valid_rows) + int(self.skipped_rows):
            raise ValueError("quality count mismatch")
        return self


class Ranking(DTO):
    service_instance_id: Text
    user_run_id: Text
    common_name: Text
    index_revision: Text
    bin_width: Width
    total: UInt
    next_offset: UInt | None
    file_quality: Quality
    rows: list[RankRow]


class Modes(DTO):
    user_run_id: Text
    appid: Text
    index_revision: Text
    bin_width: Width
    total: UInt
    next_offset: UInt | None
    bins: list[ModeBin]


class Scenario(DTO):
    scenario_id: Text
    revision: PositiveIntText
    model_id: ModelId
    common_name: Text
    deployment: Text
    source: Literal["user_assumption", "verified_measurement"]
    source_description: Text
    evidence_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None
    measurement_boundary: Text
    workload_description: Text
    thinking_mode: Text
    min_prompt_tokens: UInt
    max_prompt_tokens: PositiveIntText
    chunk_tokens: PositiveIntText
    chunk_seconds: DecimalText
    overhead_seconds: DecimalText
    sample_count: UInt
    calibration_notes: Text

    @model_validator(mode="after")
    def valid_scenario(self) -> Self:
        from decimal import Decimal

        if Decimal(self.chunk_seconds) <= 0:
            raise ValueError("chunk_seconds must be positive")
        if int(self.min_prompt_tokens) > int(self.max_prompt_tokens):
            raise ValueError("invalid coverage")
        if self.source == "verified_measurement" and (
            not self.evidence_sha256 or int(self.sample_count) == 0
        ):
            raise ValueError("measurements require evidence and samples")
        return self


class EvaluationRequest(DTO):
    submission_key: Text
    user_run_id: Text
    appid: Text
    scenario_id: Text
    scenario_revision: PositiveIntText
    target_seconds: DecimalText
    waiting_seconds: DecimalText
    comparator: Literal["le", "lt"]

    @model_validator(mode="after")
    def positive_target(self) -> Self:
        from decimal import Decimal

        if Decimal(self.target_seconds) <= 0:
            raise ValueError("target must be positive")
        return self


class Evaluation(DTO):
    evaluation_id: Text
    service_instance_id: Text
    request: EvaluationRequest
    scenario: Scenario
    status: Literal["reference", "reference_with_limit", "no_budget", "out_of_scope", "unavailable"]
    reason: Text | None
    request_count: UInt
    prompt_p90: UInt | None
    allowed_chunks: UInt | None
    computable_tokens: UInt | None
    required_hit_fraction: Fraction | None
    required_hit_rate: Ratio | None
    limitations: list[Text]

    @model_validator(mode="after")
    def available_values(self) -> Self:
        values = (
            self.allowed_chunks,
            self.computable_tokens,
            self.required_hit_fraction,
            self.required_hit_rate,
        )
        if self.status in ("reference", "reference_with_limit"):
            if any(v is None for v in values) or not self.prompt_p90 or int(self.prompt_p90) == 0:
                raise ValueError("reference requires all computed values")
            if self.required_hit_fraction is not None:
                n = int(self.required_hit_fraction.numerator)
                d = int(self.required_hit_fraction.denominator)
                if (
                    n > d
                    or self.required_hit_rate is None
                    or abs(n / d - self.required_hit_rate) > 1e-12
                ):
                    raise ValueError("reference fraction mismatch")
        elif any(v is not None for v in values) or self.reason is None:
            raise ValueError("unavailable requires reason and null result")
        return self


class Error(DTO):
    code: Text
    message: Text


class ErrorEnvelope(DTO):
    error: Error
