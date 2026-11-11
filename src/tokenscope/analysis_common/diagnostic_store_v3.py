"""Explicit sample diagnosis queue and verified immutable report reads."""

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from tokenscope.analysis_common.execution_v3 import Execution3, WorkerSpec3
from tokenscope.analysis_common.preparation_store import PreparationStore
from tokenscope.analysis_common.runtime_v3 import Checkpoint3, CheckpointJournal
from tokenscope.errors import TokenScopeError


class DiagnosticStore3:
    def __init__(self, preparations: PreparationStore) -> None:
        self.preparations = preparations
        self.root = preparations.root
        with preparations.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS diagnoses (id TEXT PRIMARY KEY, "
                "submission TEXT UNIQUE NOT NULL, preparation TEXT NOT NULL, "
                "state TEXT NOT NULL, value TEXT NOT NULL)"
            )

    def submit(self, preparation_id: str, submission_key: str) -> Execution3:
        if self.preparations.receipt(preparation_id).state != "completed":
            raise TokenScopeError("SAMPLE_NOT_READY", "Preparation is incomplete", 409)
        with self.preparations.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT * FROM diagnoses WHERE submission=?", (submission_key,)
            ).fetchone()
            if row:
                if row["preparation"] != preparation_id:
                    raise TokenScopeError("SUBMISSION_CONFLICT", "Submission identity differs", 409)
                return Execution3.model_validate_json(row["value"])
            value = Execution3(task_id="diag-" + uuid4().hex, state="queued", phase="diagnosis")
            db.execute(
                "INSERT INTO diagnoses VALUES (?,?,?,?,?)",
                (
                    value.task_id,
                    submission_key,
                    preparation_id,
                    value.state,
                    value.model_dump_json(),
                ),
            )
            return value

    def catalog(self, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        with self.preparations.connect() as db:
            rows = db.execute(
                "SELECT * FROM diagnoses ORDER BY rowid DESC LIMIT ? OFFSET ?", (limit + 1, offset)
            ).fetchall()
        return {
            "items": [
                {
                    "execution": Execution3.model_validate_json(row["value"]),
                    "source": self.preparations.request(row["preparation"]).source,
                    "preparation_id": row["preparation"],
                }
                for row in rows[:limit]
            ],
            "next_offset": str(offset + limit) if len(rows) > limit else None,
        }

    def execution(self, task_id: str) -> Execution3:
        with self.preparations.connect() as db:
            row = db.execute("SELECT value FROM diagnoses WHERE id=?", (task_id,)).fetchone()
        if row is None:
            raise TokenScopeError("DIAGNOSIS_NOT_FOUND", "Unknown sample diagnosis", 404)
        return Execution3.model_validate_json(row["value"])

    def claim(self) -> tuple[Execution3, str] | None:
        with self.preparations.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT * FROM diagnoses WHERE state='queued' ORDER BY rowid LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            value = Execution3.model_validate_json(row["value"]).model_copy(
                update={"state": "running"}
            )
            db.execute(
                "UPDATE diagnoses SET state=?,value=? WHERE id=?",
                (value.state, value.model_dump_json(), value.task_id),
            )
            return value, row["preparation"]

    def cancel(self, task_id: str) -> Execution3:
        with self.preparations.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT value FROM diagnoses WHERE id=?", (task_id,)).fetchone()
            if row is None:
                raise TokenScopeError("DIAGNOSIS_NOT_FOUND", "Unknown sample diagnosis", 404)
            value = Execution3.model_validate_json(row["value"])
            if value.state in ("queued", "running"):
                update: dict[str, Any] = {"cancel_requested": True}
                if value.state == "queued":
                    update.update(state="stopped", reason_code="USER_CANCELLED")
                value = value.model_copy(update=update)
                db.execute(
                    "UPDATE diagnoses SET state=?,value=? WHERE id=?",
                    (value.state, value.model_dump_json(), task_id),
                )
            return value

    def finish(
        self, task_id: str, result: dict[str, Any], profile_digest: str | None
    ) -> Execution3:
        with self.preparations.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT value FROM diagnoses WHERE id=?", (task_id,)).fetchone()
            if row is None:
                raise TokenScopeError("DIAGNOSIS_NOT_FOUND", "Unknown sample diagnosis", 404)
            previous = Execution3.model_validate_json(row["value"])
            if previous.state != "running":
                return previous
            value = Execution3(
                task_id=task_id,
                state="stopped" if previous.cancel_requested else result["state"],
                phase="diagnosis",
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
            db.execute(
                "UPDATE diagnoses SET state=?,value=? WHERE id=?",
                (value.state, value.model_dump_json(), task_id),
            )
            return value

    def journal(self, task_id: str) -> CheckpointJournal:
        self.execution(task_id)
        root = self.root / "jobs" / task_id
        path = root / "job.json"
        if path.stat().st_size > 1024 * 1024:
            raise TokenScopeError("INVALID_ARTIFACT", "Invalid worker specification", 409)
        spec = WorkerSpec3.model_validate_json(path.read_bytes())
        if spec.job_id != task_id or Path(spec.job_root).resolve() != root.resolve():
            raise TokenScopeError("INVALID_ARTIFACT", "Worker specification identity differs", 409)
        return CheckpointJournal(
            root,
            max_entries=spec.profile.budgets["checkpoints"],
            max_bytes=spec.profile.sample.max_metadata_bytes,
        )

    def recover(self) -> None:
        # Called only while owning the shared worker lock.
        with self.preparations.connect() as db:
            ids = [row[0] for row in db.execute("SELECT id FROM diagnoses WHERE state='running'")]
        for task_id in ids:
            checkpoints: tuple[Checkpoint3, ...] = ()
            try:
                checkpoints = self.journal(task_id).committed()
            except (OSError, ValueError, TokenScopeError):
                pass
            self.finish(
                task_id,
                {
                    "state": "interrupted",
                    "reason_code": "WORKER_INTERRUPTED",
                    "checkpoints": checkpoints,
                },
                None,
            )

    def report(self, task_id: str) -> dict[str, Any]:
        try:
            journal = self.journal(task_id)
            committed = journal.committed()
        except FileNotFoundError as exc:
            raise TokenScopeError("REPORT_NOT_READY", "No sealed report", 409) from exc
        reports = [item for item in committed if item.kind == "report"]
        if not reports:
            raise TokenScopeError("REPORT_NOT_READY", "No sealed report", 409)
        report: dict[str, Any] = json.loads(
            journal.checked_artifact(reports[-1].artifact).read_bytes()
        )
        if report["task_id"] != task_id:
            raise TokenScopeError("INVALID_ARTIFACT", "Report identity differs", 409)
        # Every published row/plan reference must itself be committed and hash verified.
        references = {item.artifact for item in committed}
        for recommendation in report["recommendations"]:
            for window in recommendation["windows"]:
                for name in ("rows_ref", "plan_ref"):
                    if window[name] and window[name] not in references:
                        raise TokenScopeError(
                            "INVALID_ARTIFACT", "Report has unsealed evidence", 409
                        )
        return report
