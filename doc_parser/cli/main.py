"""CLI interface for document parser."""

import asyncio
import click
from pathlib import Path
import sys
from typing import Optional

from ..core.config import ParserConfig
from ..core.registry import ParserRegistry
from ..prompts.base import PromptTemplate


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file (YAML/JSON)",
)
@click.option(
    "--outputs", "-o", type=click.Path(path_type=Path), help="Output file path"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "json", "html"]),
    default="markdown",
    help="Output format",
)
@click.option(
    "--prompt-template",
    "-p",
    type=click.Path(exists=True, path_type=Path),
    help="Custom prompt template file",
)
@click.option("--cache/--no-cache", default=True, help="Enable/disable caching")
@click.option("--workers", "-w", type=int, help="Maximum concurrent workers")
@click.option("--verbose", "-v", is_flag=True, help="Verbose outputs")
def cli(
    input_file: Path,
    config: Optional[Path],
    output: Optional[Path],
    format: str,
    prompt_template: Optional[Path],
    cache: bool,
    workers: Optional[int],
    verbose: bool,
) -> None:
    """
    Parse documents with customizable options.

    Supports PDF, Excel (XLSX/XLS), Word (DOCX), and web content (Perplexity).
    """
    asyncio.run(
        parse_document(
            input_file, config, output, format, prompt_template, cache, workers, verbose
        )
    )


async def parse_document(
    input_file: Path,
    config_path: Optional[Path],
    output_path: Optional[Path],
    format: str,
    prompt_template_path: Optional[Path],
    use_cache: bool,
    workers: Optional[int],
    verbose: bool,
) -> None:
    """Async document parsing function."""

    try:
        # Load or create configuration
        if config_path:
            config = ParserConfig.from_file(config_path)
            if verbose:
                click.echo(f"Loaded configuration from {config_path}")
        else:
            config = ParserConfig()

        # Override settings from CLI
        config.output_format = format
        config.use_cache = use_cache
        if workers:
            config.max_workers = workers

        # Load custom prompt template if provided
        prompt = None
        if prompt_template_path:
            prompt = PromptTemplate.from_file(prompt_template_path)
            if verbose:
                click.echo(f"Loaded prompt template from {prompt_template_path}")

        # Get appropriate parser
        if not ParserRegistry.is_supported(input_file):
            click.echo(f"Error: Unsupported file type '{input_file.suffix}'", err=True)
            click.echo(
                f"Supported formats: {list(ParserRegistry.list_parsers().keys())}",
                err=True,
            )
            sys.exit(1)

        parser = ParserRegistry.get_parser(input_file, config)

        if verbose:
            click.echo(f"Using parser: {parser.__class__.__name__}")
            click.echo(f"Processing: {input_file}")

        # Parse document
        with click.progressbar(length=1, label="Parsing document") as bar:
            result = await parser.parse_with_cache(input_file, prompt_template=prompt)
            bar.update(1)

        # Check for errors
        if result.errors:
            click.echo("Errors encountered during parsing:", err=True)
            for error in result.errors:
                click.echo(f"  - {error}", err=True)
            if not result.content:
                sys.exit(1)

        # Output results
        if output_path:
            output_path.write_text(result.content)
            click.echo(f"Output saved to: {output_path}")
        else:
            click.echo(result.content)

        # Display metadata if verbose
        if verbose:
            click.echo("\nMetadata:")
            for key, value in result.metadata.items():
                click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@click.command()
@click.option(
    "--save", "-s", type=click.Path(path_type=Path), help="Save example config to file"
)
def config_example(save: Optional[Path]) -> None:
    """Show example configuration."""
    example_config = ParserConfig(
        cache_dir=Path("./cache"),
        output_dir=Path("./outputs"),
        max_workers=20,
        model_name="gpt-4o-mini",
        parser_settings={
            "pdf": {"dpi": 300, "batch_size": 1},
            "excel": {"include_formulas": True, "include_formatting": False},
            "docx": {"extract_images": True, "preserve_formatting": True},
            "html": {"extract_sources": True, "follow_links": False},
            "pptx": {
                "extract_images": True,
                "extract_notes": False,
                "preserve_formatting": True,
                "slide_delimiter": "---",
            },
        },
    )

    if save:
        example_config.save(save)
        click.echo(f"Example configuration saved to: {save}")
    else:
        import yaml

        click.echo("Example configuration (YAML format):")
        click.echo(yaml.dump(example_config.to_dict(), default_flow_style=False))


@click.command()
def list_parsers() -> None:
    """List available parsers and supported formats."""
    parsers = ParserRegistry.list_parsers()

    if not parsers:
        click.echo("No parsers registered. Make sure to import parser modules.")
        return

    click.echo("Available parsers:")
    for parser_name, extensions in parsers.items():
        ext_list = ", ".join(extensions)
        click.echo(f"  {parser_name}: {ext_list}")


# Create CLI group
@click.group()
def main() -> None:
    """Document Parser CLI - Parse various document formats to structured text."""
    pass


main.add_command(cli, name="parse")
main.add_command(config_example, name="config-example")
main.add_command(list_parsers, name="list-parsers")


if __name__ == "__main__":
    main()
