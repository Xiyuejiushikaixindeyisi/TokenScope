"""Additive v3 sampling contracts; legacy contracts remain frozen."""

from typing import Literal, Self

from pydantic import Field, model_validator

from tokenscope.analysis_common.contracts import (
    AnalysisScope,
    Contract,
    Digest,
    Name,
    SourceSelection,
    stable_id,
)
from tokenscope.analysis_common.sampling_v3 import SamplingDecision

SAMPLING_VERSION: Literal["diagnostics-sampling-3"] = "diagnostics-sampling-3"


class PreparationRequest3(Contract):
    submission_key: str = Field(min_length=1, max_length=128)
    source: SourceSelection
    direction: Literal["low_hit"] = "low_hit"
    discovery_mode: Literal["automatic"] = "automatic"

    @property
    def intent_digest(self) -> str:
        return stable_id("intent", self.model_dump(exclude={"submission_key"}))


class PreparationReceipt3(Contract):
    version: Literal["diagnostics-sampling-3"] = SAMPLING_VERSION
    preparation_id: str = Field(pattern=r"^prep-[0-9a-f]{32}$")
    state: Literal["queued", "running", "completed", "stopped", "failed", "interrupted"]
    intent_digest: Name
    sample_id: Name | None = None
    manifest_sha256: Digest | None = None
    reason_code: Name | None = None

    @model_validator(mode="after")
    def complete_reference(self) -> Self:
        if (self.sample_id is None) != (self.manifest_sha256 is None):
            raise ValueError("Incomplete sample reference")
        if (self.state == "completed") != (self.sample_id is not None):
            raise ValueError("Only completed preparation has a sample")
        return self


class SnapshotFile3(Contract):
    path: str = Field(pattern=r"^(discovery|review)/[0-9]+\.(raw|view|tokens)$")
    size: int = Field(ge=0)
    sha256: Digest


class SampleManifest3(Contract):
    version: Literal["diagnostics-sampling-3"] = SAMPLING_VERSION
    parent_scope: AnalysisScope
    source_selection: SourceSelection
    source_index_revision: Name | None = None
    decision: SamplingDecision
    files: tuple[SnapshotFile3, ...]
    verification_bytes: int = Field(ge=0)
    selected_raw_bytes: int = Field(ge=0)
    selected_token_bytes: int = Field(ge=0)

    @model_validator(mode="after")
    def references(self) -> Self:
        if self.parent_scope.request_count != self.decision.parent_count:
            raise ValueError("Parent count differs")
        if self.parent_scope.request_keys_digest != self.decision.parent_keys_digest:
            raise ValueError("Parent digest differs")
        if self.parent_scope.appid != self.source_selection.appid:
            raise ValueError("App selection differs")
        if self.parent_scope.window != self.source_selection.window:
            raise ValueError("Parent time window differs")
        source = self.parent_scope.source
        if self.source_selection.source_kind == "base":
            if self.source_selection.base_run_id != source.base_run_id:
                raise ValueError("Base source differs")
            if self.source_index_revision is not None or source.user_run_id is not None:
                raise ValueError("Unexpected user source")
        elif (
            self.source_selection.user_run_id != source.user_run_id
            or self.source_index_revision is None
            or self.source_selection.expected_index_revision
            not in (None, self.source_index_revision)
        ):
            raise ValueError("User source differs")
        expected = {
            f"{w.role}/{m.key.source_record_index}.{extension}"
            for w in self.decision.windows
            for m in w.members
            for extension in ("raw", "view", "tokens")
        }
        if len({f.path for f in self.files}) != len(self.files):
            raise ValueError("Duplicate snapshot file")
        if {f.path for f in self.files} != expected:
            raise ValueError("Snapshot file membership differs")
        indexed = {f.path: f for f in self.files}
        for window in self.decision.windows:
            for member in window.members:
                stem = f"{window.role}/{member.key.source_record_index}"
                if (
                    indexed[stem + ".raw"].size != member.raw_bytes
                    or indexed[stem + ".tokens"].size != 4 * (member.prompt_tokens or 0)
                    or indexed[stem + ".view"].size > self.decision.limits.max_metadata_bytes
                ):
                    raise ValueError("Snapshot file size differs")
        if sum(f.size for f in self.files) > self.decision.limits.max_snapshot_bytes:
            raise ValueError("Snapshot exceeds disk budget")
        if any(
            m.key.base_run_id != source.base_run_id
            for w in self.decision.windows
            for m in w.members
        ):
            raise ValueError("Member source differs")
        if self.selected_raw_bytes != sum(w.raw_bytes for w in self.decision.windows):
            raise ValueError("Raw byte total differs")
        if self.selected_token_bytes != 4 * sum(w.prompt_tokens for w in self.decision.windows):
            raise ValueError("Token byte total differs")
        return self

    @property
    def sample_id(self) -> str:
        # Execution telemetry does not change the reproducible sample identity.
        return stable_id(
            "sample",
            self.model_dump(exclude={"verification_bytes"}),
        )
