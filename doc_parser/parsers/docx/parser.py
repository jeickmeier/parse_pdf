"""DOCX parser implementation."""

from pathlib import Path
import docx
from docx.document import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import json
from typing import Any, Iterable, Union, Dict, List

from ...core.base import BaseParser, ParseResult
from ...core.registry import ParserRegistry
from ...core.settings import Settings
from ...utils.file_validators import is_supported_file
from ...utils.format_helpers import rows_to_markdown


@ParserRegistry.register("docx", [".docx"])
class DocxParser(BaseParser):
    """Parser for Word documents."""

    def __init__(self, config: Settings):
        """Initialize DOCX parser."""
        super().__init__(config)

        # Get DOCX-specific settings
        docx_config = config.get_parser_config("docx")
        self.extract_images = docx_config.get("extract_images", True)
        self.extract_headers_footers = docx_config.get("extract_headers_footers", False)
        self.preserve_formatting = docx_config.get("preserve_formatting", True)

    async def validate_input(self, input_path: Path) -> bool:
        """Validate if the input file is a valid DOCX file."""
        if not is_supported_file(input_path, [".docx"]):
            return False

        try:
            # Try to open with python-docx to validate
            docx.Document(str(input_path))
            return True
        except Exception:
            return False

    async def _parse(self, input_path: Path, **kwargs: Any) -> ParseResult:
        """
        Parse DOCX document.

        Args:
            input_path: Path to DOCX file
            **kwargs: Additional options

        Returns:
            ParseResult with extracted content
        """
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Invalid DOCX file: {input_path}"],
            )

        try:
            doc = docx.Document(str(input_path))

            # Extract content based on format
            if self.settings.output_format == "markdown":
                content = await self._extract_as_markdown(doc, input_path)
            elif self.settings.output_format == "json":
                content = await self._extract_as_json(doc, input_path)
            else:
                content = await self._extract_as_markdown(doc, input_path)

            # Build metadata
            metadata = self.get_metadata(input_path)
            metadata.update(
                {
                    "paragraphs": len(doc.paragraphs),
                    "tables": len(doc.tables),
                    "sections": len(doc.sections),
                }
            )

            # Add document properties if available
            if hasattr(doc.core_properties, "title") and doc.core_properties.title:
                metadata["title"] = doc.core_properties.title
            if hasattr(doc.core_properties, "author") and doc.core_properties.author:
                metadata["author"] = doc.core_properties.author

            return ParseResult(
                content=content, metadata=metadata, format=self.settings.output_format
            )

        except Exception as e:
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Failed to parse DOCX file: {str(e)}"],
            )

    async def _extract_as_markdown(self, doc: Document, input_path: Path) -> str:
        """Extract DOCX content as Markdown."""
        content_parts: List[str] = []

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

    async def _extract_as_json(self, doc: Document, input_path: Path) -> str:
        """Extract DOCX content as JSON."""
        data: Dict[str, Any] = {
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
            table_data = []
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text.strip())
                table_data.append(row_data)
            tables_list = data["tables"]
            if isinstance(tables_list, list):
                tables_list.append(table_data)

        # Add properties
        if hasattr(doc.core_properties, "title"):
            data["properties"]["title"] = doc.core_properties.title
        if hasattr(doc.core_properties, "author"):
            data["properties"]["author"] = doc.core_properties.author

        return json.dumps(data, indent=2, ensure_ascii=False)

    def _iter_block_items(
        self, parent: Union[Document, Any]
    ) -> Iterable[Union[Paragraph, Table]]:
        """
        Yield each paragraph and table child within parent, in document order.
        """
        from docx.document import Document
        from docx.oxml.table import CT_Tbl
        from docx.oxml.text.paragraph import CT_P
        from docx.table import _Cell, Table
        from docx.text.paragraph import Paragraph

        if isinstance(parent, Document):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            raise ValueError("Parent must be Document or _Cell")

        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    def _paragraph_to_markdown(self, paragraph: Paragraph) -> str:
        """Convert a paragraph to Markdown."""
        text = paragraph.text.strip()
        if not text:
            return ""

        # Detect heading styles
        style_name = paragraph.style.name if paragraph.style else ""

        if style_name.startswith("Heading 1"):
            return f"# {text}"
        elif style_name.startswith("Heading 2"):
            return f"## {text}"
        elif style_name.startswith("Heading 3"):
            return f"### {text}"
        elif style_name.startswith("Heading 4"):
            return f"#### {text}"
        elif style_name.startswith("Heading 5"):
            return f"##### {text}"
        elif style_name.startswith("Heading 6"):
            return f"###### {text}"

        # Handle list items
        if style_name.startswith("List"):
            if "Bullet" in style_name:
                return f"- {text}"
            else:
                return f"1. {text}"

        # Handle formatting if preserving
        if self.preserve_formatting and paragraph.runs:
            formatted_text = ""
            for run in paragraph.runs:
                run_text = run.text
                if run.bold:
                    run_text = f"**{run_text}**"
                if run.italic:
                    run_text = f"*{run_text}*"
                if run.underline:
                    run_text = f"<u>{run_text}</u>"
                formatted_text += run_text
            return formatted_text

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
                header_text = " ".join(
                    p.text.strip() for p in section.header.paragraphs if p.text.strip()
                )
                if header_text:
                    content.append(f"**Header:** {header_text}")

            # Footer
            if section.footer and section.footer.paragraphs:
                footer_text = " ".join(
                    p.text.strip() for p in section.footer.paragraphs if p.text.strip()
                )
                if footer_text:
                    content.append(f"**Footer:** {footer_text}")

        return "\n".join(content)
