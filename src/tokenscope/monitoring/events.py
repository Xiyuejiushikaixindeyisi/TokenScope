"""Bounded persistent event replay. No transaction survives a network await."""

import asyncio
import re
import threading
import time
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

from starlette.responses import StreamingResponse
from starlette.types import Send

from tokenscope.errors import TokenScopeError
from tokenscope.monitoring import publications
from tokenscope.monitoring.view_models import canonical


class PublicationEventReader:
    def __init__(
        self,
        control: Any,
        *,
        heartbeat: float = 20,
        poll: float = 0.1,
        capacity: int = 64,
        send_timeout: float = 10,
    ) -> None:
        self.control = control
        self.heartbeat, self.poll, self.capacity, self.send_timeout = (
            heartbeat,
            poll,
            capacity,
            send_timeout,
        )
        self.active = 0
        self.lock = threading.Lock()
        self.read_lock = threading.Lock()
        self.empty_cache: tuple[float, str, dict[str, Any], int] | None = None

    def read(
        self, cursor: str | None
    ) -> tuple[dict[str, Any], int, str | None, list[dict[str, Any]]]:
        # Empty-tail readers share one bounded freshness window. Replay rows and reset
        # decisions are never cached; durable SQLite remains the event source of truth.
        with self.read_lock:
            cached = self.empty_cache
            if (
                cursor is not None
                and cached is not None
                and cached[1] == cursor
                and time.monotonic() - cached[0] < self.poll
            ):
                return cached[2], cached[3], None, []
            result = self._read(cursor)
            if cursor is not None and result[2] is None and not result[3]:
                self.empty_cache = (time.monotonic(), cursor, result[0], result[1])
            return result

    def _read(
        self, cursor: str | None
    ) -> tuple[dict[str, Any], int, str | None, list[dict[str, Any]]]:
        with self.control.connect() as db:
            db.execute("BEGIN")
            ident = publications.identity(db)
            high = publications.highwater(db)
            floor = db.execute("SELECT event_floor FROM service_metadata WHERE id=1").fetchone()[0]
            after = high
            reason = None
            if cursor is not None:
                parts = cursor.rsplit(":", 1)
                if (
                    len(parts) != 2
                    or len(parts[1]) > 20
                    or not re.fullmatch(r"0|[1-9][0-9]*", parts[1])
                ):
                    reason = "invalid_cursor"
                elif parts[0] != ident["service_instance_id"]:
                    reason = "instance_changed"
                else:
                    after = int(parts[1])
                    if after > high:
                        reason = "future_cursor"
                    elif after < floor:
                        reason = "expired"
            rows = (
                []
                if reason
                else [
                    dict(row)
                    for row in db.execute(
                        "SELECT seq,kind,payload FROM ui_events WHERE seq>? ORDER BY seq LIMIT 128",
                        (after,),
                    )
                ]
            )
        return ident, after, reason, rows

    async def stream(self, cursor: str | None) -> AsyncIterator[bytes]:
        yield b"retry: 3000\n\n"
        last = time.monotonic()
        while True:
            ident, after, reason, rows = await asyncio.to_thread(self.read, cursor)
            if reason:
                value = {**ident, "reason": reason, "catalog_url": "/monitoring/catalog"}
                yield b"event: reset\ndata: " + canonical(value) + b"\n\n"
                return
            cursor = ident["service_instance_id"] + ":" + str(after)
            for row in rows:
                cursor = ident["service_instance_id"] + ":" + str(row["seq"])
                yield (
                    "id: "
                    + cursor
                    + "\nevent: "
                    + row["kind"]
                    + "\ndata: "
                    + row["payload"]
                    + "\n\n"
                ).encode()
                last = time.monotonic()
            if time.monotonic() - last >= self.heartbeat:
                yield b": heartbeat\n\n"
                last = time.monotonic()
            if not rows:
                await asyncio.sleep(self.poll)

    def reserve(self) -> None:
        with self.lock:
            if self.active >= self.capacity:
                raise TokenScopeError("SSE_CAPACITY_EXCEEDED", "Too many event connections", 503)
            self.active += 1

    def release(self) -> None:
        with self.lock:
            self.active -= 1

    def prune(self, *, max_rows: int = 100000, days: int = 7) -> None:
        if max_rows < 1 or days < 0:
            raise ValueError("Invalid retention")
        cutoff = (datetime.now(UTC) - timedelta(days=days)).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        ) + "000Z"
        with self.control.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            aged = db.execute(
                "SELECT coalesce(max(seq),0) FROM ui_events WHERE created_at<?", (cutoff,)
            ).fetchone()[0]
            overflow = db.execute(
                "SELECT seq FROM ui_events ORDER BY seq DESC LIMIT 1 OFFSET ?", (max_rows,)
            ).fetchone()
            boundary = max(aged, overflow[0] if overflow else 0)
            if boundary:
                db.execute("DELETE FROM ui_events WHERE seq<=?", (boundary,))
                db.execute(
                    "UPDATE service_metadata SET event_floor=max(event_floor,?) WHERE id=1",
                    (boundary,),
                )

        with self.read_lock:
            self.empty_cache = None


class EventResponse(StreamingResponse):
    def __init__(self, reader: PublicationEventReader, cursor: str | None, instance: str) -> None:
        self.reader = reader
        super().__init__(
            reader.stream(cursor),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-store",
                "X-Accel-Buffering": "no",
                "X-TokenScope-Instance-Id": instance,
            },
        )

    async def stream_response(self, send: Send) -> None:
        async def bounded(message: Any) -> None:
            async with asyncio.timeout(self.reader.send_timeout):
                await send(message)

        await super().stream_response(bounded)

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        try:
            await super().__call__(scope, receive, send)
        finally:
            self.reader.release()
