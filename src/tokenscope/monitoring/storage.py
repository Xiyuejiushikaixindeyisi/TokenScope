"""SQLite control state and per-input request staging. No successful result is fabricated."""

import fcntl
import json
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from tokenscope.domain import (
    DEFAULT_SETTINGS,
    ModelSettings,
    Quality,
    RunState,
    RunSubmission,
    SettingsUpdate,
    capability,
)
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import CsvBatchReader, RequestRecord, RowIssue
from tokenscope.monitoring import publications
from tokenscope.monitoring.rules import RuleUpdate
from tokenscope.monitoring.view_models import canonical
from tokenscope.paths import InputRoot

DB_VERSION = 3


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f") + "000Z"


class ControlStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        # Serialize backup creation across service/CLI startup; never leave a partial backup.
        with path.with_suffix(".migration.lock").open("a") as migration_lock:
            fcntl.flock(migration_lock, fcntl.LOCK_EX)
            if path.exists():
                with self.connect() as old:
                    old_version = old.execute("PRAGMA user_version").fetchone()[0]
                    backup = path.with_name(f"{path.stem}.schema{old_version}.backup.sqlite3")
                    if old_version in (1, 2) and not backup.exists():
                        temporary = backup.with_name(backup.name + "." + str(uuid4()) + ".pending")
                        try:
                            target = sqlite3.connect(temporary)
                            try:
                                old.backup(target)
                                if target.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                                    raise OSError("Invalid migration backup")
                            finally:
                                target.close()
                            with temporary.open("rb") as stream:
                                os.fsync(stream.fileno())
                            temporary.rename(backup)
                            parent = os.open(path.parent, os.O_RDONLY)
                            try:
                                os.fsync(parent)
                            finally:
                                os.close(parent)
                        finally:
                            temporary.unlink(missing_ok=True)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1, 2, DB_VERSION):
                raise TokenScopeError(
                    "UNSUPPORTED_DB_VERSION", "Control database version is unsupported"
                )
            db.execute("""CREATE TABLE IF NOT EXISTS model_settings (
                model_id TEXT NOT NULL, revision INTEGER NOT NULL, settings_json TEXT NOT NULL,
                PRIMARY KEY (model_id, revision))""")
            db.execute("""CREATE TABLE IF NOT EXISTS analysis_runs (
                queue_sequence INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT UNIQUE NOT NULL,
                file_ref TEXT NOT NULL, model_id TEXT NOT NULL, status TEXT NOT NULL,
                created_at TEXT NOT NULL, started_at TEXT, finished_at TEXT,
                settings_json TEXT, error_code TEXT)""")
            db.execute("""CREATE TABLE IF NOT EXISTS threshold_rules (
                appid TEXT,model_id TEXT,rule_id TEXT,revision INTEGER,rule_json TEXT,
                PRIMARY KEY(appid,model_id,rule_id,revision))""")
            db.execute("""CREATE TABLE IF NOT EXISTS run_snapshots (
                run_id TEXT PRIMARY KEY,rules_json TEXT NOT NULL,runtime_json TEXT)""")
            db.execute("""CREATE TABLE IF NOT EXISTS completed_results (
                run_id TEXT PRIMARY KEY,summary_json TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS outbox (
                event_id TEXT PRIMARY KEY,payload_json TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS run_signals (
                run_id TEXT,event_id TEXT REFERENCES outbox(event_id),
                PRIMARY KEY(run_id,event_id))""")
            for settings in DEFAULT_SETTINGS.values():
                db.execute(
                    "INSERT OR IGNORE INTO model_settings VALUES (?, ?, ?)",
                    (settings.model_id, settings.revision, settings.model_dump_json()),
                )
            publications.initialize(db)
            db.execute(f"PRAGMA user_version = {DB_VERSION}")

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA foreign_keys = ON")
            db.execute("PRAGMA synchronous = FULL")
            with db:
                yield db
        finally:
            db.close()

    def settings(self, model_id: str, db: sqlite3.Connection | None = None) -> ModelSettings:
        if db is None:
            with self.connect() as connection:
                return self.settings(model_id, connection)
        row = db.execute(
            "SELECT settings_json FROM model_settings WHERE model_id=? "
            "ORDER BY revision DESC LIMIT 1",
            (model_id,),
        ).fetchone()
        if row is None:
            raise TokenScopeError("MODEL_NOT_FOUND", "Unknown model", 404)
        return ModelSettings.model_validate_json(row[0])

    def update_settings(self, model_id: str, update: SettingsUpdate) -> ModelSettings:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            current = self.settings(model_id, db)
            if current.revision != update.expected_revision:
                raise TokenScopeError(
                    "REVISION_CONFLICT", "Reload model settings before updating", 409
                )
            values = current.model_dump()
            changes = update.changes.model_dump(exclude_unset=True)
            if not changes:
                raise TokenScopeError("EMPTY_UPDATE", "At least one setting must change")
            values.update(changes)
            values["revision"] = current.revision + 1
            try:
                updated = ModelSettings.model_validate(values)
            except ValidationError as exc:
                raise TokenScopeError("INVALID_SETTINGS", "Invalid model settings") from exc
            db.execute(
                "INSERT INTO model_settings VALUES (?, ?, ?)",
                (model_id, updated.revision, updated.model_dump_json()),
            )
        return updated

    def find_submission(self, submission: RunSubmission) -> RunState | None:
        if submission.submission_key is None:
            return None
        with self.connect() as db:
            row = db.execute(
                "SELECT * FROM submission_receipts WHERE submission_key=?",
                (submission.submission_key,),
            ).fetchone()
        if row is None:
            return None
        expected = canonical(
            dict(file_ref=submission.file_ref, model_id=submission.model_id)
        ).decode()
        if row["request_json"] != expected:
            raise TokenScopeError(
                "SUBMISSION_KEY_CONFLICT", "Submission key has different input", 409
            )
        return self.run(row["run_id"])

    def enqueue(self, submission: RunSubmission) -> RunState:
        """Atomically persist receipt and run; public validation happens before this transaction."""
        InputRoot.parts(submission.file_ref)
        run_id = str(uuid4())
        request_json = canonical(
            dict(file_ref=submission.file_ref, model_id=submission.model_id)
        ).decode()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if submission.submission_key is not None:
                row = db.execute(
                    "SELECT * FROM submission_receipts WHERE submission_key=?",
                    (submission.submission_key,),
                ).fetchone()
                if row is not None:
                    if row["request_json"] != request_json:
                        raise TokenScopeError(
                            "SUBMISSION_KEY_CONFLICT", "Submission key has different input", 409
                        )
                    run_id = row["run_id"]
                    return self.run(run_id)
            self.settings(submission.model_id, db)
            db.execute(
                "INSERT INTO analysis_runs (run_id,file_ref,model_id,status,created_at) "
                "VALUES (?,?,?,'queued',?)",
                (run_id, submission.file_ref, submission.model_id, utc_now()),
            )
            if submission.submission_key is not None:
                db.execute(
                    "INSERT INTO submission_receipts VALUES(?,?,?)",
                    (submission.submission_key, request_json, run_id),
                )
        return self.run(run_id)

    def claim_next(self) -> RunState | None:
        """One active run globally; freeze latest model revision at claim, not enqueue."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM analysis_runs WHERE status='running'").fetchone():
                return None
            row = db.execute("""SELECT * FROM analysis_runs WHERE status='queued'
                                ORDER BY queue_sequence LIMIT 1""").fetchone()
            if row is None:
                return None
            settings = self.settings(row["model_id"], db)
            rules = self.rules(row["model_id"], db)
            db.execute(
                "INSERT INTO run_snapshots VALUES (?,?,NULL)", (row["run_id"], json.dumps(rules))
            )
            supported = capability(settings).executable
            db.execute(
                """UPDATE analysis_runs SET status=?, started_at=?, finished_at=?,
                       settings_json=?, error_code=? WHERE run_id=?""",
                (
                    "running" if supported else "failed",
                    utc_now(),
                    None if supported else utc_now(),
                    settings.model_dump_json(),
                    None if supported else "UNSUPPORTED_CACHE_MODE",
                    row["run_id"],
                ),
            )
            run_id = str(row["run_id"])
            if not supported:
                terminal = db.execute(
                    "SELECT * FROM analysis_runs WHERE run_id=?", (run_id,)
                ).fetchone()
                publications.append_event(
                    db,
                    "run_terminal",
                    run_id,
                    terminal["model_id"],
                    "failed",
                    terminal["finished_at"],
                    terminal["error_code"],
                )
        return self.run(run_id)

    def rules(
        self, model_id: str | None = None, db: sqlite3.Connection | None = None
    ) -> list[dict[str, Any]]:
        if db is None:
            with self.connect() as connection:
                return self.rules(model_id, connection)
        rows = db.execute(
            """SELECT r.rule_json FROM threshold_rules r WHERE
            r.revision=(SELECT max(s.revision) FROM threshold_rules s WHERE
                r.appid=s.appid AND r.model_id=s.model_id AND r.rule_id=s.rule_id)
            AND (? IS NULL OR r.model_id=?) ORDER BY r.model_id,r.appid,r.rule_id""",
            (model_id, model_id),
        )
        return [json.loads(row[0]) for row in rows]

    def update_rule(self, update: RuleUpdate) -> dict[str, Any]:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self.settings(update.model_id, db)
            current = db.execute(
                """SELECT coalesce(max(revision),0) FROM threshold_rules
                WHERE appid=? AND model_id=? AND rule_id=?""",
                (update.appid, update.model_id, update.rule_id),
            ).fetchone()[0]
            if current != update.expected_revision:
                raise TokenScopeError(
                    "REVISION_CONFLICT", "Reload threshold rule before updating", 409
                )
            rule = update.model_dump(exclude={"expected_revision"})
            rule["revision"] = current + 1
            db.execute(
                "INSERT INTO threshold_rules VALUES (?,?,?,?,?)",
                (update.appid, update.model_id, update.rule_id, current + 1, json.dumps(rule)),
            )
            db.execute("UPDATE service_metadata SET rules_revision=rules_revision+1 WHERE id=1")
        return rule

    def snapshot(self, run_id: str) -> dict[str, Any]:
        with self.connect() as db:
            row = db.execute("SELECT * FROM run_snapshots WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            raise TokenScopeError("SNAPSHOT_NOT_READY", "Run has not started", 409)
        return dict(
            rules=json.loads(row["rules_json"]),
            runtime=json.loads(row["runtime_json"]) if row["runtime_json"] else None,
        )

    def bind_runtime(self, run_id: str, runtime: dict[str, Any]) -> None:
        with self.connect() as db:
            changed = db.execute(
                """UPDATE run_snapshots SET runtime_json=? WHERE run_id=?
                AND runtime_json IS NULL AND EXISTS (SELECT 1 FROM analysis_runs
                WHERE run_id=? AND status='running')""",
                (json.dumps(runtime), run_id, run_id),
            ).rowcount
            if changed != 1:
                raise TokenScopeError(
                    "INVALID_RUN_TRANSITION", "Runtime snapshot already bound", 409
                )

    def complete(
        self,
        run_id: str,
        summary: dict[str, Any],
        signals: list[dict[str, Any]],
        projection: dict[str, Any] | None = None,
    ) -> None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            status = "completed" if summary["quality"]["valid_requests"] else "no_valid_rows"
            changed = db.execute(
                """UPDATE analysis_runs SET status=?,finished_at=?
                WHERE run_id=? AND status='running' """,
                (status, utc_now(), run_id),
            ).rowcount
            if changed != 1:
                raise TokenScopeError(
                    "INVALID_RUN_TRANSITION", "Only running tasks can complete", 409
                )
            db.execute("INSERT INTO completed_results VALUES (?,?)", (run_id, json.dumps(summary)))
            for signal in signals:
                db.execute(
                    "INSERT OR IGNORE INTO outbox VALUES (?,?)",
                    (signal["event_id"], json.dumps(signal)),
                )
                db.execute("INSERT INTO run_signals VALUES (?,?)", (run_id, signal["event_id"]))

            if projection is not None:
                row = db.execute(
                    "SELECT finished_at,file_ref FROM analysis_runs WHERE run_id=?", (run_id,)
                ).fetchone()
                publications.publish(
                    db, run_id, summary, projection, row["finished_at"], row["file_ref"]
                )

    def result(self, run_id: str) -> dict[str, Any]:
        self.run(run_id)
        with self.connect() as db:
            row = db.execute(
                "SELECT summary_json FROM completed_results WHERE run_id=?", (run_id,)
            ).fetchone()
        if row is None:
            raise TokenScopeError("RESULT_NOT_READY", "Run has no complete result", 409)
        result: dict[str, Any] = json.loads(row[0])
        return result

    def signals(self, run_id: str) -> list[dict[str, Any]]:
        self.result(run_id)
        with self.connect() as db:
            return [
                json.loads(row[0])
                for row in db.execute(
                    """SELECT payload_json FROM outbox
                JOIN run_signals USING(event_id) WHERE run_id=? ORDER BY event_id""",
                    (run_id,),
                )
            ]

    def run(self, run_id: str) -> RunState:
        with self.connect() as db:
            row = db.execute("SELECT * FROM analysis_runs WHERE run_id=?", (run_id,)).fetchone()
            snapshot = db.execute(
                "SELECT * FROM run_snapshots WHERE run_id=?", (run_id,)
            ).fetchone()
            result = db.execute(
                "SELECT summary_json FROM completed_results WHERE run_id=?", (run_id,)
            ).fetchone()
        if row is None:
            raise TokenScopeError("RUN_NOT_FOUND", "Unknown analysis run", 404)
        values = dict(row)
        values.pop("queue_sequence")
        settings_json = values.pop("settings_json")
        values["settings"] = json.loads(settings_json) if settings_json else None
        values["snapshot"] = (
            dict(
                rules=json.loads(snapshot["rules_json"]),
                runtime=json.loads(snapshot["runtime_json"]) if snapshot["runtime_json"] else None,
            )
            if snapshot
            else None
        )
        values["result"] = json.loads(result[0]) if result else None
        return RunState.model_validate(values)

    def fail(self, run_id: str, code: str, *, interrupted: bool = False) -> RunState:
        if not code or not all(c.isupper() or c.isdigit() or c == "_" for c in code):
            raise ValueError("Error code must be a safe identifier")
        with self.connect() as db:
            changed = db.execute(
                """UPDATE analysis_runs SET status=?,finished_at=?,error_code=?
                                 WHERE run_id=? AND status='running'""",
                ("interrupted" if interrupted else "failed", utc_now(), code, run_id),
            ).rowcount
            if changed != 1:
                raise TokenScopeError("INVALID_RUN_TRANSITION", "Only a running task can fail", 409)
            terminal = db.execute(
                "SELECT * FROM analysis_runs WHERE run_id=?", (run_id,)
            ).fetchone()
            publications.append_event(
                db,
                "run_terminal",
                run_id,
                terminal["model_id"],
                terminal["status"],
                terminal["finished_at"],
                code,
            )
        return self.run(run_id)


class RawRequestStore:
    """A new database for a single input; partial failures remain explicitly incomplete."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation prevents a retry from clearing existing evidence.
        with path.open("xb"):
            pass
        with self.connect() as db:
            db.execute("PRAGMA journal_mode = WAL")
            db.execute("""CREATE TABLE request_records (
                source_record_index INTEGER PRIMARY KEY, physical_line_start INTEGER NOT NULL,
                physical_line_end INTEGER NOT NULL, hash_id TEXT NOT NULL, appid TEXT NOT NULL,
                time_ns INTEGER NOT NULL, time_utc TEXT NOT NULL,
                completion_tokens INTEGER NOT NULL,
                request_input TEXT NOT NULL, duplicate_hash_id INTEGER NOT NULL)""")
            db.execute("CREATE INDEX record_hash ON request_records(hash_id)")
            db.execute(
                "CREATE INDEX replay_order ON request_records(appid,time_ns,source_record_index)"
            )
            db.execute("""CREATE TABLE row_errors (source_record_index INTEGER PRIMARY KEY,
                physical_line_start INTEGER, physical_line_end INTEGER, code TEXT, field TEXT)""")
            db.execute("""CREATE TABLE input_status (started INTEGER NOT NULL,
                       complete INTEGER NOT NULL, quality_json TEXT)""")
            db.execute("INSERT INTO input_status VALUES (0,0,NULL)")

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def ingest(self, snapshot: Path, reader: CsvBatchReader) -> Quality:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("UPDATE input_status SET started=1 WHERE started=0").rowcount != 1:
                raise TokenScopeError(
                    "INPUT_ALREADY_STARTED", "Use a new staging store for retry", 409
                )
        read = valid = invalid = duplicates = 0
        with self.connect() as db, snapshot.open("rb") as stream:
            for batch in reader.batches(stream):
                with db:
                    for record in batch:
                        read += 1
                        if isinstance(record, RowIssue):
                            invalid += 1
                            db.execute(
                                "INSERT INTO row_errors VALUES (?,?,?,?,?)",
                                tuple(asdict(record).values()),
                            )
                        else:
                            valid += 1
                            duplicate = (
                                db.execute(
                                    "SELECT 1 FROM request_records WHERE hash_id=? LIMIT 1",
                                    (record.hash_id,),
                                ).fetchone()
                                is not None
                            )
                            duplicates += int(duplicate)
                            db.execute(
                                "INSERT INTO request_records VALUES (?,?,?,?,?,?,?,?,?,?)",
                                (*asdict(record).values(), int(duplicate)),
                            )
            quality = Quality(
                records_read=read,
                valid_requests=valid,
                skipped_rows=invalid,
                duplicate_hash_id_rows=duplicates,
            )
            db.execute(
                "UPDATE input_status SET complete=1,quality_json=?", (quality.model_dump_json(),)
            )
        return quality

    def replay_records(self) -> Iterator[RequestRecord]:
        with self.connect() as db:
            if not db.execute("SELECT complete FROM input_status").fetchone()[0]:
                raise TokenScopeError("INPUT_INCOMPLETE", "Input validation did not complete", 409)
            for row in db.execute(
                "SELECT * FROM request_records ORDER BY appid,time_ns,source_record_index"
            ):
                values = dict(row)
                values.pop("duplicate_hash_id")
                yield RequestRecord(**values)
