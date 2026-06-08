# Copyright 2026 Evangelos Kassos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LaTeX rendering for table blocks."""

from swift_book_pdf.core.blocks.models import TableBlock
from swift_book_pdf.pdf.config import RenderingMode
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.inline import (
    DocReferenceResolver,
    apply_formatting,
)


def convert_table_block(
    block: TableBlock,
    mode: RenderingMode,
    doc_references: DocReferenceResolver | None = None,
) -> list[str]:
    """Render a Markdown table block as LaTeX table markup.

    Args:
        block: Parsed table block.
        mode: PDF rendering mode.
        doc_references: Optional resolver for subset-build document refs.

    Returns:
        Rendered LaTeX table lines.
    """
    rows = [row for row in block.rows if row]
    if not rows:
        return []
    column_count = max(len(row) for row in rows)

    padded_rows = [_pad_row(row, column_count) for row in rows]
    is_header = [index == 0 for index in range(len(padded_rows))]
    cells = [
        [
            format_table_cell(row[column], mode, doc_references, bold=header)
            for row, header in zip(padded_rows, is_header, strict=False)
        ]
        for column in range(column_count)
    ]

    output = ["\\DocCTableBegin"]
    output.extend(
        "\\DocCTableMeasureColumn{" + "".join(column_cells) + "}"
        for column_cells in cells
    )

    formatted_rows = [
        " & ".join(
            format_table_cell(cell, mode, doc_references, bold=header)
            for cell in row
        )
        for row, header in zip(padded_rows, is_header, strict=False)
    ]
    body = " \\\\ \\hline\n".join(formatted_rows) + " \\\\"
    output.append("\\DocCTableRender{%\n" + body + "}")
    return output


def format_table_cell(
    cell: str,
    mode: RenderingMode,
    doc_references: DocReferenceResolver | None = None,
    *,
    bold: bool = False,
) -> str:
    """Format one table cell.

    Args:
        cell: Raw cell text value.
        mode: PDF rendering mode.
        doc_references: Optional resolver for subset-build document refs.
        bold: Whether to render the cell in bold.

    Returns:
        LaTeX for a single table cell.
    """
    content = apply_formatting(convert_inline_code(cell), mode, doc_references)
    if bold:
        content = f"\\textbf{{{content}}}"
    return "\\DocCTableCell{" + content + "}"


def _pad_row(row: list[str], column_count: int) -> list[str]:
    """Pad a ragged Markdown table row to the table's widest row."""
    return [*row, *([""] * (column_count - len(row)))]
