# Copyright 2025-2026 Evangelos Kassos
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

from swift_book_pdf.core.blocks.models import (
    Block,
    CodeBlock,
    Header2Block,
    Header3Block,
    Header4Block,
    ImageBlock,
    NoteBlock,
    OrderedListBlock,
    ParagraphBlock,
    TableBlock,
    TermListBlock,
    UnorderedListBlock,
)
from swift_book_pdf.pdf.latex.images import convert_image_block
from swift_book_pdf.pdf.latex.inline import (
    apply_formatting,
    convert_inline_code,
    override_characters,
)
from swift_book_pdf.pdf.latex.tables import convert_table_block
from swift_book_pdf.pdf.options import Appearance, RenderingMode


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
            out += override_characters(line) + "\n"
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
        return convert_image_block(block, assets_dir, appearance)
    header_block = _convert_header_like_block(block, file_name, mode)
    if header_block is not None:
        return header_block
    if isinstance(block, NoteBlock):
        return _convert_note_block(block, mode)
    if isinstance(block, ParagraphBlock):
        return [_convert_paragraph_block(block, mode)]
    if isinstance(block, TableBlock):
        return convert_table_block(block, mode, main_font, body_font_size)
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
    output.extend(override_characters(line, True) for line in block.lines)
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
