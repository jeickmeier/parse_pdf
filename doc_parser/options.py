"""Option objects for parser runtime configuration.

These classes replace the previous ad-hoc ``**kwargs`` mechanism that passed
miscellaneous options into ``BaseParser.parse``.  Each parser now receives a
strongly-typed options object, improving validation and static type-checking.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, validator  # Pydantic v1 compatible

# Standard library

# ----------------------------------------------------------------------------
# Shared helpers
# ----------------------------------------------------------------------------

PageRange = tuple[int, int]


class _BaseOptions(BaseModel):  # pylint: disable=too-few-public-methods
    """Common ancestor to allow isinstance checks across option objects."""

    class Config:  # pylint: disable=too-few-public-methods
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "forbid"  # Disallow unexpected kwargs to catch typos early.


# ----------------------------------------------------------------------------
# Parser-specific option models
# ----------------------------------------------------------------------------


class PdfOptions(_BaseOptions):
    """Run-time options specific to the PDF parser."""

    page_range: PageRange | None = Field(
        default=None,
        description="Inclusive 1-based (start, end) page range to extract.  If\n        *None*, the full document is processed.",
    )
    prompt_template: str | None = Field(
        default=None,
        description="Custom prompt template (template string or ID) used during\n        downstream LLM summarisation, if applicable.",
    )

    # Ensure correct ordering of the tuple and positive indices
    @validator("page_range")
    def _validate_page_range(cls, v: PageRange | None) -> PageRange | None:  # noqa: N805
        if v is None:
            return v
        start, end = v
        if start <= 0 or end <= 0:
            raise ValueError("page_range values must be positive and 1-based")
        if start > end:
            raise ValueError("page_range start must be <= end")
        return v


class HtmlOptions(_BaseOptions):
    """Run-time options specific to the HTML parser."""

    extract_sources: bool | None = Field(
        default=None,
        description="Whether to include source links embedded in the page content.",
    )
    follow_links: bool | None = Field(
        default=None,
        description="If *True*, the parser will crawl linked pages up to\n        *max_depth*.",
    )
    max_depth: int | None = Field(
        default=None,
        ge=1,
        description="Maximum recursion depth when *follow_links* is *True*.",
    )


class DocxOptions(_BaseOptions):
    """Run-time options specific to the DOCX parser."""

    extract_images: bool | None = Field(default=None)
    extract_headers_footers: bool | None = Field(default=None)
    preserve_formatting: bool | None = Field(default=None)


class ExcelOptions(_BaseOptions):
    """Run-time options specific to the Excel parser."""

    include_formulas: bool | None = Field(default=None)
    include_formatting: bool | None = Field(default=None)
    sheet_names: list[str] | None = Field(
        default=None,
        description="Subset of sheet names to parse; *None* parses all sheets.",
    )


class PptxOptions(_BaseOptions):
    """Run-time options specific to the PPTX parser."""

    extract_images: bool | None = Field(default=None)
    extract_notes: bool | None = Field(default=None)
    preserve_formatting: bool | None = Field(default=None)
    slide_delimiter: str | None = Field(default=None)


# ----------------------------------------------------------------------------
# Public re-exports
# ----------------------------------------------------------------------------

__all__ = [
    "DocxOptions",
    "ExcelOptions",
    "HtmlOptions",
    "PageRange",
    "PdfOptions",
    "PptxOptions",
]
