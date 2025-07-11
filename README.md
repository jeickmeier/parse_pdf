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

### Quick-Start (TL;DR)

> Get parsing in seconds — no configuration required.

```bash
# 1. Install
pip install parse-pdf

# 2. Parse a PDF from the CLI
python -m doc_parser.cli parse docs/sample.pdf --format markdown -o sample.md

# 3. Or use the Python API (async)
python - <<'PY'
from pathlib import Path
import asyncio
from doc_parser.config import AppConfig

async def main() -> None:
    parser = AppConfig.from_path(Path("docs/sample.pdf"))
    result = await parser.parse(Path("docs/sample.pdf"))
    print(result.content[:500])
asyncio.run(main())
PY
```

#### Architecture at a glance

```mermaid
graph TD
    A["User"] -->|"CLI / Python API"| B["AppConfig"]
    B --> C["Parser Registry"]
    C --> D{"File Extension"}
    D -->|".pdf"| E["PDFParser"]
    D -->|".docx"| F["DOCXParser"]
    D -->|".xlsx"| G["ExcelParser"]
    D -->|".pptx"| H["PPTXParser"]
    D -->|".html"| I["HTMLParser"]
    E --> J["Extractors"]
    F --> J
    G --> J
    H --> J
    I --> J
    J --> K["LLM Post-Processor"]
    K --> L["ParseResult (content + metadata)"]
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

#### Shared helper mixins

To avoid duplicating common helper code, the library exposes two mixins:

* `TableMarkdownMixin` – provides a `_table_to_markdown(table)` method that
  handles both **python-docx** and **python-pptx** table objects.
* `DataFrameMarkdownMixin` – provides a `_dataframe_to_markdown(df)` method
  that wraps the standard `utils.format_helpers.dataframe_to_markdown` utility.

Simply add the mixin before `BaseParser` in your subclass' inheritance list and
call the helper inside your extraction logic:

```python
from doc_parser.utils.mixins import TableMarkdownMixin
from doc_parser.core.base import BaseParser

class MyDocxVariantParser(TableMarkdownMixin, BaseParser):
    async def _extract_as_markdown(self, doc):
        md_tables = [self._table_to_markdown(t) for t in doc.tables]
        return "\n\n".join(md_tables)
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
## Error Handling & Debug Logging

The library now follows a **fail-fast** philosophy:

* Parsers only catch *expected* exceptions (IO, value, network, PDF-specific, etc.) declared in
  `doc_parser.core.error_policy`.  These are re-packaged into the `errors` list of a
  `ParseResult` so callers can decide what to do.
* *Unexpected* errors propagate – they are no longer swallowed by a broad
  `except Exception` block.  This surfaces real bugs earlier and simplifies debugging.
* All handled errors are logged at **DEBUG** level just
  before returning, so you can enable detailed traces by exporting
  `DOC_PARSER_DEBUG=1` *before* running your script/CLI.

The `doc_parser.utils.logging_config` module configures a sensible root logger
on import.  You can override the level programmatically:

```python
from doc_parser.utils import logging_config

logging_config.init(debug=True)  # or init(level=logging.WARNING)
```

For applications with their own logging setup simply import **doc_parser** *after*
you have configured logging to avoid the auto-initialisation overriding your
handlers.

---
## Contributing

Contributions are welcome! Please submit a pull request or open an issue at our GitHub repository.