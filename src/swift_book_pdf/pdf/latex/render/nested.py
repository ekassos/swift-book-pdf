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

"""Nested block rendering used by list and aside renderers."""

from swift_book_pdf.core.blocks.models import Block, CodeBlock, ParagraphBlock
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.context import LaTeXRenderContext
from swift_book_pdf.pdf.latex.render.escaping import override_characters
from swift_book_pdf.pdf.latex.render.inline import (
    apply_formatting,
)


def convert_nested_block(block: Block, context: LaTeXRenderContext) -> str:
    """Render a block nested inside another block.

    Args:
        block: Parsed nested block.
        context: LaTeX rendering state for the current document.

    Returns:
        Rendered LaTeX for the nested block.

    Raises:
        TypeError: If the nested block type is unsupported.
    """
    if isinstance(block, ParagraphBlock):
        para = " ".join(block.lines)
        return apply_formatting(
            convert_inline_code(para), context.mode, context.doc_references
        )
    if isinstance(block, CodeBlock):
        out = [
            "\\begin{DocCCodeListingSwiftBox}",
        ]
        out.extend(override_characters(line) for line in block.lines)
        out.append("\\end{DocCCodeListingSwiftBox}")
        return "\n".join(out)

    from swift_book_pdf.pdf.latex.render.blocks import _convert_block_to_latex

    return "\n".join(_convert_block_to_latex(block, context))


def convert_nested_block_sequence(
    blocks: list[Block],
    context: LaTeXRenderContext,
    *,
    paragraph_environment: str,
) -> list[str]:
    """Render nested sibling blocks with first-child top margin suppression.

    Args:
        blocks: Parsed sibling blocks inside a parent list item or aside.
        context: LaTeX rendering state for the current document.
        paragraph_environment: LaTeX environment used for nested paragraphs in
            this parent context.

    Returns:
        Rendered LaTeX chunks in source order.

    Raises:
        TypeError: If a nested block type is unsupported by the LaTeX backend.
    """
    output: list[str] = []
    for index, block in enumerate(blocks):
        prefix = "\\DocCSuppressNextTopMargin\n" if index == 0 else ""
        if isinstance(block, ParagraphBlock):
            output.append(
                f"{prefix}\\begin{{{paragraph_environment}}}\n"
                f"{convert_nested_block(block, context)}\n"
                f"\\end{{{paragraph_environment}}}"
            )
            continue
        output.append(f"{prefix}{convert_nested_block(block, context)}")
    return output
