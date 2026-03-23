# Copyright 2025 Evangelos Kassos
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

import logging
import os
import re
import struct
from pathlib import Path, PureWindowsPath

from swift_book_pdf.schema import (
    Appearance,
    Block,
    CodeBlock,
    Header2Block,
    Header3Block,
    Header4Block,
    ImageBlock,
    NoteBlock,
    OrderedListBlock,
    ParagraphBlock,
    RenderingMode,
    TableBlock,
    TermListBlock,
    UnorderedListBlock,
)
from swift_book_pdf.typography import get_font_size, get_spacing

logger = logging.getLogger(__name__)
MAX_IMAGE_WIDTH_IN = 6.5


def generate_chapter_title(
    lines: list[str], file_name: str
) -> tuple[str, list[str]]:
    """
    Generate the chapter title LaTeX from the provided lines.

    :param lines: The lines to generate the title from
    :return: A tuple containing the title and the remaining lines
    """
    header_line = None
    subtitle_line = None

    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("#"):
            header_line = lines[i].lstrip("#").strip()
            i += 1
            break
        i += 1
    while i < len(lines):
        if lines[i].strip():
            subtitle_line = lines[i].strip()
            i += 1
            break
        i += 1

    title_subtitle_snippet = rf"""
    \thispagestyle{{firstpagestyle}}
    \renewcommand{{\customheader}}{{{header_line}}}
    \vspace*{{0.3in}}
    \HeroBox{{{header_line}}}{{{file_name}}}{{{subtitle_line}}}
    \vspace*{{0.3in}}
    """

    return title_subtitle_snippet, lines[i:]


def escape_texttt(text: str) -> str:
    """
    Escape characters in text that cause issues inside `\texttt`.
    """
    # Order matters: escape backslash first
    text = text.replace("\\", r"\textbackslash ")

    # Escape curly braces and underscore that conflict with LaTeX grouping
    text = text.replace("{", r"\{")
    text = text.replace("}", r"\}")
    text = text.replace("_", r"\_")

    # Escape hash symbol (if not already escaped)
    text = re.sub(r"(?<!\\)#", r"\#", text)

    # Escape other special characters
    text = text.replace("$", r"\$")
    text = text.replace("&", r"\&")
    text = text.replace("%", r"\%")
    text = text.replace("^", r"\textasciicircum ")
    text = text.replace("`", r"\textasciigrave ")
    text = text.replace("~", r"\textasciitilde ")
    text = text.replace("[", r"{[}")
    text = text.replace("]", r"{]}")
    text = text.replace("(", r"{(}")
    text = text.replace(")", r"{)}")
    text = text.replace(".", r"{.}")
    text = text.replace(",", r"{,}")
    text = text.replace(":", r"{:}")
    text = text.replace(";", r"{;}")
    text = text.replace("=", r"{=}")
    text = text.replace("@", r"{@}")
    text = text.replace("?", r"{?}")
    text = text.replace("!", r"{!}")

    # The arrow token "->" is two characters long.
    # Replace it before any chance of interfering with its hyphen.
    text = text.replace("->", r"{->}")

    return override_characters(text)


def override_characters(text: str, in_code_block: bool = False) -> str:
    """
    Override characters in text that may have special formatting in LaTeX.
    """
    override_set = {"é⃝": "\\textcircled{é}"}

    if in_code_block:
        override_set = {k: f"|{v}|" for k, v in override_set.items()}

    for char, replacement in override_set.items():
        text = text.replace(char, replacement)
    return text


