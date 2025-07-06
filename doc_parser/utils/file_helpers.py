r"""File helper utilities for saving Markdown content to disk.

Provides functions for common file operations such as saving Markdown content to disk
while ensuring directory creation.

Functions:
    save_markdown(content: str, output_path: PathLike) -> None

Examples:
    >>> from pathlib import Path
    >>> from doc_parser.utils.file_helpers import save_markdown
    >>> content = "# Heading\n\nSample paragraph"
    >>> save_markdown(content, "outputs/sample.md")
    >>> Path("outputs/sample.md").read_text().startswith("# Heading")
    True
"""

from pathlib import Path

from doc_parser.core.types import PathLike


def save_markdown(content: str, output_path: PathLike) -> None:
    """Save markdown content to disk at the specified path.

    Ensures that the parent directory of *output_path* exists before writing.

    Args:
        content (str): Markdown content to write.
        output_path (PathLike): Destination path where the Markdown file will be saved.

    Raises:
        OSError: If writing to the file system fails.

    Example:
        >>> save_markdown("# Title", "outputs/title.md")
        >>> Path("outputs/title.md").read_text().strip()
        "# Title"
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(content)
