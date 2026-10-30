"""MA-only transactional receipts and publication index."""

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from tokenscope.domain import ModelSettings
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import parse_utc
from tokenscope.monitoring.ma.contracts import Receipt, Submit
from tokenscope.monitoring.ma.ingest import connect
from tokenscope.paths import InputRoot


def normalize(binding: Submit) -> Submit:
    data = binding.model_dump()
    for field in ("pre_start", "now_start", "now_end"):
        data[field] = parse_utc(data[field])[1]
    for field in ("pre_file_ref", "now_file_ref"):
        data[field] = "/".join(InputRoot.parts(data[field]))
    return Submit.model_validate(data)


class Store:
    def __init__(self, root: Path, service_id: str) -> None:
        self.root, self.service_id = root, service_id
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / "control.sqlite3"
        with connect(self.path) as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS metadata (id INTEGER PRIMARY KEY,revision INTEGER);
            INSERT OR IGNORE INTO metadata VALUES (1,0);
            CREATE TABLE IF NOT EXISTS runs (seq INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT UNIQUE, submission_key TEXT UNIQUE, binding TEXT NOT NULL,
              state TEXT NOT NULL, error_code TEXT, settings TEXT, revision INTEGER,
              summary TEXT);
            PRAGMA user_version=1;
            """)
            if "error_detail" not in {row[1] for row in db.execute("PRAGMA table_info(runs)")}:
                db.execute("ALTER TABLE runs ADD COLUMN error_detail TEXT")

    def receipt(self, run_id: str) -> Receipt:
        with connect(self.path, readonly=True) as db:
            row = db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            raise TokenScopeError("RUN_NOT_FOUND", "Unknown MA run", 404)
        return Receipt(
            service_instance_id=self.service_id,
            ma_run_id=row["run_id"],
            binding=Submit.model_validate_json(row["binding"]),
            state=row["state"],
            error_code=row["error_code"],
            error_detail=row["error_detail"],
            catalog_revision=str(row["revision"]) if row["revision"] is not None else None,
        )

    def find(self, key: str) -> Receipt | None:
        with connect(self.path, readonly=True) as db:
            row = db.execute("SELECT run_id FROM runs WHERE submission_key=?", (key,)).fetchone()
        return self.receipt(row[0]) if row else None

    def enqueue(self, binding: Submit) -> Receipt:
        binding = normalize(binding)
        with connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT run_id,binding FROM runs WHERE submission_key=?", (binding.submission_key,)
            ).fetchone()
            if row:
                if Submit.model_validate_json(row["binding"]) != binding:
                    raise TokenScopeError(
                        "SUBMISSION_CONFLICT", "Submission key binding differs", 409
                    )
                run_id = row["run_id"]
            else:
                run_id = str(uuid4())
                db.execute(
                    "INSERT INTO runs(run_id,submission_key,binding,state) VALUES (?,?,?,'queued')",
                    (run_id, binding.submission_key, binding.model_dump_json()),
                )
        return self.receipt(run_id)

    def queued(self) -> Receipt | None:
        with connect(self.path, readonly=True) as db:
            row = db.execute(
                "SELECT run_id FROM runs WHERE state='queued' ORDER BY seq LIMIT 1"
            ).fetchone()
        return self.receipt(row[0]) if row else None

    def claim(self, run_id: str, settings: ModelSettings) -> None:
        with connect(self.path) as db:
            changed = db.execute(
                "UPDATE runs SET state='running',settings=? WHERE run_id=? AND state='queued'",
                (settings.model_dump_json(), run_id),
            ).rowcount
            if changed != 1:
                raise TokenScopeError("CLAIM_CONFLICT", "MA task is not queued", 409)

    def settings(self, run_id: str) -> ModelSettings:
        with connect(self.path, readonly=True) as db:
            row = db.execute("SELECT settings FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None or row[0] is None:
            raise TokenScopeError("SNAPSHOT_NOT_READY", "MA configuration snapshot missing", 409)
        return ModelSettings.model_validate_json(row[0])

    def fail(
        self, run_id: str, code: str, *, interrupted: bool = False, detail: str | None = None
    ) -> None:
        with connect(self.path) as db:
            db.execute(
                "UPDATE runs SET state=?,error_code=?,error_detail=? WHERE run_id=? "
                "AND state IN ('queued','running')",
                ("interrupted" if interrupted else "failed", code, detail, run_id),
            )

    def complete(self, run_id: str, summary: dict[str, Any]) -> None:
        with connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT state FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if row and row[0] == "completed":
                return
            if not row or row[0] != "running":
                raise TokenScopeError("PUBLICATION_CONFLICT", "MA task is not running", 409)
            db.execute("UPDATE metadata SET revision=revision+1 WHERE id=1")
            revision = db.execute("SELECT revision FROM metadata WHERE id=1").fetchone()[0]
            db.execute(
                "UPDATE runs SET state='completed',summary=?,revision=? WHERE run_id=?",
                (json.dumps(summary, allow_nan=False), revision, run_id),
            )

    def summary(self, run_id: str) -> dict[str, Any]:
        with connect(self.path, readonly=True) as db:
            row = db.execute("SELECT state,summary FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            raise TokenScopeError("RUN_NOT_FOUND", "Unknown MA run", 404)
        if row[0] != "completed":
            raise TokenScopeError("RESULT_NOT_READY", "MA result is not published", 409)
        result: dict[str, Any] = json.loads(row[1])
        return result
