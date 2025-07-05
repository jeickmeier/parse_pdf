"""Abstract base classes for document parsers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, List, TYPE_CHECKING
import hashlib
import json
from datetime import datetime

if TYPE_CHECKING:
    from .config import ParserConfig
    from ..prompts.base import PromptTemplate
    from ..utils.cache import CacheManager


@dataclass
class ParseResult:
    """Standardized parse result container."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    format: str = "markdown"
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "format": self.format,
            "errors": self.errors,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class BaseParser(ABC):
    """Abstract base class for all parsers."""

    def __init__(self, config: "ParserConfig") -> None:
        self.config: "ParserConfig" = config
        # Lazily initialized cache manager
        self._cache_manager: "CacheManager | None" = None

    @property
    def cache(self) -> "CacheManager":
        """Lazy-load cache manager."""
        if self._cache_manager is None:
            from ..utils.cache import CacheManager

            self._cache_manager = CacheManager(self.config.cache_dir)
        return self._cache_manager

    @abstractmethod
    async def parse(self, input_path: Path, **kwargs: Any) -> ParseResult:
        """
        Parse the input file and return structured result.

        Args:
            input_path: Path to the input file
            **kwargs: Additional parser-specific arguments

        Returns:
            ParseResult containing the extracted content
        """
        pass

    @abstractmethod
    async def validate_input(self, input_path: Path) -> bool:
        """
        Validate if the input file can be parsed.

        Args:
            input_path: Path to the input file

        Returns:
            True if file can be parsed, False otherwise
        """
        pass

    async def parse_with_cache(self, input_path: Path, **kwargs: Any) -> ParseResult:
        """Parse with caching support."""
        cache_key = self.generate_cache_key(input_path, **kwargs)

        if self.config.use_cache:
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return ParseResult(**cached_result)

        result = await self.parse(input_path, **kwargs)

        if self.config.use_cache and not result.errors:
            await self.cache.set(cache_key, result.to_dict())

        return result

    def generate_cache_key(self, input_path: Path, **kwargs: Any) -> str:
        """Generate unique cache key for the parsing operation."""
        key_data = {
            "file": str(input_path.absolute()),
            "mtime": input_path.stat().st_mtime,
            "config": self.config.to_dict(),
            "kwargs": kwargs,
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get_metadata(self, input_path: Path) -> Dict[str, Any]:
        """Get basic file metadata."""
        stat = input_path.stat()
        return {
            "filename": input_path.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "parser": self.__class__.__name__,
        }


class BaseExtractor(ABC):
    """Base class for content extractors."""

    @abstractmethod
    async def extract(
        self, content: Any, prompt_template: Optional["PromptTemplate"] = None
    ) -> str:
        """
        Extract structured information from content.

        Args:
            content: Content to extract from (format depends on implementation)
            prompt_template: Optional custom prompt template

        Returns:
            Extracted text content
        """
        pass

    @abstractmethod
    def get_default_prompt(self) -> str:
        """Get the default prompt for this extractor."""
        pass
