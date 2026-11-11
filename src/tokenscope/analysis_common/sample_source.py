"""Bounded sample-only adapter compatible with the shared encoding/replay core."""

import hashlib
import json
import sqlite3
import struct
from collections.abc import Iterator
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Literal

from tokenscope.analysis_common.contracts import AnalysisScope, RequestKey, RequestView
from tokenscope.analysis_common.contracts_v3 import SampleManifest3, SnapshotFile3
from tokenscope.analysis_common.runtime_v3 import BudgetLedger, guard_json
from tokenscope.analysis_common.sampling_v3 import SampleMetadata
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.encoding.shards import TokenSlice
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.monitoring.service import MonitoringService


@dataclass(frozen=True)
class SampleResolvedSource(ResolvedSource):
    manifest: SampleManifest3
    manifest_sha256: str
    role: Literal["discovery", "review"]
    control: BudgetLedger | None = None

    @cached_property
    def member_index(self) -> dict[RequestKey, SampleMetadata]:
        window = next(w for w in self.manifest.decision.windows if w.role == self.role)
        return {member.key: member for member in window.members}

    @cached_property
    def file_index(self) -> dict[str, SnapshotFile3]:
        return {ref.path: ref for ref in self.manifest.files}

    def _checked_file(self, name: str) -> Path:
        ref = self.file_index.get(name)
        if ref is None or not name.startswith(self.role + "/"):
            raise TokenScopeError("REQUEST_NOT_IN_SCOPE", "File is outside sample window", 404)
        path = (self.directory / name).resolve(strict=True)
        if self.control is not None:
            self.control.reserve("verification_bytes", ref.size)
        if (
            not path.is_relative_to(self.directory.resolve())
            or path.stat().st_size != ref.size
            or file_digest(path) != ref.sha256
        ):
            raise TokenScopeError("SAMPLE_CHANGED", "Sample file differs", 409)
        return path

    def verify(self) -> None:
        path = self.directory / "manifest.json"
        size = path.stat().st_size
        if size > self.manifest.decision.limits.max_metadata_bytes:
            raise TokenScopeError("SAMPLE_CHANGED", "Sample manifest size differs", 409)
        if self.control is not None:
            self.control.reserve("verification_bytes", size)
        if file_digest(path) != self.manifest_sha256:
            raise TokenScopeError("SAMPLE_CHANGED", "Sample manifest changed", 409)
        # Discovery never opens B files, including for hashing.
        for ref in self.manifest.files:
            if ref.path.startswith(self.role + "/"):
                self._checked_file(ref.path)

    def _rows(self, index: int | None = None) -> Iterator[sqlite3.Row]:
        raise TokenScopeError("SAMPLE_ACCESS_ONLY", "Use exact sample member access", 409)

    def iter_requests(self) -> Iterator[RequestView]:
        self.verify()
        window = next(w for w in self.manifest.decision.windows if w.role == self.role)
        for member in window.members:
            yield self.read_request(member.key)

    def read_request(self, key: RequestKey) -> RequestView:
        member = self.member_index.get(key)
        if member is None:
            raise TokenScopeError("REQUEST_NOT_IN_SCOPE", "Request is outside sample window", 404)
        if self.control is not None:
            self.control.reserve_many({"requests": 1, "raw_read_bytes": member.raw_bytes})
        stem = f"{self.role}/{key.source_record_index}"
        metadata_raw = self._checked_file(stem + ".view").read_text()
        if self.control is not None:
            guard_json(
                metadata_raw,
                max_bytes=self.manifest.decision.limits.max_metadata_bytes,
                max_depth=self.control.profile.max_json_depth,
                max_nodes=self.control.profile.max_json_nodes,
            )
        metadata = json.loads(metadata_raw)
        raw = self._checked_file(stem + ".raw").read_bytes()
        if len(raw) != member.raw_bytes:
            raise TokenScopeError("SAMPLE_CHANGED", "Sample body length differs", 409)
        if (
            metadata["request_key"] != key.model_dump(mode="json")
            or metadata["time_ns"] != member.time_ns
            or metadata["appid"] != self.scope.appid
            or metadata["baseline_metrics"]["p"] != member.prompt_tokens
            or metadata["encoder_identity"] != self.scope.source.encoder_identity
            or metadata["asset_identity"] != self.scope.source.asset_identity
        ):
            raise TokenScopeError("SAMPLE_CHANGED", "Sample metadata differs", 409)
        metadata["scope_id"] = self.scope.scope_id
        metadata["raw_body"] = raw.decode("utf-8")
        if self.control is not None:
            guard_json(
                metadata["raw_body"],
                max_bytes=self.manifest.decision.limits.max_record_bytes,
                max_depth=self.control.profile.max_json_depth,
                max_nodes=self.control.profile.max_json_nodes,
            )
        return RequestView.model_validate(metadata)

    def read_ids(self, request: RequestView) -> list[int]:
        stored = self.read_request(request.request_key)
        if stored != request or stored.token_slice_json is None:
            raise TokenScopeError("SAMPLE_CHANGED", "Request view differs", 409)
        ref = TokenSlice.model_validate_json(stored.token_slice_json)
        if self.control is not None:
            self.control.reserve("token_read_bytes", 4 * stored.baseline_metrics.p)
        content = self._checked_file(
            f"{self.role}/{request.request_key.source_record_index}.tokens"
        ).read_bytes()
        if (
            len(content) != 4 * stored.baseline_metrics.p
            or hashlib.sha256(content).hexdigest() != ref.sha256
        ):
            raise TokenScopeError("TOKEN_COUNT_MISMATCH", "Sample token reference differs", 409)
        return [item[0] for item in struct.iter_unpack("<I", content)]


def open_sample_window(
    service: MonitoringService,
    directory: Path,
    manifest_sha256: str,
    role: Literal["discovery", "review"],
    *,
    metadata_limit: int,
    control: BudgetLedger | None = None,
) -> SampleResolvedSource:
    directory = directory.resolve(strict=True)
    path = directory / "manifest.json"
    if not path.resolve(strict=True).is_relative_to(directory):
        raise TokenScopeError("SAMPLE_CHANGED", "Sample manifest escapes", 409)
    size = path.stat().st_size
    if size > metadata_limit:
        raise TokenScopeError("SAMPLE_CHANGED", "Sample manifest size differs", 409)
    if control is not None:
        control.reserve("verification_bytes", size)
    if file_digest(path) != manifest_sha256:
        raise TokenScopeError("SAMPLE_CHANGED", "Sample manifest differs", 409)
    manifest = SampleManifest3.model_validate_json(path.read_bytes())
    window = next((w for w in manifest.decision.windows if w.role == role), None)
    if window is None:
        raise TokenScopeError("REVIEW_UNAVAILABLE", "Sample window unavailable", 409)
    scope = AnalysisScope(
        source=manifest.parent_scope.source,
        appid=manifest.parent_scope.appid,
        window=manifest.parent_scope.window,
        request_count=len(window.members),
        request_keys_digest=window.keys_digest,
        baseline_origin="selected_window_recomputed",
    )
    return SampleResolvedSource(service, scope, directory, manifest, manifest_sha256, role, control)
