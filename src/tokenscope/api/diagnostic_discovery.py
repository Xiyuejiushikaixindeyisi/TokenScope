"""Independent, additive discovery protocol. Frozen diagnostic v1 remains unchanged."""

import asyncio
import json
import threading
import time
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Depends, Header
from starlette.responses import JSONResponse, StreamingResponse
from starlette.types import Send

from tokenscope.analysis_common.discovery import VERSION, Discovery
from tokenscope.analysis_common.discovery_contracts import schemas
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.errors import TokenScopeError


def frame(event: str, payload: object, event_id: str | None = None) -> bytes:
    prefix = "" if event_id is None else f"id: {event_id}\n"
    return (
        prefix + f"event: {event}\ndata: " + json.dumps(payload, ensure_ascii=False) + "\n\n"
    ).encode()


class DiscoveryResponse(StreamingResponse):
    def __init__(self, reader: Discovery, cursor: str, slots: threading.BoundedSemaphore) -> None:
        self.slots = slots
        super().__init__(
            stream(reader, cursor),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )

    async def stream_response(self, send: Send) -> None:
        async def bounded(message: Any) -> None:
            async with asyncio.timeout(10):
                await send(message)

        await super().stream_response(bounded)

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if not self.slots.acquire(blocking=False):
            await JSONResponse(
                {
                    "error": {
                        "code": "DISCOVERY_STREAM_CAPACITY",
                        "message": "Too many discovery subscriptions",
                    }
                },
                status_code=503,
            )(scope, receive, send)
            return
        try:
            await super().__call__(scope, receive, send)
        finally:
            self.slots.release()


async def stream(reader: Discovery, cursor: str) -> AsyncIterator[bytes]:
    yield b"retry: 3000\n\n"
    heartbeat = time.monotonic()
    while True:
        try:
            batch = await asyncio.to_thread(reader.events, cursor)
        except TokenScopeError as exc:
            yield frame(
                "reset",
                {
                    "version": VERSION,
                    "service_instance_id": reader.instance_id,
                    "reason": exc.code,
                    "catalog_url": "/diagnostics/discovery/catalog",
                },
            )
            return
        for item in batch["items"]:
            yield frame(
                "terminal",
                {"version": VERSION, "service_instance_id": reader.instance_id, **item},
                item["event_id"],
            )
        cursor = batch["cursor"]
        if not batch["items"]:
            if time.monotonic() - heartbeat >= 20:
                yield b": heartbeat\n\n"
                heartbeat = time.monotonic()
            await asyncio.sleep(1)


def router(service: DiagnosticService, instance_id: str) -> APIRouter:
    root = APIRouter(prefix="/diagnostics/discovery")
    reader = Discovery(service.store, instance_id)
    slots = threading.BoundedSemaphore(64)

    @root.get("/capabilities")
    def capabilities() -> dict[str, object]:
        return {
            "version": VERSION,
            "service_instance_id": instance_id,
            "catalog_url": "/diagnostics/discovery/catalog",
            "events_url": "/diagnostics/discovery/events",
            "terminal_url_template": "/diagnostics/discovery/tasks/{task_id}/terminal",
            "transport": "fetch-sse",
            "retention": "no_automatic_deletion",
            "default_policy": "ready_analysis_per_binding_direction_publication_order",
            "schemas": schemas(),
        }

    def identity(x_tokenscope_service_instance: str = Header()) -> None:
        if x_tokenscope_service_instance != instance_id:
            raise TokenScopeError("SERVICE_INSTANCE_MISMATCH", "Diagnostic instance differs", 409)

    api = APIRouter(dependencies=[Depends(identity)])

    @api.get("/catalog")
    def catalog(
        snapshot: str | None = None, after: str = "0", limit: int = 50
    ) -> dict[str, object]:
        return reader.catalog(snapshot, after, limit)

    @api.get("/tasks/{task_id}/terminal")
    def terminal(task_id: str) -> dict[str, object]:
        return reader.terminal(task_id)

    @api.get("/events")
    def events(cursor: str) -> StreamingResponse:
        # All resume cursors are explicit query values; fetch carries the instance header.
        # A bad cursor receives an SSE reset, never silent tail-only resubscription.
        return DiscoveryResponse(reader, cursor, slots)

    root.include_router(api)
    return root
