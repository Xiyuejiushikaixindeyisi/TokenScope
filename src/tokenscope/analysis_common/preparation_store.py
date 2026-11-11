"""Durable, idempotent v3 prepare receipts; registration does no source I/O."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from tokenscope.analysis_common.contracts_v3 import PreparationReceipt3, PreparationRequest3
from tokenscope.analysis_common.execution_v3 import Execution3, WorkerSpec3
from tokenscope.analysis_common.runtime_v3 import CheckpointJournal
from tokenscope.errors import TokenScopeError


class PreparationStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "preparations.sqlite3"
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS preparations ("
                "id TEXT PRIMARY KEY, submission_key TEXT UNIQUE NOT NULL,"
                "request TEXT NOT NULL, intent TEXT NOT NULL, receipt TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS executions "
                "(id TEXT PRIMARY KEY, state TEXT NOT NULL, value TEXT NOT NULL)"
            )
            for row in db.execute(
                "SELECT id,receipt FROM preparations WHERE id NOT IN (SELECT id FROM executions)"
            ):
                receipt = PreparationReceipt3.model_validate_json(row["receipt"])
                value = Execution3(task_id=row["id"], state=receipt.state, phase="preparation")
                db.execute(
                    "INSERT INTO executions VALUES (?,?,?)",
                    (row["id"], receipt.state, value.model_dump_json()),
                )

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def submit(self, request: PreparationRequest3) -> PreparationReceipt3:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            previous = db.execute(
                "SELECT intent,receipt FROM preparations WHERE submission_key=?",
                (request.submission_key,),
            ).fetchone()
            if previous:
                if previous["intent"] != request.intent_digest:
                    raise TokenScopeError(
                        "SUBMISSION_CONFLICT", "Submission key has another intent", 409
                    )
                return PreparationReceipt3.model_validate_json(previous["receipt"])
            receipt = PreparationReceipt3(
                preparation_id="prep-" + uuid4().hex,
                state="queued",
                intent_digest=request.intent_digest,
            )
            db.execute(
                "INSERT INTO preparations VALUES (?,?,?,?,?)",
                (
                    receipt.preparation_id,
                    request.submission_key,
                    request.model_dump_json(),
                    request.intent_digest,
                    receipt.model_dump_json(),
                ),
            )
            value = Execution3(task_id=receipt.preparation_id, state="queued", phase="preparation")
            db.execute(
                "INSERT INTO executions VALUES (?,?,?)",
                (receipt.preparation_id, "queued", value.model_dump_json()),
            )
        return receipt

    def receipt(self, preparation_id: str) -> PreparationReceipt3:
        with self.connect() as db:
            row = db.execute(
                "SELECT receipt FROM preparations WHERE id=?", (preparation_id,)
            ).fetchone()
        if row is None:
            raise TokenScopeError("PREPARATION_NOT_FOUND", "Unknown source preparation", 404)
        return PreparationReceipt3.model_validate_json(row["receipt"])

    def request(self, preparation_id: str) -> PreparationRequest3:
        with self.connect() as db:
            row = db.execute(
                "SELECT request FROM preparations WHERE id=?", (preparation_id,)
            ).fetchone()
        if row is None:
            raise TokenScopeError("PREPARATION_NOT_FOUND", "Unknown source preparation", 404)
        return PreparationRequest3.model_validate_json(row["request"])

    def execution(self, task_id: str) -> Execution3:
        with self.connect() as db:
            row = db.execute("SELECT value FROM executions WHERE id=?", (task_id,)).fetchone()
        if row is None:
            raise TokenScopeError("PREPARATION_NOT_FOUND", "Unknown source preparation", 404)
        return Execution3.model_validate_json(row["value"])

    def _save(self, db: sqlite3.Connection, value: Execution3) -> PreparationReceipt3:
        row = db.execute("SELECT receipt FROM preparations WHERE id=?", (value.task_id,)).fetchone()
        if row is None:
            raise TokenScopeError("PREPARATION_NOT_FOUND", "Unknown source preparation", 404)
        old = PreparationReceipt3.model_validate_json(row["receipt"])
        receipt = PreparationReceipt3(
            preparation_id=value.task_id,
            state=value.state,
            intent_digest=old.intent_digest,
            reason_code=value.reason_code,
            sample_id=value.telemetry.get("sample_id") if value.state == "completed" else None,
            manifest_sha256=value.telemetry.get("manifest_sha256")
            if value.state == "completed"
            else None,
        )
        db.execute(
            "UPDATE executions SET state=?,value=? WHERE id=?",
            (value.state, value.model_dump_json(), value.task_id),
        )
        db.execute(
            "UPDATE preparations SET receipt=? WHERE id=?",
            (receipt.model_dump_json(), value.task_id),
        )
        return receipt

    def claim(self) -> PreparationReceipt3 | None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT value FROM executions WHERE state='queued' ORDER BY rowid LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            value = Execution3.model_validate_json(row["value"]).model_copy(
                update={"state": "running"}
            )
            return self._save(db, value)

    def cancel(self, task_id: str) -> PreparationReceipt3:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT value FROM executions WHERE id=?", (task_id,)).fetchone()
            if row is None:
                raise TokenScopeError("PREPARATION_NOT_FOUND", "Unknown source preparation", 404)
            value = Execution3.model_validate_json(row["value"])
            if value.state in ("queued", "running"):
                changes: dict[str, Any] = {"cancel_requested": True}
                if value.state == "queued":
                    changes.update(state="stopped", reason_code="USER_CANCELLED")
                value = value.model_copy(update=changes)
            return self._save(db, value)

    def finish(
        self, task_id: str, result: dict[str, Any], profile_digest: str | None
    ) -> PreparationReceipt3:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT value FROM executions WHERE id=?", (task_id,)).fetchone()
            if row is None:
                raise TokenScopeError("PREPARATION_NOT_FOUND", "Unknown source preparation", 404)
            previous = Execution3.model_validate_json(row["value"])
            if previous.state != "running":
                return self._save(db, previous)
            value = Execution3(
                task_id=task_id,
                state="stopped" if previous.cancel_requested else result["state"],
                phase="preparation",
                reason_code="USER_CANCELLED"
                if previous.cancel_requested
                else result.get("reason_code"),
                profile_digest=profile_digest,
                checkpoints=tuple(result.get("checkpoints", ())),
                telemetry=result,
                cancel_requested=previous.cancel_requested,
                exit_code=result.get("exit_code"),
                forced_termination=result.get("forced_termination", False),
            )
            return self._save(db, value)

    def recover(self) -> None:
        """Caller holds worker.lock. Never requeue a running/half-written task."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            for row in db.execute("SELECT value FROM executions WHERE state='running'").fetchall():
                value = Execution3.model_validate_json(row["value"])
                checkpoints = value.checkpoints
                root = self.root / "jobs" / value.task_id
                job = root / "job.json"
                try:
                    if job.stat().st_size <= 1024 * 1024:
                        spec = WorkerSpec3.model_validate_json(job.read_bytes())
                        if (
                            Path(spec.job_root).resolve() == root.resolve()
                            and spec.job_id == value.task_id
                        ):
                            checkpoints = CheckpointJournal(
                                root,
                                max_entries=spec.profile.budgets["checkpoints"],
                                max_bytes=spec.profile.sample.max_metadata_bytes,
                            ).committed()
                except (OSError, ValueError, TokenScopeError):
                    pass
                self._save(
                    db,
                    value.model_copy(
                        update={
                            "state": "interrupted",
                            "reason_code": "WORKER_INTERRUPTED",
                            "checkpoints": checkpoints,
                        }
                    ),
                )

    def retry(self, task_id: str, submission_key: str) -> PreparationReceipt3:
        if self.receipt(task_id).state not in ("stopped", "failed", "interrupted"):
            raise TokenScopeError("RETRY_NOT_ALLOWED", "Only stopped tasks can be retried", 409)
        old = self.request(task_id)
        if submission_key == old.submission_key:
            raise TokenScopeError(
                "RETRY_IDENTITY_REQUIRED", "Retry requires a new submission key", 409
            )
        return self.submit(
            PreparationRequest3.model_validate(
                old.model_dump() | {"submission_key": submission_key}
            )
        )
