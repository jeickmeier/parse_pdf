# mypy: ignore-errors

import json

from doc_parser.config import AppConfig as Settings
from doc_parser.prompts.base import PromptRegistry, PromptTemplate
from doc_parser.utils.llm_post_processor import LLMPostProcessor

import pytest

# Ensure all tests run under an asyncio event loop when using pytest-asyncio
pytestmark = pytest.mark.asyncio


async def test_resolve_prompt_literal(tmp_path):
    cfg = Settings(cache_dir=tmp_path)
    pp = LLMPostProcessor(cfg)
    result = await pp.process("hello", "echo this")
    assert isinstance(result, str) and result.strip()  # non-empty string


async def test_resolve_prompt_template(tmp_path):
    template = PromptTemplate("Return '{{text}}'", {"text": "foo"})
    PromptRegistry.register("echo", template)

    cfg = Settings(cache_dir=tmp_path)
    pp = LLMPostProcessor(cfg)
    out1 = await pp.process("bar", "echo")
    out2 = await pp.process("bar", "echo")  # should hit cache

    assert out1 == out2


# Simple Pydantic model validation example
async def test_response_model_validation(tmp_path):
    try:
        from pydantic import BaseModel  # type: ignore
    except ImportError:
        return  # Skip if pydantic not available

    class Echo(BaseModel):
        value: str

    # Dump model to a temporary module
    module_path = tmp_path / "mymodel.py"
    module_path.write_text(
        "from pydantic import BaseModel\nclass Echo(BaseModel):\n    value: str\n"
    )

    cfg = Settings(cache_dir=tmp_path, response_model="mymodel:Echo", use_cache=False)

    # Manipulate sys.path so import works
    import sys, importlib  # noqa: E401

    sys.path.insert(0, str(tmp_path))
    importlib.invalidate_caches()

    pp = LLMPostProcessor(cfg)
    # Provide valid JSON that matches Echo schema
    result = await pp.process(json.dumps({"value": "hi"}), "echo")
    assert hasattr(result, "value")
    # Ensure the value is a string, actual content may vary depending on live LLM response
    assert isinstance(result.value, str) and result.value
