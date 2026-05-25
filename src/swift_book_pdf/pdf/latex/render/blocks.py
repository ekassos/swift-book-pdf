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
    ImageBlock,
    NoteBlock,
    ParagraphBlock,
    TableBlock,
)
from swift_book_pdf.pdf.latex.render.code_blocks import convert_code_block
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.context import LaTeXRenderContext
from swift_book_pdf.pdf.latex.render.headings import convert_header_like_block
from swift_book_pdf.pdf.latex.render.images import convert_image_block
from swift_book_pdf.pdf.latex.render.lists import convert_list_like_block
from swift_book_pdf.pdf.latex.render.notes import convert_note_block
from swift_book_pdf.pdf.latex.render.paragraphs import (
    convert_paragraph_block,
)
from swift_book_pdf.pdf.latex.render.tables import convert_table_block


def convert_blocks_to_latex(
    blocks: list[Block],
    context: LaTeXRenderContext,
) -> list[str]:
    """Convert parsed blocks into corresponding LaTeX lines."""
    output: list[str] = []
    for block in blocks:
        output.extend(_convert_block_to_latex(block, context))
    return output


def _convert_block_to_latex(  # noqa: PLR0911
    block: Block,
    context: LaTeXRenderContext,
) -> list[str]:
    if isinstance(block, CodeBlock):
        return convert_code_block(block)
    list_block = convert_list_like_block(block, context.mode)
    if list_block is not None:
        return list_block
    if isinstance(block, ImageBlock):
        return convert_image_block(
            block, context.assets_dir, context.appearance
        )
    header_block = convert_header_like_block(
        block, context.file_name, context.mode
    )
    if header_block is not None:
        return header_block
    if isinstance(block, NoteBlock):
        return convert_note_block(block, context.mode)
    if isinstance(block, ParagraphBlock):
        return [convert_paragraph_block(block, context.mode)]
    if isinstance(block, TableBlock):
        return convert_table_block(
            block,
            context.mode,
            context.main_font,
            context.body_font_size,
        )
    text = " ".join(block.get("lines", []))
    return [f"\\ParagraphStyle{{{convert_inline_code(text)}}}\n"]
