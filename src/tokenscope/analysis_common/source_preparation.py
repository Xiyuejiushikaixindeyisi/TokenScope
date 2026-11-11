"""Prepare an immutable, bounded derivative of a sealed source.

Never called by a GET or in the HTTP submission path. Runtime v3 supplies
checkpoint/reservation callbacks; the default supports isolated component tests.
"""

import hashlib
import json
import os
import sqlite3
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tokenscope.analysis_common.contracts import RequestKey, SourceSelection, canonical_metadata
from tokenscope.analysis_common.contracts_v3 import SampleManifest3, SnapshotFile3
from tokenscope.analysis_common.sampling_v3 import SampleLimits, SampleMetadata, select_windows
from tokenscope.analysis_common.source import ResolvedSource, SourceResolver
from tokenscope.encoding.shards import TokenSlice
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import sync_directory

CHUNK = 1024 * 1024


def no_checkpoint() -> None:
    pass


def no_charge(count: int) -> None:
    pass


def no_guard(raw: str) -> None:
    pass


@dataclass
class PreparationIO:
    metadata_limit: int
    checkpoint: Callable[[], None] = no_checkpoint
    charge_verification: Callable[[int], None] = no_charge
    charge_snapshot: Callable[[int], None] = no_charge
    charge_member: Callable[[SampleMetadata], None] = lambda member: None
    guard: Callable[[str], None] = no_guard
    phase: Callable[[str], None] = no_guard
    charge_metadata: Callable[[int], None] = no_charge
    verification_bytes: int = 0

    def digest(self, path: Path) -> str:
        value = hashlib.sha256()
        with path.open("rb") as stream:
            remaining = os.fstat(stream.fileno()).st_size
            while remaining:
                self.checkpoint()
                count = min(CHUNK, remaining)
                self.charge_verification(count)
                chunk = stream.read(count)
                if len(chunk) != count:
                    raise TokenScopeError(
                        "SOURCE_CHANGED", "Source changed during verification", 409
                    )
                self.verification_bytes += count
                value.update(chunk)
                remaining -= count
            if stream.read(1):
                raise TokenScopeError("SOURCE_CHANGED", "Source grew during verification", 409)
        return value.hexdigest()

    def read_metadata(self, path: Path) -> Any:
        self.checkpoint()
        with path.open("rb") as stream:
            size = os.fstat(stream.fileno()).st_size
            if size > self.metadata_limit:
                raise TokenScopeError("METADATA_LIMIT", "Source metadata exceeds its limit", 422)
            self.charge_verification(size)
            data = stream.read(size + 1)
        self.verification_bytes += len(data)
        if len(data) != size:
            raise TokenScopeError("SOURCE_CHANGED", "Source metadata changed", 409)
        raw = data.decode("utf-8")
        self.guard(raw)
        return json.loads(raw)


def blob_text(db: sqlite3.Connection, table: str, column: str, index: int, limit: int) -> str:
    # blobopen works on SQLite TEXT and exposes its UTF-8 length without SELECTing
    # the full string into Python (or CASTing it to an allocated BLOB in SQLite).
    with db.blobopen(table, column, index, readonly=True) as blob:
        if len(blob) > limit:
            raise TokenScopeError("RECORD_BYTE_LIMIT", "Selected field exceeds its limit", 422)
        return blob.read().decode("utf-8")


def metadata_rows(
    source: ResolvedSource, db: sqlite3.Connection, io: PreparationIO
) -> Iterator[SampleMetadata]:
    clause, values = source._where()
    query = (
        "SELECT source_record_index,time_ns,prompt_tokens "
        "FROM request_records LEFT JOIN encoded_requests USING(source_record_index) "
        f"WHERE {clause} ORDER BY time_ns,source_record_index"
    )
    for row in db.execute(query, values):
        io.checkpoint()
        io.charge_metadata(32)
        with db.blobopen("request_records", "request_input", row[0], readonly=True) as blob:
            size = len(blob)
        yield SampleMetadata(
            key=RequestKey(base_run_id=source.scope.source.base_run_id, source_record_index=row[0]),
            time_ns=row[1],
            raw_bytes=size,
            prompt_tokens=row[2],
        )


