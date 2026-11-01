"""Read-only diagnostic scope resolution over sealed monitoring runs."""

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tokenscope.analysis_common.contracts import (
    AnalysisScope,
    BaselineMetrics,
    RequestKey,
    RequestView,
    SourceIdentity,
    SourceSelection,
    canonical_metadata,
)
from tokenscope.encoding.shards import TokenSlice, read_slice
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest, verify_seal
from tokenscope.monitoring.service import MonitoringService
from tokenscope.user_monitoring.contracts import UserState
from tokenscope.user_monitoring.service import UserRunService


@dataclass(frozen=True)
class ResolvedSource:
    service: MonitoringService
    scope: AnalysisScope
    directory: Path

    def verify(self) -> None:
        if file_digest(self.directory / "manifest.json") != self.scope.source.manifest_sha256:
            raise TokenScopeError("SOURCE_IDENTITY_CHANGED", "Source manifest changed", 409)
        verify_seal(self.directory, self.scope.source.base_run_id)

    def _where(self) -> tuple[str, tuple[Any, ...]]:
        clause = "appid=?"
        values: tuple[Any, ...] = (self.scope.appid,)
        if self.scope.window is not None:
            clause += " AND time_ns>=? AND time_ns<?"
            values += (self.scope.window.start_ns, self.scope.window.end_ns)
        return clause, values

    def _rows(self, index: int | None = None) -> Iterator[sqlite3.Row]:
        clause, values = self._where()
        if index is not None:
            clause += " AND source_record_index=?"
            values += (index,)
        with self.service.result_db(self.scope.source.base_run_id) as db:
            yield from db.execute(
                "SELECT * FROM request_records JOIN encoded_requests USING(source_record_index) "
                f"WHERE {clause} ORDER BY time_ns,source_record_index",
                values,
            )

    def _view(self, row: sqlite3.Row) -> RequestView:
        source = self.scope.source
        evidence = json.loads(row["evidence_json"])
        raw = row["request_input"]
        if hashlib.sha256(raw.encode("utf-8")).hexdigest() != evidence["raw_json_sha256"]:
            raise TokenScopeError("SOURCE_DIGEST_MISMATCH", "Stored request has changed", 409)
        if row["encoder_identity"] != source.encoder_identity:
            raise TokenScopeError("ENCODER_IDENTITY_MISMATCH", "Mixed encoder identity", 409)
        return RequestView(
            request_key=RequestKey(
                base_run_id=source.base_run_id, source_record_index=row["source_record_index"]
            ),
            scope_id=self.scope.scope_id,
            appid=row["appid"],
            time_ns=row["time_ns"],
            hash_id=row["hash_id"],
            raw_body=raw,
            raw_sha256=evidence["raw_json_sha256"],
            raw_body_complete=True,
            baseline_metrics=BaselineMetrics(
                j=row["json_tokens"],
                p=row["prompt_tokens"],
                h=row["ideal_cached_input_tokens"],
                c=row["ideal_compute_input_tokens"],
                o=row["completion_tokens"],
            ),
            encoder_identity=source.encoder_identity,
            asset_identity=source.asset_identity,
            effective_options_json=json.dumps(evidence["effective_options"], ensure_ascii=False),
            token_slice_json=row["token_slice_json"],
            light_evidence_json=row["evidence_json"],
        )

    def iter_requests(self) -> Iterator[RequestView]:
        self.verify()
        digest, count = hashlib.sha256(), 0
        for row in self._rows():
            view = self._view(row)
            digest.update(canonical_metadata(view.request_key) + b"\n")
            count += 1
            yield view
        if (
            count != self.scope.request_count
            or digest.hexdigest() != self.scope.request_keys_digest
        ):
            raise TokenScopeError("SCOPE_CHANGED", "Source scope membership changed", 409)

    def read_request(self, key: RequestKey) -> RequestView:
        if key.base_run_id != self.scope.source.base_run_id:
            raise TokenScopeError("REQUEST_NOT_IN_SCOPE", "Request is outside scope", 404)
        if key.source_record_index > 2**63 - 1:
            raise TokenScopeError("REQUEST_NOT_IN_SCOPE", "Request is outside scope", 404)
        row = next(self._rows(key.source_record_index), None)
        if row is None:
            raise TokenScopeError("REQUEST_NOT_IN_SCOPE", "Request is outside scope", 404)
        return self._view(row)

    def read_ids(self, request: RequestView) -> list[int]:
        stored = self.read_request(request.request_key)
        if stored != request or stored.token_slice_json is None:
            raise TokenScopeError("SOURCE_IDENTITY_CHANGED", "Request view differs", 409)
        ref = TokenSlice.model_validate_json(stored.token_slice_json)
        ids = read_slice(self.directory / "tokens", ref)
        if len(ids) != stored.baseline_metrics.p:
            raise TokenScopeError("TOKEN_COUNT_MISMATCH", "Stored input length differs", 409)
        return ids


