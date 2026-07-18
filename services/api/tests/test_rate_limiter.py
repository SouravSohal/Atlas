from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Request

from app.infrastructure.security.rate_limiter import (
    InMemorySlidingWindowLimiter,
    RateLimiterDependency,
    parse_rate,
)


def test_parse_rate() -> None:
    assert parse_rate("5/second") == (5, 1)
    assert parse_rate("10/minute") == (10, 60)
    assert parse_rate("20/hour") == (20, 3600)
    assert parse_rate("30/day") == (30, 86400)
    assert parse_rate("invalid-string") == (60, 60)

@pytest.mark.asyncio
async def test_sliding_window_limiter() -> None:
    limiter = InMemorySlidingWindowLimiter()
    key = "test-key"
    
    # Allow 2 requests per 5 seconds
    is_limited, retry = await limiter.is_rate_limited(key, 2, 5)
    assert not is_limited
    assert retry == 0

    is_limited, retry = await limiter.is_rate_limited(key, 2, 5)
    assert not is_limited
    assert retry == 0

    # Third request exceeds limit
    is_limited, retry = await limiter.is_rate_limited(key, 2, 5)
    assert is_limited
    assert retry > 0

@pytest.mark.asyncio
async def test_rate_limiter_dependency() -> None:
    # Arrange
    dep = RateLimiterDependency("auth")
    
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock()
    mock_request.state.user = None
    mock_request.headers = {"Authorization": "Bearer some-fake-token"}
    
    mock_settings = MagicMock()
    mock_settings.rate_limits.auth = "1/minute"
    mock_settings.rate_limits.default = "60/minute"
    
    # Clear limiter store first to avoid test pollution
    from app.infrastructure.security.rate_limiter import _limiter_store
    _limiter_store._windows.clear()

    # Act & Assert
    # First request should pass
    await dep(request=mock_request, settings=mock_settings)

    # Second request should trigger 429
    with pytest.raises(HTTPException) as exc_info:
        await dep(request=mock_request, settings=mock_settings)
        
    assert exc_info.value.status_code == 429
    assert exc_info.value.headers["Retry-After"] is not None
    assert "Too many requests" in exc_info.value.detail
