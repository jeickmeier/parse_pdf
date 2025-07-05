"""Document parser implementations."""

# Import parsers to trigger registration
from . import pdf, excel, docx, html, pptx

__all__ = ["pdf", "excel", "docx", "html", "pptx"]
