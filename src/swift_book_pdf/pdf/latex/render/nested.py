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
from swift_book_pdf.pdf.latex.render.escaping import override_characters
from swift_book_pdf.pdf.latex.render.inline import apply_formatting
from swift_book_pdf.pdf.options import RenderingMode


def convert_nested_block(block: Block, mode: RenderingMode) -> str:
    if isinstance(block, ParagraphBlock):
        para = " ".join(block.lines)
        return apply_formatting(convert_inline_code(para), mode)
    if isinstance(block, CodeBlock):
        out = "\\parskip=0pt\n" + r"\begin{swiftstyledbox}" + "\n"
        for line in block.lines:
            out += override_characters(line) + "\n"
        return out + r"\end{swiftstyledbox}" + "\n"

    text = " ".join(block.lines if "lines" in block.model_fields else [])
    return apply_formatting(convert_inline_code(text), mode)
