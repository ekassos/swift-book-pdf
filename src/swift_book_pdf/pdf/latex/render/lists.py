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
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.context import LaTeXRenderContext
from swift_book_pdf.pdf.latex.render.inline import apply_formatting
from swift_book_pdf.pdf.latex.render.nested import (
    convert_nested_block_sequence,
)


def convert_list_like_block(
    block: Block,
    context: LaTeXRenderContext,
) -> list[str] | None:
    """Render a list block when the block is a supported list type.

    Args:
        block: Candidate parsed block.
        context: LaTeX rendering state for the current document.

    Returns:
        Rendered LaTeX list lines, or `None` for non-list blocks.
    """
    if isinstance(block, UnorderedListBlock):
        return _convert_unordered_list_block(block, context)
    if isinstance(block, OrderedListBlock):
        return _convert_ordered_list_block(block, context)
    if isinstance(block, TermListBlock):
        return _convert_term_list_block(block, context)
    return None


def _convert_unordered_list_block(
    block: UnorderedListBlock,
    context: LaTeXRenderContext,
) -> list[str]:
    """Render a parsed unordered list as an itemize environment.

    Args:
        block: Parsed unordered list block.
        context: LaTeX rendering state for the current document.

    Returns:
        Rendered LaTeX lines.
    """
    output = [
        r"\DocCDocumentationTopicContentNodeListBefore",
        r"\begin{itemize}",
    ]
    for index, item in enumerate(block.items):
        if item:
            output.extend(_convert_unordered_list_item(item, context, index))
    output.append(
        r"\end{itemize}" + "\n\\DocCDocumentationTopicContentNodeListAfter"
    )
    return output


def _convert_unordered_list_item(
    item: list[Block], context: LaTeXRenderContext, index: int
) -> list[str]:
    """Render nested blocks that make up one unordered-list item.

    Args:
        item: Parsed nested blocks for one list item.
        context: LaTeX rendering state for the current document.
        index: Zero-based position of this item in the enclosing list.

    Returns:
        Rendered LaTeX lines for the item.
    """
    prefix = "" if index == 0 else "\\DocCContentNodeListItemBefore\n"
    return [
        prefix
        + "\\item "
        + "\n".join(
            convert_nested_block_sequence(
                item,
                context,
                paragraph_environment="DocCContentListItemParagraph",
            )
        )
        + "\n"
    ]


def _convert_ordered_list_block(
    block: OrderedListBlock,
    context: LaTeXRenderContext,
) -> list[str]:
    """Render a parsed ordered list as an enumerate environment.

    Args:
        block: Parsed ordered list block.
        context: LaTeX rendering state for the current document.

    Returns:
        Rendered LaTeX lines.
    """
    output = [r"\DocCContentNodeOrderedListBefore", r"\begin{enumerate}"]
    output.extend(
        _convert_ordered_list_item(item, context, index)
        for index, item in enumerate(block.items)
    )
    output.append(
        r"\end{enumerate}"
        + "\n\\DocCDocumentationTopicContentNodeListAfter\\global\\AtPageTopfalse\n"
    )
    return output


def _convert_ordered_list_item(
    item: str, context: LaTeXRenderContext, index: int
) -> str:
    """Render one ordered-list item.

    Args:
        item: Parsed ordered-list item text.
        context: LaTeX rendering state for the current document.
        index: Zero-based position of this item in the enclosing list.

    Returns:
        Rendered LaTeX for the item.
    """
    prefix = "" if index == 0 else "\\DocCContentNodeOrderedListItemBefore\n"
    return (
        prefix
        + "\\item \\DocCSuppressNextTopMargin\n"
        + "\\begin{DocCContentListItemParagraph}\n"
        + apply_formatting(
            convert_inline_code(item), context.mode, context.doc_references
        )
        + "\n\\end{DocCContentListItemParagraph}\n"
    )


def _convert_term_list_block(
    block: TermListBlock, context: LaTeXRenderContext
) -> list[str]:
    """Render a term list as labeled prose blocks.

    Args:
        block: Parsed term list block.
        context: LaTeX rendering state for the current document.

    Returns:
        Rendered LaTeX lines.
    """
    output = [
        r"\DocCContentNodeTermListBefore",
        r"\begin{DocCContentNodeTermList}",
    ]
    for term in block.items:
        label_conv = apply_formatting(
            convert_inline_code(term.label),
            context.mode,
            context.doc_references,
        )
        content_conv = apply_formatting(
            convert_inline_code(term.content),
            context.mode,
            context.doc_references,
        )
        output.append(
            f"\\DocCContentNodeTermListItem{{{label_conv}}}{{{content_conv}}}",
        )
    output.extend(
        [
            r"\end{DocCContentNodeTermList}",
            r"\DocCContentNodeTermListAfter",
        ]
    )
    return output