class SnapshotWriter:
    def __init__(
        self,
        root: Path,
        maximum: int,
        checkpoint: Callable[[], None],
        charge: Callable[[int], None] = no_charge,
    ) -> None:
        self.root, self.maximum, self.checkpoint = root, maximum, checkpoint
        self.charge = charge
        self.used = 0
        self.files: list[SnapshotFile3] = []

    def reserve(self, size: int) -> None:
        self.checkpoint()
        if self.used + size > self.maximum:
            raise TokenScopeError("SNAPSHOT_DISK_LIMIT", "Snapshot disk budget exhausted", 422)
        self.charge(size)
        self.used += size

    def write(self, relative: str, content: bytes) -> None:
        self.reserve(len(content))
        path = self.root / relative
        path.parent.mkdir(exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        self.files.append(
            SnapshotFile3(
                path=relative, size=len(content), sha256=hashlib.sha256(content).hexdigest()
            )
        )

    def copy_tokens(self, source: Path, ref: TokenSlice, relative: str) -> None:
        if ref.offset_bytes % 4:
            raise TokenScopeError("INVALID_TOKEN_SLICE", "Unaligned token reference", 409)
        size = ref.token_count * 4
        self.reserve(size)
        digest = hashlib.sha256()
        target = self.root / relative
        target.parent.mkdir(exist_ok=True)
        with source.open("rb") as src, target.open("xb") as dst:
            if ref.offset_bytes + size > os.fstat(src.fileno()).st_size:
                raise TokenScopeError("TRUNCATED_TOKEN_SHARD", "Source tokens incomplete", 409)
            src.seek(ref.offset_bytes)
            remaining = size
            while remaining:
                self.checkpoint()
                content = src.read(min(CHUNK, remaining))
                if not content:
                    raise TokenScopeError("TRUNCATED_TOKEN_SHARD", "Source tokens incomplete", 409)
                dst.write(content)
                digest.update(content)
                remaining -= len(content)
            dst.flush()
            os.fsync(dst.fileno())
        if digest.hexdigest() != ref.sha256:
            raise TokenScopeError("TOKEN_SHARD_DIGEST_MISMATCH", "Source tokens changed", 409)
        self.files.append(SnapshotFile3(path=relative, size=size, sha256=ref.sha256))


def selected_view(
    source: ResolvedSource,
    db: sqlite3.Connection,
    member: SampleMetadata,
    limits: SampleLimits,
    *,
    guard: Callable[[str], None] = no_guard,
) -> dict[str, Any]:
    index = member.key.source_record_index
    row = db.execute(
        "SELECT source_record_index,time_ns,completion_tokens,"
        "json_tokens,prompt_tokens,ideal_cached_input_tokens,ideal_compute_input_tokens "
        "FROM request_records JOIN encoded_requests USING(source_record_index) "
        "WHERE source_record_index=? AND appid=?",
        (index, source.scope.appid),
    ).fetchone()
    if row is None or row["time_ns"] != member.time_ns:
        raise TokenScopeError("SCOPE_CHANGED", "Selected member changed", 409)
    record = dict(row)
    record["appid"] = source.scope.appid  # The WHERE predicate checked this binding.
    record["hash_id"] = blob_text(
        db, "request_records", "hash_id", index, limits.max_metadata_bytes
    )
    record["encoder_identity"] = blob_text(
        db, "encoded_requests", "encoder_identity", index, limits.max_metadata_bytes
    )
    record["request_input"] = blob_text(
        db,
        "request_records",
        "request_input",
        index,
        min(limits.max_record_bytes, member.raw_bytes),
    )
    if len(record["request_input"].encode("utf-8")) != member.raw_bytes:
        raise TokenScopeError("SOURCE_CHANGED", "Selected body length changed", 409)
    for column in ("evidence_json", "token_slice_json"):
        record[column] = blob_text(db, "encoded_requests", column, index, limits.max_metadata_bytes)
        guard(record[column])
    guard(record["request_input"])
    view = source._view(record)
    if view.baseline_metrics.p != member.prompt_tokens or view.token_slice_json is None:
        raise TokenScopeError("SOURCE_CHANGED", "Selected encoding changed", 409)
    return view.model_dump(mode="json")


def prepare_snapshot(
    resolver: SourceResolver,
    selection: SourceSelection,
    limits: SampleLimits,
    target: Path,
    *,
    io: PreparationIO | None = None,
    calibrate: Callable[[ResolvedSource, SampleLimits], SampleLimits] | None = None,
) -> SampleManifest3:
    """Exclusive target; failures retain an unpublished .working directory."""
    io = io or PreparationIO(limits.max_metadata_bytes)
    target = target.resolve()
    if target.exists():
        raise TokenScopeError("SNAPSHOT_EXISTS", "Use a new preparation identity", 409)
    working = target.with_name(target.name + ".working")
    working.mkdir(parents=True, exist_ok=False)
    pinned_selection = selection
    revision = None
    if selection.source_kind == "user_v2":
        if resolver.user is None or selection.user_run_id is None:
            raise TokenScopeError("USER_SOURCE_UNAVAILABLE", "User source unavailable", 503)
        receipt = resolver.user.receipt(selection.user_run_id)
        revision = receipt.index_revision
        if selection.expected_index_revision not in (None, revision):
            raise TokenScopeError("INDEX_REVISION_CONFLICT", "User index revision differs", 409)
        pinned_selection = selection.model_copy(update={"expected_index_revision": revision})
    io.phase("verification")
    source = resolver.resolve_scope(
        pinned_selection, digest=io.digest, read_metadata=io.read_metadata, checkpoint=io.checkpoint
    )
    if calibrate is not None:
        limits = calibrate(source, limits)
    io.phase("selection")
    writer = SnapshotWriter(working, limits.max_snapshot_bytes, io.checkpoint, io.charge_snapshot)
    with source.service.result_db(source.scope.source.base_run_id) as db:
        db.execute("PRAGMA cache_size=-2048")
        db.execute("PRAGMA temp_store=FILE")
        db.execute("BEGIN")
        encoded_digest = hashlib.sha256()
        encoded_count = 0

        def checked_metadata() -> Iterator[SampleMetadata]:
            nonlocal encoded_count
            for row in metadata_rows(source, db, io):
                if row.prompt_tokens is not None:
                    encoded_count += 1
                    encoded_digest.update(canonical_metadata(row.key) + b"\n")
                yield row

        decision = select_windows(checked_metadata(), limits)
        if (
            encoded_count != source.scope.request_count
            or encoded_digest.hexdigest() != source.scope.request_keys_digest
        ):
            raise TokenScopeError("SCOPE_CHANGED", "Parent membership changed", 409)
        if not decision.windows:
            raise TokenScopeError(
                "NO_ADMISSIBLE_SAMPLE", "No complete request fits the profile", 422
            )
        io.phase("snapshot")
        for window in decision.windows:
            for member in window.members:
                io.checkpoint()
                io.charge_member(member)
                if io.guard is no_guard:
                    data = selected_view(source, db, member, limits)
                else:
                    data = selected_view(source, db, member, limits, guard=io.guard)
                stem = f"{window.role}/{member.key.source_record_index}"
                raw = data.pop("raw_body").encode("utf-8")
                writer.write(stem + ".raw", raw)
                view_bytes = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
                if len(view_bytes) > limits.max_metadata_bytes:
                    raise TokenScopeError("METADATA_LIMIT", "Selected metadata exceeds limit", 422)
                writer.write(stem + ".view", view_bytes)
                try:
                    ref = TokenSlice.model_validate_json(data["token_slice_json"])
                except ValueError as exc:
                    raise TokenScopeError(
                        "INVALID_TOKEN_SLICE", "Source token reference is invalid", 409
                    ) from exc
                if ref.token_count != member.prompt_tokens:
                    raise TokenScopeError("TOKEN_COUNT_MISMATCH", "Source token count differs", 409)
                token_file = (source.directory / "tokens" / ref.shard).resolve(strict=True)
                if not token_file.is_relative_to(source.directory):
                    raise TokenScopeError("INVALID_TOKEN_SLICE", "Source token path escapes", 409)
                writer.copy_tokens(token_file, ref, stem + ".tokens")
        # The transaction guarantees one SQLite view; before/after full seals
        # additionally bind the external token shards and the published identity.
        io.phase("verification")
        after = resolver.resolve_scope(
            pinned_selection,
            digest=io.digest,
            read_metadata=io.read_metadata,
            checkpoint=io.checkpoint,
        )
        if after.scope != source.scope:
            raise TokenScopeError("SOURCE_CHANGED", "Source changed during snapshot", 409)
    manifest = SampleManifest3(
        parent_scope=source.scope.model_copy(
            update={
                "request_count": decision.parent_count,
                "request_keys_digest": decision.parent_keys_digest,
            }
        ),
        source_selection=pinned_selection,
        source_index_revision=revision,
        decision=decision,
        files=tuple(writer.files),
        verification_bytes=io.verification_bytes,
        selected_raw_bytes=sum(w.raw_bytes for w in decision.windows),
        selected_token_bytes=sum(w.prompt_tokens for w in decision.windows) * 4,
    )
    manifest_bytes = manifest.model_dump_json().encode("utf-8")
    if len(manifest_bytes) > limits.max_metadata_bytes:
        raise TokenScopeError("METADATA_LIMIT", "Sample manifest exceeds its limit", 422)
    writer.reserve(len(manifest_bytes))
    with (working / "manifest.json").open("xb") as stream:
        stream.write(manifest_bytes)
        stream.flush()
        os.fsync(stream.fileno())
    for window in decision.windows:
        sync_directory(working / window.role)
    sync_directory(working)
    io.checkpoint()
    working.rename(target)
    sync_directory(target.parent)
    return manifest
