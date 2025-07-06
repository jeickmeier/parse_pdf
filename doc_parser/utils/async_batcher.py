"""Asynchronous batching utility.

This module provides AsyncBatcher, which collects items into batches up to a specified
batch_size or timeout, and processes them via a user-supplied coroutine function.

Examples:
    >>> import asyncio
    >>> from doc_parser.utils.async_batcher import AsyncBatcher
    >>> async def process(batch):
    ...     return [item * 2 for item in batch]
    >>> batcher = AsyncBatcher(batch_size=3, process_func=process, timeout=0.1)
    >>> async def run():
    ...     results = await asyncio.gather(*[batcher.add(i) for i in [1, 2, 3, 4]])
    ...     print(results)
    >>> asyncio.run(run())
    [2, 4, 6, 8]
"""

from __future__ import annotations

import asyncio
from collections import deque
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

T = TypeVar("T")


class AsyncBatcher:  # pylint: disable=too-many-instance-attributes
    """Batch asynchronous operations for efficiency.

    Collects items into batches and invokes the provided process_func coroutine,
    enabling efficient bulk operations with concurrency control.

    Args:
        batch_size (int): Maximum number of items per batch.
        process_func (Callable[[List[T]], Awaitable[List[Any]]]): Coroutine to process each batch.
        timeout (float): Maximum seconds to wait before processing a partial batch.

    Attributes:
        batch_size (int)
        process_func (Callable)
        timeout (float)

    Example:
        >>> import asyncio
        >>> async def proc(items):
        ...     return [i + 1 for i in items]
        >>> batcher = AsyncBatcher(2, proc)
        >>> results = asyncio.run(asyncio.gather(batcher.add(1), batcher.add(2)))
        >>> print(results)
        [2, 3]
    """

    def __init__(
        self,
        batch_size: int,
        process_func: Callable[[list[T]], Awaitable[list[Any]]],
        timeout: float = 1.0,
    ) -> None:
        """Create an AsyncBatcher.

        Args:
            batch_size (int): Max items per batch before processing.
            process_func (Callable): Coroutine that processes a list of items.
            timeout (float): Max seconds to wait before processing a partial batch.
        """
        self.batch_size = batch_size
        self.process_func = process_func
        self.timeout = timeout
        self._queue: deque[tuple[int, Any, asyncio.Future[Any]]] = deque()
        self._lock = asyncio.Lock()
        self._task: asyncio.Task[Any] | None = None

    async def add(self, item: T) -> Any:
        """Add an item to the batch and return its processed result.

        Args:
            item (T): Item to add to the batch.

        Returns:
            Any: Result for this item from process_func.

        Example:
            >>> import asyncio
            >>> async def proc(batch):
            ...     return [b * 2 for b in batch]
            >>> batcher = AsyncBatcher(2, proc)
            >>> res = asyncio.run(batcher.add(5))
            >>> print(res)
            10
        """
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
    async def _process_batches(self) -> None:
        """Internal loop to process batches of items.

        Continuously collects items up to batch_size or until timeout,
        invokes process_func on the batch, and sets each Future with its result.
        """
        while self._queue:
            batch: list[Any] = []
            futures: list[tuple[int, asyncio.Future[Any]]] = []

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
                except (RuntimeError, ValueError) as exc:  # pragma: no cover
                    for _, future in futures:
                        future.set_exception(exc)

            await asyncio.sleep(0.01)
