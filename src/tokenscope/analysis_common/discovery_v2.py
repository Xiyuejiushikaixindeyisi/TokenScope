"""Additive partial selection; original v1 journal and contract are unchanged."""

from typing import Any

from tokenscope.analysis_common.discovery import Discovery


class DiscoveryV2(Discovery):
    def catalog_v2(
        self, snapshot: str | None = None, after: str = "0", limit: int = 50
    ) -> dict[str, Any]:
        result = self.catalog(snapshot, after, limit)
        cutoff = int(result["snapshot"].rpartition(":")[2])
        selected: dict[tuple[str, str], dict[str, Any]] = {}
        with self.store.connect(True) as db:
            db.execute("BEGIN")
            identity, high = self._identity(db)
            self._position(result["snapshot"], identity, high)
            for row in db.execute(
                "SELECT * FROM diagnostic_terminals WHERE seq<=? AND legacy=0 "
                "AND report_digest IS NOT NULL AND status IN ('ready','partial') "
                "AND json_extract(intent,'$.kind')='analysis' ORDER BY seq",
                (cutoff,),
            ):
                entry = self._entry(row)
                for direction in entry["directions"]:
                    key = (entry["binding_id"], direction)
                    if (
                        entry["status"] == "partial"
                        and selected.get(key, {}).get("status") == "ready"
                    ):
                        continue
                    selected[key] = {
                        "binding_id": key[0],
                        "direction": direction,
                        "task_id": entry["task_id"],
                        "sequence": entry["sequence"],
                        "status": entry["status"],
                        "selection_kind": "ready"
                        if entry["status"] == "ready"
                        else "published_partial_fallback",
                    }
        return {
            **result,
            "version": "diagnostics-discovery-2",
            "selected_reports": list(selected.values()),
        }
