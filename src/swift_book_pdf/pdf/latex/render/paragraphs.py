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

"""LaTeX rendering for paragraph blocks."""

from swift_book_pdf.core.blocks.models import ParagraphBlock
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.inline import apply_formatting
from swift_book_pdf.pdf.options import RenderingMode


def _convert_paragraph_block(
    block: ParagraphBlock, mode: RenderingMode
) -> str:
    para_conv = apply_formatting(
        convert_inline_code(" ".join(block.lines)), mode
    )
    return f"\\ParagraphStyle{{{para_conv}}}\n"
