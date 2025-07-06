import asyncio
from collections import Counter

import pytest

from doc_parser.utils.async_helpers import RateLimiter, run_with_retry
from doc_parser.utils.async_batcher import AsyncBatcher


@pytest.mark.asyncio
async def test_run_with_retry_success_after_failures():
    attempts = Counter()

    async def flaky(x: int) -> int:
        attempts["count"] += 1
        # Fail the first two times
        if attempts["count"] < 3:
            raise RuntimeError("boom")
        return x

    result = await run_with_retry(flaky, 5, max_retries=3, backoff_factor=0.01)
    assert result == 5
    # Should have attempted exactly 3 times (2 failures + 1 success)
    assert attempts["count"] == 3


@pytest.mark.asyncio
async def test_rate_limiter_max_concurrency():
    max_concurrent = 2
    limiter = RateLimiter(max_concurrent)
    active = 0
    peak = 0

    async def task():
        nonlocal active, peak
        async with limiter:
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.05)
            active -= 1

    await asyncio.gather(*(task() for _ in range(6)))
    assert peak <= max_concurrent


@pytest.mark.asyncio
async def test_async_batcher_basic():
    async def process(batch):
        # Double every number
        await asyncio.sleep(0.01)
        return [i * 2 for i in batch]

    batcher = AsyncBatcher(batch_size=3, process_func=process, timeout=0.05)

    results = await asyncio.gather(*[batcher.add(i) for i in [1, 2, 3, 4]])
    assert results == [2, 4, 6, 8] 