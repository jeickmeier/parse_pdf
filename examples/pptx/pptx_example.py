"""Example usage of the PptxParser.

This script generates a small sample PowerPoint file on the fly (to avoid
committing binary assets) and then parses it using the library. The resulting
Markdown is printed to stdout.
"""

# mypy: ignore-errors

from __future__ import annotations

import asyncio
from pathlib import Path

from pptx import Presentation  # type: ignore
from pptx.util import Inches  # type: ignore

from doc_parser.config import AppConfig


def _build_sample_pptx(path: Path) -> None:
    """Create a minimal two-slide PPTX for demonstration purposes."""
    prs = Presentation()

    # Slide 1 – title & bullet list
    slide_layout = prs.slide_layouts[1]  # Title & content
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Document Parser Demo"
    body = slide.shapes.placeholders[1].text_frame
    body.text = "Key Features"
    for line in [
        "Supports PDF, DOCX, XLSX, PPTX, HTML",
        "AI-powered extraction",
        "Smart caching",
    ]:
        p = body.add_paragraph()
        p.text = line
        p.level = 1

    # Slide 2 – table example
    slide_layout = prs.slide_layouts[5]  # Title only
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Simple Table"

    rows, cols = 3, 3
    left, top, width, height = Inches(1), Inches(2), Inches(8), Inches(1.5)
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    tbl = table_shape.table

    # Header row formatting
    headers = ["Col A", "Col B", "Col C"]
    for col, text in enumerate(headers):
        cell = tbl.cell(0, col)
        cell.text = text
        cell.text_frame.paragraphs[0].font.bold = True

    # Data rows
    for row in range(1, rows):
        for col in range(cols):
            tbl.cell(row, col).text = f"R{row}C{col}"

    prs.save(path)


async def _demo() -> None:
    # Ensure output directory exists and generate sample PPTX
    sample_path = Path("outputs/sample_demo.pptx")
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    _build_sample_pptx(sample_path)

    # Configure parser
    cfg = AppConfig(output_format="markdown")
    parser = AppConfig.from_path(sample_path, cfg)

    # Parse the PPTX file
    result = await parser.parse(sample_path)

    # Print the resulting Markdown to stdout
    print(result.content)


if __name__ == "__main__":
    asyncio.run(_demo())