def apply_formatting(text: str, mode: RenderingMode) -> str:
    """
    Apply formatting to the given text.
    """
    # Temporarily extract inline code segments produced by convert_inline_code
    inline_segments: dict[str, str] = {}

    def replace_inline(match: re.Match[str]) -> str:
        token = f"%%INLINE-CODE-{len(inline_segments)}%%"
        inline_segments[token] = match.group(0)
        return token

    text = re.sub(r"(\{\\CodeStyle\s+\\texttt\{.*?\}\})", replace_inline, text)

    # Escape literal currency/math markers from source text before we inject
    # formatter-owned LaTeX snippets that intentionally use math mode.
    text = text.replace("$", r"\$")

    # Apply formatting to the rest of the text.
    text = text.replace("→", r"\scalebox{1.2}{$\rightarrow$}")
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"\*(.+?)\*", r"\\emph{\1}", text)
    text = re.sub(r"\s\\\s", r" \\\\ ", text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?:\/\/[^\s()]+(?:\([^()]*\)[^\s()]*)*)\)",
        (
            r"\\href{\2}{\1}\\footnote{\\url{\2}}"
            if mode == RenderingMode.PRINT
            else r"\\href{\2}{\1}"
        ),
        text,
    )
    text = re.sub(r"(?<!\\)_", r"\_", text)
    text = re.sub(r"---", r"\\textemdash \\ ", text)
    text = re.sub(r"--", r"\\textendash", text)
    text = re.sub(r"\(\\\`\)", r"(\;\`\; )", text)
    text = re.sub(
        r"<doc:([^>#]+)#([^>]+)>",
        lambda m: (
            "\\fallbackrefbook{"
            if mode == RenderingMode.PRINT
            else "\\fallbackrefdigital{"
        )
        + m.group(1).lower()
        + "_"
        + m.group(2).lower()
        + "}",
        text,
    )
    text = re.sub(
        r"<doc:([^>#]+)>",
        lambda m: (
            "\\fallbackrefbook{"
            if mode == RenderingMode.PRINT
            else "\\fallbackrefdigital{"
        )
        + m.group(1).lower()
        + "}",
        text,
    )
    text = re.sub(r"(?<!\\)#", r"\#", text)

    # Restore the inline code segments.
    for token, segment in inline_segments.items():
        text = text.replace(token, segment)

    return override_characters(text)


def convert_inline_code(text: str) -> str:
    """
    Replace inline code delimited by unescaped backticks with
    `{\\CodeStyle \texttt{...}}`.

    This converter supports two kinds of delimiters:
      • Double backticks (``...``): These blocks are processed first
        and “protected” so that any inner single backticks (as in “`x`”)
        are not processed a second time.
      • Single backticks (`...`): Handled afterward.

    Escaped backticks (preceded by a backslash) are not processed.
    """
    # Protect double-backtick replacements with placeholders.
    double_placeholder: dict[str, str] = {}

    def repl_double(match: re.Match[str]) -> str:
        inner = match.group(1)  # Everything between the double backticks.
        processed = (
            r"{\CodeStyle \texttt{" + escape_texttt(inner).strip() + "}}"
        )
        # Create a unique token unlikely to appear in the text.
        token = f"@@DOUBLE{len(double_placeholder)}@@"
        double_placeholder[token] = processed
        return token

    # Process double-backtick code first.
    # This regex matches two unescaped backticks on each side.
    text = re.sub(r"(?<!\\)``(.*?)``", repl_double, text)

    # Now process single-backtick code.
    def repl_single(match: re.Match[str]) -> str:
        inner = match.group(1)
        return r"{\CodeStyle \texttt{" + escape_texttt(inner).strip() + "}}"

    text = re.sub(r"(?<!\\)`(.*?)`", repl_single, text)

    # Finally, restore the double-backtick replacements.
    for token, replacement in double_placeholder.items():
        text = text.replace(token, replacement)

    return text


def convert_nested_block(block: Block, mode: RenderingMode) -> str:
    if isinstance(block, ParagraphBlock):
        para = " ".join(block.lines)
        return apply_formatting(convert_inline_code(para), mode)
    if isinstance(block, CodeBlock):
        out = (
            "\\parskip=0pt\n"
            r"\begin{swiftstyledbox}" + "\n"
        )
        for line in block.lines:
            line2 = line.replace("%", r"\%")
            out += override_characters(line2) + "\n"
        out += r"\end{swiftstyledbox}" + "\n"
        return out
    # fallback
    text = " ".join(block.lines if "lines" in block.model_fields else [])
    return apply_formatting(convert_inline_code(text), mode)


