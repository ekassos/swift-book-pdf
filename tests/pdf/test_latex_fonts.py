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

import pytest

from swift_book_pdf.pdf.latex.fonts import resolver as resolver_module
from swift_book_pdf.pdf.latex.fonts.resolver import resolve_for_latex


def test_resolve_for_latex_uses_backend_option_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gathered: dict[str, object] = {}

    def fake_gather_candidate_fonts(
        custom_fonts: tuple[str | None, ...],
        default_font_lists: tuple[list[str], ...],
    ) -> dict[str, bool]:
        gathered["custom_fonts"] = custom_fonts
        gathered["default_font_lists"] = default_font_lists
        fonts = {font for font in custom_fonts if font}
        for font_list in default_font_lists:
            fonts.update(font_list)
        return dict.fromkeys(fonts, True)

    monkeypatch.setattr(
        resolver_module,
        "_gather_candidate_fonts",
        fake_gather_candidate_fonts,
    )

    config = resolve_for_latex(
        {
            "main": "New York",
            "mono": "Berkeley Mono",
            "unicode": ("Noto Sans Symbols 2",),
            "emoji": "Apple Color Emoji",
            "header_footer": "SF Pro",
        }
    )

    assert config.main_font == "New York"
    assert config.mono_font == "Berkeley Mono"
    assert config.unicode_fonts == ("Noto Sans Symbols 2",)
    assert config.emoji_font == "Apple Color Emoji"
    assert config.header_footer_font == "SF Pro"
    assert gathered["custom_fonts"] == (
        "New York",
        "Berkeley Mono",
        "Apple Color Emoji",
        "SF Pro",
    )
