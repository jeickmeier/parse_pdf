"""Automatic parser discovery and registration.

This module provides a registry that maps file extensions and parser names to
parser classes. It supports:
- Dynamic registration via decorator
- Lookup of parser by file path or URL
- Listing available parsers and their extensions
- Checking support for given file type

Classes and methods:
- ParserRegistry.register(name: str, extensions: List[str]) -> Callable[[Type[BaseParser]], Type[BaseParser]]:
  Decorator to register a parser class for the given extensions.
- ParserRegistry.from_path(file_path: Path | str, settings: Optional[Settings] = None) -> BaseParser:
  Lookup parser by file extension or URL string and return an initialized instance.
- ParserRegistry.get_parser_by_name(name: str, settings: Optional[Settings] = None) -> BaseParser:
  Instantiate parser by its registered name.
- ParserRegistry.list_parsers() -> Dict[str, List[str]]:
  Return mapping of parser names to supported extensions.
- ParserRegistry.is_supported(file_path: Path) -> bool:
  Check if given file extension is supported.

Examples:
>>> from pathlib import Path
>>> from doc_parser.core.registry import ParserRegistry
>>> # List available parsers
>>> ParserRegistry.list_parsers()
{'pdf': ['.pdf'], 'docx': ['.docx'], ...}
>>> # Instantiate a parser by file extension
>>> parser = ParserRegistry.from_path(Path("sample.pdf"))
>>> result = await parser.parse_markdown(Path("sample.pdf"))
"""

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from .base import BaseParser
from .exceptions import UnsupportedFormatError
from .settings import Settings

if TYPE_CHECKING:
    from collections.abc import Callable


class ParserRegistry:
    """Singleton registry mapping file extensions and parser names to parser classes.

    Use class methods to register and retrieve parser implementations dynamically.

    Examples:
    >>> from doc_parser.core.registry import ParserRegistry
    >>> # Register a custom parser
    >>> @ParserRegistry.register("txt", [".txt"])
    ... class CustomTextParser(BaseParser):
    ...     async def validate_input(self, input_path):
    ...         return True
    ...
    ...     async def _parse(self, input_path, **kwargs):
    ...         return ParseResult(content="text", metadata={})
    >>> # Retrieve the parser by name
    >>> parser = ParserRegistry.get_parser_by_name("txt")
    >>> assert parser.__class__.__name__ == "CustomTextParser"
    """

    _parsers: ClassVar[dict[str, type[BaseParser]]] = {}
    _extensions: ClassVar[dict[str, str]] = {}

    @classmethod
    def register(cls, name: str, extensions: list[str]) -> "Callable[[type[BaseParser]], type[BaseParser]]":
        """Decorator to register a parser.

        Args:
            name: Unique name for the parser
            extensions: List of file extensions this parser handles

        Returns:
            Decorator function
        """

        def decorator(parser_class: type[BaseParser]) -> type[BaseParser]:
            # Validate parser class
            if not issubclass(parser_class, BaseParser):
                raise TypeError(f"{parser_class} must inherit from BaseParser")

            # Register parser
            cls._parsers[name] = parser_class

            # Register extensions
            for raw_ext in extensions:
                ext = raw_ext.lower()
                if not ext.startswith("."):
                    ext = f".{ext}"
                cls._extensions[ext] = name

            return parser_class

        return decorator

    @classmethod
    def from_path(
        cls,
        file_path: "Path | str",
        settings: Settings | None = None,
    ) -> BaseParser:
        """Get appropriate parser for file.

        Args:
            file_path: Path to the file to parse
            settings: Optional settings object; if omitted a default instance is created

        Returns:
            Initialized parser instance

        Raises:
            UnsupportedFormatError: If no parser found for file type
        """
        # ------------------------------------------------------------------
        # Accept both Path objects and raw strings (e.g. URLs)
        # ------------------------------------------------------------------
        if isinstance(file_path, str):
            # Treat raw URLs specially - they map to the HTML parser.
            if file_path.startswith(("http://", "https://")):
                parser_name = "html"
                parser_class = cls._parsers.get(parser_name)
                if parser_class is None:
                    raise UnsupportedFormatError("HTML parser is not registered. Cannot handle URL input.")

                if settings is None:
                    settings = Settings()

                return parser_class(settings)

            # Otherwise interpret *file_path* as a filesystem path string.
            file_path = Path(file_path)

        # At this point we guarantee *file_path* is a Path instance.
        ext = file_path.suffix.lower()

        if ext not in cls._extensions:
            raise UnsupportedFormatError(
                f"No parser found for extension '{ext}'. Supported extensions: {list(cls._extensions.keys())}"
            )

        parser_name = cls._extensions[ext]
        parser_class = cls._parsers[parser_name]

        if settings is None:
            settings = Settings()

        return parser_class(settings)

    @classmethod
    def get_parser_by_name(
        cls,
        name: str,
        settings: Settings | None = None,
    ) -> BaseParser:
        """Get parser by name.

        Args:
            name: Parser name
            settings: Optional settings

        Returns:
            Initialized parser instance

        Raises:
            ValueError: If parser not found
        """
        if name not in cls._parsers:
            raise ValueError(f"Parser '{name}' not found. Available: {list(cls._parsers.keys())}")

        if settings is None:
            settings = Settings()

        return cls._parsers[name](settings)

    @classmethod
    def list_parsers(cls) -> dict[str, list[str]]:
        """List all registered parsers and their extensions.

        Returns:
            Dictionary mapping parser names to supported extensions
        """
        result: dict[str, list[str]] = {}
        for ext, parser_name in cls._extensions.items():
            if parser_name not in result:
                result[parser_name] = []
            result[parser_name].append(ext)
        return result

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        """Check if file type is supported.

        Args:
            file_path: Path to check

        Returns:
            True if supported, False otherwise
        """
        return file_path.suffix.lower() in cls._extensions
