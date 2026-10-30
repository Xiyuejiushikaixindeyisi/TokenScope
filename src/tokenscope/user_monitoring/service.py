"""User runs bind one GB service to the existing independent-appid replay."""

import csv
import io
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

from tokenscope.domain import RunSubmission
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest, verify_seal
from tokenscope.monitoring.publications import identity
from tokenscope.monitoring.service import MonitoringService
from tokenscope.user_monitoring import projection
from tokenscope.user_monitoring.contracts import Bind, Receipt, Submit, UserState
from tokenscope.user_monitoring.storage import Store, canonical


class UserRunService:
    def __init__(self, base: MonitoringService) -> None:
        self.base = base
        self.store = Store(base.state_root / "user_monitoring")
        self.root = self.store.root
        with base.control.connect() as db:
            self.service_id = str(identity(db, require_ready=False)["service_instance_id"])

    def receipt(self, run_id: str) -> Receipt:
        row = self.store.run(run_id)
        return Receipt(
            service_instance_id=self.service_id,
            user_run_id=row["id"],
            base_run_id=row["base_id"],
            common_name=row["common_name"],
            model_id=row["model_id"],
            state=UserState(row["state"]),
            index_revision=row["revision"],
            error_code=row["error"],
        )

    def validate_name(self, name: str, model_id: str) -> None:
        matches = [
            m["settings"]["model_id"]
            for m in self.base.models()
            if name in (m["settings"]["model_id"], *m["settings"]["model_aliases"])
        ]
        if matches != [model_id]:
            raise TokenScopeError(
                "MODEL_MISMATCH", "Service requires an unambiguous model alias", 422
            )

    def submit(self, request: Submit | Bind) -> Receipt:
        intent = canonical(request.model_dump(mode="json"))
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT id,intent FROM runs WHERE submission_key=?", (request.submission_key,)
            ).fetchone()
            if prior:
                if prior["intent"] != intent:
                    raise TokenScopeError("SUBMISSION_KEY_CONFLICT", "Submission differs", 409)
                return self.receipt(prior["id"])
            base_id = request.base_run_id if isinstance(request, Bind) else None
            if isinstance(request, Bind):
                model = self.base.control.run(request.base_run_id).model_id
            else:
                model = request.model_id
            self.validate_name(request.common_name, model)
            if base_id:
                # A crash may leave the owned base receipt visible before base_id is saved here.
                # Explicit historical binding must not steal that reserved run.
                with self.base.control.connect() as source_db:
                    base_key = source_db.execute(
                        "SELECT submission_key FROM submission_receipts WHERE run_id=?", (base_id,)
                    ).fetchone()
                if (
                    base_key
                    and base_key[0].startswith("uv2.")
                    and db.execute("SELECT 1 FROM runs WHERE id=?", (base_key[0][4:],)).fetchone()
                ):
                    raise TokenScopeError(
                        "SERVICE_BINDING_CONFLICT", "Base reserved by a user submission", 422
                    )
                previous = db.execute(
                    "SELECT id,common_name FROM runs WHERE base_id=?", (base_id,)
                ).fetchone()
                if previous:
                    if previous["common_name"] != request.common_name:
                        raise TokenScopeError("SERVICE_BINDING_CONFLICT", "Base already bound", 422)
                    raise TokenScopeError(
                        "SUBMISSION_KEY_CONFLICT", "Use original binding key", 409
                    )
            else:
                assert isinstance(request, Submit)
                with self.base.inputs.open(request.file_ref):
                    pass
            run_id = "ur-" + uuid4().hex
            db.execute(
                "INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    run_id,
                    request.submission_key,
                    intent,
                    base_id,
                    request.common_name,
                    model,
                    "base_pending" if base_id else "accepted",
                    None,
                    None,
                ),
            )
        return self.receipt(run_id)

    @staticmethod
    def check_csv(stream: Any, common_name: str) -> None:
        # Match the base reader's field allowance; never rewrite or parse request JSON here.
        csv.field_size_limit(2**31 - 1)
        wrapper = io.TextIOWrapper(stream, encoding="utf-8-sig", newline="")
        try:
            reader = csv.DictReader(wrapper)
            if reader.fieldnames and "common_name" in reader.fieldnames:
                for row in reader:
                    if row.get("common_name") != common_name:
                        raise TokenScopeError("SERVICE_BINDING_CONFLICT", "Mixed service CSV", 422)
        except (csv.Error, UnicodeError) as exc:
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid source CSV", 422) from exc
        finally:
            wrapper.detach()

    def process_next(self) -> Receipt | None:
        import fcntl

        with (self.base.state_root / "worker.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return None
            with self.store.connect(readonly=True) as db:
                pending = [
                    dict(r)
                    for r in db.execute(
                        "SELECT * FROM runs WHERE state IN "
                        "('accepted','base_pending','indexing') ORDER BY rowid"
                    )
                ]
            for row in pending:
                run_id = row["id"]
                try:
                    if row["base_id"] is None:
                        request = Submit.model_validate_json(row["intent"])
                        submission = RunSubmission(
                            submission_key="uv2." + run_id,
                            file_ref=request.file_ref,
                            model_id=request.model_id,
                        )
                        base_run = self.base.control.find_submission(submission)
                        if base_run is None:
                            with self.base.inputs.open(request.file_ref) as stream:
                                self.check_csv(stream, request.common_name)
                            base_run = self.base.submit(submission)
                        self.store.update(
                            run_id, base_id=base_run.run_id, state="base_pending", error=None
                        )
                        return self.receipt(run_id)
                    base_run = self.base.control.run(row["base_id"])
                    if base_run.status in ("queued", "running"):
                        continue
                    if base_run.status in ("failed", "interrupted"):
                        self.store.update(
                            run_id,
                            state=base_run.status,
                            error=base_run.error_code or "BASE_FAILED",
                        )
                    elif base_run.status in ("completed", "no_valid_rows"):
                        self.store.update(run_id, state="indexing")
                        directory = self.base.state_root / "runs" / base_run.run_id
                        if not (directory / "requests.sqlite3").is_file():
                            raise TokenScopeError(
                                "REANALYSIS_REQUIRED", "Source facts missing", 409
                            )
                        sealed = verify_seal(directory, base_run.run_id)
                        with (directory / "input.csv").open("rb") as stream:
                            self.check_csv(stream, row["common_name"])
                        quality = sealed["summary"]["quality"]
                        meta = dict(
                            user_run_id=run_id,
                            base_run_id=base_run.run_id,
                            common_name=row["common_name"],
                            algorithm="user-index-1",
                            source_seal=file_digest(directory / "manifest.json"),
                            file_quality=dict(
                                read_rows=str(quality["records_read"]),
                                valid_rows=str(quality["valid_requests"]),
                                skipped_rows=str(quality["skipped_rows"]),
                            ),
                        )
                        destination = self.root / (run_id + ".sqlite3")
                        # Rebuild an unpublished orphan from immutable facts; never trust its name.
                        revision = projection.build(
                            directory / "requests.sqlite3", destination, meta
                        )
                        self.publish(run_id, revision, quality["valid_requests"] == 0)
                    return self.receipt(run_id)
                except TokenScopeError as exc:
                    self.store.update(run_id, state="failed", error=exc.code)
                    return self.receipt(run_id)
                except (OSError, sqlite3.Error):
                    # Retry indexing/intent on the next worker pass, including rename-before-commit.
                    try:
                        self.store.update(run_id, error="STORAGE_UNAVAILABLE")
                    except (OSError, sqlite3.Error):
                        pass
                    return self.receipt(run_id)
            return None

    def publish(self, run_id: str, revision: str, empty: bool) -> None:
        self.store.update(
            run_id, state="empty" if empty else "ready", revision=revision, error=None
        )

    @contextmanager
    def index(self, run_id: str, revision: str | None = None) -> Iterator[sqlite3.Connection]:
        row = self.store.run(run_id)
        if row["state"] not in ("ready", "empty"):
            raise TokenScopeError("RESULT_NOT_READY", "User index is not published", 409)
        if revision is not None and revision != row["revision"]:
            raise TokenScopeError("INDEX_REVISION_CONFLICT", "Index revision differs", 409)
        path = self.root / (row["id"] + ".sqlite3")
        if not path.is_file():
            raise TokenScopeError(
                "INDEX_NOT_READY", "Index file missing; worker rebuild required", 503
            )
        if file_digest(path) != row["revision"]:
            raise TokenScopeError("RESULT_SEAL_INVALID", "User index digest differs", 409)
        db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        try:
            yield db
        finally:
            db.close()

    def rebuild(self, run_id: str) -> None:
        """Explicit maintenance action, never called by a GET or an automatic read."""
        self.store.run(run_id)
        self.store.update(run_id, state="base_pending", revision=None, error=None)