def convert_blocks_to_latex(  # noqa: PLR0913
    blocks: list[Block],
    file_name: str,
    assets_dir: str,
    mode: RenderingMode,
    appearance: Appearance,
    main_font: str,
    body_font_size: float = 9.0,
) -> list[str]:
    """
    Convert parsed blocks into corresponding LaTeX lines.

    :param blocks: The parsed blocks to convert
    :param file_name: The name of the file being converted
    :param assets_dir: The directory containing the images
    :param mode: The rendering mode
    :param appearance: The appearance mode (light or dark)
    :param main_font: The font to be used for the main text
    :param body_font_size: The body font size in points
    :return: A list of LaTeX lines
    """
    output: list[str] = []
    for block in blocks:
        output.extend(
            _convert_block_to_latex(
                block,
                file_name,
                assets_dir,
                mode,
                appearance,
                main_font,
                body_font_size,
            ),
        )
    return output


def _convert_block_to_latex(  # noqa: PLR0913,PLR0911
    block: Block,
    file_name: str,
    assets_dir: str,
    mode: RenderingMode,
    appearance: Appearance,
    main_font: str,
    body_font_size: float = 9.0,
) -> list[str]:
    if isinstance(block, CodeBlock):
        return _convert_code_block(block)
    list_block = _convert_list_like_block(block, mode)
    if list_block is not None:
        return list_block
    if isinstance(block, ImageBlock):
        return _convert_image_block(block, assets_dir, appearance)
    header_block = _convert_header_like_block(block, file_name, mode)
    if header_block is not None:
        return header_block
    if isinstance(block, NoteBlock):
        return _convert_note_block(block, mode)
    if isinstance(block, ParagraphBlock):
        return [_convert_paragraph_block(block, mode)]
    if isinstance(block, TableBlock):
        return _convert_table_block(block, mode, main_font, body_font_size)
    text = " ".join(block.get("lines", []))
    return [f"\\ParagraphStyle{{{convert_inline_code(text)}}}\n"]


def _convert_list_like_block(
    block: Block,
    mode: RenderingMode,
) -> list[str] | None:
    if isinstance(block, UnorderedListBlock):
        return _convert_unordered_list_block(block, mode)
    if isinstance(block, OrderedListBlock):
        return _convert_ordered_list_block(block, mode)
    if isinstance(block, TermListBlock):
        return _convert_term_list_block(block, mode)
    return None


def _convert_header_like_block(
    block: Block,
    file_name: str,
    mode: RenderingMode,
) -> list[str] | None:
    if isinstance(block, Header2Block):
        return [
            _convert_header_block(
                block.content, file_name, mode, "SectionHeader"
            )
        ]
    if isinstance(block, Header3Block):
        return [
            _convert_header_block(
                block.content, file_name, mode, "SubsectionHeader"
            )
        ]
    if isinstance(block, Header4Block):
        return [
            _convert_header_block(
                block.content, file_name, mode, "SubsubsectionHeader"
            )
        ]
    return None


def _convert_code_block(block: CodeBlock) -> list[str]:
    output = ["\\parskip=0pt\n" + r"\begin{flushleft}\begin{swiftstyledbox}"]
    output.extend(
        override_characters(line.replace("%", r"\%"), True)
        for line in block.lines
    )
    output.append(r"\end{swiftstyledbox}" + "\n\\end{flushleft}\n")
    return output


def _convert_unordered_list_block(
    block: UnorderedListBlock,
    mode: RenderingMode,
) -> list[str]:
    output = [r"\begin{itemize}"]
    for item in block.items:
        if item:
            output.extend(_convert_unordered_list_item(item, mode))
    output.append(r"\end{itemize}" + "\n\\global\\AtPageTopfalse\n")
    return output


def _convert_unordered_list_item(
    item: list[Block], mode: RenderingMode
) -> list[str]:
    output: list[str] = []
    for index, sub_block in enumerate(item):
        latex_sub = convert_nested_block(sub_block, mode)
        if index == 0:
            output.append(f"\\item \\ParagraphStyle{{{latex_sub}}}\n")
        elif latex_sub.startswith(r"\parskip"):
            output.append(latex_sub)
        else:
            output.append(f"\\ParagraphStyle{{{latex_sub}}}\n")
    return output


