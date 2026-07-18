import asyncio
from unittest.mock import MagicMock

import pytest
from fastapi import Request

from app.infrastructure.cache.manager import (
    cache_manager,
    check_cache_bypass,
)


@pytest.mark.asyncio
async def test_cache_set_get_ttl() -> None:
    # Clear cache
    await cache_manager.clear()
    
    # Set entry with 1 second TTL
    await cache_manager.set("test:ttl", {"data": "ok"}, 1.0)
    
    # Retrieve
    val = await cache_manager.get("test:ttl")
    assert val == {"data": "ok"}
    
    # Wait for expiry
    await asyncio.sleep(1.1)
    
    # Should be None/expired
    val_expired = await cache_manager.get("test:ttl")
    assert val_expired is None

@pytest.mark.asyncio
async def test_cache_invalidate_and_prefix() -> None:
    await cache_manager.clear()
    
    await cache_manager.set("test:1", "val1", 10.0)
    await cache_manager.set("test:2", "val2", 10.0)
    await cache_manager.set("other:key", "val3", 10.0)
    
    # Invalidate prefix
    await cache_manager.invalidate_prefix("test:")
    
    assert await cache_manager.get("test:1") is None
    assert await cache_manager.get("test:2") is None
    assert await cache_manager.get("other:key") == "val3"

def test_check_cache_bypass() -> None:
    # 1. No bypass
    req1 = MagicMock(spec=Request)
    req1.headers = {}
    assert not check_cache_bypass(req1, refresh=False)
    
    # 2. Bypass via query param
    assert check_cache_bypass(req1, refresh=True)
    
    # 3. Bypass via Cache-Control header
    req2 = MagicMock(spec=Request)
    req2.headers = {"Cache-Control": "no-cache"}
    assert check_cache_bypass(req2, refresh=False)
