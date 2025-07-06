"""doc_parser command-line interface (CLI).

This CLI enables parsing of documents (PDF, DOCX, Excel, HTML, PPTX) and URLs
with optional caching and LLM-based post-processing.

Commands:
  parse   Parse a document or URL and output in markdown or JSON.

Examples:
  >>> python -m doc_parser.cli parse sample.pdf -f markdown
  >>> python -m doc_parser.cli parse sample.docx --format json --no-cache -o result.json
  >>> python -m doc_parser.cli parse https://example.com --post-prompt "Summarize content"
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer

from .core.registry import ParserRegistry
from .core.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path

app = typer.Typer(add_completion=False, help="Document parser CLI")

# Add module-level Typer argument and option defaults to avoid function calls in defaults (B008)
FILE_ARG = typer.Argument(..., exists=True, readable=True, help="Input document or URL to parse")
FORMAT_OPTION = typer.Option("markdown", "--format", "-f", help="Output format: markdown or json")
NO_CACHE_OPTION = typer.Option(False, "--no-cache", help="Disable cache for this run")
POST_PROMPT_OPTION = typer.Option(None, "--post-prompt", help="LLM prompt for post-processing")
OUTPUT_OPTION = typer.Option(None, "--output", "-o", help="File path to save output instead of stdout")


@app.command()
def parse(
    file: Path = FILE_ARG,
    format: str = FORMAT_OPTION,
    no_cache: bool = NO_CACHE_OPTION,
    post_prompt: str | None = POST_PROMPT_OPTION,
    output: Path | None = OUTPUT_OPTION,
) -> None:
    """Parse a document or URL and print or save the result.

    Determines the appropriate parser based on file extension or URL,
    applies caching and optional post-processing, and outputs content.

    Args:
        file (Path): Input document path or URL.
        format (str): 'markdown' or 'json'.
        no_cache (bool): If True, disables caching.
        post_prompt (Optional[str]): LLM prompt for post-processing.
        output (Optional[Path]): Destination file path for saving result.

    Examples:
        >>> # Parse PDF to markdown and print
        >>> python -m doc_parser.cli parse sample.pdf -f markdown
        >>> # Parse DOCX to JSON without cache and save
        >>> python -m doc_parser.cli parse doc.docx --format json --no-cache -o result.json
        >>> # Parse URL with a post-processing prompt
        >>> python -m doc_parser.cli parse example.url --post-prompt "Summarize content"
    """
    settings = Settings(output_format=format, use_cache=not no_cache, post_prompt=post_prompt)

    parser = ParserRegistry.from_path(file, settings)

    # Run synchronously for CLI ease
    result = parser.parse_sync(file)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.content, encoding="utf-8")
        typer.echo(f"Saved output to {output}")
    else:
        typer.echo(result.content)


if __name__ == "__main__":  # pragma: no cover
    app()
