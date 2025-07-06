"""Caching utilities for document parsers."""

import json
import asyncio
from pathlib import Path
from typing import Any, Optional, Dict, cast, Dict as _Dict, Any as _Any
import aiofiles
from datetime import datetime, timedelta

from ..core.exceptions import CacheError


class CacheManager:
    """Manages caching for parsed documents."""

    def __init__(self, cache_dir: Path, ttl: Optional[timedelta] = None):
        """
        Initialize cache manager.

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

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        if not cache_path.exists():
            return None

        try:
            # Check expiration
            if self.ttl and meta_path.exists():
                async with aiofiles.open(meta_path, "r") as f:
                    metadata = json.loads(await f.read())

                created = datetime.fromisoformat(metadata["created"])
                if datetime.now() - created > self.ttl:
                    await self.delete(key)
                    return None

            # Read cached data
            async with aiofiles.open(cache_path, "r") as f:
                data = json.loads(await f.read())

            return cast(Dict[str, Any], data)

        except Exception as e:
            raise CacheError(f"Failed to read cache: {e}")

    async def set(self, key: str, data: Dict[str, Any]) -> None:
        """
        Set cached data.

        Args:
            key: Cache key
            data: Data to cache
        """
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

        except Exception as e:
            raise CacheError(f"Failed to write cache: {e}")

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
        total = 0
        for path in self.cache_dir.glob("*.json"):
            total += path.stat().st_size
        return total


# ---------------------------------------------------------------------------
# Lightweight functional helpers – preferred over calling ``CacheManager``
# methods directly from client code.  They keep call-sites concise and decouple
# them from the underlying implementation should we swap backends in the future.
# ---------------------------------------------------------------------------


async def cache_get(manager: "CacheManager", key: str) -> Optional[Dict[str, Any]]:  # noqa: D401
    """Return cached data for *key* using *manager* (or ``None``)."""
    return await manager.get(key)


async def cache_set(manager: "CacheManager", key: str, data: _Dict[str, _Any]) -> None:  # noqa: D401
    """Persist *data* in *manager* under *key*."""
    await manager.set(key, data)
