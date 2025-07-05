"""Excel parser implementation."""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter

from ...core.base import BaseParser, ParseResult
from ...core.registry import ParserRegistry
from ...core.config import ParserConfig


@ParserRegistry.register("excel", [".xlsx", ".xls", ".xlsm"])
class ExcelParser(BaseParser):
    """Parser for Excel files."""

    def __init__(self, config: ParserConfig):
        """Initialize Excel parser."""
        super().__init__(config)

        # Get Excel-specific settings
        excel_config = config.get_parser_config("excel")
        self.include_formulas = excel_config.get("include_formulas", False)
        self.include_formatting = excel_config.get("include_formatting", False)
        self.sheet_names = excel_config.get(
            "sheet_names", None
        )  # None means all sheets

    async def validate_input(self, input_path: Path) -> bool:
        """Validate if the input file is a valid Excel file."""
        if not input_path.exists():
            return False

        if input_path.suffix.lower() not in [".xlsx", ".xls", ".xlsm"]:
            return False

        try:
            # Try to open with pandas to validate
            pd.ExcelFile(input_path)
            return True
        except Exception:
            return False

    async def parse(self, input_path: Path, **kwargs: Any) -> ParseResult:
        """
        Parse Excel document.

        Args:
            input_path: Path to Excel file
            **kwargs: Additional options

        Returns:
            ParseResult with extracted content
        """
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Invalid Excel file: {input_path}"],
            )

        try:
            # Extract content based on format
            if self.config.output_format == "markdown":
                content = await self._extract_as_markdown(input_path, **kwargs)
            elif self.config.output_format == "json":
                content = await self._extract_as_json(input_path, **kwargs)
            else:
                content = await self._extract_as_markdown(input_path, **kwargs)

            # Build metadata
            metadata = self.get_metadata(input_path)
            excel_file = pd.ExcelFile(input_path)
            metadata.update(
                {
                    "sheets": excel_file.sheet_names,
                    "sheet_count": len(excel_file.sheet_names),
                }
            )

            return ParseResult(
                content=content, metadata=metadata, format=self.config.output_format
            )

        except Exception as e:
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Failed to parse Excel file: {str(e)}"],
            )

    async def _extract_as_markdown(self, input_path: Path, **kwargs: Any) -> str:
        """Extract Excel content as Markdown."""
        excel_file = pd.ExcelFile(input_path)
        content_parts = []

        # Determine which sheets to process
        sheets_to_process: List[str] = self.sheet_names or excel_file.sheet_names  # type: ignore[assignment]
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

    async def _extract_as_json(self, input_path: Path, **kwargs: Any) -> str:
        """Extract Excel content as JSON."""
        import json

        excel_file = pd.ExcelFile(input_path)
        data = {}

        # Determine which sheets to process
        sheets_to_process: List[str] = self.sheet_names or excel_file.sheet_names  # type: ignore[assignment]
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
                sheet_data["formulas"] = await self._extract_formulas(
                    input_path, sheet_name
                )

            data[sheet_name] = sheet_data

        return json.dumps(data, indent=2, default=str)

    def _dataframe_to_markdown(self, df: pd.DataFrame) -> str:
        """Convert DataFrame to Markdown table."""
        # Handle empty DataFrame
        if df.empty:
            return "*No data*"

        # Find the first row that looks like headers
        header_row = 0
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            if all(pd.notna(val) and str(val).strip() for val in row[:5]):
                header_row = i
                break

        # Use the identified row as headers
        if header_row > 0:
            headers = df.iloc[header_row].astype(str).tolist()
            data_df = df.iloc[header_row + 1 :].reset_index(drop=True)
            data_df.columns = headers
        else:
            # Use default column names
            data_df = df
            headers = [f"Column {i + 1}" for i in range(len(df.columns))]
            data_df.columns = headers

        # Build markdown table
        lines = []

        # Header
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["-" * max(8, len(h)) for h in headers]) + " |")

        # Data rows
        for _, row in data_df.iterrows():
            row_values = []
            for val in row:
                if pd.isna(val):
                    row_values.append("")
                else:
                    # Escape pipe characters
                    str_val = str(val).replace("|", "\\|")
                    row_values.append(str_val)
            lines.append("| " + " | ".join(row_values) + " |")

        return "\n".join(lines)

    async def _extract_formulas(
        self, input_path: Path, sheet_name: str
    ) -> Dict[str, str]:
        """Extract formulas from Excel sheet."""
        formulas = {}

        try:
            wb = openpyxl.load_workbook(str(input_path), data_only=False)
            ws = wb[sheet_name]

            for row in ws.iter_rows():
                for cell in row:
                    if (
                        cell.value
                        and isinstance(cell.value, str)
                        and cell.value.startswith("=")
                    ):
                        cell_ref = f"{get_column_letter(cell.column)}{cell.row}"
                        formulas[cell_ref] = cell.value

            wb.close()
        except Exception:
            pass

        return formulas
