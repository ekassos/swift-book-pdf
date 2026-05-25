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

"""LaTeX rendering for heading blocks."""

from swift_book_pdf.core.blocks.models import (
    Block,
    Header2Block,
    Header3Block,
    Header4Block,
)
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.inline import apply_formatting
from swift_book_pdf.pdf.options import RenderingMode


def _convert_header_like_block(
    block: Block,
    file_name: str,
    mode: RenderingMode,
) -> list[str] | None:
    if isinstance(block, Header2Block):
        return [
            _convert_header_block(
                block.content, file_name, mode, "SectionHeader"
            )
        ]
    if isinstance(block, Header3Block):
        return [
            _convert_header_block(
                block.content, file_name, mode, "SubsectionHeader"
            )
        ]
    if isinstance(block, Header4Block):
        return [
            _convert_header_block(
                block.content, file_name, mode, "SubsubsectionHeader"
            )
        ]
    return None


def _convert_header_block(
    content: str,
    file_name: str,
    mode: RenderingMode,
    command: str,
) -> str:
    inline_content = convert_inline_code(content)
    label_name = (
        "-".join(inline_content.title().split()).lower().replace("'", "")
    )
    file_label = file_name.replace("'", "")
    return (
        f"\\{command}{{{apply_formatting(inline_content, mode)}}}"
        f"{{{file_label}_{label_name}}}\n"
    )
