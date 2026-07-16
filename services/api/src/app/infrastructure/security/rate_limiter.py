import re
import time
import asyncio
import hashlib
from typing import Any, Dict, List, Tuple
import structlog
from fastapi import Request, HTTPException, status, Depends
from dependency_injector.wiring import Provide, inject

from app.config import Settings
from app.dependencies.container import ApplicationContainer

logger = structlog.get_logger()

def parse_rate(rate_str: str) -> Tuple[int, int]:
    """Parses a rate limit string like '5/minute' into (requests_count, duration_in_seconds)."""
    match = re.match(r"^(\d+)\s*/\s*(second|minute|hour|day)$", rate_str.strip().lower())
    if not match:
        return 60, 60
    count = int(match.group(1))
    unit = match.group(2)
    if unit == "second":
        return count, 1
    elif unit == "minute":
        return count, 60
    elif unit == "hour":
        return count, 3600
    elif unit == "day":
        return count, 86400
    return count, 60

class InMemorySlidingWindowLimiter:
    """A thread-safe in-memory sliding window rate limiter."""
    def __init__(self) -> None:
        self._windows: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()

    async def is_rate_limited(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """Checks if a request is rate limited for the given key.

        Returns (is_limited, retry_after_seconds).
        """
        async with self._lock:
            now = time.time()
            cutoff = now - window_seconds

            # Retrieve and filter history
            history = self._windows.get(key, [])
            history = [ts for ts in history if ts > cutoff]

            if len(history) >= max_requests:
                oldest_request = history[0]
                retry_after = int(window_seconds)
                if oldest_request > cutoff:
                    retry_after = int((oldest_request + window_seconds) - now)
                retry_after = max(1, retry_after)
                self._windows[key] = history
                return True, retry_after

            # Record hit
            history.append(now)
            self._windows[key] = history
            return False, 0

_limiter_store = InMemorySlidingWindowLimiter()

class RateLimiterDependency:
    """FastAPI Dependency for rate limiting based on client IP or User ID."""
    def __init__(self, limit_type: str) -> None:
        self.limit_type = limit_type

    @inject
    async def __call__(
        self,
        request: Request,
        settings: Settings = Depends(Provide[ApplicationContainer.config]),
    ) -> None:
        rate_limits = settings.rate_limits
        rate_str = getattr(rate_limits, self.limit_type, rate_limits.default)
        max_requests, window_seconds = parse_rate(rate_str)

        # 1. Identify requester (User ID or IP/token hash fallback)
        requester_id = None

        if hasattr(request.state, "user") and request.state.user:
            requester_id = f"user:{request.state.user.id}"
        else:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                requester_id = f"token:{hashlib.sha256(token.encode('utf-8')).hexdigest()}"

        if not requester_id:
            # IP-based fallback (Cloud Run compatible)
            client_host = request.client.host if request.client else "127.0.0.1"
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_host = forwarded_for.split(",")[0].strip()
            requester_id = f"ip:{client_host}"

        # 2. Check rate limit
        limit_key = f"{self.limit_type}:{requester_id}"
        is_limited, retry_after = await _limiter_store.is_rate_limited(limit_key, max_requests, window_seconds)

        if is_limited:
            logger.warning(
                "Rate limit exceeded",
                limit_type=self.limit_type,
                requester_id=requester_id,
                retry_after=retry_after,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )
