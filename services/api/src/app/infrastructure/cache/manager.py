import asyncio
import time
from typing import Any

import structlog
from fastapi import Query, Request

logger = structlog.get_logger()

class CacheEntry:
    def __init__(self, value: Any, ttl_seconds: float) -> None:
        self.value = value
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

class LightweightCacheManager:
    """Lightweight in-memory cache manager supporting TTL, cache invalidation, and manual bypass."""
    def __init__(self) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """Retrieves an entry if it exists and has not expired."""
        async with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry.is_expired():
                logger.debug("Cache entry expired", key=key)
                del self._cache[key]
                return None
            logger.debug("Cache hit", key=key)
            return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: float) -> None:
        """Saves a value to the cache with a TTL."""
        async with self._lock:
            self._cache[key] = CacheEntry(value, ttl_seconds)
            logger.debug("Cache entry set", key=key, ttl_seconds=ttl_seconds)

    async def invalidate(self, key: str) -> None:
        """Deletes a specific key from the cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.info("Cache key invalidated", key=key)

    async def invalidate_prefix(self, prefix: str) -> None:
        """Invalidates all cache keys that start with a prefix."""
        async with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._cache[k]
            logger.info("Cache prefix invalidated", prefix=prefix, count=len(keys_to_delete))

    async def clear(self) -> None:
        """Clears all cached entries."""
        async with self._lock:
            self._cache.clear()
            logger.info("Entire cache cleared")

# Global singleton
cache_manager = LightweightCacheManager()

def check_cache_bypass(request: Request, refresh: bool = Query(False)) -> bool:
    """FastAPI dependency to detect if the client requested cache bypass/manual refresh."""
    if refresh:
        return True
    cache_control = request.headers.get("Cache-Control", "")
    if "no-cache" in cache_control or "no-store" in cache_control:
        return True
    return False
