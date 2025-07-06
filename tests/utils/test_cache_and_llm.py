import asyncio
from datetime import timedelta
from pathlib import Path

import pytest

from doc_parser.config import AppConfig
from doc_parser.utils.cache import CacheManager, cache_set, cache_get
from doc_parser.utils.llm_post_processor import LLMPostProcessor


@pytest.mark.asyncio
async def test_cache_manager_roundtrip(tmp_path):
    cm = CacheManager(Path(tmp_path), ttl=timedelta(seconds=5))
    await cache_set(cm, "key", {"value": 1})
    data = await cache_get(cm, "key")
    assert data == {"value": 1}


@pytest.mark.asyncio
async def test_llm_post_processor_basic(tmp_path):
    settings = AppConfig(use_cache=True, cache_dir=tmp_path)
    proc = LLMPostProcessor(settings)

    # First call should compute and cache and return non-empty string
    out1 = await proc.process("hello", "Summarize")
    assert isinstance(out1, str) and out1.strip()  # non-empty

    # Second call should hit cache (simulate by checking same object)
    out2 = await proc.process("hello", "Summarize")
    assert out1 == out2  # should hit cache and match first output 