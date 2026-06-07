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

"""Dispatcher for parsed Markdown block rendering."""

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
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.context import LaTeXRenderContext
from swift_book_pdf.pdf.latex.render.escaping import override_characters
from swift_book_pdf.pdf.latex.render.headings import convert_header_like_block
from swift_book_pdf.pdf.latex.render.images import convert_image_block
from swift_book_pdf.pdf.latex.render.inline import apply_formatting
from swift_book_pdf.pdf.latex.render.lists import convert_list_like_block
from swift_book_pdf.pdf.latex.render.nested import convert_nested_block
from swift_book_pdf.pdf.latex.render.tables import convert_table_block


def convert_blocks_to_latex(
    blocks: list[Block],
    context: LaTeXRenderContext,
) -> list[str]:
    """Convert parsed blocks into corresponding LaTeX lines.

    Args:
        blocks: Parsed backend-neutral block tree.
        context: LaTeX rendering state for the current document.

    Returns:
        Rendered LaTeX lines.
    """
    output: list[str] = []
    for block in blocks:
        output.extend(_convert_block_to_latex(block, context))
    return output


def _convert_block_to_latex(  # noqa: PLR0911
    block: Block,
    context: LaTeXRenderContext,
) -> list[str]:
    """Dispatch one parsed block to the matching LaTeX renderer.

    Args:
        block: Parsed backend-neutral block.
        context: LaTeX rendering state for the current document.

    Returns:
        Rendered LaTeX lines.

    Raises:
        TypeError: If the block type is not supported by the LaTeX backend.
    """
    match block:
        case CodeBlock():
            return _convert_code_block(block)
        case ImageBlock():
            return convert_image_block(
                block, context.assets_dir, context.appearance
            )
        case NoteBlock():
            return _convert_note_block(block, context)
        case ParagraphBlock():
            return [_convert_paragraph_block(block, context)]
        case TableBlock():
            return convert_table_block(
                block,
                context.mode,
                context.main_font,
                context.body_font_size,
                context.doc_references,
            )
        case UnorderedListBlock() | OrderedListBlock() | TermListBlock():
            list_block = convert_list_like_block(block, context)
            if list_block is not None:
                return list_block
        case Header2Block() | Header3Block() | Header4Block():
            header_block = convert_header_like_block(
                block,
                context.file_name,
                context.mode,
                context.doc_references,
            )
            if header_block is not None:
                return header_block

    raise TypeError(f"Unsupported LaTeX block type: {type(block).__name__}")


def _convert_code_block(block: CodeBlock) -> list[str]:
    """Render a fenced code block as a styled LaTeX box.

    Args:
        block: Parsed code block.

    Returns:
        Rendered LaTeX lines.
    """
    output = ["\\parskip=0pt\n" + r"\begin{flushleft}\begin{swiftstyledbox}"]
    output.extend(override_characters(line, True) for line in block.lines)
    output.append(r"\end{swiftstyledbox}" + "\n\\end{flushleft}\n")
    return output


def _convert_note_block(
    block: NoteBlock, context: LaTeXRenderContext
) -> list[str]:
    """Render a note block as an aside box.

    Args:
        block: Parsed note block.
        context: LaTeX rendering state for the current document.

    Returns:
        Rendered LaTeX lines.
    """
    aside_content = "\n".join(
        convert_nested_block(sub_block, context) for sub_block in block.blocks
    )
    return [
        "\\begin{flushleft}\\begin{asideNote}",
        f" \\textbf{{{block.label}}} \\vspace*{{4pt}} \\\\",
        aside_content,
        "\\end{asideNote}\\end{flushleft}" + "\n",
    ]


def _convert_paragraph_block(
    block: ParagraphBlock, context: LaTeXRenderContext
) -> str:
    """Render a paragraph block with inline Markdown formatting.

    Args:
        block: Parsed paragraph block.
        context: LaTeX rendering state for the current document.

    Returns:
        Rendered LaTeX paragraph line.
    """
    paragraph = apply_formatting(
        convert_inline_code(" ".join(block.lines)),
        context.mode,
        context.doc_references,
    )
    return f"\\ParagraphStyle{{{paragraph}}}\n"
