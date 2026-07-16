from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send


class SecurityHeadersMiddleware:
    """Middleware that appends security headers to all HTTP responses."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            # Direct pass-through for WebSockets to avoid connection drops
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers_mut = MutableHeaders(raw=message.setdefault("headers", []))
                headers_mut["X-Frame-Options"] = "DENY"
                headers_mut["X-Content-Type-Options"] = "nosniff"
                headers_mut["X-XSS-Protection"] = "1; mode=block"
                headers_mut["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
                headers_mut["Content-Security-Policy"] = "default-src 'self'"
                headers_mut["Referrer-Policy"] = "strict-origin-when-cross-origin"
            await send(message)

        await self.app(scope, receive, send_wrapper)
