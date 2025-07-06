# DocParser

A modular, extensible document parsing library supporting multiple formats (PDF, Excel, DOCX, PPTX, HTML) with AI-powered extraction, caching, and templating.

---
## Installation

```bash
pip install parse-pdf
```

For development with extra dependencies:

```bash
pip install -e .[dev]
```

---
## Basic Usage

### Command-Line Interface (CLI)

Parse a document to Markdown and save (auto-loads configs from `DOC_PARSER_CONFIG` or `--config-file`):

```bash
python -m doc_parser.cli parse path/to/document.pdf --format markdown -o output.md
```

# Or with an external config file (TOML/JSON/YAML) overriding defaults
python -m doc_parser.cli parse path/to/document.pdf -c cfg.toml

Parse to JSON without using cache:

```bash
python -m doc_parser.cli parse path/to/file.docx --format json --no-cache
```

### Python API

```python
from pathlib import Path
from doc_parser.config import AppConfig

# Configure global settings
settings = AppConfig(output_format="markdown", use_cache=False)

# Instantiate parser based on file extension
parser = AppConfig.from_path(Path("document.pdf"), settings)

# Async parse (Python 3.11+)
import asyncio

result = asyncio.run(parser.parse(Path("document.pdf")))
print(result.content)
```

---
## Advanced Features

### Caching

Enable or disable persistent caching and configure cache parameters:

```python
from pathlib import Path
from datetime import timedelta
from doc_parser.config import AppConfig as Settings

settings = Settings(
    use_cache=True,
    cache_dir="./cache",
    parser_settings={
        "pdf": {"dpi": 300, "batch_size": 2},
    },
)
```

### Custom Prompts & Templates

`doc_parser.prompts.PromptTemplate` makes it straightforward to work with pure
Markdown templates that use **standard** `str.format` placeholders—no Jinja2
dependency required:

```python
from pathlib import Path
from pydantic import BaseModel
from doc_parser.prompts import PromptTemplate

class SummariseInput(BaseModel):
    language: str = "en"

# Load template text from Markdown file (``.md`` recommended)
tmpl = PromptTemplate.from_file(
    Path("templates/summarise.md"),
    input_schema=SummariseInput,
)

# Render the prompt for the LLM
prompt_text = tmpl.render({"language": "fr"})

# Pass via CLI
# python -m doc_parser.cli parse paper.pdf --post-prompt "{prompt_text}"
```

### Prompt Template Management

Since templates are plain files, you can ship additional templates by placing
Markdown files in a directory and reading them at runtime:

```python
from pathlib import Path
from pydantic import BaseModel
from doc_parser.prompts import PromptTemplate

class Empty(BaseModel):
    pass  # Template expects no variables

template_path = Path("my_templates/special_prompt.md")
template = PromptTemplate.from_file(template_path, input_schema=Empty)
print(template.render())
```

### Extending with Custom Parsers

#### Lightweight structured parsers via `BaseStructuredParser`

If your format follows the common *open → extract → metadata* pattern (like
DOCX, Excel, etc.) you can subclass
`doc_parser.parsers.base_structured.BaseStructuredParser` and implement just a
few hook methods — no need to duplicate the validation/metadata boilerplate.

```python
from pathlib import Path
import pandas as pd

from doc_parser.config import AppConfig
from doc_parser.parsers.base_structured import BaseStructuredParser


@AppConfig.register("csv", [".csv"])
class CsvParser(BaseStructuredParser):
    async def _open_document(self, input_path: Path, **_kw: object) -> pd.DataFrame:  # noqa: D401
        return pd.read_csv(input_path)

    async def _extract_as_markdown(self, df: pd.DataFrame) -> str:  # noqa: D401
        from doc_parser.utils.format_helpers import dataframe_to_markdown

        return dataframe_to_markdown(df)

    async def _extract_as_json(self, df: pd.DataFrame) -> str:  # noqa: D401
        import json

        return json.dumps(df.to_dict(orient="records"), indent=2)

    def _extra_metadata(self, df: pd.DataFrame) -> dict[str, object]:  # noqa: D401
        return {"rows": len(df), "columns": len(df.columns)}
```

#### Full-control parsers

For formats that require bespoke workflows (streamed HTML, vision-based PDF,
etc.), inherit directly from `BaseParser` instead:

```python
from pathlib import Path
from doc_parser.core.base import BaseParser, ParseResult
from doc_parser.config import AppConfig

@AppConfig.register("txt", [".txt"])
class TextParser(BaseParser):
    async def validate_input(self, input_path: Path) -> bool:
        return input_path.suffix == ".txt"

    async def _parse(self, input_path: Path, **kwargs) -> ParseResult:
        content = input_path.read_text()
        return ParseResult(
            content=content,
            metadata=self.get_metadata(input_path)
        )
```

---
## Typed Options API

All parser-specific configuration is now provided via **typed option objects** imported from `doc_parser.options`:

```python
from doc_parser.options import PdfOptions
from doc_parser.config import AppConfig
from doc_parser.parsers.pdf.parser import PDFParser

settings = AppConfig(use_cache=False)
parser = PDFParser(settings)

result = await parser.parse(
    Path("report.pdf"),
    options=PdfOptions(page_range=(1, 5), prompt_template="custom-prompt")
)
```

### CLI

The `doc_parser` CLI exposes matching flags for PDFs:

```bash
python -m doc_parser.cli parse sample.pdf --page-range 1:5 --prompt-template "custom-prompt"
```

Other generic flags remain the same (`--format`, `--no-cache`, `--post-prompt`, etc.).

---
## Contributing

Contributions are welcome! Please submit a pull request or open an issue at our GitHub repository.