"""Excel parser implementation.

This module provides a parser for Microsoft Excel files (.xlsx, .xls, .xlsm). It
supports extraction of sheet data into Markdown or JSON, optional formulas and
formatting, and metadata aggregation (sheet names, counts).

Examples:
>>> from pathlib import Path
>>> import asyncio
>>> from doc_parser.parsers.excel.parser import ExcelParser
>>> from doc_parser.core.settings import Settings
>>> settings = Settings(output_format="json", parser_settings={"excel": {"include_formulas": True}})
>>> parser = ExcelParser(settings)
>>> result = asyncio.run(parser.parse(Path("example.xlsx")))
>>> assert "sheets" in result.metadata
"""

from pathlib import Path
from typing import Any

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.utils.exceptions import InvalidFileException
import pandas as pd

from doc_parser.config import AppConfig as ParserRegistry, AppConfig as Settings
from doc_parser.core.base import BaseParser, ParseResult
from doc_parser.utils.format_helpers import dataframe_to_markdown


@ParserRegistry.register("excel", [".xlsx", ".xls", ".xlsm"])
class ExcelParser(BaseParser):
    """Parser for Excel files (.xlsx, .xls, .xlsm).

    Args:
        config (Settings): Global settings, with optional Excel-specific keys:
            - include_formulas (bool): Whether to extract cell formulas (default False).
            - include_formatting (bool): Whether to include cell formatting (default False).
            - sheet_names (List[str] | None): Specific sheets to parse; None for all (default).

    Attributes:
        include_formulas (bool): If True, extract formulas.
        include_formatting (bool): If True, include formatting.
        sheet_names (List[str] | None): Sheets to process.

    Examples:
        >>> from pathlib import Path
        >>> import asyncio
        >>> from doc_parser.parsers.excel.parser import ExcelParser
        >>> from doc_parser.core.settings import Settings
        >>> settings = Settings(output_format="markdown", parser_settings={"excel": {"include_formulas": True}})
        >>> parser = ExcelParser(settings)
        >>> result = asyncio.run(parser.parse(Path("data.xlsx")))
        >>> print(result.format)
        'markdown'
    """

    def __init__(self, config: Settings):
        """Initialize Excel parser."""
        super().__init__(config)

        # Get Excel-specific settings
        excel_config = config.get_parser_config("excel")
        self.include_formulas = excel_config.get("include_formulas", False)
        self.include_formatting = excel_config.get("include_formatting", False)
        self.sheet_names = excel_config.get("sheet_names", None)  # None means all sheets

    async def validate_input(self, input_path: Path) -> bool:
        """Validate whether the input path points to a readable Excel file.

        Args:
            input_path (Path): Path to the Excel file.

        Returns:
            bool: True if file exists, has supported extension, and is readable via pandas.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> parser = ExcelParser(Settings())
            >>> valid = asyncio.run(parser.validate_input(Path("file.xlsx")))
            >>> print(valid)
        """
        if not self._has_supported_extension(input_path):
            return False
        try:
            # Try to open with pandas to validate
            pd.ExcelFile(input_path)
        except (InvalidFileException, ValueError, OSError):
            return False
        return True

    async def _parse(self, input_path: Path, **_kwargs: Any) -> ParseResult:
        """Parse an Excel document and return the extraction results.

        This method handles validation, format selection (markdown/json), metadata,
        and error reporting.

        Args:
            input_path (Path): Path to the Excel file.
            **_kwargs: Additional options (currently unused).

        Returns:
            ParseResult: Contains extracted content, metadata (sheets, counts), format, and errors.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> parser = ExcelParser(Settings())
            >>> result = asyncio.run(parser.parse(Path("file.xlsx")))
            >>> print(result.metadata["sheet_count"])
        """
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Invalid Excel file: {input_path}"],
            )

        try:
            # Extract content based on format
            if self.settings.output_format == "markdown":
                content = await self._extract_as_markdown(input_path, **_kwargs)
            elif self.settings.output_format == "json":
                content = await self._extract_as_json(input_path, **_kwargs)
            else:
                content = await self._extract_as_markdown(input_path, **_kwargs)

            # Build metadata
            metadata = self.get_metadata(input_path)
            excel_file = pd.ExcelFile(input_path)
            metadata.update({
                "sheets": excel_file.sheet_names,
                "sheet_count": len(excel_file.sheet_names),
            })

            return ParseResult(content=content, metadata=metadata, format=self.settings.output_format)

        except (ValueError, OSError, InvalidFileException, KeyError) as exc:
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Failed to parse Excel file: {exc!s}"],
            )

    async def _extract_as_markdown(self, input_path: Path, **_kwargs: Any) -> str:
        """Extract Excel content as a Markdown string.

        Iterates over sheets, converts DataFrames to markdown tables, includes empty sheet markers,
        and appends formulas if configured.

        Args:
            input_path (Path): Path to the Excel file.
            **_kwargs: Additional options (sheet filters).

        Returns:
            str: Combined Markdown content for all processed sheets.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> parser = ExcelParser(Settings(parser_settings={"excel": {"include_formulas": True}}))
            >>> md = asyncio.run(parser._extract_as_markdown(Path("file.xlsx")))
            >>> assert "# Sheet:" in md
        """
        excel_file = pd.ExcelFile(input_path)
        content_parts = []

        # Determine which sheets to process
        sheets_to_process: list[str] = self.sheet_names or excel_file.sheet_names  # type: ignore[assignment]
        sheets_to_process = [s for s in sheets_to_process if s in excel_file.sheet_names]

        for sheet_name in sheets_to_process:
            # Add sheet header
            content_parts.append(f"# Sheet: {sheet_name}\n")

            # Read sheet data
            df = pd.read_excel(input_path, sheet_name=sheet_name, header=None)

            # Convert to markdown table
            if not df.empty:
                markdown_table = self._dataframe_to_markdown(df)
                content_parts.append(markdown_table)
            else:
                content_parts.append("*Empty sheet*")

            # Add formulas if requested
            if self.include_formulas:
                formulas = await self._extract_formulas(input_path, sheet_name)
                if formulas:
                    content_parts.append("\n## Formulas\n")
                    for cell, formula in formulas.items():
                        content_parts.append(f"- {cell}: `{formula}`")

            content_parts.append("\n")

        return "\n".join(content_parts)

    async def _extract_as_json(self, input_path: Path, **_kwargs: Any) -> str:
        """Extract Excel content as a JSON string.

        Serializes each sheet into an object containing data records, column names, shape,
        and optional formulas.

        Args:
            input_path (Path): Path to the Excel file.
            **_kwargs: Additional options (sheet filters).

        Returns:
            str: JSON-formatted string of sheet data.

        Example:
            >>> import asyncio, json
            >>> from pathlib import Path
            >>> parser = ExcelParser(Settings())
            >>> js = asyncio.run(parser._extract_as_json(Path("file.xlsx")))
            >>> data = json.loads(js)
            >>> assert isinstance(data, dict)
        """
        import json

        excel_file = pd.ExcelFile(input_path)
        data = {}

        # Determine which sheets to process
        sheets_to_process: list[str] = self.sheet_names or excel_file.sheet_names  # type: ignore[assignment]
        sheets_to_process = [s for s in sheets_to_process if s in excel_file.sheet_names]

        for sheet_name in sheets_to_process:
            df = pd.read_excel(input_path, sheet_name=sheet_name)

            # Convert to dict
            sheet_data = {
                "data": df.to_dict(orient="records"),
                "columns": df.columns.tolist(),
                "shape": df.shape,
            }

            # Add formulas if requested
            if self.include_formulas:
                sheet_data["formulas"] = await self._extract_formulas(input_path, sheet_name)

            data[sheet_name] = sheet_data

        return json.dumps(data, indent=2, default=str)

    def _dataframe_to_markdown(self, df: pd.DataFrame) -> str:
        """Convert a pandas DataFrame to a GitHub-flavored Markdown table.

        Args:
            df (pd.DataFrame): DataFrame to convert.

        Returns:
            str: Markdown table as string.

        Example:
            >>> import pandas as pd
            >>> from doc_parser.parsers.excel.parser import ExcelParser
            >>> df = pd.DataFrame([[1, 2], [3, 4]])
            >>> md = ExcelParser(Settings())._dataframe_to_markdown(df)
            >>> assert "|" in md
        """
        return dataframe_to_markdown(df)

    async def _extract_formulas(self, input_path: Path, sheet_name: str) -> dict[str, str]:
        """Extract cell formulas from a specific sheet of an Excel file.

        Args:
            input_path (Path): Path to the Excel file.
            sheet_name (str): Name of the sheet to extract formulas from.

        Returns:
            Dict[str, str]: Mapping of cell references to formula strings.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> parser = ExcelParser(Settings(parser_settings={"excel": {"include_formulas": True}}))
            >>> formulas = asyncio.run(parser._extract_formulas(Path("file.xlsx"), "Sheet1"))
            >>> assert isinstance(formulas, dict)
        """
        formulas: dict[str, str] = {}
        try:
            wb = openpyxl.load_workbook(str(input_path), data_only=False)
            try:
                ws = wb[sheet_name]
                for row in ws.iter_rows():
                    for cell in row:
                        if cell.value and isinstance(cell.value, str) and cell.value.startswith("="):
                            cell_ref = f"{get_column_letter(cell.column)}{cell.row}"
                            formulas[cell_ref] = cell.value
            finally:
                wb.close()
        except (InvalidFileException, KeyError, OSError):
            # Failed to load workbook or sheet not found
            return {}
        return formulas
