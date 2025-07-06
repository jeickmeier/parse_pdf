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
from doc_parser.config import AppConfig as Settings
from doc_parser.config import AppConfig as ParserRegistry

# Configure global settings
settings = Settings(output_format="markdown", use_cache=False)

# Instantiate parser based on file extension
parser = ParserRegistry.from_path(Path("document.pdf"), settings)

# Synchronous parse for scripts
result = parser.parse_sync(Path("document.pdf"))
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

Leverage Jinja2 templates for fine-tuned extraction prompts:

```python
from pathlib import Path
from doc_parser.prompts.base import PromptTemplate, PromptRegistry

# Load and register a custom Jinja2 template
template = PromptTemplate.from_file(Path("templates/custom_prompt.j2"))
PromptRegistry.register("custom", template)

# Use via CLI
# python -m doc_parser.cli parse paper.pdf --post-prompt custom
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

from doc_parser.config import AppConfig as ParserRegistry
from doc_parser.parsers.base_structured import BaseStructuredParser


@ParserRegistry.register("csv", [".csv"])
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
from doc_parser.config import AppConfig as ParserRegistry

@ParserRegistry.register("txt", [".txt"])
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

### Prompt Template Management

Manage prompt templates programmatically:

```python
from pathlib import Path
from doc_parser.prompts.base import PromptRegistry

# Load bundled or local templates
PromptRegistry.init(Path("doc_parser/prompts/templates"))
print(PromptRegistry.list_templates())
```

---
## Contributing

Contributions are welcome! Please submit a pull request or open an issue at our GitHub repository.