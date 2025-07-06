# Document Parser Library

A modular, extensible document parsing library that transforms various document formats (PDF, Excel, Word, Web) into structured text using AI-powered extraction.

## Features

- **Multiple Format Support**: PDF, Excel (XLSX/XLS), Word (DOCX), PowerPoint (PPTX), and Web content
- **Modular Architecture**: Easy to extend with new parsers
- **AI-Powered Extraction**: Uses OpenAI's vision models for accurate content extraction
- **Customizable Prompts**: Template system for fine-tuning extraction behavior
- **Async Processing**: Efficient concurrent processing with rate limiting
- **Smart Caching**: Avoids reprocessing with intelligent cache management
- **Multiple Output Formats**: Markdown, JSON, or HTML output
- **CLI and API**: Use as a command-line tool or Python library

## Installation

```bash
pip install -e .
```

Or install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

Parse a PDF file:
```bash
doc-parser parse document.pdf -o output.md
```

Parse with custom configuration:
```bash
doc-parser parse document.xlsx --config config.yaml --format json
```

List available parsers:
```bash
doc-parser list-parsers
```

### Python API Usage

```python
import asyncio
from doc_parser import ParserConfig, ParserRegistry
from pathlib import Path

async def parse_document():
    # Configure parser
    config = ParserConfig(
        max_workers=20,
        model_name="gpt-4o-mini",
        output_format="markdown"
    )
    
    # Get parser for file type
    parser = ParserRegistry.get_parser(Path("document.pdf"), config)
    
    # Parse document
    result = await parser.parse_with_cache(Path("document.pdf"))
    
    # Access results
    print(result.content)
    print(result.metadata)

# Run
asyncio.run(parse_document())
```

## Quick Start (v0.2)

```python
from doc_parser.core.registry import ParserRegistry
from doc_parser.core.settings import Settings

settings = Settings()
parser = ParserRegistry.from_path("/path/to/doc.pdf", settings)
result = parser.parse_sync("/path/to/doc.pdf")
print(result.content[:500])
```

CLI usage:

```bash
$ doc-parser parse myfile.pdf --format markdown -o output.md
```

## Configuration

Create a configuration file (YAML or JSON):

```yaml
# config.yaml
cache_dir: ./cache
output_dir: ./output
max_workers: 20
timeout: 60
model_name: gpt-4o-mini
output_format: markdown

parser_settings:
  pdf:
    dpi: 300
    batch_size: 1
  excel:
    include_formulas: true
    include_formatting: false
  docx:
    extract_images: true
    preserve_formatting: true
  pptx:
    extract_images: true
    extract_notes: false
    preserve_formatting: true
    slide_delimiter: "---"
  html:
    extract_sources: true
    follow_links: false
```

Generate example configuration:
```bash
doc-parser config-example --save config.yaml
```

## Custom Prompts

Create custom extraction prompts using Jinja2 templates:

```jinja2
{# my_prompt.j2 #}
Extract the following information from the document:
- Main topics discussed
- Key findings or conclusions
- Any numerical data or statistics

Format as structured markdown with clear sections.

{% if document_type == "research" %}
Pay special attention to methodology and results sections.
{% endif %}
```

Use custom prompt:
```bash
doc-parser parse paper.pdf --prompt-template my_prompt.j2
```

## Extending the Library

### Create a Custom Parser

```python
from doc_parser.core import BaseParser, ParseResult, ParserRegistry
from pathlib import Path

@ParserRegistry.register("custom", [".custom", ".xyz"])
class CustomParser(BaseParser):
    async def validate_input(self, input_path: Path) -> bool:
        # Validate file format
        return input_path.suffix in ['.custom', '.xyz']
    
    async def parse(self, input_path: Path, **kwargs) -> ParseResult:
        # Implement parsing logic
        content = await self.extract_content(input_path)
        
        return ParseResult(
            content=content,
            metadata=self.get_metadata(input_path),
            format=self.config.output_format
        )
```

### Create a Custom Extractor

```python
from doc_parser.core import BaseExtractor
from doc_parser.prompts import PromptTemplate

class CustomExtractor(BaseExtractor):
    async def extract(self, content: Any, prompt_template: Optional[PromptTemplate] = None) -> str:
        # Implement extraction logic
        prompt = self._get_prompt(prompt_template)
        # Process content with AI model
        return extracted_text
    
    def get_default_prompt(self) -> str:
        return "Extract structured information from the content..."
```

## API Reference

