"""Read-only discovery of sealed user indexes; no import, rebuild or persistent cache."""

import hashlib
import json
from typing import Any

from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.user_monitoring.contracts import RankRow
from tokenscope.user_monitoring.discovery_contracts import (
    DiscoveryEntry,
    DiscoveryPage,
    DiscoveryQuery,
    TraceSource,
)
from tokenscope.user_monitoring.service import UserRunService
from tokenscope.user_monitoring.storage import canonical


class Discovery:
    def __init__(self, user: UserRunService) -> None:
        self.user = user

    def published(self) -> list[dict[str, Any]]:
        with self.user.store.connect(readonly=True) as db:
            return [
                dict(row)
                for row in db.execute(
                    "SELECT rowid AS registration_order,* FROM runs "
                    "WHERE state IN ('ready','empty') ORDER BY rowid DESC"
                )
            ]

    def source(self, run_id: str, revision: str, metadata: dict[str, Any]) -> TraceSource:
        row = self.user.store.run(run_id)
        directory = self.user.base.state_root / "runs" / str(row["base_id"])
        if not directory.resolve().is_relative_to((self.user.base.state_root / "runs").resolve()):
            raise TokenScopeError("RESULT_SEAL_INVALID", "Source path differs", 409)
        try:
            manifest_path = directory / "manifest.json"
            manifest_sha = file_digest(manifest_path)
            manifest = json.loads(manifest_path.read_text())
            summary_path = directory / "summary.json"
            expected = next(f["sha256"] for f in manifest["files"] if f["path"] == "summary.json")
            if (
                metadata["user_run_id"] != run_id
                or metadata["base_run_id"] != row["base_id"]
                or metadata["common_name"] != row["common_name"]
                or manifest["run_id"] != row["base_id"]
                or manifest_sha != metadata["source_seal"]
                or file_digest(summary_path) != expected
            ):
                raise TokenScopeError("RESULT_SEAL_INVALID", "Source identity differs", 409)
            summary = json.loads(summary_path.read_text())
            if summary["model_id"] != row["model_id"] or summary["run_id"] != row["base_id"]:
                raise TokenScopeError("MODEL_MISMATCH", "Source model differs", 409)
            return TraceSource(
                base_run_id=row["base_id"],
                user_run_id=run_id,
                common_name=row["common_name"],
                model_id=row["model_id"],
                index_revision=revision,
                input_sha256=summary["input_sha256"],
                manifest_sha256=manifest_sha,
                settings_sha256=hashlib.sha256(canonical(summary["settings"]).encode()).hexdigest(),
                encoder_identity=summary["runtime"]["encoder_identity"],
                asset_identity=summary["runtime"]["asset_identity"],
                file_observed_time_range_utc=tuple(summary["time_range_utc"]),
            )
        except (KeyError, ValueError, StopIteration) as exc:
            raise TokenScopeError(
                "RESULT_SEAL_INVALID", "Source metadata unavailable", 409
            ) from exc

    def entry(self, run_id: str, appid: str, revision: str) -> DiscoveryEntry:
        row = self.user.store.run(run_id)
        with self.user.index(run_id, revision) as db:
            metadata = json.loads(db.execute("SELECT payload FROM metadata").fetchone()[0])
            group = db.execute(
                "SELECT payload FROM groups WHERE width=5000 AND appid=?", (appid,)
            ).fetchone()
            metrics = RankRow.model_validate_json(group[0]) if group else None
            source = self.source(run_id, revision, metadata)
        with self.user.store.connect(readonly=True) as db:
            order = db.execute("SELECT rowid FROM runs WHERE id=?", (run_id,)).fetchone()[0]
        return DiscoveryEntry(
            source=source,
            appid=appid,
            state=row["state"],
            registration_order=str(order),
            is_default=False,
            request_count=metrics.request_count if metrics else "0",
            prompt_p90=metrics.prompt_p90 if metrics else None,
        )

    def catalog(self, query: DiscoveryQuery) -> DiscoveryPage:
        before = self.published()
        entries: list[DiscoveryEntry] = []
        defaults: set[tuple[str | None, str, str]] = set()
        for row in before:
            with self.user.index(row["id"], row["revision"]) as db:
                metadata = json.loads(db.execute("SELECT payload FROM metadata").fetchone()[0])
                source = self.source(row["id"], row["revision"], metadata)
                groups: list[RankRow | None] = [
                    RankRow.model_validate_json(g[0])
                    for g in db.execute(
                        "SELECT payload FROM groups WHERE width=5000 ORDER BY appid"
                    )
                ]
                for metrics in groups or [None]:
                    appid = metrics.appid if metrics else None
                    key = (appid, row["model_id"], row["common_name"])
                    entry = DiscoveryEntry(
                        source=source,
                        appid=appid,
                        state=row["state"],
                        registration_order=str(row["registration_order"]),
                        is_default=key not in defaults,
                        request_count=metrics.request_count if metrics else "0",
                        prompt_p90=metrics.prompt_p90 if metrics else None,
                    )
                    defaults.add(key)
                    entries.append(entry)
        if before != self.published():
            raise TokenScopeError(
                "DISCOVERY_SNAPSHOT_CONFLICT", "Published set changed; restart", 409
            )
        entries = [
            e
            for e in entries
            if (
                (query.appid is None or e.appid == query.appid)
                and (query.common_name is None or e.source.common_name == query.common_name)
                and (query.model_id is None or e.source.model_id == query.model_id)
                and (query.user_run_id is None or e.source.user_run_id == query.user_run_id)
            )
        ]
        selection = query.model_dump(exclude={"snapshot", "offset", "limit"})
        snapshot = hashlib.sha256(
            canonical(
                {
                    "instance": self.user.service_id,
                    "selection": selection,
                    "entries": [e.model_dump(mode="json") for e in entries],
                }
            ).encode()
        ).hexdigest()
        if (query.snapshot is not None and query.snapshot != snapshot) or (
            int(query.offset) > 0 and query.snapshot is None
        ):
            raise TokenScopeError("DISCOVERY_SNAPSHOT_CONFLICT", "Snapshot differs; restart", 409)
        if query.user_run_id is not None and not entries:
            # Distinguish a deliberately fixed but unavailable history from an empty search.
            self.user.receipt(query.user_run_id)
            raise TokenScopeError("RESULT_NOT_READY", "No matching published history", 409)
        offset, total = int(query.offset), len(entries)
        end = min(total, offset + query.limit)
        return DiscoveryPage(
            service_instance_id=self.user.service_id,
            snapshot=snapshot,
            total=str(total),
            next_offset=str(end) if end < total else None,
            entries=entries[offset:end],
        )
