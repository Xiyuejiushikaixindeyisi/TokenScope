"""Read-only presentation access to committed publications and immutable projections."""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.publications import identity
from tokenscope.monitoring.view_models import canonical, page, sha, utc_ns, wire
from tokenscope.monitoring.view_projection import SORTS, location


class MonitoringViewService:
    def __init__(self, control: Any, root: Path) -> None:
        self.control = control
        self.root = root

    def group(self, run_id: str, appid: str) -> dict[str, Any]:
        with self.control.connect() as db:
            db.execute("BEGIN")
            ident = identity(db)
            publication = db.execute(
                "SELECT * FROM publications WHERE run_id=?", (run_id,)
            ).fetchone()
            if publication is None:
                exists = db.execute(
                    "SELECT 1 FROM analysis_runs WHERE run_id=?", (run_id,)
                ).fetchone()
                raise TokenScopeError(
                    "RESULT_NOT_READY" if exists else "RUN_NOT_FOUND",
                    "No committed result" if exists else "Unknown run",
                    409 if exists else 404,
                )
            if not db.execute(
                "SELECT 1 FROM publication_groups WHERE run_id=? AND appid=?", (run_id, appid)
            ).fetchone():
                raise TokenScopeError("GROUP_NOT_FOUND", "Unknown result group", 404)
            return {
                **ident,
                "run_id": run_id,
                "appid": appid,
                "model_id": publication["model_id"],
                "publish_seq": str(publication["publish_seq"]),
                "published_at": publication["published_at"],
            }

    # A streaming iterator is resumed sequentially, but Starlette may choose a
    # different worker for each next()/close(). Connections are request-local,
    # read-only and never used concurrently.
    @contextmanager
    def projection(self, run_id: str) -> Iterator[sqlite3.Connection]:
        db = None
        try:
            path = location(self.root, run_id) / "view.sqlite3"
            db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, check_same_thread=False)
            db.row_factory = sqlite3.Row
            yield db
        except sqlite3.Error as exc:
            raise TokenScopeError(
                "VIEW_ARTIFACT_UNAVAILABLE", "View data unavailable", 503
            ) from exc
        finally:
            if db is not None:
                db.close()

    def snapshot(self, run_id: str, appid: str) -> tuple[bytes, str]:
        ident = self.group(run_id, appid)
        with self.projection(run_id) as db:
            row = db.execute(
                "SELECT body,sha256 FROM view_groups WHERE appid=?", (appid,)
            ).fetchone()
        if row is None or sha(row["body"]) != row["sha256"]:
            raise TokenScopeError("VIEW_ARTIFACT_UNAVAILABLE", "View integrity check failed", 503)
        try:
            body = json.loads(row["body"])
            body["provenance"]["published_at"] = ident.pop("published_at")
            body["identity"] = ident
            raw = canonical(body)
        except (ValueError, TypeError, KeyError) as exc:
            raise TokenScopeError("VIEW_ARTIFACT_UNAVAILABLE", "Invalid view data", 503) from exc
        return raw, '"' + sha(raw) + '"'

    def receipt(self, key: str) -> dict[str, Any]:
        with self.control.connect() as db:
            db.execute("BEGIN")
            ident = identity(db)
            row = db.execute(
                "SELECT r.* FROM submission_receipts s JOIN analysis_runs r USING(run_id) "
                "WHERE submission_key=?",
                (key,),
            ).fetchone()
            if row is None:
                raise TokenScopeError("SUBMISSION_NOT_FOUND", "Unknown submission key", 404)
            return {
                **ident,
                "submission_key": key,
                **{
                    k: row[k]
                    for k in (
                        "run_id",
                        "model_id",
                        "status",
                        "created_at",
                        "started_at",
                        "finished_at",
                        "error_code",
                    )
                },
                "run_url": f"/analysis-runs/{row['run_id']}",
            }

    def guard(self, expected: str | None) -> str:
        with self.control.connect() as db:
            actual = identity(db, False)["service_instance_id"]
        if expected is not None and expected != actual:
            raise TokenScopeError("SERVICE_INSTANCE_CHANGED", "Reload service identity", 409)
        return actual

    @staticmethod
    def context(ident: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in ident.items() if k not in ("publish_seq", "published_at")}

    @staticmethod
    def fact(run_id: str, row: sqlite3.Row) -> dict[str, Any]:
        return dict(
            request_ref=dict(run_id=run_id, source_record_index=str(row["source_record_index"])),
            hash_id=row["hash_id"],
            time_utc=utc_ns(row["time_ns"]),
            **{k: str(row[k]) for k in SORTS if k not in ("time_ns", "source_record_index")},
        )

    def requests(
        self, run_id: str, appid: str, query: "RequestQuery", offset: int, limit: int
    ) -> dict[str, Any]:
        ident = self.group(run_id, appid)
        page(offset, limit, 0)
        where, args = query.sql(appid)
        with self.projection(run_id) as db:
            total = db.execute(
                "SELECT count(*) FROM request_projection WHERE " + where, args
            ).fetchone()[0]
            rows = db.execute(
                "SELECT * FROM request_projection WHERE "
                + where
                + query.order_sql()
                + " LIMIT ? OFFSET ?",
                (*args, limit, min(offset, 2**63 - 1)),
            )
            items = [
                dict(position=str(offset + i + 1), **self.fact(run_id, row))
                for i, row in enumerate(rows)
            ]
        return {
            **self.context(ident),
            **page(offset, limit, total),
            "filter": query.filter(),
            "sort": query.sort(),
            "items": items,
        }

    def request_identity(
        self, run_id: str, appid: str, index: int
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        ident = self.group(run_id, appid)
        if index <= 0 or index > 2**63 - 1:
            raise TokenScopeError("REQUEST_NOT_FOUND", "Unknown request", 404)
        with self.projection(run_id) as db:
            row = db.execute(
                "SELECT * FROM request_projection WHERE appid=? AND source_record_index=?",
                (appid, index),
            ).fetchone()
        if row is None:
            raise TokenScopeError("REQUEST_NOT_FOUND", "Unknown request", 404)
        return self.context(ident), self.fact(run_id, row)

    @contextmanager
    def original(self, run_id: str) -> Iterator[sqlite3.Connection]:
        path = self.root / "runs" / run_id / "requests.sqlite3"
        db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, check_same_thread=False)
        db.row_factory = sqlite3.Row
        try:
            yield db
        finally:
            db.close()

    def stored_evidence(self, run_id: str, index: int) -> tuple[dict[str, Any], dict[str, Any]]:
        with self.original(run_id) as db:
            row = db.execute(
                "SELECT evidence_json FROM encoded_requests WHERE source_record_index=?", (index,)
            ).fetchone()
        if row is None:
            raise TokenScopeError("VIEW_ARTIFACT_UNAVAILABLE", "Stored evidence unavailable", 503)
        evidence = json.loads(row[0])
        summary = {
            k: wire(v)
            for k, v in evidence.items()
            if k not in ("special_ranges", "source_fields", "effective_options")
        }
        summary.update(
            special_ranges_count=str(len(evidence["special_ranges"])),
            source_fields_count=str(len(evidence["source_fields"])),
            effective_options_json=canonical(evidence["effective_options"]).decode(),
        )
        return summary, evidence

    def detail(self, run_id: str, appid: str, index: int) -> dict[str, Any]:
        ident, fact = self.request_identity(run_id, appid, index)
        summary, _ = self.stored_evidence(run_id, index)
        with self.original(run_id) as db:
            row = db.execute(
                "SELECT length(CAST(request_input AS BLOB)), "
                "substr(CAST(request_input AS BLOB),1,65536) FROM request_records "
                "WHERE source_record_index=?",
                (index,),
            ).fetchone()
        text = row[1].decode("utf-8", errors="ignore")
        n = len(text.encode())
        from urllib.parse import urlencode

        base = f"/analysis-runs/{run_id}/requests/{index}"
        query = urlencode(dict(appid=appid))
        return {
            **ident,
            "request": fact,
            "evidence_summary": summary,
            "body_preview": dict(
                text=text,
                total_utf8_bytes=str(row[0]),
                preview_utf8_bytes=str(n),
                truncated=n < row[0],
            ),
            "capabilities": dict(original_json=True, light_evidence=True, templated_text=False),
            "links": dict(body=base + "/body?" + query, evidence=base + "/evidence?" + query),
        }

    def body(self, run_id: str, index: int) -> Iterator[bytes]:
        with self.original(run_id) as db:
            position = 1
            while True:
                row = db.execute(
                    "SELECT substr(CAST(request_input AS BLOB),?,65536) FROM request_records "
                    "WHERE source_record_index=?",
                    (position, index),
                ).fetchone()
                if row is None:
                    raise OSError("Stored body unavailable")
                chunk = bytes(row[0])
                if not chunk:
                    break
                yield chunk
                position += len(chunk)

    def evidence(
        self, run_id: str, appid: str, index: int, section: str, offset: int, limit: int
    ) -> dict[str, Any]:
        if section not in ("special_ranges", "source_fields"):
            raise TokenScopeError("INVALID_REQUEST", "Invalid evidence section", 422)
        page(offset, limit, 0)
        ident, fact = self.request_identity(run_id, appid, index)
        summary, original = self.stored_evidence(run_id, index)
        values = original[section]
        items = values[offset : offset + limit]
        if section == "special_ranges":
            items = [dict(start=str(x[0]), end=str(x[1])) for x in items]
        else:
            items = wire(items)
        return {
            **ident,
            **page(offset, limit, len(values)),
            "request_ref": fact["request_ref"],
            "section": section,
            "summary": summary,
            "items": items,
        }

    def signals(self, run_id: str, appid: str, offset: int, limit: int) -> dict[str, Any]:
        ident = self.group(run_id, appid)
        page(offset, limit, 0)
        with self.control.connect() as db:
            where = (
                " FROM run_signals r JOIN outbox o USING(event_id) WHERE r.run_id=? "
                "AND json_extract(o.payload_json,'$.appid')=?"
            )
            total = db.execute("SELECT count(*)" + where, (run_id, appid)).fetchone()[0]
            rows = db.execute(
                "SELECT o.payload_json" + where + " ORDER BY o.event_id LIMIT ? OFFSET ?",
                (run_id, appid, limit, min(offset, 2**63 - 1)),
            )
            items = []
            for row in rows:
                event = json.loads(row[0])
                kind = (
                    "ratio"
                    if event["metric"] == "ideal_hit_rate"
                    else "integer"
                    if isinstance(event["threshold"], int)
                    else "number"
                )
                items.append(
                    dict(
                        run_id=run_id,
                        published_at=ident["published_at"],
                        **{
                            k: event[k]
                            for k in (
                                "appid",
                                "model_id",
                                "event_id",
                                "metric",
                                "comparator",
                                "rule_id",
                                "route",
                                "status",
                            )
                        },
                        revision=str(event["revision"]),
                        value_kind=kind,
                        threshold=str(event["threshold"])
                        if kind == "integer"
                        else float(event["threshold"]),
                        observed_value=event["observed_value"]
                        if kind == "ratio"
                        else wire(event["observed_value"]),
                    )
                )
        return {**self.context(ident), **page(offset, limit, total), "items": items}


