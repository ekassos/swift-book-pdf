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
from swift_book_pdf.pdf.latex.render.code_blocks import _convert_code_block
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.headings import _convert_header_like_block
from swift_book_pdf.pdf.latex.render.images import convert_image_block
from swift_book_pdf.pdf.latex.render.lists import _convert_list_like_block
from swift_book_pdf.pdf.latex.render.notes import _convert_note_block
from swift_book_pdf.pdf.latex.render.paragraphs import (
    _convert_paragraph_block,
)
from swift_book_pdf.pdf.latex.render.tables import convert_table_block
from swift_book_pdf.pdf.options import Appearance, RenderingMode


def convert_blocks_to_latex(  # noqa: PLR0913
    blocks: list[Block],
    file_name: str,
    assets_dir: str,
    mode: RenderingMode,
    appearance: Appearance,
    main_font: str,
    body_font_size: float = 9.0,
) -> list[str]:
    """Convert parsed blocks into corresponding LaTeX lines."""
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
