"""LLM-based post-processing for parsed content.

This module provides LLMPostProcessor to perform a secondary LLM call using the OpenAI Agents SDK,
applying custom prompts or templates, with optional caching and structured response support.

Classes:
    LLMPostProcessor: Handles post-parse prompting, caching, and optional Pydantic model coercion.

Examples:
    >>> import asyncio
    >>> from pathlib import Path
    >>> from doc_parser.core.settings import Settings
    >>> from doc_parser.utils.llm_post_processor import LLMPostProcessor
    >>> settings = Settings(use_cache=False)
    >>> processor = LLMPostProcessor(settings)
    >>> result = asyncio.run(processor.process("raw text", "Summarize content"))
    >>> print(result)
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from agents import Agent, Runner

from doc_parser.prompts.base import PromptRegistry, PromptTemplate
from doc_parser.utils.cache import CacheManager, cache_get, cache_set

if TYPE_CHECKING:
    from doc_parser.core.settings import Settings

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


class LLMPostProcessor:
    """Performs secondary LLM-based post-processing of parsed content.

    Args:
        config (Settings): Global configuration including response_model and caching.
        cache_manager (Optional[CacheManager]): Custom cache manager; defaults to one based on config.cache_dir.

    Attributes:
        config (Settings): Parser and post-processing settings.
        cache (CacheManager): Cache manager for post-processing results.

    Examples:
        >>> import asyncio
        >>> from pathlib import Path
        >>> from doc_parser.core.settings import Settings
        >>> from doc_parser.utils.llm_post_processor import LLMPostProcessor
        >>> settings = Settings(use_cache=True, response_model=None)
        >>> processor = LLMPostProcessor(settings)
        >>> output = asyncio.run(processor.process("content", "Summarize"))
        >>> print(output)
    """

    def __init__(self, config: Settings, cache_manager: CacheManager | None = None):
        """Create a new post-processor.

        Args:
            config (Settings): Application settings containing post-processing options.
            cache_manager (CacheManager | None): Optional cache override. If omitted a
                new `CacheManager` is created from ``config.cache_dir``.
        """
        self.config: Settings = config
        self.cache = cache_manager or CacheManager(Path(config.cache_dir))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def process(self, primary_content: str, post_prompt: str) -> Any:
        """Post-process parsed content using a second LLM call.

        Args:
            primary_content (str): Main content to be post-processed.
            post_prompt (str): Prompt template name or literal prompt for LLM.

        Returns:
            Any: Post-processed content, which may be a string or Pydantic model instance if configured.

        Raises:
            Exception: If LLM call or caching fails unexpectedly.

        Example:
            >>> output = await processor.process("Hello world", "Translate to French")
        """
        resolved_prompt = self._resolve_prompt(post_prompt)

        cache_key = self._make_cache_key(primary_content, resolved_prompt)
        if self.config.use_cache:
            cached = await cache_get(self.cache, cache_key)
            if cached:
                cached_content = cached.get("post_content")
                # If a structured response model is configured and the cached value
                # is a JSON string, convert it back into the Pydantic object so that
                # callers always receive the same rich type that a live LLM call
                # would return.
                if self.config.response_model and isinstance(cached_content, str):
                    try:
                        model_cls = self._import_response_model(self.config.response_model)
                        if issubclass(model_cls, BaseModel):
                            return model_cls.model_validate_json(cached_content)
                    except (ValueError, TypeError):  # pragma: no cover
                        pass  # fall through to return cached string
                return cached_content

        # Call LLM (placeholder implementation)
        post_content = await self._call_llm(resolved_prompt, primary_content)

        # If we expect a structured object but received a JSON/string, coerce now
        if self.config.response_model:
            model_cls = self._import_response_model(self.config.response_model)
            if model_cls and issubclass(model_cls, BaseModel) and not isinstance(post_content, model_cls):
                post_content = model_cls.model_validate_json(str(post_content))

        # Cache - store something that can be JSON-encoded
        if self.config.use_cache and post_content is not None:
            serialisable = post_content.model_dump_json() if isinstance(post_content, BaseModel) else post_content
            await cache_set(self.cache, cache_key, {"post_content": serialisable})

        return post_content

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_prompt(self, prompt_or_name: str) -> str:
        """Resolve prompt text from registry or literal string.

        Args:
            prompt_or_name (str): Registered template name or literal prompt.

        Returns:
            str: Rendered prompt text ready for LLM.

        Example:
            >>> text = processor._resolve_prompt("pdf_extraction")
        """
        template: PromptTemplate | None = PromptRegistry.get(prompt_or_name)
        if template:
            return template.render()
        return prompt_or_name

    def _make_cache_key(self, primary_content: str, prompt: str) -> str:
        """Generate a stable cache key based on content and prompt.

        Args:
            primary_content (str): Original parsed content.
            prompt (str): Resolved prompt text.

        Returns:
            str: SHA256 hex digest for caching.

        Example:
            >>> key = processor._make_cache_key("data", "prompt")
        """
        key_data = {
            "primary": primary_content,
            "prompt": prompt,
            "model": self.config.response_model,
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()

    async def _call_llm(self, prompt: str, content: str) -> str:
        """Call an LLM (via Agents SDK) **or** fall back to a deterministic stub.

        The behaviour is now as follows:

        1. **Live mode** - If an ``OPENAI_API_KEY`` environment variable is
           present we *attempt* a real call using the Agents SDK.  This is
           opt-in so that CI and unit tests remain fully deterministic.
        2. **Offline mode** - When the API key is missing **or** a live call
           fails for *any* reason, we gracefully fall back to the original
           stub logic that guarantees repeatable output.

        This hybrid strategy keeps the test-suite fast and reliable while
        allowing end-users to benefit from high-fidelity post-processing when
        credentials are provided locally.

        Args:
            prompt (str): The user/system prompt (may include a JSON schema).
            content (str): Primary content to send to the LLM.

        Returns:
            str: The raw LLM output (string or JSON) which will later be
                 coerced into a Pydantic model if ``response_model`` is set.
        """
        import os

        # Require an API key - fail fast if not configured to avoid silent
        # fall-throughs that yield unusable output.
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY not found in environment. Set it (e.g. via a .env "
                "file or shell export) to enable LLM post-processing."
            )

        system_prompt, output_type = self._build_system_prompt(prompt)
        return await self._run_agent(system_prompt, content, output_type)

    def _build_system_prompt(self, prompt: str) -> tuple[str, type | None]:
        """Build the system prompt and determine the output type based on config.

        Args:
            prompt (str): Base prompt text or template.

        Returns:
            Tuple[str, type | None]: System prompt with schema and optional Pydantic type.

        Example:
            >>> sys, typ = processor._build_system_prompt("Prompt")
        """
        system_prompt = prompt
        output_type: type | None = None

        if self.config.response_model:
            try:
                model_cls = self._import_response_model(self.config.response_model)
                if model_cls and issubclass(model_cls, BaseModel):
                    schema_json = json.dumps(model_cls.model_json_schema(), indent=2)
                    system_prompt = (
                        f"{prompt}\n\n"
                        "When you respond, output ONLY a JSON object that strictly matches "
                        "the following JSON schema. Do not wrap the JSON in markdown or "
                        "any additional text.\n\n"
                        f"{schema_json}"
                    )
                    output_type = model_cls
            except (ValueError, TypeError):  # pragma: no cover
                # Ignore schema embedding on failure, proceed with plain prompt
                output_type = None

        return system_prompt, output_type

    async def _run_agent(self, system_prompt: str, content: str, output_type: type | None) -> str:
        """Execute an Agents SDK Agent with system prompt and input content.

        Args:
            system_prompt (str): Instructions for the agent.
            content (str): Input content to process.
            output_type (Optional[type]): Expected output type for structured responses.

        Returns:
            str: Agent's final output as string.

        Example:
            >>> out = await processor._run_agent("sys", "content", None)
        """
        agent = Agent(
            name="PostProcessor",
            instructions=system_prompt,
            model=self.config.model_name,
            output_type=output_type,
        )

        result = await Runner.run(agent, content)

        # If a structured model instance was returned, serialise to JSON so that
        # downstream ``model_validate_json`` receives valid input rather than a
        # Python repr string such as ``authors=['...', ...]``.
        final = result.final_output
        try:
            if output_type and isinstance(final, BaseModel):
                return final.model_dump_json()
        except ImportError:  # pragma: no cover - pydantic always installed in lib
            pass

        return str(final)

    def _import_response_model(self, import_path: str) -> Any:
        """Dynamically import and return a class from an import path.

        Args:
            import_path (str): Dotted or colon-separated module path to a class.

        Returns:
            Any: Imported class or attribute.

        Raises:
            ImportError: If the path is invalid or the attribute not found.

        Example:
            >>> cls = processor._import_response_model("mypkg.models:MyModel")
        """
        module_path, _, attr = import_path.partition(":") if ":" in import_path else import_path.rpartition(".")
        if not module_path or not attr:
            raise ImportError("Invalid import path for response model")
        module = importlib.import_module(module_path)
        return getattr(module, attr)
