import asyncio
import sqlite3
import threading
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.staticfiles import StaticFiles

from tokenscope import __version__
from tokenscope.api.openapi import install as install_openapi
from tokenscope.api.views import router as view_router
from tokenscope.domain import ModelId, ModelView, RunState, RunSubmission, SettingsUpdate
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.events import EventResponse, PublicationEventReader
from tokenscope.monitoring.rules import RuleUpdate
from tokenscope.monitoring.service import MonitoringService
from tokenscope.monitoring.view_models import Nonempty, QueryDecimal


def create_app(
    service: MonitoringService, *, start_worker: bool = True, viewer_root: Path | None = None
) -> FastAPI:
    if viewer_root is not None and not (viewer_root / "index.html").is_file():
        raise TokenScopeError("VIEWER_BUILD_MISSING", "Viewer build requires index.html", 503)
    events = PublicationEventReader(service.control)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        stop = threading.Event()

        def work() -> None:
            next_prune = 0.0
            while not stop.is_set():
                try:
                    result = service.processor.process_next()
                    if time.monotonic() >= next_prune:
                        events.prune()
                        next_prune = time.monotonic() + 60
                except (OSError, sqlite3.Error):
                    result = None
                if result is None:
                    stop.wait(0.5)

        worker = threading.Thread(target=work, daemon=True, name="tokenscope-worker")
        if start_worker:
            worker.start()
        try:
            yield
        finally:
            stop.set()
            if start_worker:
                await asyncio.to_thread(worker.join, 30)

    app = FastAPI(title="TokenScope Monitoring", version=__version__, lifespan=lifespan)

    @app.exception_handler(TokenScopeError)
    async def domain_error(request: Request, exc: TokenScopeError) -> JSONResponse:
        return JSONResponse({"error": exc.as_dict()}, status_code=exc.http_status)

    @app.exception_handler(RequestValidationError)
    async def request_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Do not echo a request body, file path or arbitrary supplied values in errors.
        return JSONResponse(
            {"error": {"code": "INVALID_REQUEST", "message": "Invalid API input"}}, status_code=422
        )

    @app.exception_handler(sqlite3.Error)
    @app.exception_handler(OSError)
    async def storage_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            {"error": {"code": "STORAGE_UNAVAILABLE", "message": "Local storage operation failed"}},
            status_code=503,
        )

    app.include_router(view_router(service))
    app.state.events = events

    @app.get("/monitoring/events")
    async def event_stream(request: Request, after: str | None = None) -> EventResponse:
        cursor = request.headers.get("last-event-id") or after
        ident, initial, _, _ = await asyncio.to_thread(events.read, cursor)
        if cursor is None:
            cursor = ident["service_instance_id"] + ":" + str(initial)
        events.reserve()
        return EventResponse(events, cursor, ident["service_instance_id"])

    @app.get("/monitoring/catalog")
    def catalog(
        appid: Nonempty | None = None,
        model_id: ModelId | None = None,
        offset: QueryDecimal = 0,
        limit: int = 100,
        catalog_revision: QueryDecimal | None = None,
    ) -> dict[str, Any]:
        return service.publications.catalog(appid, model_id, offset, limit, catalog_revision)

    @app.get("/monitoring/runs")
    def published_runs(
        appid: Nonempty | None = None,
        model_id: ModelId | None = None,
        offset: QueryDecimal = 0,
        limit: int = 100,
        catalog_revision: QueryDecimal | None = None,
    ) -> dict[str, Any]:
        return service.publications.catalog(
            appid, model_id, offset, limit, catalog_revision, runs=True
        )

    @app.get("/analysis-runs/{run_id}/view-snapshot")
    def view_snapshot(run_id: str, appid: Nonempty, request: Request) -> Response:
        raw, etag = service.views.snapshot(run_id, appid)
        headers = {"ETag": etag, "Cache-Control": "private, no-cache"}
        candidates = request.headers.get("if-none-match", "").split(",")
        if any(x.strip().removeprefix("W/") in (etag, "*") for x in candidates):
            return Response(status_code=304, headers=headers)
        return Response(raw, media_type="application/json", headers=headers)

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/readyz")
    def ready() -> JSONResponse:
        result = service.readiness()
        return JSONResponse(result, status_code=200 if result["ready"] else 503)

    @app.get("/version")
    def version() -> dict[str, Any]:
        return service.version()

    @app.get("/models", response_model=list[ModelView])
    def models() -> list[dict[str, Any]]:
        return service.models()

    @app.get("/models/{model_id}/settings", response_model=ModelView)
    def settings(model_id: str) -> dict[str, Any]:
        return service.model(model_id)

    @app.put("/models/{model_id}/settings", response_model=ModelView)
    def update_settings(model_id: str, update: SettingsUpdate) -> dict[str, Any]:
        return service.update_settings(model_id, update)

    @app.post("/analysis-runs", response_model=RunState, status_code=202)
    def submit(submission: RunSubmission, request: Request, response: Response) -> RunState:
        if "submission_key" in submission.model_fields_set and submission.submission_key is None:
            raise TokenScopeError("INVALID_REQUEST", "Submission key cannot be null", 422)
        response.headers["X-TokenScope-Instance-Id"] = service.views.guard(
            request.headers.get("x-tokenscope-instance-id")
        )
        response.headers["Cache-Control"] = "no-store"
        return service.submit(submission)

    @app.get("/analysis-runs/{run_id}", response_model=RunState)
    def run(run_id: str, request: Request, response: Response) -> RunState:
        response.headers["X-TokenScope-Instance-Id"] = service.views.guard(
            request.headers.get("x-tokenscope-instance-id")
        )
        response.headers["Cache-Control"] = "no-store"
        return service.control.run(run_id)

    @app.get("/analysis-runs/{run_id}/metrics")
    def metrics(
        run_id: str, appid: str | None = None, offset: int = 0, limit: int = 100
    ) -> dict[str, Any]:
        return service.metrics(run_id, appid, offset, limit)

    @app.get("/analysis-runs/{run_id}/length-histograms")
    def histograms(run_id: str, appid: str, bin_width: int = 5000) -> dict[str, Any]:
        return service.histograms(run_id, appid, bin_width)

    @app.get("/analysis-runs/{run_id}/lengths")
    def lengths(
        run_id: str,
        appid: str,
        metric: str = "prompt_tokens",
        lower: int = 0,
        upper: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        return service.lengths(run_id, appid, metric, lower, upper, offset, limit)

    @app.get("/analysis-runs/{run_id}/signals")
    def signals(run_id: str) -> dict[str, Any]:
        return dict(run_id=run_id, signals=service.control.signals(run_id))

    @app.get("/threshold-rules")
    def rules(model_id: str | None = None) -> dict[str, Any]:
        return dict(rules=service.control.rules(model_id))

    @app.put("/threshold-rules")
    def update_rule(update: RuleUpdate) -> dict[str, Any]:
        return service.control.update_rule(update)

    install_openapi(app)
    # Mount last so API/health/error semantics win over the static hash-routed UI.
    if viewer_root is not None:
        app.mount("/", StaticFiles(directory=viewer_root, html=True), name="viewer")
    return app
