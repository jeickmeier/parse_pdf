from doc_parser.config import AppConfig
from doc_parser.parsers.pdf.parser import PDFParser


def test_combine_results():
    pdf_parser = PDFParser(AppConfig())
    inputs = ["Line 1", "", "Line 2", "", "", "Line 3"]
    combined = pdf_parser._combine_results(inputs)  # noqa: SLF001
    # Should join with single blank lines between distinct blocks, no leading/trailing multiples
    expected = "Line 1\n\nLine 2\n\nLine 3"
    assert combined == expected 