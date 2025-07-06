"""Asynchronous batching utility.

```
 +-----------+     add(item)      +--------------+
 | Producer  |  ----------------> | AsyncBatcher |
 +-----------+                    +--------------+
       ^                                  |
       |   batched process_func()          v
       |<------------------------------------ (results)
```

AsyncBatcher collects items up to *batch_size* or *timeout* and then forwards
that batch to a user-supplied ``process_func`` coroutine.  Callers simply
``await batcher.add(item)`` and receive the processed result for that item,
abstracting away all concurrency & batching concerns.
"""

from __future__ import annotations

import asyncio
from collections import deque
from typing import Any, Awaitable, Callable, Deque, List, Optional, Tuple, TypeVar

T = TypeVar("T")


class AsyncBatcher:  # pylint: disable=too-many-instance-attributes
    """Batch async operations for efficiency."""

    def __init__(
        self,
        batch_size: int,
        process_func: Callable[[List[T]], Awaitable[List[Any]]],
        timeout: float = 1.0,
    ) -> None:
        self.batch_size = batch_size
        self.process_func = process_func
        self.timeout = timeout
        self._queue: Deque[Tuple[int, Any, asyncio.Future[Any]]] = deque()
        self._lock = asyncio.Lock()
        self._task: Optional[asyncio.Task[Any]] = None

    async def add(self, item: T) -> Any:
        """Add *item* to the batch and return its processed result."""
        item_id = id(item)
        future: asyncio.Future[Any] = asyncio.Future()

        async with self._lock:
            self._queue.append((item_id, item, future))

            if self._task is None or self._task.done():
                self._task = asyncio.create_task(self._process_batches())

        return await future

    # ------------------------------------------------------------------
    # Internal machinery
    # ------------------------------------------------------------------
    async def _process_batches(self) -> None:  # noqa: D401
        while self._queue:
            batch: List[Any] = []
            futures: List[Tuple[int, asyncio.Future[Any]]] = []

            async with self._lock:
                while self._queue and len(batch) < self.batch_size:
                    item_id, item, future = self._queue.popleft()
                    batch.append(item)
                    futures.append((item_id, future))

            if batch:
                try:
                    results = await self.process_func(batch)
                    for i, (_, future) in enumerate(futures):
                        if i < len(results):
                            future.set_result(results[i])
                        else:
                            future.set_exception(Exception("No result for item"))
                except Exception as exc:  # pragma: no cover
                    for _, future in futures:
                        future.set_exception(exc)

            await asyncio.sleep(0.01)
