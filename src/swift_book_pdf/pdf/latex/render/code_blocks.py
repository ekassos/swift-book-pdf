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

"""LaTeX rendering for code blocks."""

from swift_book_pdf.core.blocks.models import CodeBlock
from swift_book_pdf.pdf.latex.render.escaping import override_characters


def convert_code_block(block: CodeBlock) -> list[str]:
    output = ["\\parskip=0pt\n" + r"\begin{flushleft}\begin{swiftstyledbox}"]
    output.extend(override_characters(line, True) for line in block.lines)
    output.append(r"\end{swiftstyledbox}" + "\n\\end{flushleft}\n")
    return output
