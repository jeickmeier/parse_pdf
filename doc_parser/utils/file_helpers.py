from pathlib import Path


def save_markdown(content: str, output_path: Path) -> None:
    """Save *content* to *output_path* in Markdown format.

    The function ensures that the parent directory exists and writes the file
    using UTF-8 encoding.

    Args:
        content: Markdown content to write.
        output_path: Destination path where the Markdown file will be saved.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content) 