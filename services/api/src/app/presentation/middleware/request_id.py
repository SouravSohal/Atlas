from collections.abc import MutableMapping
from typing import Any
import uuid

import structlog
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send

logger = structlog.get_logger()

class RequestIdMiddleware:
    """Middleware that injects a unique X-Request-ID header into every incoming request and response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            # Direct pass-through for WebSockets to avoid connection drops
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = headers.get("X-Request-ID") or headers.get("x-request-id") or str(uuid.uuid4())

        # Bind request_id to structlog context
        structlog.contextvars.bind_contextvars(request_id=request_id)

        async def send_wrapper(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.start":
                headers_mut = MutableHeaders(raw=message.setdefault("headers", []))
                headers_mut["X-Request-ID"] = request_id
            await send(message)

        await self.app(scope, receive, send_wrapper)
