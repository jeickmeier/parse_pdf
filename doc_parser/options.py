"""Option objects for parser runtime configuration.

These classes replace the previous ad-hoc ``**kwargs`` mechanism that passed
miscellaneous options into ``BaseParser.parse``.  Each parser now receives a
strongly-typed options object, improving validation and static type-checking.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

# Standard library

# ----------------------------------------------------------------------------
# Shared helpers
# ----------------------------------------------------------------------------

PageRange = tuple[int, int]


class _BaseOptions(BaseModel):
    """Common ancestor for all strongly-typed parser option models."""

    # ``model_config`` replaces the legacy *Config* inner-class in Pydantic v2.
    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "forbid",  # Disallow unexpected kwargs to catch typos early.
    }


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
    @field_validator("page_range")
    @classmethod
    def _validate_page_range(cls, v: PageRange | None) -> PageRange | None:
        """Ensure *(start, end)* tuple is positive, ordered and 1-based."""
        if v is None:
            return v
        start, end = v
        if start <= 0 or end <= 0:
            raise ValueError("page_range values must be positive and 1-based")
        if start > end:
            raise ValueError("page_range start must be <= end")
        return v

    # ---------------- permanent configuration settings ----------------
    dpi: int | None = Field(
        default=None,
        description="Image resolution (dots-per-inch) used when rasterising PDF pages.",
        ge=72,
        le=600,
    )
    batch_size: int | None = Field(
        default=None,
        description="Number of pages to process per extraction batch; falls back to global *batch_size* if *None*.",
        ge=1,
    )


class HtmlOptions(_BaseOptions):
    """Run-time options specific to the HTML parser."""

    extract_sources: bool | None = Field(
        default=None,
        description="Whether to include source links embedded in the page content.",
    )
    follow_links: bool | None = Field(
        default=None,
        description="If *True*, the parser will crawl linked pages up to *max_depth*.",
    )
    max_depth: int | None = Field(
        default=None,
        ge=1,
        description="Maximum recursion depth when *follow_links* is *True*.",
    )

    # Provide sensible defaults if not explicitly overridden.
    model_config = {
        **_BaseOptions.model_config,
        "validate_default": True,
    }


class DocxOptions(_BaseOptions):
    """Run-time options specific to the DOCX parser."""

    extract_images: bool | None = Field(default=None, description="If False, embedded images are ignored.")
    extract_headers_footers: bool | None = Field(default=None, description="Include header/footer text in output.")
    preserve_formatting: bool | None = Field(default=None, description="Preserve inline formatting such as bold/italic.")


class ExcelOptions(_BaseOptions):
    """Run-time options specific to the Excel parser."""

    include_formulas: bool | None = Field(default=None, description="Include cell formulas in the output.")
    include_formatting: bool | None = Field(default=None, description="Include cell formatting metadata.")
    sheet_names: list[str] | None = Field(
        default=None,
        description="Subset of sheet names to parse; *None* parses all sheets.",
    )


class PptxOptions(_BaseOptions):
    """Run-time options specific to the PPTX parser."""

    extract_images: bool | None = Field(default=None, description="Extract slide images where possible.")
    extract_notes: bool | None = Field(default=None, description="Extract speaker notes for each slide.")
    preserve_formatting: bool | None = Field(default=None, description="Preserve basic formatting codes.")
    slide_delimiter: str | None = Field(default=None, description="Delimiter inserted between slides in Markdown output.")


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

# -----------------------------------------------------------------------------
# Notes
# -----------------------------------------------------------------------------

# This module originally depended on *Pydantic v1*'s ``validator`` API.  The
# code-base has since migrated to *Pydantic v2*, replacing the old decorators
# with :pyfunc:`pydantic.field_validator` and adopting the ``model_config``
# style for class configuration.
