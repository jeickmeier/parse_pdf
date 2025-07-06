"""Document parser implementations."""

# Import parsers to trigger registration
from . import docx, excel, html, pdf, pptx

__all__ = ["docx", "excel", "html", "pdf", "pptx"]
