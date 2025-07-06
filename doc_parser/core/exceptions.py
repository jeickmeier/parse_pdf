"""Custom exceptions for the document parser library.

This module defines exception types used across the doc_parser library
to signal various error conditions during parsing, configuration,
extraction, and caching.

Examples:
>>> from doc_parser.core.exceptions import ParserError, ConfigurationError
>>> try:
...     raise ConfigurationError("Invalid value for 'dpi'")
... except ParserError as e:
...     print(f"Caught error: {e}")
Caught error: Invalid value for 'dpi'
"""


class ParserError(Exception):
    """Base exception for all parser-related errors.

    All custom exceptions in this library inherit from ParserError.
    """


class ConfigurationError(ParserError):
    """Raised when there's an issue with parser or application configuration.

    This error indicates invalid or missing settings that prevent parsing.

    Examples:
    >>> from doc_parser.core.exceptions import ConfigurationError
    >>> raise ConfigurationError("Missing required setting: 'cache_dir'")
    Traceback (most recent call last):
      ...
    ConfigurationError: Missing required setting: 'cache_dir'
    """


class ExtractionError(ParserError):
    """Raised when content extraction fails.

    Signals errors during content extraction (e.g., OCR failures).

    Examples:
    >>> from doc_parser.core.exceptions import ExtractionError
    >>> raise ExtractionError("Failed to extract text from image")
    Traceback (most recent call last):
      ...
    ExtractionError: Failed to extract text from image
    """


class UnsupportedFormatError(ParserError):
    """Raised when attempting to parse an unsupported file format.

    Indicates no parser is registered for the given extension or input.

    Examples:
    >>> from doc_parser.core.exceptions import UnsupportedFormatError
    >>> raise UnsupportedFormatError(".txt files are not supported")
    Traceback (most recent call last):
      ...
    UnsupportedFormatError: .txt files are not supported
    """


class CacheError(ParserError):
    """Raised when cache operations fail.

    Includes read/write errors or TTL expiration issues in the cache.

    Examples:
    >>> from doc_parser.core.exceptions import CacheError
    >>> raise CacheError("Unable to write to cache directory")
    Traceback (most recent call last):
      ...
    CacheError: Unable to write to cache directory
    """


# ------------------------------------------------------------------
# Public exports
# ------------------------------------------------------------------
__all__ = [
    "CacheError",
    "ConfigurationError",
    "ExtractionError",
    "ParserError",
    "UnsupportedFormatError",
]
