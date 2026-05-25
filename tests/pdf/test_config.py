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

from typing import TYPE_CHECKING, cast
from unittest.mock import Mock

import pytest

from swift_book_pdf.core.config import ResolvedBuildSource
from swift_book_pdf.pdf.latex.config import LaTeXConfig, LaTeXPDFConfig
from swift_book_pdf.pdf.latex.fonts import config as font_config_module
from swift_book_pdf.pdf.layout import DocConfig

if TYPE_CHECKING:
    from swift_book_pdf.pdf.latex.fonts.config import FontConfig


class _FontDiagnostics:
    def __str__(self) -> str:
        return "Font diagnostics"


def test_font_config_construction_is_cheap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        font_config_module,
        "gather_all_candidate_fonts",
        Mock(side_effect=AssertionError("font discovery should be explicit")),
    )

    config = font_config_module.FontConfig(
        main_font="New York",
        mono_font="Berkeley Mono",
        emoji_font="Apple Color Emoji",
        unicode_font_list=("Noto Sans Symbols 2",),
        header_footer_font="SF Pro",
    )

    assert config.main_font == "New York"
    assert config.unicode_font_list == ("Noto Sans Symbols 2",)


def test_latex_config_formats_backend_diagnostics() -> None:
    config = LaTeXConfig(
        font_config=cast("FontConfig", _FontDiagnostics()),
        typesets=3,
    )

    assert str(config) == "Typesets: 3\nFont diagnostics"


def test_latex_pdf_config_formats_document_and_backend_diagnostics() -> None:
    config = LaTeXPDFConfig(
        source=ResolvedBuildSource(
            temp_dir="build",
            root_dir="book/TSPL.docc",
            toc_file_path="book/TSPL.docc/The-Swift-Programming-Language.md",
            assets_dir="book/TSPL.docc/Assets",
            original_work_copyright_year_range=(2014, 2026),
        ),
        output_path="book.pdf",
        doc_config=DocConfig(),
        latex_config=LaTeXConfig(
            font_config=cast("FontConfig", _FontDiagnostics()),
            typesets=3,
        ),
    )

    diagnostics = config.diagnostic_details()

    assert "Rendering mode: digital" in diagnostics
    assert "Font size: 9.0pt" in diagnostics
    assert "Typesets: 3" in diagnostics
    assert "Font diagnostics" in diagnostics
