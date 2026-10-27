"""Fixed S0 presentation routes; read paths consume existing committed facts."""

import asyncio
import json
from collections.abc import Iterator
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import ValidationError
from starlette.types import Receive, Scope, Send

from tokenscope.domain import ModelId
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.publications import identity
from tokenscope.monitoring.service import MonitoringService
from tokenscope.monitoring.view_export import ViewExport
from tokenscope.monitoring.view_models import (
    Nonempty,
    QueryDecimal,
    QueryPositive,
    ViewRuleUpdate,
    ViewSettingsUpdate,
    page,
    rule_wire,
    wire,
)
from tokenscope.monitoring.views import RequestQuery


class ClosingResponse(StreamingResponse):
    def __init__(self, iterator: Iterator[bytes], **kwargs: Any) -> None:
        self.source_iterator = iterator
        super().__init__(iterator, **kwargs)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await super().__call__(scope, receive, send)
        finally:
            close = getattr(self.source_iterator, "close", None)
            if close is not None:
                await asyncio.to_thread(close)


def router(service: MonitoringService) -> APIRouter:
    api = APIRouter()

    def query(
        metric: str = "prompt_tokens",
        lower: QueryDecimal = 0,
        upper: QueryDecimal | None = None,
        hash_id: str | None = None,
        hash_match: str = "exact",
        sort_by: str = "prompt_tokens",
        sort_order: str = "desc",
    ) -> RequestQuery:
        return RequestQuery(metric, lower, upper, hash_id, hash_match, sort_by, sort_order)

    @api.get("/analysis-submissions/{submission_key}")
    def receipt(submission_key: str, request: Request) -> Response:
        instance = service.views.guard(request.headers.get("x-tokenscope-instance-id"))
        from tokenscope.monitoring.view_models import canonical

        return Response(
            canonical(service.views.receipt(submission_key)),
            media_type="application/json",
            headers={"Cache-Control": "no-store", "X-TokenScope-Instance-Id": instance},
        )

    @api.get("/analysis-runs/{run_id}/requests")
    def requests(
        run_id: str,
        appid: Nonempty,
        query: Annotated[RequestQuery, Depends(query)],
        offset: QueryDecimal = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        return service.views.requests(run_id, appid, query, offset, limit)

    @api.get("/analysis-runs/{run_id}/requests/export")
    def export(
        run_id: str,
        appid: Nonempty,
        query: Annotated[RequestQuery, Depends(query)],
        request: Request,
        format: Literal["ndjson", "csv"] = "ndjson",
    ) -> StreamingResponse:
        if "offset" in request.query_params or "limit" in request.query_params:
            raise TokenScopeError("INVALID_REQUEST", "Export does not accept pagination", 422)
        output = ViewExport(service.views, run_id, appid, query)
        return ClosingResponse(
            output.stream(format),
            headers=output.headers(format),
            media_type="application/x-ndjson; charset=utf-8"
            if format == "ndjson"
            else "text/csv; charset=utf-8",
        )

    @api.get("/analysis-runs/{run_id}/requests/{source_record_index}")
    def detail(run_id: str, appid: Nonempty, source_record_index: QueryPositive) -> dict[str, Any]:
        return service.views.detail(run_id, appid, source_record_index)

    @api.get("/analysis-runs/{run_id}/requests/{source_record_index}/body")
    def body(run_id: str, appid: Nonempty, source_record_index: QueryPositive) -> StreamingResponse:
        service.views.request_identity(run_id, appid, source_record_index)
        return ClosingResponse(
            service.views.body(run_id, source_record_index),
            media_type="application/json",
            headers={"Cache-Control": "no-store"},
        )

    @api.get("/analysis-runs/{run_id}/requests/{source_record_index}/evidence")
    def evidence(
        run_id: str,
        appid: Nonempty,
        source_record_index: QueryPositive,
        section: str = "special_ranges",
        offset: QueryDecimal = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        return service.views.evidence(run_id, appid, source_record_index, section, offset, limit)

    @api.get("/analysis-runs/{run_id}/view-signals")
    def signals(
        run_id: str, appid: Nonempty, offset: QueryDecimal = 0, limit: int = 100
    ) -> dict[str, Any]:
        return service.views.signals(run_id, appid, offset, limit)

    @api.get("/monitoring/models/{model_id}/settings")
    def settings(model_id: ModelId) -> dict[str, Any]:
        with service.control.connect() as db:
            ident = identity(db)
        return {**ident, **wire(service.model(model_id))}

    @api.put("/monitoring/models/{model_id}/settings")
    def put_settings(model_id: ModelId, update: ViewSettingsUpdate) -> dict[str, Any]:
        with service.control.connect() as db:
            ident = identity(db)
        try:
            result = service.update_settings(model_id, update.domain())
        except (ValidationError, ValueError) as exc:
            raise TokenScopeError("INVALID_REQUEST", "Invalid settings input", 422) from exc
        return {**ident, **wire(result)}

    @api.get("/monitoring/threshold-rules")
    def rules(
        appid: Nonempty | None = None,
        model_id: ModelId | None = None,
        offset: QueryDecimal = 0,
        limit: int = 100,
        rules_revision: QueryDecimal | None = None,
    ) -> dict[str, Any]:
        page(offset, limit, 0)
        with service.control.connect() as db:
            db.execute("BEGIN")
            ident = identity(db)
            revision = db.execute(
                "SELECT rules_revision FROM service_metadata WHERE id=1"
            ).fetchone()[0]
            if (offset and rules_revision is None) or (
                rules_revision is not None and rules_revision != revision
            ):
                raise TokenScopeError("RULES_REVISION_CHANGED", "Reload rules", 409)
            where = (
                " FROM threshold_rules r WHERE revision=(SELECT max(s.revision) "
                "FROM threshold_rules s "
                "WHERE r.appid=s.appid AND r.model_id=s.model_id AND r.rule_id=s.rule_id) "
                "AND (? IS NULL OR r.appid=?) AND (? IS NULL OR r.model_id=?)"
            )
            args = (appid, appid, model_id, model_id)
            total = db.execute("SELECT count(*)" + where, args).fetchone()[0]
            rows = db.execute(
                "SELECT rule_json" + where + " ORDER BY appid,model_id,rule_id LIMIT ? OFFSET ?",
                (*args, limit, min(offset, 2**63 - 1)),
            )
            items = [rule_wire(json.loads(row[0])) for row in rows]
        return {
            **ident,
            **page(offset, limit, total),
            "rules_revision": str(revision),
            "items": items,
        }

    @api.put("/monitoring/threshold-rules")
    def put_rule(update: ViewRuleUpdate) -> dict[str, Any]:
        with service.control.connect() as db:
            ident = identity(db)
        try:
            rule = service.control.update_rule(update.domain())
        except (ValidationError, ValueError) as exc:
            raise TokenScopeError("INVALID_REQUEST", "Invalid rule input", 422) from exc
        with service.control.connect() as db:
            revision = db.execute(
                "SELECT rules_revision FROM service_metadata WHERE id=1"
            ).fetchone()[0]
        return {**ident, "rules_revision": str(revision), "rule": rule_wire(rule)}

    return api
