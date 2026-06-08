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

from swift_book_pdf.core.blocks.models import TableBlock
from swift_book_pdf.pdf.config import RenderingMode
from swift_book_pdf.pdf.latex.render.tables import convert_table_block


def test_emits_one_measurement_per_column() -> None:
    """Every column is handed to LaTeX to measure; ragged rows count too."""
    block = TableBlock(
        rows=[
            ["Literal", "Default type", "Protocol"],
            ["Integer", "`Int`", "`ExpressibleByIntegerLiteral`"],
            ["Regular expression", "`Regex`"],
        ]
    )

    output = convert_table_block(block, RenderingMode.PRINT)

    assert output[0] == "\\DocCTableBegin"
    measure = [
        line for line in output if line.startswith("\\DocCTableMeasureColumn")
    ]
    assert len(measure) == 3
    assert output[-1].startswith("\\DocCTableRender")


def test_python_assigns_no_column_widths() -> None:
    """Column sizing is delegated to LaTeX: no width is computed here."""
    block = TableBlock(rows=[["a", "b", "c"], ["d", "e", "f"]])

    rendered = "\n".join(convert_table_block(block, RenderingMode.PRINT))

    # No fixed-width column boxes and no length units leak from Python.
    assert "m{" not in rendered
    assert "pt" not in rendered
    assert "\\linewidth" not in rendered


def test_header_row_is_bold_and_body_is_not() -> None:
    block = TableBlock(rows=[["Name", "Type"], ["x", "y"]])

    render_line = convert_table_block(block, RenderingMode.PRINT)[-1]
    header_line, body_line = render_line.split("\\\\")[:2]

    assert header_line.count("\\textbf") == 2
    assert "\\textbf" not in body_line


def test_inline_code_in_cells_is_converted() -> None:
    block = TableBlock(rows=[["Type"], ["`Int`"]])

    rendered = "\n".join(convert_table_block(block, RenderingMode.PRINT))

    # The backticked source must be rendered as code, not left as literal
    # backticks in the output.
    assert "`Int`" not in rendered
    assert "Int" in rendered


def test_empty_rows_are_dropped() -> None:
    block = TableBlock(rows=[["Name", "Type"], ["x", "y"], []])

    render_line = convert_table_block(block, RenderingMode.PRINT)[-1]

    # Two real rows -> exactly one internal rule between them, and the empty
    # row contributes nothing to the measured columns.
    assert render_line.count("\\hline") == 1
