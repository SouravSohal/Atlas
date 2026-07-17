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

        path = scope.get("path", "")
        # Apply a relaxed CSP specifically for API documentation pages, keeping production endpoints strictly protected
        if path in ("/docs", "/redoc", "/openapi.json"):
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "connect-src 'self'"
            )
        else:
            csp = "default-src 'self'"

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers_mut = MutableHeaders(raw=message.setdefault("headers", []))
                headers_mut["X-Frame-Options"] = "DENY"
                headers_mut["X-Content-Type-Options"] = "nosniff"
                headers_mut["X-XSS-Protection"] = "1; mode=block"
                headers_mut["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
                headers_mut["Content-Security-Policy"] = csp
                headers_mut["Referrer-Policy"] = "strict-origin-when-cross-origin"
            await send(message)

        await self.app(scope, receive, send_wrapper)
