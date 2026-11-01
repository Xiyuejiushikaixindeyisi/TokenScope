"""Append-only diagnostic terminal outbox and snapshot report discovery (v1)."""

import hashlib
import json
import re
import sqlite3
from typing import Any
from uuid import uuid4

from tokenscope.analysis_common.contracts import AnalysisScope
from tokenscope.analysis_common.storage import DiagnosticStore
from tokenscope.analysis_common.wire import to_wire
from tokenscope.errors import TokenScopeError

VERSION = "diagnostics-discovery-1"
TERMINAL = "'ready','partial','empty','failed','interrupted'"


def install(db: sqlite3.Connection) -> None:
    """Run inside store initialization, before workers can change task state."""
    db.execute("BEGIN IMMEDIATE")
    db.execute("CREATE TABLE IF NOT EXISTS discovery_meta (id INTEGER PRIMARY KEY, epoch TEXT)")
    db.execute("INSERT OR IGNORE INTO discovery_meta VALUES (1,?)", (str(uuid4()),))
    db.execute(
        "CREATE TABLE IF NOT EXISTS diagnostic_terminals ("
        "seq INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT UNIQUE NOT NULL, "
        "status TEXT NOT NULL, intent TEXT NOT NULL, scope TEXT NOT NULL, "
        "report_digest TEXT, error TEXT, terminal_at TEXT, published_at TEXT, "
        "legacy INTEGER NOT NULL DEFAULT 0)"
    )
    # Legacy timestamps and publication ordering are unknown; never infer them from mtime.
    db.execute(
        "INSERT OR IGNORE INTO diagnostic_terminals "
        "(task_id,status,intent,scope,report_digest,error,legacy) "
        "SELECT id,status,intent,scope,report_digest,error,1 FROM tasks "
        f"WHERE status IN ({TERMINAL}) ORDER BY rowid"
    )
    db.execute(
        "CREATE TRIGGER IF NOT EXISTS diagnostic_terminal_outbox AFTER UPDATE ON tasks "
        f"WHEN NEW.status IN ({TERMINAL}) AND OLD.status NOT IN ({TERMINAL}) BEGIN "
        "INSERT INTO diagnostic_terminals "
        "(task_id,status,intent,scope,report_digest,error,terminal_at,published_at) VALUES "
        "(NEW.id,NEW.status,NEW.intent,NEW.scope,NEW.report_digest,NEW.error,"
        "strftime('%Y-%m-%dT%H:%M:%fZ','now'),"
        "CASE WHEN NEW.report_digest IS NOT NULL THEN "
        "strftime('%Y-%m-%dT%H:%M:%fZ','now') ELSE NULL END); END"
    )


