"""Custom exceptions for the document parser library."""


class ParserError(Exception):
    """Base exception for all parser errors."""

    pass


class ConfigurationError(ParserError):
    """Raised when there's an issue with configuration."""

    pass


class ExtractionError(ParserError):
    """Raised when content extraction fails."""

    pass


class UnsupportedFormatError(ParserError):
    """Raised when attempting to parse an unsupported file format."""

    pass


class CacheError(ParserError):
    """Raised when cache operations fail."""

    pass
