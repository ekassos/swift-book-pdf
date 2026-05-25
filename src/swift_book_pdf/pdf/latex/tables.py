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
from swift_book_pdf.pdf.latex.inline import (
    apply_formatting,
    convert_inline_code,
)
from swift_book_pdf.pdf.options import RenderingMode
from swift_book_pdf.pdf.styling.typography import get_font_size, get_spacing


def convert_table_block(
    block: TableBlock,
    mode: RenderingMode,
    main_font: str,
    body_font_size: float = 9.0,
) -> list[str]:
    font_size = get_font_size("body", body_font_size)
    parskip = get_spacing("parskip", body_font_size)
    baselineskip = get_spacing("baselineskip_table", body_font_size)
    output = [
        "\\begin{table}[H]\n\\centering\n\\setlength{\\tymin}{1in}\\arrayrulecolor{table_border}\n\\renewcommand{\\arraystretch}{1.5}\n\\mainFontWithFallback{"
        + main_font
        + "}\\fontsize{"
        + font_size
        + "pt}{"
        + baselineskip
        + "}\\selectfont\\setlength{\\parskip}{"
        + parskip
        + "}\\raggedright",
    ]
    header_row = block.rows[0]
    output.append(
        f"\\begin{{tabulary}}{{1.0\\textwidth}}{{{'|'.join('L' for _ in header_row)}}}",
    )
    output.append(
        format_table_row(header_row, mode, bold=True) + " \\\\ \\hline"
    )
    output.extend(
        format_table_row(row, mode) + " \\\\ \\hline"
        for row in block.rows[1:-1]
    )
    if block.rows[-1]:
        output.append(format_table_row(block.rows[-1], mode) + " \\\\")
    output.extend(["\\end{tabulary}", "\\end{table}", "\n"])
    return output


def format_table_row(
    row: list[str],
    mode: RenderingMode,
    *,
    bold: bool = False,
) -> str:
    cells = [apply_formatting(convert_inline_code(cell), mode) for cell in row]
    if bold:
        cells = [f"\\textbf{{{cell}}}" for cell in cells]
    return " & ".join(cells)
