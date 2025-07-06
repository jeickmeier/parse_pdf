"""Asynchronous utility functions and helpers.

This module provides:
- RateLimiter: A context manager for limiting concurrent async operations.
- run_with_retry: Retry logic for asynchronous functions with exponential backoff.
- gather_with_progress: Concurrent task execution with progress bar support.

Examples:
    >>> import asyncio
    >>> from doc_parser.utils.async_helpers import run_with_retry, gather_with_progress
    >>> async def unstable(x):
    ...     if x < 3:
    ...         raise ValueError("fail")
    ...     return x
    >>> result = asyncio.run(run_with_retry(unstable, 3, max_retries=2))
    >>> print(result)
    3
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


class RateLimiter:
    """Rate limiter for async operations.

    Args:
        max_concurrent (int): Maximum concurrent operations when used as an async context.

    Usage:
        >>> from doc_parser.utils.async_helpers import RateLimiter
        >>> limiter = RateLimiter(max_concurrent=2)
        >>> async with limiter:
        ...     # protected block
        ...     await some_async_task()
    """

    def __init__(self, max_concurrent: int = 10) -> None:
        """Initialize rate limiter.

        Args:
            max_concurrent: Maximum concurrent operations
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self) -> "RateLimiter":
        """Acquire a semaphore slot for rate limiting."""
        await self.semaphore.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Release the semaphore slot after operation."""
        self.semaphore.release()


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
    """Run an async function with retry logic and exponential backoff.

    Args:
        func (Callable[..., Awaitable[Any]]): Async function to run.
        *args: Positional arguments for func.
        max_retries (int): Maximum number of retry attempts.
        backoff_factor (float): Exponential backoff multiplier (sleep = backoff_factor**attempt).
        retry_exceptions (tuple[type[Exception], ...]): Tuple of exceptions to retry on.
        **kwargs: Keyword arguments for func.

    Returns:
        Any: Result of the async function on success.

    Raises:
        Exception: Last exception raised if all retries are exhausted.

    Example:
        >>> import asyncio
        >>> from doc_parser.utils.async_helpers import run_with_retry
        >>> async def flaky():
        ...     raise RuntimeError("fail")
        >>> try:
        ...     asyncio.run(run_with_retry(flaky, max_retries=1))
        ... except RuntimeError as e:
        ...     print(e)
        fail
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


async def gather_with_progress(
    tasks: list[Callable[[], Awaitable[Any]]],
    desc: str = "Processing",
    max_concurrent: int | None = None,
) -> list[Any]:
    """Run a list of async callables concurrently with progress bar support.

    Args:
        tasks (List[Callable[[], Awaitable[Any]]]): List of zero-arg async callables.
        desc (str): Description text for the progress bar.
        max_concurrent (Optional[int]): Limit on simultaneous tasks.

    Returns:
        List[Any]: Results from each task, ordered by input list.

    Example:
        >>> import asyncio
        >>> from doc_parser.utils.async_helpers import gather_with_progress
        >>> async def f(i):
        ...     return i * i
        >>> tasks = [lambda i=i: f(i) for i in range(5)]
        >>> results = asyncio.run(gather_with_progress(tasks, desc="Squares", max_concurrent=2))
        >>> print(results)
        [0, 1, 4, 9, 16]
    """
    from tqdm.asyncio import tqdm

    if max_concurrent:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_task(task: Callable[[], Awaitable[Any]]) -> Any:
            async with semaphore:
                return await task()

        awaitable_list: list[Awaitable[Any]] = [limited_task(task) for task in tasks]
    else:
        awaitable_list = [task() for task in tasks]

    return await tqdm.gather(*awaitable_list, desc=desc)
