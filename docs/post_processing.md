# Post-Parse Prompting

The **post-parse prompting** feature allows you to run a second LLM pass over the
primary parsed output. This is useful for tasks like summarisation, extraction
of custom entities, or transforming the content into a different schema.

## Quick start (CLI)

```bash
parse_pdf parse my.pdf --post-prompt "Summarise each section." --response-model mypkg.models:Summary
```

Flags:

* `--post-prompt` – literal prompt or the name of a template registered in
  `PromptRegistry`.
* `--response-model` – dotted import path (e.g. `mypkg.models:Summary`) to a
  Pydantic model that will validate the LLM response.
* `--no-post-cache` – disable cache for this step.
* `--strict-post` – exit with non-zero status if validation fails.

## Programmatic example

```python
from pathlib import Path
from doc_parser.config import AppConfig, AppConfig as ParserRegistry

cfg = AppConfig(post_prompt="Extract all tables", response_model="mypkg.TableSchema")
parser = ParserRegistry.from_path(Path("report.pdf"), cfg)
result = await parser.parse(Path("report.pdf"))
print(result.post_content)
```

See `examples/post_processing_example.py` for a complete example. 