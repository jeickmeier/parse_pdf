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

import asyncio
from pathlib import Path  # required at runtime
from typing import Any, cast

import typer

from .config import AppConfig
from .options import PdfOptions

# For type checking only (avoid reimport warnings)

app = typer.Typer(add_completion=False, help="Document parser CLI")

# Add module-level Typer argument and option defaults to avoid function calls in defaults (B008)
FILE_ARG = typer.Argument(..., exists=True, readable=True, help="Input document or URL to parse")
FORMAT_OPTION = typer.Option("markdown", "--format", "-f", help="Output format: markdown or json")
NO_CACHE_OPTION = typer.Option(False, "--no-cache", help="Disable cache for this run")
POST_PROMPT_OPTION = typer.Option(None, "--post-prompt", help="LLM prompt for post-processing")
OUTPUT_OPTION = typer.Option(None, "--output", "-o", help="File path to save output instead of stdout")

# PDF-specific options
PAGE_RANGE_OPTION = typer.Option(
    None,
    "--page-range",
    help="For PDFs: inclusive 1-based page range, e.g. '1:3'",
)
PROMPT_TEMPLATE_OPTION = typer.Option(
    None,
    "--prompt-template",
    help="Custom prompt template (string or template ID) for extraction (PDF only).",
)

# New configuration helpers
CONFIG_FILE_OPTION = typer.Option(
    None,
    "--config-file",
    "-c",
    exists=True,
    readable=True,
    help="Optional JSON/TOML/YAML file with Settings overrides",
)

_ENV_CONFIG_PATH = "DOC_PARSER_CONFIG"


def _load_config_file(path: Path | None) -> dict[str, Any]:
    """Return dictionary from *path* (JSON / TOML / YAML)."""
    import json
    from pathlib import Path as _Path

    if path is None:
        return {}

    path = _Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    if suffix in {".json"}:
        return cast("dict[str, Any]", json.loads(path.read_text()))
    if suffix in {".toml"}:
        try:
            import tomllib as _toml
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise RuntimeError("TOML support requires Python 3.11+ or 'tomli' package") from exc
        return _toml.loads(path.read_text())
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml as _yaml  # PyYAML
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise RuntimeError("YAML support requires 'pyyaml' package") from exc
        loaded = _yaml.safe_load(path.read_text()) or {}
        if not isinstance(loaded, dict):
            raise TypeError("YAML config must represent a mapping at top-level")
        return cast("dict[str, Any]", loaded)
    raise ValueError("Unsupported config file extension (use .json, .toml, .yaml)")


@app.command()
def parse(
    file: Path = FILE_ARG,
    format: str = FORMAT_OPTION,
    no_cache: bool = NO_CACHE_OPTION,
    post_prompt: str | None = POST_PROMPT_OPTION,
    output: Path | None = OUTPUT_OPTION,
    page_range: str | None = PAGE_RANGE_OPTION,
    prompt_template: str | None = PROMPT_TEMPLATE_OPTION,
    config_file: Path | None = CONFIG_FILE_OPTION,
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
        page_range (Optional[str]): For PDFs: inclusive 1-based page range, e.g. '1:3'.
        prompt_template (Optional[str]): Custom prompt template (string or template ID) for extraction (PDF only).
        config_file (Optional[Path]): Optional JSON/TOML/YAML file with Settings overrides.

    Examples:
        >>> # Parse PDF to markdown and print
        >>> python -m doc_parser.cli parse sample.pdf -f markdown
        >>> # Parse DOCX to JSON without cache and save
        >>> python -m doc_parser.cli parse doc.docx --format json --no-cache -o result.json
        >>> # Parse URL with a post-processing prompt
        >>> python -m doc_parser.cli parse example.url --post-prompt "Summarize content"
    """
    # ------------------------------------------------------------------
    # Merge CLI / env / file overrides into Settings
    # ------------------------------------------------------------------
    import os

    # 1) Load from --config-file or env path
    file_cfg: dict[str, Any] = {}
    cfg_path: Path | None = config_file
    if cfg_path is None and (env_val := os.getenv(_ENV_CONFIG_PATH)):
        cfg_path = Path(env_val)
    if cfg_path is not None:
        file_cfg = _load_config_file(cfg_path)

    # 2) CLI overrides always win
    cli_overrides: dict[str, Any] = {
        "output_format": format,
        "use_cache": not no_cache,
        "post_prompt": post_prompt,
    }
    # Remove None values so they don't override file settings
    cli_overrides = {k: v for k, v in cli_overrides.items() if v is not None}

    merged_cfg = {**file_cfg, **cli_overrides}

    settings = AppConfig(**merged_cfg)

    parser = AppConfig.from_path(file, settings)

    # ------------------------------------------------------------------
    # Build typed options object based on parser type
    # ------------------------------------------------------------------
    options_obj: Any | None = None
    from doc_parser.parsers.pdf.parser import PDFParser  # local import to avoid heavy deps on startup

    if isinstance(parser, PDFParser):
        # Page range conversion if provided
        pr: tuple[int, int] | None = None
        if page_range:
            try:
                parts = page_range.split(":")
                if len(parts) == 2:  # noqa: PLR2004
                    pr = (int(parts[0]), int(parts[1]))
                else:
                    raise ValueError
            except ValueError as exc:  # pragma: no cover
                typer.echo("--page-range must be of form START:END", err=True)
                raise typer.Exit(1) from exc

        options_obj = PdfOptions(page_range=pr, prompt_template=prompt_template)

    # Execute asynchronous parse via asyncio.run for CLI convenience
    result = asyncio.run(parser.parse(file, options=options_obj))

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.content, encoding="utf-8")
        typer.echo(f"Saved output to {output}")
    else:
        typer.echo(result.content)


if __name__ == "__main__":  # pragma: no cover
    app()
