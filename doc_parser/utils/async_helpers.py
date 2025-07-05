"""Async utility functions and classes."""

import asyncio
from collections import deque
from typing import (
    Any,
    Awaitable,
    Callable,
    Deque,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
)

T = TypeVar("T")


class RateLimiter:
    """Rate limiter for async operations."""

    def __init__(self, max_concurrent: int = 10) -> None:
        """
        Initialize rate limiter.

        Args:
            max_concurrent: Maximum concurrent operations
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self) -> "RateLimiter":
        await self.semaphore.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Optional[object],
    ) -> None:
        self.semaphore.release()


class AsyncBatcher:
    """Batch async operations for efficiency."""

    def __init__(
        self,
        batch_size: int,
        process_func: Callable[[List[T]], Awaitable[List[Any]]],
        timeout: float = 1.0,
    ) -> None:
        """
        Initialize async batcher.

        Args:
            batch_size: Maximum items per batch
            process_func: Async function to process batches
            timeout: Maximum time to wait before processing partial batch
        """
        self.batch_size = batch_size
        self.process_func = process_func
        self.timeout = timeout
        self._queue: Deque[Tuple[int, Any, asyncio.Future[Any]]] = deque()
        self._results: Dict[int, Any] = {}
        self._lock = asyncio.Lock()
        self._task: Optional[asyncio.Task[Any]] = None

    async def add(self, item: T) -> Any:
        """Add item to batch and get result."""
        item_id = id(item)
        future: asyncio.Future[Any] = asyncio.Future()

        async with self._lock:
            self._queue.append((item_id, item, future))

            if self._task is None or self._task.done():
                self._task = asyncio.create_task(self._process_batches())

        return await future

    async def _process_batches(self) -> None:
        """Process queued items in batches."""
        while self._queue:
            batch: List[Any] = []
            futures = []

            async with self._lock:
                # Collect batch
                while self._queue and len(batch) < self.batch_size:
                    item_id, item, future = self._queue.popleft()
                    batch.append(item)
                    futures.append((item_id, future))

            if batch:
                try:
                    # Process batch
                    results = await self.process_func(batch)

                    # Distribute results
                    for i, (item_id, future) in enumerate(futures):
                        if i < len(results):
                            future.set_result(results[i])
                        else:
                            future.set_exception(Exception("No result for item"))

                except Exception as e:
                    # Set exception for all futures in batch
                    for _, future in futures:
                        future.set_exception(e)

            # Small delay to allow more items to queue
            await asyncio.sleep(0.01)


async def run_with_retry(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    **kwargs: Any,
) -> Any:
    """
    Run async function with retry logic.

    Args:
        func: Async function to run
        *args: Function arguments
        max_retries: Maximum number of retries
        backoff_factor: Exponential backoff factor
        **kwargs: Function keyword arguments

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                wait_time = backoff_factor**attempt
                await asyncio.sleep(wait_time)
            else:
                raise last_exception


async def gather_with_progress(
    tasks: List[Callable[[], Awaitable[Any]]],
    desc: str = "Processing",
    max_concurrent: Optional[int] = None,
) -> List[Any]:
    """
    Run tasks concurrently with progress tracking.

    Args:
        tasks: List of async callables
        desc: Description for progress bar
        max_concurrent: Maximum concurrent tasks

    Returns:
        List of task results
    """
    from tqdm.asyncio import tqdm

    if max_concurrent:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_task(task: Callable[[], Awaitable[Any]]) -> Any:
            async with semaphore:
                return await task()

        awaitable_list: List[Awaitable[Any]] = [limited_task(task) for task in tasks]
    else:
        awaitable_list = [task() for task in tasks]

    return await tqdm.gather(*awaitable_list, desc=desc)
