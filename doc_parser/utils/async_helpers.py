"""Async utility functions and classes."""

import asyncio
from typing import Any, Awaitable, Callable, Optional, List


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
