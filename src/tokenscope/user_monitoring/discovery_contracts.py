"""Additive user monitoring 2.1.0 candidate; frozen 2.0.0 payloads stay unchanged."""

from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tokenscope.user_monitoring.contracts import (
    DTO,
    DecimalText,
    Evaluation,
    ModelId,
    PositiveIntText,
    Text,
    UInt,
)

Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Revision = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)$", max_length=18)]


class DiscoveryQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    appid: Text | None = None
    common_name: Text | None = None
    model_id: ModelId | None = None
    user_run_id: Text | None = None
    snapshot: Digest | None = None
    offset: Revision = "0"
    limit: int = Field(default=100, ge=1, le=1000)


class TraceSource(DTO):
    dataset_kind: Literal["trace"] = "trace"
    source_kind: Literal["user_v2"] = "user_v2"
    base_run_id: Text
    user_run_id: Text
    common_name: Text
    model_id: ModelId
    index_revision: Digest
    input_sha256: Digest
    manifest_sha256: Digest
    settings_sha256: Digest
    encoder_identity: Text
    asset_identity: Text
    file_observed_time_range_utc: tuple[Text | None, Text | None]
    range_kind: Literal["entire_appid_valid_set"] = "entire_appid_valid_set"


class DiscoveryEntry(DTO):
    source: TraceSource
    appid: Text | None
    state: Literal["ready", "empty"]
    registration_order: PositiveIntText
    is_default: bool
    request_count: UInt
    prompt_p90: UInt | None


class DiscoveryPage(DTO):
    service_instance_id: Text
    contract_version: Literal["2.1.0"] = "2.1.0"
    snapshot: Digest
    default_policy: Literal["latest_registered_published_run_per_appid_model_service"] = (
        "latest_registered_published_run_per_appid_model_service"
    )
    total: UInt
    next_offset: UInt | None
    entries: list[DiscoveryEntry]


class DefaultConfig(DTO):
    common_name: Text
    model_id: ModelId
    revision: PositiveIntText
    chunk_tokens: PositiveIntText
    chunk_seconds: DecimalText | None
    tau_reference_chunk_tokens: PositiveIntText
    source: Literal["user_provided"] = "user_provided"
    source_description: Text
    recorded_at: Text
    calibrated: Literal[False] = False

    @model_validator(mode="after")
    def positive_time(self) -> Self:
        if self.chunk_seconds is not None and Decimal(self.chunk_seconds) <= 0:
            raise ValueError("chunk_seconds must be positive or null (not configured)")
        return self


class DefaultUpdate(DTO):
    submission_key: Text
    common_name: Text
    model_id: ModelId
    expected_revision: Revision
    chunk_tokens: PositiveIntText = "8192"
    chunk_seconds: DecimalText | None
    tau_reference_chunk_tokens: PositiveIntText = "8192"
    source_description: Text

    @model_validator(mode="after")
    def positive_time(self) -> Self:
        if self.chunk_seconds is not None and Decimal(self.chunk_seconds) <= 0:
            raise ValueError("chunk_seconds must be positive or null")
        return self


class DefaultQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    common_name: Text | None = None
    model_id: ModelId | None = None
    revision: Revision | None = None

    @model_validator(mode="after")
    def paired_identity(self) -> Self:
        if (self.common_name is None) != (self.model_id is None):
            raise ValueError("model_id and common_name must be supplied together")
        if self.revision is not None and self.model_id is None:
            raise ValueError("historical revision requires model identity")
        return self


class DefaultPage(DTO):
    service_instance_id: Text
    contract_version: Literal["2.1.0"] = "2.1.0"
    configs: list[DefaultConfig]


class AutoEvaluationRequest(DTO):
    submission_key: Text
    user_run_id: Text
    appid: Text
    index_revision: Digest
    target_seconds: DecimalText
    waiting_seconds: DecimalText
    comparator: Literal["le", "lt"] = "le"
    chunk_tokens: PositiveIntText | None = None
    default_revision: Revision | None = None

    @model_validator(mode="after")
    def positive_target(self) -> Self:
        if Decimal(self.target_seconds) <= 0:
            raise ValueError("target_seconds must be positive")
        return self


class AutoEvaluation(DTO):
    evaluation_id: Text
    service_instance_id: Text
    contract_version: Literal["2.1.0"] = "2.1.0"
    request: AutoEvaluationRequest
    source: TraceSource
    defaults: DefaultConfig
    chunk_tokens_origin: Literal["model_default", "request_override"]
    tau_scaled: Literal[False] = False
    evaluation: Evaluation

    @model_validator(mode="after")
    def matching_snapshots(self) -> Self:
        if (
            self.source.user_run_id != self.request.user_run_id
            or self.source.index_revision != self.request.index_revision
            or self.defaults.model_id != self.source.model_id
            or self.defaults.common_name != self.source.common_name
            or self.evaluation.scenario.model_id != self.source.model_id
            or self.evaluation.scenario.common_name != self.source.common_name
            or self.evaluation.evaluation_id != self.evaluation_id
            or self.evaluation.service_instance_id != self.service_instance_id
            or self.evaluation.request.appid != self.request.appid
        ):
            raise ValueError("automatic evaluation snapshots differ")
        return self
