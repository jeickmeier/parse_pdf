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
from typing import TYPE_CHECKING, Any, TypeVar, cast

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
        batch_size: int | None = None,
        process_func: Callable[[list[T]], Awaitable[list[Any]]] | None = None,
        timeout: float = 1.0,
        max_concurrent: int | None = None,
        show_progress: bool = True,
    ) -> None:
        """Create an AsyncBatcher.

        This unified helper can be used in **two** distinct modes:

        1. *Batch mode* - supply ``batch_size`` **and** ``process_func`` then call
           :py:meth:`add` to stream items that will be processed in batches.
        2. *Gather mode* - omit ``batch_size``/``process_func`` and call
           :py:meth:`gather` with an iterable of awaitable *callables* (or
           awaitables) to run them with optional concurrency limiting and a
           progress bar.

        Args:
            batch_size: Maximum number of items per batch. Required for *batch
                mode*.
            process_func: Coroutine to process a list of items. Required for
                *batch mode*.
            timeout: Maximum seconds to wait before processing a partial batch.
            max_concurrent: Limit on simultaneously awaited tasks when using
                :py:meth:`gather` or when this object is used as an async
                context-manager.
            show_progress: Whether to render a progress bar using
                ``tqdm.asyncio`` when calling :py:meth:`gather`.
        """
        # --- Batch-specific attributes
        self.batch_size = batch_size
        self.process_func = process_func
        self.timeout = timeout

        # Internal state for batch mode
        self._queue: deque[tuple[int, Any, asyncio.Future[Any]]] = deque()
        self._lock = asyncio.Lock()
        self._task: asyncio.Task[Any] | None = None

        # --- Concurrency control
        self._semaphore: asyncio.Semaphore | None = asyncio.Semaphore(max_concurrent) if max_concurrent else None

        # UI helpers
        self._show_progress = show_progress

    async def add(self, item: T) -> Any:
        """Add an item to the batch and await its processed result.

        This method is only available in *batch mode* (when both
        ``batch_size`` and ``process_func`` were provided at construction
        time). Attempting to call it otherwise will raise ``RuntimeError``.

        Args:
            item: Item to be queued for processing.

        Returns:
            The result corresponding to the provided *item* once
            ``process_func`` has processed the batch it belongs to.
        """
        if self.batch_size is None or self.process_func is None:
            raise RuntimeError("'add' can only be used when 'batch_size' and 'process_func' are set.")

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
        # Assert required attributes for batch mode to satisfy type checker.
        assert self.batch_size is not None, "batch_size should be set in batch mode"  # noqa: S101
        assert self.process_func is not None, "process_func should be set in batch mode"  # noqa: S101

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

    # ------------------------------------------------------------------
    # Concurrency helpers
    # ------------------------------------------------------------------

    async def __aenter__(self) -> AsyncBatcher:
        """Enter the asynchronous context.

        If *max_concurrent* was supplied, this acquires the semaphore slot so
        that nested awaits can be rate-limited. When *max_concurrent* is *None*
        the context-manager is effectively a no-op.
        """
        if self._semaphore is not None:
            await self._semaphore.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit the asynchronous context and release any acquired semaphore."""
        if self._semaphore is not None:
            self._semaphore.release()

    async def gather(
        self,
        tasks: list[Callable[[], Awaitable[Any]]] | list[Awaitable[Any]],
        *,
        desc: str = "Processing",
    ) -> list[Any]:
        """Concurrently run *tasks* with optional throttling & progress bar.

        Accepts either a list of *awaitables* **or** a list of zero-argument
        async callables. The latter form enables internal semaphore wrapping
        without forcing the caller to write wrapper lambdas themselves.
        """
        from tqdm.asyncio import tqdm  # Local import to avoid heavy dep at runtime

        awaitables: list[Awaitable[Any]] = []

        if not tasks:
            return []

        # Detect whether the first element is awaitable or callable
        first = tasks[0]

        if self._semaphore is None:
            # No concurrency constraint; convert tasks directly
            awaitables = [t() if callable(t) else t for t in tasks]
        # Wrap each task in semaphore guard if callable
        elif callable(first):

            async def _wrap(task: Callable[[], Awaitable[Any]]) -> Any:
                async with self:
                    return await task()

            awaitables = [_wrap(cast("Callable[[], Awaitable[Any]]", t)) for t in tasks]
        else:
            # Provided items are awaitables; we cannot wrap easily - we assume
            # caller wants no additional throttling. Warn via RuntimeError.
            raise RuntimeError(
                "When using 'gather' with 'max_concurrent', provide a list of callables, not awaitables."
            )

        if self._show_progress:
            # tqdm.asyncio.gather accepts **kwargs such as desc
            return await tqdm.gather(*awaitables, desc=desc)

        # Fall back to standard asyncio.gather (no desc parameter)
        return await asyncio.gather(*awaitables)

    # ------------------------------------------------------------------
    # Static utilities (moved from async_helpers)
    # ------------------------------------------------------------------

    @staticmethod
    async def run_with_retry(
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        retry_exceptions: tuple[type[Exception], ...] = (
            RuntimeError,
            ValueError,
            ConnectionError,
            TimeoutError,
        ),
        **kwargs: Any,
    ) -> Any:
        """Run *func* with retry logic and exponential backoff.

        This is a lift-and-shift of ``run_with_retry`` from the previous
        *async_helpers* module so callers can simply switch imports.
        """
        last_exception: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except retry_exceptions as exc:
                last_exception = exc
                if attempt < max_retries:
                    wait_time = backoff_factor**attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise last_exception from last_exception


# ----------------------------------------------------------------------
# Backwards-compat alias for legacy RateLimiter import sites
# ----------------------------------------------------------------------


class RateLimiter:  # pylint: disable=too-few-public-methods
    """Backwards-compatibility wrapper emulating the original *RateLimiter*.

    Internally this delegates to :class:`AsyncBatcher` configured with only
    the *max_concurrent* semaphore limiter. Users can therefore keep their
    existing ``async with RateLimiter(...):`` callsites unchanged.
    """

    def __init__(self, max_concurrent: int = 10) -> None:
        """Create a *RateLimiter* wrapper.

        Args:
            max_concurrent: Maximum concurrent operations permitted inside the
                managed context.
        """
        self._limiter = AsyncBatcher(max_concurrent=max_concurrent)

    async def __aenter__(self) -> RateLimiter:
        """Enter the *RateLimiter* context by delegating to the internal limiter."""
        await self._limiter.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit the context and release the internal semaphore."""
        await self._limiter.__aexit__(exc_type, exc_val, exc_tb)


# ------------------------------------------------------------------
# Public exports
# ------------------------------------------------------------------
__all__ = [
    "AsyncBatcher",
    "RateLimiter",
]
