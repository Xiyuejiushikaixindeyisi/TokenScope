"""Versioned API/domain types. All token counts are input tokens unless named otherwise."""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

PositiveInt = Annotated[int, Field(strict=True, gt=0)]
NonnegativeInt = Annotated[int, Field(strict=True, ge=0, le=2**63 - 1)]
ModelId = Literal["GLM-5.2", "Qwen3.6-27B", "DeepSeek-V4-Flash-0731"]
CacheMode = Literal["full_block", "full_block_approximation", "qwen_hybrid", "deepseek_hybrid"]
RunStatus = Literal["queued", "running", "completed", "no_valid_rows", "failed", "interrupted"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ModelSettings(StrictModel):
    model_id: ModelId
    revision: PositiveInt = 1
    block_size: PositiveInt
    block_size_unit: Literal["simulation_input_tokens"] = "simulation_input_tokens"
    cp_world_size: PositiveInt = 1
    mtp: Annotated[bool, Field(strict=True)] = True
    prefix_cache_enabled: Annotated[bool, Field(strict=True)] = True
    hybrid_enabled: Annotated[bool, Field(strict=True)] = False
    cache_mode: CacheMode
    model_aliases: tuple[str, ...] = ()
    encoding_profile: str = "default"

    @model_validator(mode="after")
    def check_mode_and_aliases(self) -> "ModelSettings":
        allowed = {
            "GLM-5.2": {"full_block"},
            "Qwen3.6-27B": {"full_block_approximation", "qwen_hybrid"},
            "DeepSeek-V4-Flash-0731": {"full_block_approximation", "deepseek_hybrid"},
        }
        if self.cache_mode not in allowed[self.model_id]:
            raise ValueError("cache_mode does not belong to this model")
        if not self.encoding_profile.strip() or any(not a.strip() for a in self.model_aliases):
            raise ValueError("encoding profile and aliases must be nonempty")
        if len(set(self.model_aliases)) != len(self.model_aliases):
            raise ValueError("model aliases must be unique")
        return self

    @property
    def effective_block_size(self) -> int:
        return self.block_size * self.cp_world_size


class SettingsChanges(StrictModel):
    block_size: PositiveInt | None = None
    cp_world_size: PositiveInt | None = None
    mtp: Annotated[bool, Field(strict=True)] | None = None
    prefix_cache_enabled: Annotated[bool, Field(strict=True)] | None = None
    hybrid_enabled: Annotated[bool, Field(strict=True)] | None = None
    cache_mode: CacheMode | None = None
    model_aliases: tuple[str, ...] | None = None
    encoding_profile: str | None = None


class SettingsUpdate(StrictModel):
    expected_revision: PositiveInt
    changes: SettingsChanges


class Capability(StrictModel):
    executable: bool
    status: Literal["available", "disabled", "not_supported"]
    strategy: str
    simulation_semantics: Literal["full_block_rule", "chained_approximation"]


class ModelView(StrictModel):
    settings: ModelSettings
    capability: Capability


def capability(settings: ModelSettings) -> Capability:
    semantics: Literal["full_block_rule", "chained_approximation"] = (
        "full_block_rule" if settings.model_id == "GLM-5.2" else "chained_approximation"
    )
    enhanced = settings.hybrid_enabled or settings.cache_mode.endswith("_hybrid")
    return Capability(
        executable=not enhanced,
        status="not_supported"
        if enhanced
        else ("available" if settings.prefix_cache_enabled else "disabled"),
        strategy=(
            "reserved_hybrid"
            if enhanced
            else ("full-block-mtp-v1" if settings.prefix_cache_enabled else "no-cache-v1")
        ),
        simulation_semantics=semantics,
    )


DEFAULT_SETTINGS: dict[str, ModelSettings] = {
    "GLM-5.2": ModelSettings(
        model_id="GLM-5.2", block_size=128, cache_mode="full_block", model_aliases=("glm-5.2",)
    ),
    "Qwen3.6-27B": ModelSettings(
        model_id="Qwen3.6-27B",
        block_size=1536,
        cache_mode="full_block_approximation",
        model_aliases=("Qwen3.6-27B",),
    ),
    "DeepSeek-V4-Flash-0731": ModelSettings(
        model_id="DeepSeek-V4-Flash-0731",
        block_size=32,
        cache_mode="full_block_approximation",
        model_aliases=("deepseek-v4-flash-0731",),
    ),
}


class RunSubmission(StrictModel):
    submission_key: str | None = Field(default=None, pattern=r"^[A-Za-z0-9._-]{1,128}$")
    file_ref: str = Field(min_length=1)
    model_id: ModelId


class Quality(StrictModel):
    records_read: NonnegativeInt = 0
    valid_requests: NonnegativeInt = 0
    skipped_rows: NonnegativeInt = 0
    duplicate_hash_id_rows: NonnegativeInt = 0

    @model_validator(mode="after")
    def conserve(self) -> "Quality":
        if self.records_read != self.valid_requests + self.skipped_rows:
            raise ValueError("quality counts do not conserve records")
        if self.duplicate_hash_id_rows > self.valid_requests:
            raise ValueError("duplicate rows are a subset of valid requests")
        return self


class RunState(StrictModel):
    run_id: str
    file_ref: str
    model_id: ModelId
    status: RunStatus
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    settings: ModelSettings | None = None
    error_code: str | None = None
    snapshot: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
