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

from swift_book_pdf.contents import replace_chapter_href_with_toc_item
from swift_book_pdf.schema import (
    Appearance,
    ChapterMetadata,
    RenderingMode,
)


def test_toc_chapter_icon_uses_em_based_width_in_digital_mode() -> None:
    lines = [r"\item \ParagraphStyle{\fallbackrefdigital{guidedtour}}"]
    metadata = {
        "guidedtour": ChapterMetadata(subtitle_line="A quick start."),
    }

    rendered = replace_chapter_href_with_toc_item(
        lines,
        metadata,
        RenderingMode.DIGITAL,
        Appearance.LIGHT,
    )

    assert r"\includegraphics[width=0.8em]{chapter-icon.png}" in rendered[0]
    assert "0.1in" not in rendered[0]


def test_toc_chapter_icon_uses_dark_asset_in_print_mode() -> None:
    lines = [r"\item \ParagraphStyle{\fallbackrefbook{guidedtour}}"]
    metadata = {
        "guidedtour": ChapterMetadata(subtitle_line="A quick start."),
    }

    rendered = replace_chapter_href_with_toc_item(
        lines,
        metadata,
        RenderingMode.PRINT,
        Appearance.DARK,
    )

    assert (
        r"\includegraphics[width=0.8em]{chapter-icon~dark.png}" in rendered[0]
    )