### Core Classes

#### ParserConfig
Configuration container for all parsers.

```python
config = ParserConfig(
    cache_dir=Path("./cache"),
    max_workers=15,
    model_name="gpt-4o-mini",
    parser_settings={"pdf": {"dpi": 300}}
)
```

#### ParseResult
Container for parsing results.

```python
result = ParseResult(
    content="Extracted content...",
    metadata={"pages": 10, "format": "pdf"},
    format="markdown",
    errors=[]
)
```

#### ParserRegistry
Manages parser registration and discovery.

```python
# Get parser by file
parser = ParserRegistry.get_parser(Path("file.pdf"), config)

# Get parser by name
parser = ParserRegistry.get_parser_by_name("pdf", config)

# Check if supported
is_supported = ParserRegistry.is_supported(Path("file.xyz"))
```

### Parser-Specific Options

#### PDF Parser
- `dpi`: Resolution for PDF to image conversion (default: 300)
- `batch_size`: Pages to process per API call (default: 1)

#### Excel Parser
- `include_formulas`: Extract cell formulas (default: False)
- `include_formatting`: Preserve cell formatting (default: False)
- `sheet_names`: List of sheets to process (default: all)

#### DOCX Parser
- `extract_images`: Extract image descriptions (default: True)
- `extract_headers_footers`: Include headers/footers (default: False)
- `preserve_formatting`: Keep text formatting (default: True)

#### PPTX Parser
- `extract_images`: Extract and link images (default: True)
- `extract_notes`: Include speaker notes in output (default: False)
- `preserve_formatting`: Keep bold/italic formatting (default: True)
- `slide_delimiter`: Markdown delimiter between slides (default: "---")

#### Perplexity Parser
- `extract_sources`: Extract source links (default: True)
- `follow_links`: Extract linked content (default: False)
- `max_depth`: Maximum link depth to follow (default: 1)

## Examples

### Batch Processing

```python
import asyncio
from pathlib import Path
from doc_parser import ParserConfig, ParserRegistry

async def batch_process(files: List[Path]):
    config = ParserConfig(max_workers=20)
    tasks = []
    
    for file_path in files:
        parser = ParserRegistry.get_parser(file_path, config)
        task = parser.parse_with_cache(file_path)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### Custom Output Processing

```python
async def parse_and_summarize(file_path: Path):
    config = ParserConfig(output_format="json")
    parser = ParserRegistry.get_parser(file_path, config)
    
    result = await parser.parse(file_path)
    
    # Process JSON output
    import json
    data = json.loads(result.content)
    
    # Custom processing...
    summary = process_data(data)
    return summary
```

### Error Handling

```python
async def safe_parse(file_path: Path):
    try:
        config = ParserConfig()
        parser = ParserRegistry.get_parser(file_path, config)
        result = await parser.parse(file_path)
        
        if result.errors:
            print(f"Warnings: {result.errors}")
        
        return result.content
        
    except UnsupportedFormatError:
        print(f"Unsupported file format: {file_path.suffix}")
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
```

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for vision models
- `DOC_PARSER_CACHE_DIR`: Override default cache directory
- `DOC_PARSER_CONFIG`: Path to default configuration file

## Performance Tips

1. **Adjust Workers**: Increase `max_workers` for faster processing of large documents
2. **Enable Caching**: Keep caching enabled to avoid reprocessing
3. **Batch Processing**: Use larger `batch_size` for multi-page documents
4. **Optimize DPI**: Lower DPI (200-250) for text-heavy documents, higher (300-400) for complex layouts

## Troubleshooting

### Common Issues

1. **PDF Processing Fails**
   - Ensure Poppler is installed: `brew install poppler` (macOS) or `apt-get install poppler-utils` (Linux)

2. **API Rate Limits**
   - Reduce `max_workers` in configuration
   - Implement exponential backoff (built-in)

3. **Memory Issues**
   - Process large PDFs in smaller batches
   - Reduce DPI for image conversion

4. **Cache Issues**
   - Clear cache: `rm -rf ./cache`
   - Disable cache: `--no-cache` flag

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Acknowledgments

Built on top of excellent libraries:
- OpenAI API for vision capabilities
- pdf2image for PDF processing
- pandas & openpyxl for Excel handling
- python-docx for Word documents
- BeautifulSoup4 for web parsing

## Post-Parse Prompting

See `docs/post_processing.md` for details on running an additional LLM pass after the primary parse to transform or validate results.