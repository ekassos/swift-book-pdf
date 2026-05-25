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

from swift_book_pdf.core.blocks.models import CodeBlock
from swift_book_pdf.pdf.latex.render.blocks import convert_blocks_to_latex
from swift_book_pdf.pdf.latex.render.context import LaTeXRenderContext
from swift_book_pdf.pdf.latex.render.nested import convert_nested_block
from swift_book_pdf.pdf.options import Appearance, RenderingMode


def test_convert_code_block_preserves_percent_for_minted() -> None:
    block = CodeBlock(lines=["-9 % 4 // equals -1"])

    rendered = "\n".join(convert_blocks_to_latex([block], _render_context()))

    assert "-9 % 4 // equals -1" in rendered
    assert r"\%" not in rendered


def test_convert_nested_code_block_preserves_percent_for_minted() -> None:
    block = CodeBlock(lines=["-9 % 4 // equals -1"])

    rendered = convert_nested_block(block, RenderingMode.PRINT)

    assert "-9 % 4 // equals -1" in rendered
    assert r"\%" not in rendered


def _render_context() -> LaTeXRenderContext:
    return LaTeXRenderContext(
        file_name="chapter",
        assets_dir="",
        mode=RenderingMode.PRINT,
        appearance=Appearance.LIGHT,
        main_font="IBM Plex Serif",
        body_font_size=10,
    )
