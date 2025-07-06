Below are engineering‑grade, step‑by‑step playbooks for implementing the two high‑impact recommendations.  Each section finishes with **migration / testing check‑lists** so you can integrate confidently.  Code fragments are illustrative and reference the current code‑base.&#x20;

---

## 2 )  Promote **typed option objects** instead of raw `**kwargs`

### 2.1 Create a dedicated *options* module

```python
# doc_parser/options.py
from typing import Annotated, Literal, TypedDict, Optional
from pydantic import BaseModel, Field
from doc_parser.prompts import PromptTemplate

class PdfOptions(BaseModel):
    # public API
    page_range: tuple[int, int] | None = Field(
        default=None, description="Inclusive 1‑based page range."
    )
    prompt_template: str | PromptTemplate | None = None

class HtmlOptions(BaseModel):
    extract_sources: bool | None = None
    follow_links: bool | None = None
    max_depth: int | None = None

# …one class per parser type
```

*Why Pydantic?* – you already depend on it for `AppConfig`, so you gain automatic validation and JSON‑serialisation at almost zero extra cost.&#x20;

### 2.2 Augment `BaseParser.parse` to accept a **single `options` kw‑arg**

```python
async def parse(
    self,
    input_path: PathLike,
    *,
    output_format: str | None = None,
    options: BaseModel | None = None,        # NEW
) -> ParseResult:
    …
```

* Rationale: keep the signature uniform across all parsers; downstream code passes the specific options object for that parser.
* Maintain backward compatibility by **also** accepting `**legacy_kwargs` for one release cycle and emitting `DeprecationWarning`.

### 2.3 Update concrete parsers

*Replace the ad‑hoc unpacking seen today:*

```python
page_range = _kwargs.get("page_range")
prompt_template = _kwargs.get("prompt_template")
```

*with*

```python
assert isinstance(options, PdfOptions)
page_range = options.page_range
prompt_template = options.prompt_template
```

* Provide a tiny adapter so older call‑sites that still pass `page_range=` are coerced into a `PdfOptions` instance automatically and logged as deprecated.

### 2.4 Expose ergonomic helpers

Add to `doc_parser.__init__.py`:

```python
def parse_pdf(path: PathLike, *, cfg: AppConfig | None = None, **opts):
    from doc_parser.options import PdfOptions
    cfg = cfg or get_config()
    parser = AppConfig.from_path(path, cfg)
    return asyncio.run(parser.parse(path, options=PdfOptions(**opts)))
```

This gives users a one‑liner while still enjoying strong typing.

### 2.5 Wire the CLI

* Map CLI flags to the matching options model:

```python
# cli.py
options = PdfOptions(
    page_range=tuple(map(int, page_range.split(":"))) if page_range else None,
    prompt_template=prompt_template,
)
result = asyncio.run(parser.parse(file, options=options))
```

### 2.6 Refactor tests and docs

* Replace uses of positional `page_range` arguments with instantiation of options objects.
* Add mypy stubs so that `parser.parse(path, options=PdfOptions(page_range=(1,2)))` type‑checks.

---

## 5 )  Tighten **exception handling** and introduce a *strict mode*

### 5.1 Add a *strict* flag to `AppConfig`

```python
class AppConfig(BaseModel):
    …
    strict_errors: bool = False      # NEW
```

### 5.2 Replace **broad `except Exception`** blocks

*Pattern*

```python
try:
    …
except Exception:                    # 👎 broad
    …
```

*Refactor*

1. Identify the *smallest* set of anticipated errors (e.g. `PackageNotFoundError`, `InvalidFileException`, `aiohttp.ClientError`).
2. Catch them explicitly **inside** the narrow scope that may raise.

Example in `HtmlParser._fetch_and_parse`:

```python
from aiohttp import ClientError, ClientTimeout

try:
    async with session.get(url, timeout=ClientTimeout(total=30)) as resp:
        resp.raise_for_status()
except ClientError as exc:
    if self.settings.strict_errors:   # propagate in strict mode
        raise
    return ParseResult(content="", metadata={"url": url}, errors=[str(exc)])
```

The outer `_parse` should *not* need a generic catch any more; unexpected exceptions should fail fast in development.

### 5.3 Elevate errors when `strict_errors=True`

In `BaseParser.parse`, wrap the high‑level workflow:

```python
try:
    …
except ParserError as exc:                # known, repackage
    return ParseResult(content="", errors=[str(exc)], metadata=self.get_metadata(input_path))
except Exception as exc:                  # truly unexpected
    if self.settings.strict_errors:
        raise                              # bubble up!
    return ParseResult(content="", errors=[f"Unhandled: {exc}"], metadata=self.get_metadata(input_path))
```

### 5.4 Provide a **context manager** for temporary strictness

```python
from contextlib import contextmanager

@contextmanager
def strict(config: AppConfig):
    prev = config.strict_errors
    config.strict_errors = True
    try:
        yield
    finally:
        config.strict_errors = prev
```

Useful for test‑suites:

```python
with strict(cfg):
    parser.parse(path)   # will raise on unexpected errors
```

### 5.5 Update unit tests

* Add **negative path** tests that assert specific exceptions are raised when `strict_errors` is enabled.
* Ensure integration tests still pass with default (non‑strict) behaviour.

---
