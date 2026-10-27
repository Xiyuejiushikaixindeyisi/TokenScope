"""Shared application boundary for HTTP and CLI."""

import json
import os
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from tokenscope import ALGORITHM_VERSION, DESIGN_VERSION, SCHEMA_VERSION, __version__
from tokenscope.domain import DEFAULT_SETTINGS, RunState, RunSubmission, SettingsUpdate, capability
from tokenscope.encoding.assets import AssetRegistry
from tokenscope.encoding.batch import EncodingBatchService
from tokenscope.encoding.models import EncodingProfile, ModelEncoder
from tokenscope.encoding.shards import TokenSlice
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import CsvBatchReader
from tokenscope.monitoring.pipeline import RunProcessor, profile_for
from tokenscope.monitoring.publications import PublicationRepository
from tokenscope.monitoring.statistics import LENGTHS, WIDTHS
from tokenscope.monitoring.storage import ControlStore, RawRequestStore
from tokenscope.monitoring.views import MonitoringViewService
from tokenscope.paths import InputRoot


class MonitoringService:
    def __init__(
        self,
        input_root: Path,
        state_root: Path,
        asset_root: Path | None = None,
        cpu_budget: int = 8,
        batch_rows: int = 256,
        batch_bytes: int = 16 * 1024 * 1024,
    ) -> None:
        self.inputs = InputRoot(input_root)
        self.state_root = state_root.resolve()
        self.control = ControlStore(self.state_root / "control.sqlite3")
        self.publications = PublicationRepository(self.control)
        self.views = MonitoringViewService(self.control, self.state_root)
        self.assets = AssetRegistry(asset_root or Path(__file__).resolve().parents[3])
        self.cpu_budget = cpu_budget
        self.processor = RunProcessor(
            self.inputs,
            self.state_root,
            self.assets,
            self.control,
            cpu_budget,
            batch_rows,
            batch_bytes,
        )

    def models(self) -> list[dict[str, Any]]:
        return [self.model(model_id) for model_id in DEFAULT_SETTINGS]

    def model(self, model_id: str) -> dict[str, Any]:
        settings = self.control.settings(model_id)
        return {
            "settings": settings.model_dump(mode="json"),
            "capability": capability(settings).model_dump(mode="json"),
        }

    def update_settings(self, model_id: str, update: SettingsUpdate) -> dict[str, Any]:
        candidate = self.control.settings(model_id).model_copy(
            update=update.changes.model_dump(exclude_unset=True)
        )
        profile_for(candidate, self.cpu_budget)
        settings = self.control.update_settings(model_id, update)
        return {
            "settings": settings.model_dump(mode="json"),
            "capability": capability(settings).model_dump(mode="json"),
        }

    def version(self) -> dict[str, Any]:
        return {
            "code_version": __version__,
            "design_version": DESIGN_VERSION,
            "schema_version": SCHEMA_VERSION,
            "algorithm_version": ALGORITHM_VERSION,
            "release_id": os.environ.get("TOKENSCOPE_RELEASE_ID"),
            "source_manifest_sha256": os.environ.get("TOKENSCOPE_SOURCE_MANIFEST_SHA256"),
            "asset_identities": [],
            "implemented_batches": ["B001", "B002", "B003", "B004", "B005", "B005.1"],
            "asset_lock": json.loads(self.assets.lock_path.read_text()),
        }

    def readiness(self) -> dict[str, Any]:
        with self.control.connect() as db:
            db.execute("SELECT 1").fetchone()
        models = {}
        for model_id in DEFAULT_SETTINGS:
            settings = self.control.settings(model_id)
            try:
                assets = self.assets.load(model_id)
                profile = profile_for(settings, self.cpu_budget)
                pending = model_id == "DeepSeek-V4-Flash-0731" and profile.default_thinking is None
                models[model_id] = dict(
                    ready=capability(settings).executable and not pending,
                    assets="verified",
                    asset_identity=assets.identity,
                    explicit_request_options_supported=True,
                    reason="ENCODING_DEFAULT_UNRESOLVED"
                    if pending
                    else None
                    if capability(settings).executable
                    else "UNSUPPORTED_CACHE_MODE",
                )
            except TokenScopeError as exc:
                models[model_id] = dict(ready=False, reason=exc.code)
        return {
            "ready": all(item["ready"] for item in models.values()),
            "storage": "ready",
            "pipeline": "implemented",
            "models": models,
        }

    def submit(self, submission: RunSubmission) -> RunState:
        prior = self.control.find_submission(submission)
        if prior is not None:
            return prior
        settings = self.control.settings(submission.model_id)
        if not capability(settings).executable:
            raise TokenScopeError(
                "UNSUPPORTED_CACHE_MODE", "Enhanced hybrid simulation is reserved", 422
            )
        with self.inputs.open(submission.file_ref):
            pass
        self.assets.load(settings.model_id)
        profile_for(settings, self.cpu_budget)
        return self.control.enqueue(submission)

    @contextmanager
    def result_db(self, run_id: str) -> Iterator[sqlite3.Connection]:
        # A completed index is mandatory; directory existence alone never exposes a result.
        self.control.result(run_id)
        path = self.state_root / "runs" / run_id / "requests.sqlite3"
        db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def pagination(offset: int, limit: int) -> None:
        if not 0 <= offset <= 2**63 - 1 or not 1 <= limit <= 1000:
            raise TokenScopeError(
                "INVALID_PAGINATION", "Limit must be 1..1000 and offset nonnegative", 422
            )

    def metrics(
        self, run_id: str, appid: str | None = None, offset: int = 0, limit: int = 100
    ) -> dict[str, Any]:
        self.pagination(offset, limit)
        with self.result_db(run_id) as db:
            total = db.execute(
                "SELECT count(*) FROM groups WHERE (? IS NULL OR appid=?)", (appid, appid)
            ).fetchone()[0]
            rows = db.execute(
                "SELECT metrics_json FROM groups WHERE (? IS NULL OR appid=?) "
                "ORDER BY appid LIMIT ? OFFSET ?",
                (appid, appid, limit, offset),
            )
            groups = [json.loads(row[0]) for row in rows]
        return dict(run_id=run_id, total_groups=total, offset=offset, limit=limit, groups=groups)

    def histograms(self, run_id: str, appid: str, bin_width: int = 5000) -> dict[str, Any]:
        if bin_width not in WIDTHS:
            raise TokenScopeError("INVALID_BIN_WIDTH", "Select 1000, 2000 or 5000", 422)
        with self.result_db(run_id) as db:
            row = db.execute(
                "SELECT histograms_json FROM groups WHERE appid=?", (appid,)
            ).fetchone()
            if row is None:
                raise TokenScopeError("GROUP_NOT_FOUND", "Unknown result group", 404)
            values = json.loads(row[0])
        return dict(
            run_id=run_id,
            appid=appid,
            metrics={metric: values[metric][str(bin_width)] for metric in LENGTHS},
        )

    def lengths(
        self,
        run_id: str,
        appid: str,
        metric: str = "prompt_tokens",
        lower: int = 0,
        upper: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        self.pagination(offset, limit)
        if (
            metric not in LENGTHS
            or not 0 <= lower <= 2**63 - 1
            or (upper is not None and not lower < upper <= 2**63 - 1)
        ):
            raise TokenScopeError("INVALID_LENGTH_QUERY", "Invalid metric or interval", 422)
        with self.result_db(run_id) as db:
            where = f"appid=? AND {metric}>=? AND (? IS NULL OR {metric}<?)"
            parameters = (appid, lower, upper, upper)
            count = db.execute(f"SELECT count(*) FROM facts WHERE {where}", parameters).fetchone()[
                0
            ]
            rows = db.execute(
                f"""WITH ranked AS (SELECT source_record_index,hash_id,appid,time_utc,
                {metric},row_number() OVER (ORDER BY {metric} DESC,source_record_index) AS rank
                FROM facts WHERE appid=?) SELECT * FROM ranked WHERE {metric}>=?
                AND (? IS NULL OR {metric}<?) ORDER BY rank LIMIT ? OFFSET ?""",
                (*parameters, limit, offset),
            )
            points = [
                dict(
                    rank=row["rank"],
                    request_ref=dict(run_id=run_id, source_record_index=row["source_record_index"]),
                    hash_id=row["hash_id"],
                    time_utc=row["time_utc"],
                    length=row[metric],
                )
                for row in rows
            ]
        return dict(
            run_id=run_id,
            appid=appid,
            metric=metric,
            lower=lower,
            upper=upper,
            offset=offset,
            limit=limit,
            total=count,
            points=points,
        )

    def explain_encoding(self, run_id: str, source_record_index: int) -> dict[str, Any]:
        result = self.control.result(run_id)
        settings = self.control.run(run_id).settings
        if settings is None:
            raise TokenScopeError("SNAPSHOT_NOT_READY", "No runtime snapshot", 409)
        with self.result_db(run_id) as db:
            row = db.execute(
                """SELECT request_input,token_slice_json FROM request_records
                JOIN encoded_requests USING(source_record_index) WHERE source_record_index=?""",
                (source_record_index,),
            ).fetchone()
            if row is None:
                raise TokenScopeError("REQUEST_NOT_FOUND", "Unknown encoded request", 404)
        assets = self.assets.load(settings.model_id)
        if assets.identity != result["runtime"]["asset_identity"]:
            raise TokenScopeError(
                "ENCODING_REPLAY_MISMATCH", "Original assets are unavailable", 409
            )
        profile = EncodingProfile.model_validate(result["runtime"]["profile"])
        encoder = EncodingBatchService(ModelEncoder(assets, settings, profile))
        reference = TokenSlice.model_validate_json(row["token_slice_json"])
        return encoder.explain(row["request_input"], reference.sha256)

    def validate_input(self, submission: RunSubmission) -> dict[str, Any]:
        """Diagnostic staging only; never creates a completed analysis run or token metrics."""
        started = time.monotonic()
        settings = self.control.settings(submission.model_id)
        validation_id = str(uuid4())
        directory = self.state_root / "validations" / validation_id
        snapshot = directory / "input.csv"
        checksum = self.inputs.snapshot(submission.file_ref, snapshot)
        store = RawRequestStore(directory / "requests.sqlite3")
        quality = store.ingest(snapshot, CsvBatchReader(settings))
        return {
            "validation_id": validation_id,
            "kind": "input_validation_only",
            "input_sha256": checksum,
            "settings_revision": settings.revision,
            "quality": quality.model_dump(),
            "elapsed_seconds": time.monotonic() - started,
            "token_metrics": None,
        }
