"""Shared helper base class for structured parsers.

This module centralises the boilerplate that previously existed in each
*structured* parser (DOCX, Excel, etc.).  By providing a template
implementation of the *validate → open → extract → metadata* flow, new
parsers can be created by simply plugging in a few hook methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from doc_parser.core.base import BaseParser, ParseResult

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


class BaseStructuredParser(BaseParser, ABC):
    """Shared helper base class for parsers that follow *open → extract → metadata* flow.

    This class collapses the ~100-line boilerplate that existed in each of the
    DOCX/Excel/PPTX (*structured*) parsers into a single place.  Concrete
    subclasses only need to provide:

    1. :pyfunc:`_open_document` - Load the raw document object using the
       third-party library of choice (``python-docx``, ``pandas``, etc.).
    2. :pyfunc:`_extract_as_markdown` - Convert the document object to a Markdown
       string.
    3. :pyfunc:`_extract_as_json` - Serialize the document object into a JSON
       string.
    4. (Optional) :pyfunc:`_extra_metadata` - Return additional metadata dict to
       merge with :pyfunc:`BaseParser.get_metadata` output.

    The class provides the shared *validate → parse → error-handling* skeleton as
    well as the extension check logic.  Subclasses can still override any
    method if they have bespoke requirements, but most should not need to.
    """

    # ------------------------------------------------------------------
    # Public entry-points
    # ------------------------------------------------------------------
    async def validate_input(self, input_path: Path) -> bool:
        """Validate that *input_path* has a supported extension and exists.

        Subclasses can override for deeper validation (e.g. trying to open the
        file with the underlying library).  The default implementation checks
        extension support and file existence.
        """
        return input_path.exists() and self._has_supported_extension(input_path)

    # ------------------------------------------------------------------
    # Shared parsing skeleton
    # ------------------------------------------------------------------
    async def _parse(self, input_path: Path, **_kwargs: Any) -> ParseResult:
        """Parse *input_path* using the template method pattern.

        The workflow is:

        1. Validate input.
        2. Open the document using :pyfunc:`_open_document`.
        3. Delegate to the format-specific extractor helper.
        4. Merge basic + extra metadata.
        5. Wrap any raised exceptions into :class:`ParseResult` errors so that
           callers do not have to handle them individually.
        """
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Invalid file: {input_path}"],
            )

        try:
            document_obj = await self._open_document(input_path, **_kwargs)

            # Choose output format
            if self.settings.output_format == "markdown":
                content = await self._extract_as_markdown(document_obj)
            elif self.settings.output_format == "json":
                content = await self._extract_as_json(document_obj)
            else:
                # Fallback to markdown for unknown/unsupported formats
                content = await self._extract_as_markdown(document_obj)

            # Metadata aggregation
            metadata = self.get_metadata(input_path)
            metadata.update(self._extra_metadata(document_obj))

            return ParseResult(content=content, metadata=metadata, format=self.settings.output_format)

        except Exception as exc:  # pylint: disable=broad-except  # noqa: BLE001
            # Convert any unexpected exception into a graceful ParseResult
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Failed to parse {input_path.name}: {exc!s}"],
            )

    # ------------------------------------------------------------------
    # Abstract hooks - to be implemented by subclasses
    # ------------------------------------------------------------------
    @abstractmethod
    async def _open_document(self, input_path: Path, **kwargs: Any) -> Any:
        """Open *input_path* and return a library-specific document object."""

    @abstractmethod
    async def _extract_as_markdown(self, document_obj: Any) -> str:
        """Convert *document_obj* to Markdown."""

    @abstractmethod
    async def _extract_as_json(self, document_obj: Any) -> str:
        """Serialize *document_obj* to a JSON string."""

    # ------------------------------------------------------------------
    # Optional extension points
    # ------------------------------------------------------------------
    def _extra_metadata(self, _document_obj: Any) -> dict[str, Any]:
        """Return extra metadata dict; subclasses may override.

        The default implementation returns an empty dict.
        """
        return {}
