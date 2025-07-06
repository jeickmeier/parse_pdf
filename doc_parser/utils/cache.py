"""Caching utilities for parsed documents.

This module provides CacheManager for persistent JSON-based caching of parser results,
with optional TTL support, and lightweight functional helpers for simple cache operations.

Classes:
    CacheManager: Manages cache entries with TTL, metadata, and file I/O.

Functions:
    cache_get(manager, key): Async helper to retrieve a cached entry.
    cache_set(manager, key, data): Async helper to store a cache entry.

Examples:
    >>> import asyncio
    >>> from pathlib import Path
    >>> from datetime import timedelta
    >>> from doc_parser.utils.cache import CacheManager, cache_set, cache_get
    >>> cm = CacheManager(Path("cache_dir"), ttl=timedelta(seconds=60))
    >>> await cache_set(cm, "test", {"foo": "bar"})
    >>> data = await cache_get(cm, "test")
    >>> print(data)
    {'foo':'bar'}
"""

import asyncio
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any, Any as _Any, cast

import aiofiles

from doc_parser.core.exceptions import CacheError


class CacheManager:
    """Manages JSON file caching for parsed documents with optional expiration (TTL).

    Attributes:
        cache_dir (Path): Directory where cache files are stored (auto-created).
        ttl (Optional[timedelta]): Time-to-live for entries; None for no expiration.

    Methods:
        get(key) -> Optional[Dict[str, Any]]: Retrieve cached data or None if missing/expired.
        set(key, data): Store data under the key with metadata.
        delete(key): Remove cache entry and metadata.
        clear(): Delete all cache files in the cache_dir.
        get_size() -> int: Return total size of cache files in bytes.

    Examples:
        >>> import asyncio
        >>> from pathlib import Path
        >>> from datetime import timedelta
        >>> from doc_parser.utils.cache import CacheManager
        >>> cm = CacheManager(Path("cache"), ttl=timedelta(minutes=5))
        >>> await cm.set("a", {"x": 1})
        >>> d = await cm.get("a")
        >>> print(d)
        {'x':1}
    """

    def __init__(self, cache_dir: Path, ttl: timedelta | None = None):
        """Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files
            ttl: Time to live for cache entries (None for no expiration)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self._lock = asyncio.Lock()

    def _get_cache_path(self, key: str) -> Path:
        """Get path for cache file."""
        return self.cache_dir / f"{key}.json"

    def _get_metadata_path(self, key: str) -> Path:
        """Get path for cache metadata file."""
        return self.cache_dir / f"{key}.meta.json"

    async def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached data for a given key.

        Args:
            key (str): Unique cache key.

        Returns:
            Optional[Dict[str, Any]]: Cached data dict or None if missing/expired.

        Example:
            >>> data = await cm.get("test")
        """
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        if not cache_path.exists():
            return None

        try:
            # Check expiration
            if self.ttl and meta_path.exists():
                async with aiofiles.open(meta_path) as f:
                    metadata = json.loads(await f.read())

                created = datetime.fromisoformat(metadata["created"])
                if datetime.now() - created > self.ttl:
                    await self.delete(key)
                    return None

            # Read cached data
            async with aiofiles.open(cache_path) as f:
                data = json.loads(await f.read())

            return cast("dict[str, Any]", data)
        except (OSError, json.JSONDecodeError) as e:
            raise CacheError(f"Failed to read cache: {e}") from e

    async def set(self, key: str, data: dict[str, Any]) -> None:
        """Persist *data* in *manager* under *key*."""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        try:
            async with self._lock:
                # Write data
                async with aiofiles.open(cache_path, "w") as f:
                    await f.write(json.dumps(data, indent=2, default=str))

                # Write metadata
                metadata = {
                    "created": datetime.now().isoformat(),
                    "key": key,
                }
                async with aiofiles.open(meta_path, "w") as f:
                    await f.write(json.dumps(metadata, indent=2))
        except (OSError, TypeError) as e:
            raise CacheError(f"Failed to write cache: {e}") from e

    async def delete(self, key: str) -> None:
        """Delete cached data."""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        if cache_path.exists():
            cache_path.unlink()
        if meta_path.exists():
            meta_path.unlink()

    async def clear(self) -> None:
        """Clear all cached data."""
        for path in self.cache_dir.glob("*.json"):
            path.unlink()

    async def get_size(self) -> int:
        """Get total cache size in bytes."""
        return sum(p.stat().st_size for p in self.cache_dir.glob("*.json"))


# ---------------------------------------------------------------------------
# Lightweight functional helpers - preferred over calling ``CacheManager``
# methods directly from client code.  They keep call-sites concise and decouple
# them from the underlying implementation should we swap backends in the future.
# ---------------------------------------------------------------------------


async def cache_get(manager: "CacheManager", key: str) -> dict[str, Any] | None:
    """Async helper to return cached data for a key using the specified manager.

    Args:
        manager (CacheManager): CacheManager instance.
        key (str): Cache key.

    Returns:
        Optional[Dict[str, Any]]: Cached data or None.

    Example:
        >>> data = await cache_get(cm, "test")
    """
    return await manager.get(key)


async def cache_set(manager: "CacheManager", key: str, data: dict[str, _Any]) -> None:
    """Async helper to store data in the cache under the specified key.

    Args:
        manager (CacheManager): CacheManager instance.
        key (str): Cache key.
        data (Dict[str, Any]): JSON-serializable data to cache.

    Example:
        >>> await cache_set(cm, "test", {"foo": "bar"})
    """
    await manager.set(key, data)


# ------------------------------------------------------------------
# Public exports
# ------------------------------------------------------------------
__all__ = [
    "CacheManager",
    "cache_get",
    "cache_set",
]
