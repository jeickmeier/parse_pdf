"""PPTX parser implementation for Microsoft PowerPoint (.pptx) presentations.

This module provides a parser that extracts slide content, images, and speaker notes
from PPTX files. It supports output in Markdown or JSON formats, caching of slide
results, and configurable extraction options.

Examples:
>>> import asyncio
>>> from pathlib import Path
>>> from doc_parser.parsers.pptx.parser import PptxParser
>>> from doc_parser.core.settings import Settings
>>> settings = Settings(output_format="markdown", parser_settings={"pptx": {"extract_images": False}})
>>> parser = PptxParser(settings)
>>> result = asyncio.run(parser.parse(Path("presentation.pptx")))
>>> print(result.metadata["slides"])
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
import uuid

from pptx import Presentation  # type: ignore[import-not-found]
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.exc import PackageNotFoundError  # type: ignore[import-not-found]

from doc_parser.config import AppConfig as ParserRegistry, AppConfig as Settings
from doc_parser.core.base import BaseParser, ParseResult
from doc_parser.utils.cache import cache_get, cache_set
from doc_parser.utils.format_helpers import rows_to_markdown

if TYPE_CHECKING:
    from pathlib import Path

    from pptx.text.text import _BaseTextFrame

    from doc_parser.core.settings import Settings

# mypy: ignore-errors


@ParserRegistry.register("pptx", [".pptx"])
class PptxParser(BaseParser):
    """Parser for PowerPoint presentations (.pptx).

    Extracts slide text, tables, images, and notes into Markdown or JSON.

    Args:
        config (Settings): Global parser settings with optional 'pptx' overrides.

    Attributes:
        extract_images (bool): Whether to save and include slide images.
        extract_notes (bool): Whether to include speaker notes.
        preserve_formatting (bool): Whether to preserve text formatting.
        slide_delimiter (str): Delimiter string between slides in Markdown.

    Examples:
        >>> import asyncio
        >>> from pathlib import Path
        >>> from doc_parser.parsers.pptx.parser import PptxParser
        >>> from doc_parser.core.settings import Settings
        >>> parser = PptxParser(Settings(parser_settings={"pptx": {"slide_delimiter": "---"}}))
        >>> result = asyncio.run(parser.parse(Path("slides.pptx")))
        >>> assert result.format == "markdown"
    """

    def __init__(self, config: Settings):
        """Initialize PPTX parser settings.

        Args:
            config (Settings): Parser configuration object.
        """
        super().__init__(config)

        # PPTX-specific configuration
        pptx_cfg = config.get_parser_config("pptx")
        self.extract_images: bool = pptx_cfg.get("extract_images", True)
        self.extract_notes: bool = pptx_cfg.get("extract_notes", False)
        self.preserve_formatting: bool = pptx_cfg.get("preserve_formatting", True)
        self.slide_delimiter: str = pptx_cfg.get("slide_delimiter", "---")

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    async def validate_input(self, input_path: Path) -> bool:
        """Validate whether input_path points to a readable PPTX file.

        Args:
            input_path (Path): Path to the .pptx file.

        Returns:
            bool: True if the file exists, has a .pptx extension, and can be opened.
        """
        if not self._has_supported_extension(input_path):
            return False
        try:
            Presentation(str(input_path))
        except (PackageNotFoundError, OSError):
            return False
        return True

    # ------------------------------------------------------------------
    # Public entry-points
    # ------------------------------------------------------------------
    async def _parse(self, input_path: Path, **_kwargs: Any) -> ParseResult:
        """Parse a PPTX file and return a ParseResult.

        Iterates through slides, extracting content and caching results.

        Args:
            input_path (Path): Path to the PPTX file.
            **kwargs: Additional parser options (unused).

        Returns:
            ParseResult: Contains combined content, metadata, and format.
        """
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Invalid PPTX file: {input_path}"],
            )

        prs = Presentation(str(input_path))

        slide_markdowns: list[str] = []
        slide_dicts: list[dict[str, Any]] = []

        # Directory to save extracted images if enabled
        images_dir = self.settings.output_dir / f"{input_path.stem}_images"
        if self.extract_images:
            images_dir.mkdir(parents=True, exist_ok=True)

        # Iterate through slides
        for idx, slide in enumerate(prs.slides, start=1):
            # Include output format in cache key so markdown & JSON caches do not collide
            cache_key = f"{input_path.stem}_{self.settings.output_format}_slide_{idx}"

            cached = await cache_get(self.cache, cache_key) if self.settings.use_cache else None

            if cached:
                # Cached content reuse
                if self.settings.output_format == "json":
                    slide_dicts.append(cached["data"])
                else:
                    slide_markdowns.append(cached["content"])
                continue

            # Fresh extraction
            if self.settings.output_format == "json":
                slide_data = self._slide_to_dict(slide, images_dir)
                slide_dicts.append(slide_data)
                await cache_set(self.cache, cache_key, {"data": slide_data})
            else:
                slide_md = self._slide_to_markdown(slide, images_dir)
                slide_markdowns.append(slide_md)
                await cache_set(self.cache, cache_key, {"content": slide_md})

        # Combine slide outputs
        if self.settings.output_format == "json":
            combined_content = json.dumps(slide_dicts, indent=2, ensure_ascii=False)
        else:
            delimiter = f"\n\n{self.slide_delimiter}\n\n"
            combined_content = delimiter.join(slide_markdowns)

        metadata = self.get_metadata(input_path)
        metadata.update({"slides": len(prs.slides)})

        return ParseResult(
            content=combined_content,
            metadata=metadata,
            format=self.settings.output_format,
        )

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _slide_to_markdown(self, slide: Any, images_dir: Path) -> str:
        """Convert a single slide to a Markdown string.

        Args:
            slide (Slide): pptx Slide object.
            images_dir (Path): Directory for saving extracted images.

        Returns:
            str: Markdown representation including title, text, tables, images, and notes.
        """
        parts: list[str] = []

        # Title placeholder
        if slide.shapes.title and slide.shapes.title.text_frame.text.strip():
            parts.append(f"# {slide.shapes.title.text_frame.text.strip()}")

        for shape in slide.shapes:
            if shape.has_table:
                parts.append(self._table_to_markdown(shape.table))
            elif shape.has_text_frame and shape is not slide.shapes.title:
                parts.extend(self._text_frame_to_markdown_lines(shape.text_frame))
            elif self.extract_images and shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                rel_path = self._save_image(shape, images_dir)
                parts.append(f"![image]({rel_path})")

        if self.extract_notes and slide.has_notes_slide and slide.notes_slide:
            note_text = slide.notes_slide.notes_text_frame.text.strip()
            if note_text:
                parts.append("\n**Notes:**\n" + note_text)

        return "\n".join(parts)

    def _slide_to_dict(self, slide: Any, images_dir: Path) -> dict[str, Any]:
        """Convert a single slide to a JSON-serializable dictionary.

        Args:
            slide (Slide): pptx Slide object.
            images_dir (Path): Directory for saving extracted images.

        Returns:
            Dict[str, Any]: Structured data with keys 'title', 'text', 'tables', 'images', 'notes'.
        """
        data: dict[str, Any] = {
            "title": slide.shapes.title.text_frame.text.strip()
            if slide.shapes.title and slide.shapes.title.text_frame.text.strip()
            else "",
            "text": [],
            "tables": [],
            "images": [],
            "notes": "",
        }

        for shape in slide.shapes:
            if shape.has_table:
                data["tables"].append(self._table_to_list(shape.table))
            elif shape.has_text_frame and shape is not slide.shapes.title:
                for para in shape.text_frame.paragraphs:
                    txt = para.text.strip()
                    if txt:
                        data["text"].append(txt)
            elif self.extract_images and shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                rel_path = self._save_image(shape, images_dir)
                data["images"].append(rel_path)

        if self.extract_notes and slide.has_notes_slide and slide.notes_slide:
            data["notes"] = slide.notes_slide.notes_text_frame.text.strip()

        return data

    # ---------------- Text helpers ----------------
    def _text_frame_to_markdown_lines(self, text_frame: _BaseTextFrame) -> list[str]:
        lines: list[str] = []
        for para in text_frame.paragraphs:
            txt = para.text.strip()
            if not txt:
                continue
            level = para.level or 0
            prefix = ("  " * level) + ("- " if level > 0 else "")
            lines.append(prefix + txt)
        return lines

    # ---------------- Table helpers ----------------
    def _table_to_markdown(self, table: Any) -> str:
        """Convert a table shape to Markdown."""
        rows = [[cell.text_frame.text.strip() for cell in row.cells] for row in table.rows]
        return rows_to_markdown(rows)

    def _table_to_list(self, table: Any) -> list[list[str]]:
        return [[cell.text_frame.text.strip() for cell in row.cells] for row in table.rows]

    # ---------------- Image helpers ----------------
    def _save_image(self, shape: Any, images_dir: Path) -> str:
        image = shape.image
        filename = f"{uuid.uuid4().hex}.{image.ext}"
        filepath = images_dir / filename
        # Save image file
        with filepath.open("wb") as f:
            f.write(image.blob)
        # Return relative path
        return str(filepath.relative_to(self.settings.output_dir).as_posix())
