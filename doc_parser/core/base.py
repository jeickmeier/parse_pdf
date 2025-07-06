"""Abstract base classes for document parsers.

This module provides core abstractions and utilities for building document parsers:

- ``ParseResult``: Data model for parser outputs, including serialization, saving, and metadata handling.
- ``BaseParser``: Abstract base class that handles caching, orchestrates parsing logic, and supports post-processing.
- ``BaseExtractor``: Abstract base class for implementing custom content extractors (e.g., vision or OCR models).

Examples:
>>> from pathlib import Path
>>> from doc_parser.core.base import BaseParser, ParseResult
>>> from doc_parser.core.settings import Settings
>>> settings = Settings(use_cache=False)
>>> class DummyParser(BaseParser):
...     async def _parse(self, input_path: Path, **kwargs):
...         return ParseResult(content="dummy content", metadata={"file": input_path.name})
...
...     async def validate_input(self, input_path: Path) -> bool:
...         return True
>>> import asyncio
>>> parser = DummyParser(settings)
>>> result = asyncio.run(parser.parse(Path("dummy.txt")))
>>> assert isinstance(result, ParseResult)
>>> print(result.content)
"dummy content"
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
import hashlib
import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from doc_parser.utils.cache import cache_get, cache_set

if TYPE_CHECKING:
    from pathlib import Path

    from doc_parser.config import AppConfig
    from doc_parser.prompts import PromptTemplate
    from doc_parser.utils.cache import CacheManager


class ParseResult(BaseModel):
    """Structured result returned by every parser.

    The model provides convenient helpers for serialization and saving.  It is
    intentionally lightweight so that individual parsers can attach arbitrary
    extra fields via the *metadata* dictionary without subclassing.
    """

    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    output_format: str = Field(default="markdown", alias="format")
    errors: list[str] = Field(default_factory=list)

    # Post-processing
    post_content: Any | None = None

    # ------------------------------------------------------------------
    # Model configuration
    # ------------------------------------------------------------------
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        """Return ``dict`` representation using *model_dump* with aliases."""
        return self.model_dump(mode="python")

    def to_json(self, **kwargs: Any) -> str:
        """Return JSON string representation.

        Additional keyword arguments are forwarded to :pyfunc:`json.dumps`.
        """
        return json.dumps(self.to_dict(), indent=2, default=str, **kwargs)

    def save_markdown(self, output_path: str | Path) -> None:
        """Write *content* to *output_path* if ``format`` is markdown."""
        from pathlib import Path as _Path

        if self.output_format != "markdown":
            raise ValueError("save_markdown() called on non-markdown result")
        output_path = _Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.content, encoding="utf-8")


class BaseParser(ABC):
    """Abstract base class for all parsers."""

    def __init__(self, settings: AppConfig) -> None:
        """Initialize BaseParser with specified settings."""
        # Public so downstream code can tweak if needed
        self.settings: AppConfig = settings

        # Lazily initialised cache manager - created on first access
        self._cache_manager: CacheManager | None = None

    @property
    def cache(self) -> CacheManager:
        """Return lazily initialised cache manager bound to *settings.cache_dir*."""
        if self._cache_manager is None:
            from doc_parser.utils.cache import CacheManager

            self._cache_manager = CacheManager(self.settings.cache_dir)
        return self._cache_manager

    # ------------------------------------------------------------------
    # Public high-level entry-point (caching baked-in)
    # ------------------------------------------------------------------
    async def parse(
        self,
        input_path: Path,
        *,
        output_format: str | None = None,
        options: BaseModel | None = None,
    ) -> ParseResult:
        """Parse *input_path* returning a :class:`ParseResult`.

        Args:
            input_path: Document path or URL to parse.
            output_format: Desired output format ("markdown" or "json"). If
                *None*, the value from :pyattr:`settings.output_format` is used.
            options: Additional parser-specific options

        The method transparently handles caching and post-processing, while
        delegating the heavy-lifting to the subtype-implemented
        :pyfunc:`_parse`. Providing *output_format* avoids mutating
        ``settings.output_format`` at call-sites while maintaining backwards
        compatibility for existing parsers that still reference the setting
        during parsing.
        """
        # ------------------------------------------------------------------
        # Temporarily override settings.output_format (if provided)
        # ------------------------------------------------------------------
        original_format = self.settings.output_format
        if output_format is not None:
            self.settings.output_format = output_format

        try:
            cache_key = self.generate_cache_key(input_path, options=options)

            if self.settings.use_cache:
                cached_result = await cache_get(self.cache, cache_key)
                if cached_result:
                    result = ParseResult(**cached_result)
                    if self.settings.post_prompt and result.post_content is None:
                        await self._run_post_processing(result)
                        await cache_set(self.cache, cache_key, result.to_dict())
                    return result

            # Delegate to concrete parser implementation
            result = await self._parse(input_path, options=options)

            # Post-proc if requested
            if self.settings.post_prompt:
                await self._run_post_processing(result)

            # Persist to cache
            if self.settings.use_cache:
                await cache_set(self.cache, cache_key, result.to_dict())

            return result
        finally:
            # Always restore original output_format to avoid side-effects
            self.settings.output_format = original_format

    # ------------------------------------------------------------------
    # Default structured parsing logic (validate → open → extract)
    # ------------------------------------------------------------------
    async def _parse(self, input_path: Path, *, options: BaseModel | None = None) -> ParseResult:
        """Default structured-document parsing implementation.

        Subclasses can override for custom behaviour, or simply implement the helper hooks:

        * validate_input
        * _open_document
        * _extract_as_markdown
        * _extract_as_json
        * _extra_metadata (optional)
        """
        # 1) Validate the input first
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Invalid file: {input_path}"],
            )

        try:
            # 2) Open the document using the subclass hook
            document_obj = await self._open_document(input_path, options=options)

            # 3) Extract content according to requested format
            if self.settings.output_format == "markdown":
                content = await self._extract_as_markdown(document_obj)
            elif self.settings.output_format == "json":
                content = await self._extract_as_json(document_obj)
            else:
                # Fallback to markdown for unsupported formats
                content = await self._extract_as_markdown(document_obj)

            # 4) Aggregate metadata
            metadata = self.get_metadata(input_path)
            metadata.update(self._extra_metadata(document_obj))

            return ParseResult(content=content, metadata=metadata, output_format=self.settings.output_format)

        except Exception as exc:  # pylint: disable=broad-except  # noqa: BLE001
            # Gracefully convert unexpected exception into a ParseResult so callers don't crash
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Failed to parse {input_path.name}: {exc!s}"],
            )

    # ------------------------------------------------------------------
    # Hook methods for structured parsers
    # ------------------------------------------------------------------
    async def _open_document(self, input_path: Path, *, options: BaseModel | None = None) -> Any:
        """Open *input_path* and return a third-party document object.

        Structured parsers **must** override this. The base implementation just raises.
        """
        raise NotImplementedError

    async def _extract_as_markdown(self, document_obj: Any) -> str:
        """Convert *document_obj* to Markdown. Must be overridden by structured parsers."""
        raise NotImplementedError

    async def _extract_as_json(self, document_obj: Any) -> str:
        """Serialize *document_obj* to a JSON string. Must be overridden by structured parsers."""
        raise NotImplementedError

    def _extra_metadata(self, _document_obj: Any) -> dict[str, Any]:
        """Return extra metadata dict; subclasses may override."""
        return {}

    @abstractmethod
    async def validate_input(self, input_path: Path) -> bool:
        """Validate if the input file can be parsed.

        Args:
            input_path: Path to the input file

        Returns:
            True if file can be parsed, False otherwise
        """

    def generate_cache_key(self, input_path: Path, *, options: BaseModel | None = None) -> str:
        """Return a stable cache key for *input_path* and current parser settings."""
        key_data = {
            "file": str(input_path.absolute()),
            "mtime": input_path.stat().st_mtime,
            "settings": self.settings.model_dump(),
            "options": options.model_dump() if isinstance(options, BaseModel) else None,
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get_metadata(self, input_path: Path) -> dict[str, Any]:
        """Get basic file metadata."""
        stat = input_path.stat()
        return {
            "filename": input_path.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "parser": self.__class__.__name__,
        }

    async def _run_post_processing(self, result: ParseResult) -> None:
        """Helper to perform post-processing and attach to *result*."""
        import logging

        logger = logging.getLogger(__name__)
        try:
            from doc_parser.utils.llm_post_processor import LLMPostProcessor

            logger.debug("Starting post-processing with prompt=%s", self.settings.post_prompt)
            post_processor = LLMPostProcessor(self.settings, cache_manager=self.cache)
            prompt_arg: str = self.settings.post_prompt or ""
            result.post_content = await post_processor.process(result.content, prompt_arg)
            logger.debug("Post-processing complete. Length=%s", len(str(result.post_content)))
        except Exception:  # pylint: disable=broad-except
            logger.exception("Post-processing failed")
            result.errors.append("Post-processing failed")

    # ------------------------------------------------------------------
    # Public convenience property for accessing settings via .config
    # ------------------------------------------------------------------
    @property
    def config(self) -> AppConfig:
        """Alias property for settings (preferred)."""
        return self.settings

    # ------------------------------------------------------------------
    # Convenience wrappers for explicit output modes
    # ------------------------------------------------------------------

    async def parse_markdown(self, input_path: Path, *, options: BaseModel | None = None) -> ParseResult:
        """Parse *input_path* and return Markdown content.

        A thin wrapper around :pyfunc:`parse` that sets ``output_format`` to
        ``"markdown"`` without mutating global settings.
        """
        return await self.parse(input_path, output_format="markdown", options=options)

    async def parse_json(self, input_path: Path, *, options: BaseModel | None = None) -> ParseResult:
        """Parse *input_path* and return JSON content (as string)."""
        return await self.parse(input_path, output_format="json", options=options)

    # ------------------------------------------------------------------
    # Class-level helpers
    # ------------------------------------------------------------------

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """Return the list of file extensions associated with *cls*.

        The information is retrieved from the global :class:`AppConfig` parser
        registry so that callers no longer rely on the legacy
        ``SUPPORTED_EXTENSIONS`` class attribute.
        """
        # Runtime import to avoid import-time cycles
        from doc_parser.config import AppConfig  # local import

        # Identify all *parser names* that map to this class
        parser_names = [name for name, p_cls in AppConfig._parsers.items() if p_cls is cls]

        # Collect extensions whose registered parser matches any of the names
        return [ext for ext, name in AppConfig._extensions.items() if name in parser_names]

    # ------------------------------------------------------------------
    # Path helpers (formerly utils.file_validators)
    # ------------------------------------------------------------------
    def _has_supported_extension(self, input_path: Path) -> bool:
        """Return ``True`` if *input_path* matches this parser's extensions.

        Args:
            input_path: Path to validate.

        Returns:
            bool: ``True`` when the suffix of *input_path* (case-insensitive) is
                one of :pyattr:`SUPPORTED_EXTENSIONS`.
        """
        ext = input_path.suffix.lower()
        return ext in self.supported_extensions()


class BaseExtractor(ABC):
    """Base class for content extractors."""

    @abstractmethod
    async def extract(self, content: Any, prompt_template: PromptTemplate | None = None) -> str:
        """Extract structured information from content.

        Args:
            content: Content to extract from (format depends on implementation)
            prompt_template: Optional custom prompt template

        Returns:
            Extracted text content
        """

    @abstractmethod
    def get_default_prompt(self) -> str:
        """Get the default prompt for this extractor."""


# ------------------------------------------------------------------
# Explicit re-export list for "from doc_parser.core.base import *" usage
# ------------------------------------------------------------------
__all__ = [
    "BaseExtractor",
    "BaseParser",
    "ParseResult",
]
