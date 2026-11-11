"""Pre-parse gate: old diagnostics are read-only; new intents are small references."""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class DiagnosticPolicy3:
    def __init__(self, app: ASGIApp, max_intent_bytes: int = 65536) -> None:
        self.app, self.maximum = app, max_intent_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or not scope["path"].startswith("/diagnostics/")
            or scope["method"] in ("GET", "HEAD", "OPTIONS")
        ):
            await self.app(scope, receive, send)
            return
        if not scope["path"].startswith("/diagnostics/v3/"):
            response = JSONResponse(
                {
                    "error": {
                        "code": "LEGACY_DIAGNOSTICS_READ_ONLY",
                        "message": "Use bounded V3 low-hit diagnostics; Token analysis is dormant",
                    }
                },
                status_code=409,
            )
            await response(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.maximum:
                response = JSONResponse(
                    {
                        "error": {
                            "code": "INTENT_BYTE_LIMIT",
                            "message": "Diagnostic intent is too large",
                        }
                    },
                    status_code=413,
                )
                await response(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay() -> Message:
            nonlocal delivered
            if delivered:
                return await receive()
            delivered = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        await self.app(scope, replay, send)