class RequestQuery:
    def __init__(
        self,
        metric: str = "prompt_tokens",
        lower: int = 0,
        upper: int | None = None,
        hash_id: str | None = None,
        hash_match: str = "exact",
        sort_by: str = "prompt_tokens",
        sort_order: str = "desc",
    ) -> None:
        if (
            metric not in ("json_tokens", "prompt_tokens", "ideal_compute_input_tokens")
            or lower < 0
            or (upper is not None and upper <= lower)
            or hash_match not in ("exact", "prefix")
            or hash_id == ""
            or sort_by not in SORTS
            or sort_order not in ("asc", "desc")
        ):
            raise TokenScopeError("INVALID_REQUEST", "Invalid request query", 422)
        self.metric, self.lower, self.upper = metric, lower, upper
        self.hash_id, self.hash_match = hash_id, hash_match
        self.sort_by, self.sort_order = sort_by, sort_order

    def filter(self) -> dict[str, Any]:
        return dict(
            metric=self.metric,
            lower=str(self.lower),
            upper=None if self.upper is None else str(self.upper),
            hash_id=self.hash_id,
            hash_match=self.hash_match,
        )

    def sort(self) -> dict[str, Any]:
        return dict(by=self.sort_by, order=self.sort_order, tie_breaker="source_record_index_asc")

    def sql(self, appid: str) -> tuple[str, list[Any]]:
        where = "appid=?"
        args: list[Any] = [appid]
        if self.lower > 2**63 - 1:
            where += " AND 0"
        else:
            where += f" AND {self.metric}>=?"
            args.append(self.lower)
        if self.upper is not None and self.upper <= 2**63 - 1:
            where += f" AND {self.metric}<?"
            args.append(self.upper)
        if self.hash_id is not None:
            # substr exact prefix is case sensitive and treats %, _ and backslash literally.
            where += (
                " AND hash_id=?"
                if self.hash_match == "exact"
                else " AND substr(hash_id,1,length(?))=?"
            )
            args.extend(
                [self.hash_id] if self.hash_match == "exact" else [self.hash_id, self.hash_id]
            )
        return where, args

    def order_sql(self) -> str:
        return f" ORDER BY {self.sort_by} {self.sort_order},source_record_index ASC"