class Discovery:
    def __init__(self, store: DiagnosticStore, instance_id: str) -> None:
        self.store, self.instance_id = store, instance_id

    def _identity(self, db: sqlite3.Connection) -> tuple[str, int]:
        epoch = db.execute("SELECT epoch FROM discovery_meta WHERE id=1").fetchone()[0]
        high = db.execute("SELECT COALESCE(MAX(seq),0) FROM diagnostic_terminals").fetchone()[0]
        return f"{self.instance_id}:{epoch}", high

    @staticmethod
    def _position(cursor: str, identity: str, high: int) -> int:
        prefix, sep, value = cursor.rpartition(":")
        if not sep or prefix != identity:
            raise TokenScopeError("DISCOVERY_RESET_REQUIRED", "Instance or journal changed", 409)
        if not re.fullmatch(r"0|[1-9][0-9]{0,18}", value) or int(value) > high:
            raise TokenScopeError("DISCOVERY_RESET_REQUIRED", "Invalid or future cursor", 409)
        return int(value)

    def _entry(self, row: sqlite3.Row) -> dict[str, Any]:
        intent = json.loads(row["intent"])
        scope = AnalysisScope.model_validate_json(row["scope"])
        kind = intent.get("kind", "analysis")
        selection = intent.get("request", {}).get("selection", {})
        directions = (
            [
                d
                for d, flag in (
                    ("low_hit", "enable_low_hit"),
                    ("token_content", "enable_token_content"),
                )
                if selection.get(flag)
            ]
            if kind == "analysis"
            else []
        )
        binding = {
            "appid": scope.appid,
            "model_id": scope.source.model_id,
            "common_name": scope.source.common_name,
            "source_kind": "user_v2" if scope.source.user_run_id else "base",
        }
        binding_id = hashlib.sha256(
            json.dumps(binding, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        return {
            "task_id": row["task_id"],
            "task_kind": kind,
            "parent_task_id": intent.get("parent"),
            "plan_refs": intent.get("plan_refs", []),
            "status": row["status"],
            "error_code": row["error"],
            "report_published": row["report_digest"] is not None,
            "report_ref": row["task_id"] if row["report_digest"] else None,
            "report_digest": row["report_digest"],
            "scope_id": scope.scope_id,
            "scope": to_wire(scope),
            "binding": binding,
            "binding_id": binding_id,
            "directions": directions,
            "sequence": str(row["seq"]),
            "terminal_at": row["terminal_at"],
            "published_at": row["published_at"],
            "analysis_completed_at": row["published_at"],
            "legacy": bool(row["legacy"]),
            "default_eligible": kind == "analysis"
            and row["status"] == "ready"
            and row["report_digest"] is not None
            and not row["legacy"],
        }

    def catalog(
        self, snapshot: str | None = None, after: str = "0", limit: int = 50
    ) -> dict[str, Any]:
        if not 1 <= limit <= 100 or not re.fullmatch(r"0|[1-9][0-9]{0,18}", after):
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid discovery page", 422)
        with self.store.connect(True) as db:
            db.execute("BEGIN")
            identity, high = self._identity(db)
            cutoff = high if snapshot is None else self._position(snapshot, identity, high)
            if int(after) > cutoff or (snapshot is None and after != "0"):
                raise TokenScopeError("INVALID_ARGUMENT", "Page requires matching snapshot", 422)
            # Immutable rows and cutoff make pagination stable across later publications.
            rows = db.execute(
                "SELECT * FROM diagnostic_terminals WHERE seq<=? AND seq>? "
                "AND report_digest IS NOT NULL AND json_extract(intent,'$.kind')='analysis' "
                "ORDER BY seq LIMIT ?",
                (cutoff, int(after), limit + 1),
            ).fetchall()
            entries = [self._entry(row) for row in rows[:limit]]
            defaults: dict[tuple[str, str], dict[str, str]] = {}
            for row in db.execute(
                "SELECT * FROM diagnostic_terminals WHERE seq<=? AND status='ready' "
                "AND report_digest IS NOT NULL AND legacy=0 "
                "AND json_extract(intent,'$.kind')='analysis' ORDER BY seq",
                (cutoff,),
            ):
                entry = self._entry(row)
                for direction in entry["directions"]:
                    defaults[(entry["binding_id"], direction)] = {
                        "binding_id": entry["binding_id"],
                        "direction": direction,
                        "task_id": entry["task_id"],
                        "sequence": entry["sequence"],
                    }
        return {
            "version": VERSION,
            "service_instance_id": self.instance_id,
            "snapshot": f"{identity}:{cutoff}",
            "event_cursor": f"{identity}:{cutoff}",
            "items": entries,
            "defaults": list(defaults.values()),
            "next_after": entries[-1]["sequence"] if len(rows) > limit else None,
        }

    def events(self, cursor: str, limit: int = 100) -> dict[str, Any]:
        if not 1 <= limit <= 100:
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid event limit", 422)
        with self.store.connect(True) as db:
            db.execute("BEGIN")
            identity, high = self._identity(db)
            after = self._position(cursor, identity, high)
            rows = db.execute(
                "SELECT * FROM diagnostic_terminals WHERE seq>? ORDER BY seq LIMIT ?",
                (after, limit),
            ).fetchall()
            events = []
            for row in rows:
                entry = self._entry(row)
                entry.pop("scope")
                events.append({"event_id": f"{identity}:{row['seq']}", **entry})
        return {
            "version": VERSION,
            "service_instance_id": self.instance_id,
            "items": events,
            "cursor": events[-1]["event_id"] if events else cursor,
        }

    def terminal(self, task_id: str) -> dict[str, Any]:
        self.store.row(task_id)  # Distinguish an active task from an unknown task.
        with self.store.connect(True) as db:
            row = db.execute(
                "SELECT * FROM diagnostic_terminals WHERE task_id=?", (task_id,)
            ).fetchone()
        return {
            "version": VERSION,
            "service_instance_id": self.instance_id,
            "terminal": self._entry(row) if row else None,
        }
