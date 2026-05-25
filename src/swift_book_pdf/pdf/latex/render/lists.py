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

"""LaTeX rendering for list-like blocks."""

from swift_book_pdf.core.blocks.models import (
    Block,
    OrderedListBlock,
    TermListBlock,
    UnorderedListBlock,
)
from swift_book_pdf.pdf.config import RenderingMode
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.inline import apply_formatting
from swift_book_pdf.pdf.latex.render.nested import convert_nested_block


def convert_list_like_block(
    block: Block,
    mode: RenderingMode,
) -> list[str] | None:
    """Render a list block when the block is a supported list type.

    Args:
        block: Candidate parsed block.
        mode: PDF rendering mode.

    Returns:
        Rendered LaTeX list lines, or `None` for non-list blocks.
    """
    if isinstance(block, UnorderedListBlock):
        return _convert_unordered_list_block(block, mode)
    if isinstance(block, OrderedListBlock):
        return _convert_ordered_list_block(block, mode)
    if isinstance(block, TermListBlock):
        return _convert_term_list_block(block, mode)
    return None


def _convert_unordered_list_block(
    block: UnorderedListBlock,
    mode: RenderingMode,
) -> list[str]:
    """Render a parsed unordered list as an itemize environment.

    Args:
        block: Parsed unordered list block.
        mode: PDF rendering mode.

    Returns:
        Rendered LaTeX lines.
    """
    output = [r"\begin{itemize}"]
    for item in block.items:
        if item:
            output.extend(_convert_unordered_list_item(item, mode))
    output.append(r"\end{itemize}" + "\n\\global\\AtPageTopfalse\n")
    return output


def _convert_unordered_list_item(
    item: list[Block], mode: RenderingMode
) -> list[str]:
    """Render nested blocks that make up one unordered-list item.

    Args:
        item: Parsed nested blocks for one list item.
        mode: PDF rendering mode.

    Returns:
        Rendered LaTeX lines for the item.
    """
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
    """Render a parsed ordered list as an enumerate environment.

    Args:
        block: Parsed ordered list block.
        mode: PDF rendering mode.

    Returns:
        Rendered LaTeX lines.
    """
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
    """Render a term list as labeled prose blocks.

    Args:
        block: Parsed term list block.
        mode: PDF rendering mode.

    Returns:
        Rendered LaTeX lines.
    """
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
