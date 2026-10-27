"""Publication writes participate in the caller's transaction; reads use short snapshots."""

import json
import sqlite3
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.view_models import SCHEMA, canonical, data_range, page


def initialize(db: sqlite3.Connection) -> None:
    db.execute(
        "CREATE TABLE IF NOT EXISTS service_metadata(id INTEGER PRIMARY KEY CHECK(id=1),ins"
        "tance_id TEXT NOT NULL,ready INTEGER NOT NULL,event_floor INTEGER NOT NULL DEFAULT"
        " 0,rules_revision INTEGER NOT NULL DEFAULT 0)"
    )
    pending = db.execute("SELECT count(*) FROM completed_results").fetchone()[0]
    db.execute(
        "INSERT OR IGNORE INTO service_metadata(id,instance_id,ready) VALUES(1,?,?)",
        (str(uuid4()), int(not pending)),
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS ui_events(seq INTEGER PRIMARY KEY AUTOINCREMENT,kind TE"
        "XT NOT NULL,run_id TEXT NOT NULL UNIQUE,payload TEXT NOT NULL,created_at TEXT NOT "
        "NULL)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS publications(run_id TEXT PRIMARY KEY,model_id TEXT,publ"
        "ish_seq INTEGER UNIQUE,published_at TEXT,status TEXT,range_json TEXT,group_count I"
        "NTEGER,input_sha256 TEXT,source_label TEXT)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS publication_groups(run_id TEXT,appid TEXT,model_id TEXT"
        ",min_ns INTEGER,max_ns INTEGER,publish_seq INTEGER,PRIMARY KEY(run_id,appid))"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS pub_group_latest ON publication_groups(appid,model_id,m"
        "ax_ns DESC,publish_seq DESC)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS active_groups(appid TEXT,model_id TEXT,run_id TEXT,max_"
        "ns INTEGER,publish_seq INTEGER,PRIMARY KEY(appid,model_id))"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS submission_receipts(submission_key TEXT PRIMARY KEY,req"
        "uest_json TEXT NOT NULL,run_id TEXT UNIQUE NOT NULL REFERENCES analysis_runs(run_i"
        "d))"
    )


def identity(db: sqlite3.Connection, require_ready: bool = True) -> dict[str, str]:
    row = db.execute("SELECT * FROM service_metadata WHERE id=1").fetchone()
    if require_ready and not row["ready"]:
        raise TokenScopeError("VIEW_INDEX_NOT_READY", "View backfill is not complete", 503)
    return dict(service_instance_id=row["instance_id"], view_schema_version=SCHEMA)


def append_event(
    db: sqlite3.Connection,
    kind: str,
    run_id: str,
    model_id: str,
    status: str,
    when: str,
    error_code: str | None = None,
) -> int:
    cur = db.execute(
        "INSERT INTO ui_events(kind,run_id,payload,created_at) VALUES(?,?,?,?)",
        (kind, run_id, "{}", when),
    )
    seq = int(cur.lastrowid or 0)
    value: dict[str, Any] = {
        **identity(db, False),
        "run_id": run_id,
        "model_id": model_id,
        "status": status,
    }
    if kind == "result_published":
        value.update(publish_seq=str(seq), published_at=when)
    else:
        value.update(event_seq=str(seq), error_code=error_code, finished_at=when)
    db.execute("UPDATE ui_events SET payload=? WHERE seq=?", (canonical(value).decode(), seq))
    return seq


def publish(
    db: sqlite3.Connection,
    run_id: str,
    summary: dict[str, Any],
    projection: dict[str, Any],
    when: str,
    source_label: str,
) -> None:
    if db.execute("SELECT 1 FROM publications WHERE run_id=?", (run_id,)).fetchone():
        return
    status = "completed" if summary["quality"]["valid_requests"] else "no_valid_rows"
    model = summary["model_id"]
    seq = append_event(db, "result_published", run_id, model, status, when)
    db.execute(
        "INSERT INTO publications VALUES(?,?,?,?,?,?,?,?,?)",
        (
            run_id,
            model,
            seq,
            when,
            status,
            json.dumps(projection["file_data_range_utc"]),
            len(projection["groups"]),
            summary["input_sha256"],
            source_label,
        ),
    )
    for group in projection["groups"]:
        db.execute(
            "INSERT INTO publication_groups VALUES(?,?,?,?,?,?)",
            (run_id, group["appid"], model, group["min_ns"], group["max_ns"], seq),
        )
        db.execute(
            (
                "INSERT INTO active_groups VALUES(?,?,?,?,?) ON CONFLICT(appid,model_id) DO UPD"
                "ATE SET run_id=excluded.run_id,max_ns=excluded.max_ns,publish_seq=excluded.pub"
                "lish_seq WHERE (excluded.max_ns,excluded.publish_seq)>(active_groups.max_ns,ac"
                "tive_groups.publish_seq)"
            ),
            (group["appid"], model, run_id, group["max_ns"], seq),
        )


def highwater(db: sqlite3.Connection) -> int:
    row = db.execute("SELECT seq FROM sqlite_sequence WHERE name='ui_events'").fetchone()
    return int(row[0]) if row else 0


class PublicationRepository:
    def __init__(self, control: Any) -> None:
        self.control = control

    def catalog(
        self,
        appid: str | None = None,
        model_id: str | None = None,
        offset: int = 0,
        limit: int = 100,
        revision: int | None = None,
        *,
        runs: bool = False,
    ) -> dict[str, Any]:
        page(offset, limit, 0)
        with self.control.connect() as db:
            db.execute("BEGIN")
            ident = identity(db)
            current = db.execute(
                "SELECT coalesce(max(publish_seq),0) FROM publications"
            ).fetchone()[0]
            if (offset and revision is None) or (revision is not None and revision != current):
                raise TokenScopeError(
                    "CATALOG_REVISION_CHANGED", "Reload the complete catalog", 409
                )
            if runs:
                query = (
                    " FROM publications p WHERE (? IS NULL OR model_id=?) AND (? IS NULL OR EXI"
                    "STS(SELECT 1 FROM publication_groups g WHERE g.run_id=p.run_id AND g.appid"
                    "=?))"
                )
                args = (model_id, model_id, appid, appid)
                total = db.execute("SELECT count(*)" + query, args).fetchone()[0]
                rows = db.execute(
                    "SELECT *" + query + " ORDER BY publish_seq DESC LIMIT ? OFFSET ?",
                    (*args, limit, min(offset, 2**63 - 1)),
                )
                items = [
                    dict(
                        run_id=r["run_id"],
                        model_id=r["model_id"],
                        publish_seq=str(r["publish_seq"]),
                        published_at=r["published_at"],
                        status=r["status"],
                        file_data_range_utc=json.loads(r["range_json"]),
                        group_count=str(r["group_count"]),
                        input_sha256=r["input_sha256"],
                        source_label=r["source_label"],
                    )
                    for r in rows
                ]
            else:
                query = (
                    " FROM active_groups a JOIN publications p ON a.run_id=p.run_id JOIN public"
                    "ation_groups g ON g.run_id=a.run_id AND g.appid=a.appid WHERE (? IS NULL O"
                    "R a.appid=?) AND (? IS NULL OR a.model_id=?)"
                )
                args = (appid, appid, model_id, model_id)
                total = db.execute("SELECT count(*)" + query, args).fetchone()[0]
                rows = db.execute(
                    (
                        "SELECT a.appid,a.model_id,a.run_id,a.publish_seq,p.published_at,g.min_"
                        "ns,g.max_ns"
                    )
                    + query
                    + " ORDER BY a.appid COLLATE BINARY,a.model_id COLLATE BINARY LIMIT ? OFFSET ?",
                    (*args, limit, min(offset, 2**63 - 1)),
                )
                items = [
                    dict(
                        appid=r["appid"],
                        model_id=r["model_id"],
                        active_run_id=r["run_id"],
                        publish_seq=str(r["publish_seq"]),
                        published_at=r["published_at"],
                        data_range_utc=data_range(r["min_ns"], r["max_ns"]),
                        snapshot_url=f"/analysis-runs/{r['run_id']}/view-snapshot?"
                        + urlencode(dict(appid=r["appid"])),
                    )
                    for r in rows
                ]
            response = {
                **ident,
                **page(offset, limit, total),
                "catalog_revision": str(current),
                "items": items,
            }
            if not runs:
                response["cursor"] = ident["service_instance_id"] + ":" + str(highwater(db))
            return response