class SourceResolver:
    def __init__(self, base: MonitoringService, user: UserRunService | None = None) -> None:
        self.base, self.user = base, user

    def resolve_scope(self, selection: SourceSelection) -> ResolvedSource:
        base_id = selection.base_run_id
        common_name = None
        user_model = None
        if selection.source_kind == "user_v2":
            if self.user is None or selection.user_run_id is None:
                raise TokenScopeError("USER_SOURCE_UNAVAILABLE", "User source is unavailable", 503)
            receipt = self.user.receipt(selection.user_run_id)
            if receipt.state not in (UserState.READY, UserState.EMPTY):
                raise TokenScopeError("RESULT_NOT_READY", "User source is not published", 409)
            with self.user.index(selection.user_run_id, selection.expected_index_revision):
                pass
            base_id, common_name, user_model = (
                receipt.base_run_id,
                receipt.common_name,
                receipt.model_id,
            )
        if base_id is None:
            raise TokenScopeError("SOURCE_UNAVAILABLE", "Base source is unavailable", 503)
        run = self.base.control.run(base_id)
        indexed = self.base.control.result(base_id)
        directory = (self.base.state_root / "runs" / run.run_id).resolve()
        if not directory.is_relative_to((self.base.state_root / "runs").resolve()):
            raise TokenScopeError("SOURCE_IDENTITY_INVALID", "Invalid source identity", 409)
        sealed = verify_seal(directory, run.run_id)["summary"]
        # Monitoring adds post-seal timings only to the control result, deliberately.
        timing_fields = {"elapsed_seconds", "elapsed_scope", "timings_seconds"}
        if {key: value for key, value in indexed.items() if key not in timing_fields} != {
            key: value for key, value in sealed.items() if key not in timing_fields
        } or run.settings is None:
            raise TokenScopeError("SOURCE_IDENTITY_CHANGED", "Source publication differs", 409)
        if user_model is not None and user_model != run.model_id:
            raise TokenScopeError("SOURCE_BINDING_MISMATCH", "Source model differs", 409)
        runtime = sealed["runtime"]
        identity = SourceIdentity(
            base_run_id=run.run_id,
            user_run_id=selection.user_run_id,
            common_name=common_name,
            model_id=run.model_id,
            manifest_sha256=file_digest(directory / "manifest.json"),
            asset_identity=runtime["asset_identity"],
            encoder_identity=runtime["encoder_identity"],
            profile_json=json.dumps(runtime["profile"]),
            settings_json=run.settings.model_dump_json(),
            algorithm_version=runtime["algorithm_version"],
        )
        clause = "appid=?"
        values: tuple[Any, ...] = (selection.appid,)
        if selection.window is not None:
            if not all(
                -(2**63) <= n < 2**63
                for n in (
                    selection.window.start_ns,
                    selection.window.end_ns,
                )
            ):
                raise TokenScopeError("INVALID_WINDOW", "Window exceeds timestamp range", 422)
            clause += " AND time_ns>=? AND time_ns<?"
            values += (selection.window.start_ns, selection.window.end_ns)
        digest, count = hashlib.sha256(), 0
        with self.base.result_db(run.run_id) as db:
            for row in db.execute(
                "SELECT source_record_index FROM request_records "
                "JOIN encoded_requests USING(source_record_index) "
                f"WHERE {clause} ORDER BY time_ns,source_record_index",
                values,
            ):
                digest.update(
                    canonical_metadata(
                        RequestKey(
                            base_run_id=run.run_id,
                            source_record_index=row[0],
                        )
                    )
                    + b"\n"
                )
                count += 1
        return ResolvedSource(
            self.base,
            AnalysisScope(
                source=identity,
                appid=selection.appid,
                window=selection.window,
                request_count=count,
                request_keys_digest=digest.hexdigest(),
                baseline_origin="original_run_window"
                if selection.window is None
                else "selected_window_recomputed",
            ),
            directory,
        )
