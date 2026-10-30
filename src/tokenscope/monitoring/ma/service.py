"""MA HTTP/CLI boundary; GET operations read only published projections."""

import json

from tokenscope.domain import capability
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.ma.contracts import (
    Catalog,
    CatalogEntry,
    QualityIssue,
    QualityPage,
    Receipt,
    Snapshot,
    Submit,
)
from tokenscope.monitoring.ma.ingest import connect
from tokenscope.monitoring.ma.pipeline import Processor
from tokenscope.monitoring.ma.storage import Store, normalize
from tokenscope.monitoring.publications import identity
from tokenscope.monitoring.service import MonitoringService


class MaService:
    def __init__(self, base: MonitoringService) -> None:
        self.base = base
        with base.control.connect() as db:
            self.service_id = identity(db, require_ready=False)["service_instance_id"]
        self.store = Store(base.state_root / "ma", self.service_id)
        self.processor = Processor(base, self.store)

    def submit(self, binding: Submit) -> Receipt:
        binding = normalize(binding)
        prior = self.store.find(binding.submission_key)
        if prior is not None:
            if prior.binding != binding:
                raise TokenScopeError("SUBMISSION_CONFLICT", "Submission key binding differs", 409)
            return prior
        if not capability(self.base.control.settings(binding.model_id)).executable:
            raise TokenScopeError("UNSUPPORTED_CACHE_MODE", "Hybrid simulation is reserved", 422)
        for ref in (binding.pre_file_ref, binding.now_file_ref):
            with self.base.inputs.open(ref):
                pass
        return self.store.enqueue(binding)

    def submission(self, key: str) -> Receipt:
        receipt = self.store.find(key)
        if receipt is None:
            raise TokenScopeError("SUBMISSION_NOT_FOUND", "Unknown MA submission", 404)
        return receipt

    def catalog(
        self,
        spec: str | None = None,
        offset: int = 0,
        limit: int = 100,
        revision: int | None = None,
    ) -> Catalog:
        self.base.pagination(offset, limit)
        with connect(self.store.path, readonly=True) as db:
            db.execute("BEGIN")
            current = db.execute("SELECT revision FROM metadata WHERE id=1").fetchone()[0]
            if (offset and revision is None) or (revision is not None and current != revision):
                raise TokenScopeError(
                    "CATALOG_REVISION_CONFLICT", "MA catalog revision changed", 409
                )
            where = (
                "state='completed' AND "
                "(? IS NULL OR json_extract(binding,'$.model_standard_name')=?)"
            )
            total = db.execute(f"SELECT count(*) FROM runs WHERE {where}", (spec, spec)).fetchone()[
                0
            ]
            entries = []
            for row in db.execute(
                f"SELECT run_id,binding,summary FROM runs WHERE {where} "
                "ORDER BY seq DESC LIMIT ? OFFSET ?",
                (spec, spec, limit, offset),
            ):
                binding, summary = json.loads(row["binding"]), json.loads(row["summary"])
                entries.append(
                    CatalogEntry(
                        ma_run_id=row["run_id"],
                        model_standard_name=binding["model_standard_name"],
                        now_start=binding["now_start"],
                        now_end=binding["now_end"],
                        instance_uuids=summary["instance_uuids"],
                        empty_scope_reason=summary["empty_scope_reason"],
                    )
                )
        return Catalog(
            service_instance_id=self.service_id,
            catalog_revision=str(current),
            total=str(total),
            next_offset=str(offset + limit) if offset + limit < total else None,
            entries=entries,
        )

    def snapshot(self, run_id: str, uuid: str) -> Snapshot:
        summary = self.store.summary(run_id)
        with connect(self.processor.runs / run_id / "requests.sqlite3", readonly=True) as db:
            row = db.execute(
                "SELECT snapshot FROM projections WHERE instance_uuid=?", (uuid,)
            ).fetchone()
        if row is None:
            raise TokenScopeError("INSTANCE_NOT_FOUND", "Unknown MA instance in this run", 404)
        return Snapshot.model_validate(
            dict(
                service_instance_id=self.service_id,
                ma_run_id=run_id,
                binding=summary["binding"],
                instance=json.loads(row[0]),
                file_quality=summary["file_quality"],
                runtime=summary["runtime"],
            )
        )

    def quality(self, run_id: str, offset: int = 0, limit: int = 100) -> QualityPage:
        self.base.pagination(offset, limit)
        self.store.summary(run_id)
        with connect(self.processor.runs / run_id / "requests.sqlite3", readonly=True) as db:
            total = db.execute("SELECT count(*) FROM issues").fetchone()[0]
            rows = db.execute(
                """SELECT * FROM issues ORDER BY CASE role WHEN 'pre' THEN 0 ELSE 1 END,
                source_record_index,field,code LIMIT ? OFFSET ?""",
                (limit, offset),
            )
            issues = [
                QualityIssue(
                    role=r["role"],
                    source_record_index=str(r["source_record_index"]),
                    physical_line_start=str(r["line_start"]),
                    physical_line_end=str(r["line_end"]),
                    field=r["field"],
                    code=r["code"],
                )
                for r in rows
            ]
        return QualityPage(
            service_instance_id=self.service_id,
            ma_run_id=run_id,
            total=str(total),
            next_offset=str(offset + limit) if offset + limit < total else None,
            issues=issues,
        )
