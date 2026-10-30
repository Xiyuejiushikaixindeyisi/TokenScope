"""Independent user control store. Source control3 and sealed facts are never migrated."""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from tokenscope.errors import TokenScopeError


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


class Store:
    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / "control.sqlite3"
        with self.connect() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise TokenScopeError("STORAGE_UNAVAILABLE", "Unsupported user schema", 503)
            db.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                  id TEXT PRIMARY KEY, submission_key TEXT UNIQUE NOT NULL,
                  intent TEXT NOT NULL, base_id TEXT UNIQUE, common_name TEXT NOT NULL,
                  model_id TEXT NOT NULL, state TEXT NOT NULL, revision TEXT, error TEXT);
                CREATE TABLE IF NOT EXISTS scenarios (
                  id TEXT, revision TEXT, payload TEXT NOT NULL, PRIMARY KEY(id,revision));
                CREATE TABLE IF NOT EXISTS evaluations (
                  id TEXT PRIMARY KEY, submission_key TEXT UNIQUE NOT NULL,
                  intent TEXT NOT NULL, payload TEXT NOT NULL);
                PRAGMA user_version=1;
            """)

    @contextmanager
    def connect(self, *, readonly: bool = False) -> Iterator[sqlite3.Connection]:
        db = (
            sqlite3.connect(
                self.path.as_uri() + ("?mode=ro" if readonly else "?mode=rw"), uri=True, timeout=30
            )
            if readonly or self.path.exists()
            else sqlite3.connect(self.path)
        )
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def run(self, run_id: str) -> dict[str, Any]:
        with self.connect(readonly=True) as db:
            row = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if row is None:
            raise TokenScopeError("RESOURCE_NOT_FOUND", "Unknown user run", 404)
        return dict(row)

    def update(self, run_id: str, **fields: Any) -> None:
        if not fields or not set(fields) <= {"base_id", "state", "revision", "error"}:
            raise ValueError("Invalid control update")
        with self.connect() as db:
            db.execute(
                "UPDATE runs SET " + ",".join(f"{k}=?" for k in fields) + " WHERE id=?",
                (*fields.values(), run_id),
            )
