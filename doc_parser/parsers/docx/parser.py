"""DOCX parser implementation.

This module provides a parser for Microsoft Word .docx files with:
- Content extraction as Markdown or JSON
- Image and header/footer extraction
- Metadata extraction (paragraph, table, section counts, author, title)

Examples:
>>> from pathlib import Path
>>> import asyncio
>>> from doc_parser.parsers.docx.parser import DocxParser
>>> from doc_parser.core.settings import Settings
>>> settings = Settings(output_format="markdown")
>>> parser = DocxParser(settings)
>>> result = asyncio.run(parser.parse(Path("example.docx")))
>>> print(result.metadata["paragraphs"])  # Number of paragraphs extracted
"""

from collections.abc import Iterable
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import docx
from docx.document import Document
from docx.opc.exceptions import PackageNotFoundError
from docx.table import Table
from docx.text.paragraph import Paragraph

from doc_parser.config import AppConfig
from doc_parser.core.base import BaseParser
from doc_parser.utils.format_helpers import rows_to_markdown

if TYPE_CHECKING:  # pragma: no cover
    from pydantic import BaseModel


@AppConfig.register("docx", [".docx"])
class DocxParser(BaseParser):
    """Parser for Microsoft Word documents (.docx).

    Provides methods to validate, parse, and extract content in Markdown or JSON formats.

    Args:
        config (Settings): Global parser settings instance.

    Attributes:
        extract_images (bool): Whether to extract embedded images.
        extract_headers_footers (bool): Whether to include headers and footers.
        preserve_formatting (bool): Whether to preserve bold, italic, and underline.

    Examples:
        >>> from pathlib import Path
        >>> import asyncio
        >>> from doc_parser.parsers.docx.parser import DocxParser
        >>> from doc_parser.core.settings import Settings
        >>> settings = Settings(parser_settings={"docx": {"extract_images": False}})
        >>> parser = DocxParser(settings)
        >>> result = asyncio.run(parser.parse(Path("sample.docx")))
        >>> assert "tables" in result.metadata
    """

    def __init__(self, config: AppConfig):
        """Initialize DOCX parser."""
        super().__init__(config)

        # Get DOCX-specific settings
        docx_config = config.parser_cfg("docx")
        self.extract_images = docx_config.get("extract_images", True)
        self.extract_headers_footers = docx_config.get("extract_headers_footers", False)
        self.preserve_formatting = docx_config.get("preserve_formatting", True)

    async def validate_input(self, input_path: Path) -> bool:
        """Validate whether the input path points to a valid DOCX file.

        Args:
            input_path (Path): Path to the .docx file.

        Returns:
            bool: True if the file is a valid DOCX document, False otherwise.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> valid = asyncio.run(DocxParser(Settings()).validate_input(Path("doc.docx")))
            >>> print(valid)
        """
        if not self._has_supported_extension(input_path):
            return False
        try:
            # Try to open with python-docx to validate
            docx.Document(str(input_path))
        except PackageNotFoundError:
            return False
        return True

    # ------------------------------------------------------------------
    # BaseStructuredParser hooks
    # ------------------------------------------------------------------

    async def _open_document(self, input_path: Path, *, options: "BaseModel | None" = None) -> Document:
        """Open *input_path* with **python-docx** and return a Document object.

        The *options* parameter is accepted for API compatibility but is not
        used by the DOCX parser at this time.
        """
        _ = options  # future-proof - avoid unused-arg warnings
        return docx.Document(str(input_path))

    def _extra_metadata(self, doc: Any) -> dict[str, Any]:
        """Return DOCX-specific metadata counts and core properties."""
        # Cast to python-docx Document for type-check; if wrong type we fall back gracefully
        from docx.document import Document

        if isinstance(doc, Document):
            document = doc
        else:
            return {}

        meta: dict[str, Any] = {
            "paragraphs": len(document.paragraphs),
            "tables": len(document.tables),
            "sections": len(document.sections),
        }

        # Optional core properties
        if getattr(document.core_properties, "title", None):
            meta["title"] = document.core_properties.title
        if getattr(document.core_properties, "author", None):
            meta["author"] = document.core_properties.author
        return meta

    async def _extract_as_markdown(self, doc: Document) -> str:
        """Convert a python-docx Document to a Markdown string.

        Iterates through paragraphs and tables, generating GitHub-flavored Markdown.
        Includes headers and footers if enabled in settings.

        Args:
            doc (Document): python-docx Document object.

        Returns:
            str: Combined Markdown content.

        Example:
            >>> import asyncio, docx
            >>> from pathlib import Path
            >>> parser = DocxParser(Settings())
            >>> doc = docx.Document(str(Path("doc.docx")))
            >>> md = asyncio.run(parser._extract_as_markdown(doc))
            >>> assert "|" in md or md.startswith("#")
        """
        content_parts: list[str] = []

        # Process document elements in order
        for element in self._iter_block_items(doc):
            if isinstance(element, Paragraph):
                md_text = self._paragraph_to_markdown(element)
                if md_text.strip():
                    content_parts.append(md_text)
            elif isinstance(element, Table):
                md_table = self._table_to_markdown(element)
                if md_table:
                    content_parts.append(md_table)

        # Extract headers/footers if requested
        if self.extract_headers_footers:
            headers_footers = self._extract_headers_footers(doc)
            if headers_footers:
                content_parts.append("\n---\n## Headers and Footers\n")
                content_parts.append(headers_footers)

        return "\n\n".join(content_parts)

    async def _extract_as_json(self, doc: Document) -> str:
        """Serialize DOCX content into a JSON string.

        Gathers paragraphs and tables into JSON arrays, with document properties.

        Args:
            doc (Document): python-docx Document object.

        Returns:
            str: JSON-formatted content with keys 'paragraphs', 'tables', and 'properties'.

        Example:
            >>> import asyncio, json, docx
            >>> from pathlib import Path
            >>> parser = DocxParser(Settings())
            >>> doc = docx.Document(str(Path("doc.docx")))
            >>> js = asyncio.run(parser._extract_as_json(doc))
            >>> data = json.loads(js)
            >>> assert isinstance(data.get("paragraphs"), list)
        """
        data: dict[str, Any] = {
            "paragraphs": [],
            "tables": [],
            "properties": {},
        }

        # Extract paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                para_data = {
                    "text": para.text,
                    "style": para.style.name if para.style else None,
                }
                if self.preserve_formatting:
                    para_data["runs"] = [
                        {
                            "text": run.text,
                            "bold": run.bold,
                            "italic": run.italic,
                            "underline": run.underline,
                        }
                        for run in para.runs
                    ]
                paragraphs = data["paragraphs"]
                if isinstance(paragraphs, list):
                    paragraphs.append(para_data)

        # Extract tables
        for table in doc.tables:
            # Use list comprehension for performance
            table_data = [[cell.text.strip() for cell in row.cells] for row in table.rows]
            tables_list = data["tables"]
            if isinstance(tables_list, list):
                tables_list.append(table_data)

        # Add properties
        if hasattr(doc.core_properties, "title"):
            data["properties"]["title"] = doc.core_properties.title
        if hasattr(doc.core_properties, "author"):
            data["properties"]["author"] = doc.core_properties.author

        return json.dumps(data, indent=2, ensure_ascii=False)

    def _iter_block_items(self, parent: Document | Any) -> Iterable[Paragraph | Table]:
        """Yield each paragraph and table child within parent, in document order."""
        from docx.oxml.table import CT_Tbl
        from docx.oxml.text.paragraph import CT_P
        from docx.table import Table, _Cell
        from docx.text.paragraph import Paragraph

        if isinstance(parent, Document):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            raise TypeError("Parent must be Document or _Cell")

        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    def _paragraph_to_markdown(self, paragraph: Paragraph) -> str:
        """Convert a python-docx Paragraph to Markdown with reduced branching."""
        text = paragraph.text.strip()
        if not text:
            return ""

        style_name = paragraph.style.name if paragraph.style else ""

        # -------------------------------------------------------------
        # Heading styles 1-6
        # -------------------------------------------------------------
        min_heading_prefix_len = 9  # len('Heading X')
        if style_name.startswith("Heading ") and len(style_name) >= min_heading_prefix_len and style_name[8].isdigit():
            level_char = style_name[8]
            level = int(level_char)
            level = max(1, min(level, 6))
            return "#" * level + f" {text}"

        # -------------------------------------------------------------
        # List items
        # -------------------------------------------------------------
        if style_name.startswith("List"):
            bullet_prefix = "- " if "Bullet" in style_name else "1. "
            return f"{bullet_prefix}{text}"

        # -------------------------------------------------------------
        # Inline formatting (bold / italic / underline)
        # -------------------------------------------------------------
        if self.preserve_formatting and paragraph.runs:
            pieces: list[str] = []
            for run in paragraph.runs:
                run_text = run.text
                if run.bold:
                    run_text = f"**{run_text}**"
                if run.italic:
                    run_text = f"*{run_text}*"
                if run.underline:
                    run_text = f"<u>{run_text}</u>"
                pieces.append(run_text)
            text = "".join(pieces) if pieces else text

        return text

    def _table_to_markdown(self, table: Table) -> str:
        """Convert a table to Markdown."""
        rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        return rows_to_markdown(rows)

    def _extract_headers_footers(self, doc: Document) -> str:
        """Extract headers and footers from document."""
        content = []

        for section in doc.sections:
            # Header
            if section.header and section.header.paragraphs:
                header_text = " ".join(p.text.strip() for p in section.header.paragraphs if p.text.strip())
                if header_text:
                    content.append(f"**Header:** {header_text}")

            # Footer
            if section.footer and section.footer.paragraphs:
                footer_text = " ".join(p.text.strip() for p in section.footer.paragraphs if p.text.strip())
                if footer_text:
                    content.append(f"**Footer:** {footer_text}")

        return "\n".join(content)

    def _has_supported_extension(self, input_path: Path) -> bool:
        return super()._has_supported_extension(input_path)
