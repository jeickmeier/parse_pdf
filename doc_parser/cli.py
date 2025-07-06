"""Command-line interface for the doc-parser library.

Example::

    $ python -m doc_parser.cli parse myfile.pdf --format markdown --no-cache
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer  # type: ignore[import-not-found]

from .core.registry import ParserRegistry
from .core.settings import Settings

app = typer.Typer(add_completion=False, help="Document parser CLI")


@app.command()  # type: ignore[misc]
def parse(
    file: Path = typer.Argument(
        ..., exists=True, readable=True, help="Input file to parse"
    ),
    format: str = typer.Option(
        "markdown", "--format", "-f", help="Output format: markdown or json"
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Disable cache for this run"
    ),
    post_prompt: Optional[str] = typer.Option(
        None, "--post-prompt", help="Optional post-processing prompt"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Save result to this path instead of stdout"
    ),
) -> None:
    """Parse *file* and print or save result."""

    settings = Settings(
        output_format=format, use_cache=not no_cache, post_prompt=post_prompt
    )

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
