"""Diagnostic-only task database and immutable, digest-checked result publication."""

import hashlib
import json
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from tokenscope.analysis_common.contracts import TaskReceipt
from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest


class DiagnosticStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, "
                "submission_key TEXT UNIQUE, intent TEXT NOT NULL, scope TEXT NOT NULL, "
                "options TEXT NOT NULL, attempt INTEGER NOT NULL, status TEXT NOT NULL, "
                "active TEXT, error TEXT, report_digest TEXT, cancel INTEGER DEFAULT 0)"
            )
            from tokenscope.analysis_common.discovery import install

            install(db)

    @contextmanager
    def connect(self, readonly: bool = False) -> Iterator[sqlite3.Connection]:
        path = self.root / "control.sqlite3"
        db = (
            sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
            if readonly
            else sqlite3.connect(path)
        )
        db.row_factory = sqlite3.Row
        try:
            yield db
            if not readonly:
                db.commit()
        finally:
            db.close()

    def submit(
        self, key: str, intent: str, scope: str, options: str, attempt: int = 1
    ) -> TaskReceipt:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("SELECT * FROM tasks WHERE submission_key=?", (key,)).fetchone()
            if existing:
                if existing["attempt"] != attempt or (
                    existing["intent"],
                    existing["scope"],
                    existing["options"],
                ) != (
                    intent,
                    scope,
                    options,
                ):
                    raise TokenScopeError("IDEMPOTENCY_CONFLICT", "Submission intent differs", 409)
                task_id = existing["id"]
            else:
                task_id = str(uuid4())
                db.execute(
                    "INSERT INTO tasks(id,submission_key,intent,scope,options,attempt,status) "
                    "VALUES (?,?,?,?,?,?, 'queued')",
                    (task_id, key, intent, scope, options, attempt),
                )
        return self.receipt(task_id)

    def row(self, task_id: str) -> dict[str, Any]:
        with self.connect(True) as db:
            row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is None:
            raise TokenScopeError("DIAGNOSTIC_NOT_FOUND", "Unknown diagnostic", 404)
        return dict(row)

    def receipt(self, task_id: str) -> TaskReceipt:
        row = self.row(task_id)
        return TaskReceipt(
            task_id=task_id,
            attempt=row["attempt"],
            status=row["status"],
            active_direction=row["active"],
            error_code=row["error"],
            report_ref=task_id if row["report_digest"] else None,
        )

    def update(self, task_id: str, **values: Any) -> None:
        if not values or set(values) - {"status", "active", "error", "report_digest", "cancel"}:
            raise ValueError("Invalid task update")
        with self.connect() as db:
            db.execute(
                "UPDATE tasks SET " + ",".join(k + "=?" for k in values) + " WHERE id=?",
                (*values.values(), task_id),
            )

    def recover(self) -> None:
        # Called only under the process-wide worker lock. Never salvage unpublished output.
        with self.connect() as db:
            db.execute(
                "UPDATE tasks SET status='interrupted',active=NULL,error='WORKER_RESTARTED' "
                "WHERE status='running'"
            )

    def pending(self) -> str | None:
        with self.connect(True) as db:
            row = db.execute(
                "SELECT id FROM tasks WHERE status='queued' ORDER BY rowid LIMIT 1"
            ).fetchone()
        return row[0] if row else None

    def claim_next(self) -> str | None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT id FROM tasks WHERE status='queued' AND cancel=0 ORDER BY rowid LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            db.execute("UPDATE tasks SET status='running' WHERE id=?", (row[0],))
            return str(row[0])

    def cancel(self, task_id: str) -> TaskReceipt:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row is None:
                raise TokenScopeError("DIAGNOSTIC_NOT_FOUND", "Unknown diagnostic", 404)
            if row[0] == "queued":
                db.execute(
                    "UPDATE tasks SET cancel=1,status='interrupted',error='ANALYSIS_INTERRUPTED' "
                    "WHERE id=?",
                    (task_id,),
                )
            elif row[0] == "running":
                db.execute("UPDATE tasks SET cancel=1 WHERE id=?", (task_id,))
        return self.receipt(task_id)

    def complete(self, task_id: str, digest: str, status: str) -> None:
        # Cancellation and publication have one transactional linearization point.
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status,cancel FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row is None or row[1]:
                raise ExecutionStopped("ANALYSIS_INTERRUPTED")
            if row[0] != "running":
                raise TokenScopeError("TASK_STATE_CHANGED", "Task cannot publish", 409)
            db.execute(
                "UPDATE tasks SET report_digest=?,status=?,active=NULL WHERE id=?",
                (digest, status, task_id),
            )

    def publish(self, task_id: str, workspace: Path, report: dict[str, Any], status: str) -> None:
        (workspace / "report.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )
        files = {}
        for path in sorted(workspace.rglob("*")):
            if path.is_file():
                files[path.relative_to(workspace).as_posix()] = file_digest(path)
                with path.open("rb") as stream:
                    os.fsync(stream.fileno())
        manifest = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
        (workspace / "manifest.json").write_bytes(manifest)
        with (workspace / "manifest.json").open("rb") as stream:
            os.fsync(stream.fileno())
        for directory in [
            *sorted((p for p in workspace.rglob("*") if p.is_dir()), reverse=True),
            workspace,
        ]:
            fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        workspace.rename(self.root / task_id)
        fd = os.open(self.root, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        self.complete(task_id, hashlib.sha256(manifest).hexdigest(), status)

    def result_directory(self, task_id: str) -> Path:
        row = self.row(task_id)
        if not row["report_digest"]:
            raise TokenScopeError("REPORT_NOT_READY", "No published report", 409)
        directory = self.root / str(row["id"])
        manifest = directory / "manifest.json"
        if file_digest(manifest) != row["report_digest"]:
            raise TokenScopeError("REPORT_DIGEST_MISMATCH", "Report seal differs", 409)
        for name, digest in json.loads(manifest.read_bytes()).items():
            path = directory / name
            if (
                path.resolve().parent != directory.resolve()
                and directory.resolve() not in path.resolve().parents
            ):
                raise TokenScopeError("REPORT_DIGEST_MISMATCH", "Unsafe manifest", 409)
            if file_digest(path) != digest:
                raise TokenScopeError("REPORT_DIGEST_MISMATCH", "Report evidence differs", 409)
        return directory


class ResultWriter:
    def __init__(self, directory: Path) -> None:
        self.closed = False
        self.db = sqlite3.connect(directory / "items.sqlite3")
        self.db.execute("CREATE TABLE items(kind TEXT,id TEXT,payload TEXT,PRIMARY KEY(kind,id))")

    def add(self, kind: str, key: str, payload: dict[str, Any]) -> None:
        self.db.execute(
            "INSERT INTO items VALUES (?,?,?)", (kind, key, json.dumps(payload, ensure_ascii=False))
        )

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        try:
            self.db.commit()
        finally:
            self.db.close()


def read_items(
    directory: Path, kind: str, key: str | None, offset: int, limit: int
) -> list[dict[str, Any]]:
    if offset < 0 or not 1 <= limit <= 100:
        raise TokenScopeError("INVALID_ARGUMENT", "Invalid page", 422)
    db = sqlite3.connect((directory / "items.sqlite3").as_uri() + "?mode=ro", uri=True)
    try:
        rows = db.execute(
            "SELECT id,payload FROM items WHERE kind=? "
            + ("AND id=? " if key else "")
            + "ORDER BY rowid LIMIT ? OFFSET ?",
            (kind, *((key,) if key else ()), limit, offset),
        )
        return [{"id": ident, "data": json.loads(payload)} for ident, payload in rows]
    finally:
        db.close()