def _convert_ordered_list_block(
    block: OrderedListBlock,
    mode: RenderingMode,
) -> list[str]:
    output = [r"\begin{enumerate}"]
    output.extend(
        f"\\item {apply_formatting(convert_inline_code(item), mode)}"
        for item in block.items
    )
    output.append(r"\end{enumerate}" + "\n\\global\\AtPageTopfalse\n")
    return output


def _convert_term_list_block(
    block: TermListBlock, mode: RenderingMode
) -> list[str]:
    output = ["\\ParagraphStyle{"]
    for term in block.items:
        label_conv = apply_formatting(convert_inline_code(term.label), mode)
        content_conv = apply_formatting(
            convert_inline_code(term.content), mode
        )
        output.append(
            f"\\needspace{{3\\baselineskip}} {label_conv} \\vspace*{{-0.09in}} \\begin{{quote}} {content_conv} \\end{{quote}}",
        )
    output.append(" }\n")
    return output


def _convert_image_block(
    block: ImageBlock,
    assets_dir: str,
    appearance: Appearance,
) -> list[str]:
    img_path = Path(assets_dir) / (
        f"{block.imgname}{'~dark' if appearance == Appearance.DARK else ''}@2x.png"
    )
    latex_img_path = (
        PureWindowsPath(img_path).as_posix()
        if os.sep == "\\"
        else str(img_path)
    )
    width = _read_image_width(img_path)
    if width is None:
        return []

    final_width = (
        f"{MAX_IMAGE_WIDTH_IN}in"
        if width > MAX_IMAGE_WIDTH_IN
        else f"{width}in"
    )
    return [
        f"\\begin{{figure}}[H]\n\\centering\\includegraphics[width={final_width}]{{{latex_img_path}}}\n\\end{{figure}}\n\\global\\AtPageTopfalse\n",
    ]


def _read_image_width(img_path: Path) -> float | None:
    try:
        with img_path.open("rb") as f:
            f.seek(16)
            width, _ = struct.unpack(">II", f.read(8))
        return width / 273.2
    except (OSError, struct.error) as exc:
        logger.debug(f"Failed to read image width for {img_path}: {exc}")
        return None


def _convert_header_block(
    content: str,
    file_name: str,
    mode: RenderingMode,
    command: str,
) -> str:
    inline_content = convert_inline_code(content)
    label_name = (
        "-".join(inline_content.title().split()).lower().replace("'", "")
    )
    file_label = file_name.replace("'", "")
    return (
        f"\\{command}{{{apply_formatting(inline_content, mode)}}}"
        f"{{{file_label}_{label_name}}}\n"
    )


def _convert_note_block(block: NoteBlock, mode: RenderingMode) -> list[str]:
    aside_content = "\n".join(
        convert_nested_block(sub_block, mode) for sub_block in block.blocks
    )
    return [
        "\\begin{flushleft}\\begin{asideNote}",
        f" \\textbf{{{block.label}}} \\vspace*{{4pt}} \\\\",
        aside_content,
        "\\end{asideNote}\\end{flushleft}" + "\n",
    ]


def _convert_paragraph_block(
    block: ParagraphBlock, mode: RenderingMode
) -> str:
    para_conv = apply_formatting(
        convert_inline_code(" ".join(block.lines)), mode
    )
    return f"\\ParagraphStyle{{{para_conv}}}\n"


def _convert_table_block(
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
        _format_table_row(header_row, mode, bold=True) + " \\\\ \\hline"
    )
    output.extend(
        _format_table_row(row, mode) + " \\\\ \\hline"
        for row in block.rows[1:-1]
    )
    if block.rows[-1]:
        output.append(_format_table_row(block.rows[-1], mode) + " \\\\")
    output.extend(["\\end{tabulary}", "\\end{table}", "\n"])
    return output


def _format_table_row(
    row: list[str],
    mode: RenderingMode,
    *,
    bold: bool = False,
) -> str:
    cells = [apply_formatting(convert_inline_code(cell), mode) for cell in row]
    if bold:
        cells = [f"\\textbf{{{cell}}}" for cell in cells]
    return " & ".join(cells)
