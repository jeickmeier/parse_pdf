"""Parser registry for automatic parser discovery and registration."""

from pathlib import Path
from typing import Dict, Type, List, Optional, Callable
from .base import BaseParser
from .config import ParserConfig
from .exceptions import UnsupportedFormatError


class ParserRegistry:
    """Registry for document parsers."""

    _parsers: Dict[str, Type[BaseParser]] = {}
    _extensions: Dict[str, str] = {}

    @classmethod
    def register(
        cls, name: str, extensions: List[str]
    ) -> "Callable[[Type[BaseParser]], Type[BaseParser]]":
        """
        Decorator to register a parser.

        Args:
            name: Unique name for the parser
            extensions: List of file extensions this parser handles

        Returns:
            Decorator function
        """

        def decorator(parser_class: Type[BaseParser]) -> Type[BaseParser]:
            # Validate parser class
            if not issubclass(parser_class, BaseParser):
                raise TypeError(f"{parser_class} must inherit from BaseParser")

            # Register parser
            cls._parsers[name] = parser_class

            # Register extensions
            for ext in extensions:
                ext = ext.lower()
                if not ext.startswith("."):
                    ext = f".{ext}"
                cls._extensions[ext] = name

            return parser_class

        return decorator

    @classmethod
    def get_parser(
        cls, file_path: Path, config: Optional[ParserConfig] = None
    ) -> BaseParser:
        """
        Get appropriate parser for file.

        Args:
            file_path: Path to the file to parse
            config: Optional parser configuration

        Returns:
            Initialized parser instance

        Raises:
            UnsupportedFormatError: If no parser found for file type
        """
        ext = file_path.suffix.lower()

        if ext not in cls._extensions:
            raise UnsupportedFormatError(
                f"No parser found for extension '{ext}'. "
                f"Supported extensions: {list(cls._extensions.keys())}"
            )

        parser_name = cls._extensions[ext]
        parser_class = cls._parsers[parser_name]

        if config is None:
            config = ParserConfig()

        return parser_class(config)

    @classmethod
    def get_parser_by_name(
        cls, name: str, config: Optional[ParserConfig] = None
    ) -> BaseParser:
        """
        Get parser by name.

        Args:
            name: Parser name
            config: Optional parser configuration

        Returns:
            Initialized parser instance

        Raises:
            ValueError: If parser not found
        """
        if name not in cls._parsers:
            raise ValueError(
                f"Parser '{name}' not found. Available: {list(cls._parsers.keys())}"
            )

        if config is None:
            config = ParserConfig()

        return cls._parsers[name](config)

    @classmethod
    def list_parsers(cls) -> Dict[str, List[str]]:
        """
        List all registered parsers and their extensions.

        Returns:
            Dictionary mapping parser names to supported extensions
        """
        result: Dict[str, List[str]] = {}
        for ext, parser_name in cls._extensions.items():
            if parser_name not in result:
                result[parser_name] = []
            result[parser_name].append(ext)
        return result

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        """
        Check if file type is supported.

        Args:
            file_path: Path to check

        Returns:
            True if supported, False otherwise
        """
        return file_path.suffix.lower() in cls._extensions
