"""PPTX parser implementation (skeleton)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Dict

from pptx import Presentation  # type: ignore[import-not-found]
from pptx.enum.shapes import MSO_SHAPE_TYPE
import json
import uuid

from ...core.base import BaseParser, ParseResult
from ...core.settings import Settings
from ...core.registry import ParserRegistry
from ...utils.cache import cache_get, cache_set
from ...utils.file_validators import is_supported_file
from ...utils.format_helpers import rows_to_markdown

# mypy: ignore-errors


@ParserRegistry.register("pptx", [".pptx"])
class PptxParser(BaseParser):
    """Parser for PowerPoint presentations (PPTX)."""

    def __init__(self, config: Settings):
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
    async def validate_input(self, input_path: Path) -> bool:  # noqa: D401
        """Return *True* if *input_path* points to a readable PPTX file."""
        if not is_supported_file(input_path, [".pptx"]):
            return False

        try:
            Presentation(str(input_path))
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Public entry-points
    # ------------------------------------------------------------------
    async def _parse(self, input_path: Path, **kwargs: Any) -> ParseResult:  # noqa: D401
        """Parse a PPTX file and return a ParseResult."""
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Invalid PPTX file: {input_path}"],
            )

        prs = Presentation(str(input_path))

        slide_markdowns: List[str] = []
        slide_dicts: List[Dict[str, Any]] = []

        # Directory to save extracted images if enabled
        images_dir = self.settings.output_dir / f"{input_path.stem}_images"
        if self.extract_images:
            images_dir.mkdir(parents=True, exist_ok=True)

        # Iterate through slides
        for idx, slide in enumerate(prs.slides, start=1):
            cache_key = f"{input_path.stem}_slide_{idx}"

            cached = (
                await cache_get(self.cache, cache_key)
                if self.settings.use_cache
                else None
            )

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

    def _slide_to_markdown(self, slide, images_dir: Path) -> str:
        """Convert a single slide to Markdown."""
        parts: List[str] = []

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

    def _slide_to_dict(self, slide, images_dir: Path) -> Dict[str, Any]:
        """Convert slide to a dictionary for JSON output."""
        data: Dict[str, Any] = {
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
    def _text_frame_to_markdown_lines(self, text_frame) -> List[str]:
        lines: List[str] = []
        for para in text_frame.paragraphs:
            txt = para.text.strip()
            if not txt:
                continue
            level = para.level or 0
            prefix = ("  " * level) + ("- " if level > 0 else "")
            lines.append(prefix + txt)
        return lines

    # ---------------- Table helpers ----------------
    def _table_to_markdown(self, table) -> str:
        rows = [
            [cell.text_frame.text.strip() for cell in row.cells] for row in table.rows
        ]
        return rows_to_markdown(rows)

    def _table_to_list(self, table):
        return [
            [cell.text_frame.text.strip() for cell in row.cells] for row in table.rows
        ]

    # ---------------- Image helpers ----------------
    def _save_image(self, shape, images_dir: Path) -> str:
        image = shape.image
        filename = f"{uuid.uuid4().hex}.{image.ext}"
        filepath = images_dir / filename
        with open(filepath, "wb") as f:
            f.write(image.blob)
        # Return relative path
        return str(filepath.relative_to(self.settings.output_dir).as_posix())
