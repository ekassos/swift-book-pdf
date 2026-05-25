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

"""LaTeX rendering for note blocks."""

from swift_book_pdf.core.blocks.models import NoteBlock
from swift_book_pdf.pdf.latex.render.nested import convert_nested_block
from swift_book_pdf.pdf.options import RenderingMode


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
