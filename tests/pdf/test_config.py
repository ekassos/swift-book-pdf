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

from swift_book_pdf.core.config import ResolvedBuildSource
from swift_book_pdf.pdf.cli.config import (
    build_content_selection,
    build_doc_config,
)
from swift_book_pdf.pdf.config import PDFContentSelection, PDFDocumentConfig
from swift_book_pdf.pdf.latex.config import LaTeXConfig, LaTeXPDFConfig
from swift_book_pdf.pdf.latex.fonts.resolver import LaTeXFontConfig


def _font_config() -> LaTeXFontConfig:
    return LaTeXFontConfig(
        main_font="New York",
        mono_font="Berkeley Mono",
        emoji_font="Apple Color Emoji",
        unicode_fonts=("Noto Sans Symbols 2",),
        header_footer_font="SF Pro",
    )


def test_latex_font_config_construction_is_cheap() -> None:
    config = _font_config()

    assert config.main_font == "New York"
    assert config.unicode_fonts == ("Noto Sans Symbols 2",)


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
        doc_config=PDFDocumentConfig(),
        latex_config=LaTeXConfig(
            font_config=_font_config(),
            typesets=3,
        ),
    )

    diagnostics = config.diagnostic_details()

    assert "Rendering mode: digital" in diagnostics
    assert "Font size: 9.5625pt" in diagnostics
    assert "Content: full" in diagnostics
    assert "Build target: pdf" in diagnostics
    assert "Typesets: 3" in diagnostics
    assert "Main font: New York (custom font)" in diagnostics


def test_latex_pdf_config_formats_build_error_details() -> None:
    config = LaTeXPDFConfig(
        source=ResolvedBuildSource(
            temp_dir="build",
            root_dir="book/TSPL.docc",
            toc_file_path="book/TSPL.docc/The-Swift-Programming-Language.md",
            assets_dir="book/TSPL.docc/Assets",
            original_work_copyright_year_range=(2014, 2026),
        ),
        output_path="book.pdf",
        doc_config=PDFDocumentConfig(),
        latex_config=LaTeXConfig(
            font_config=_font_config(),
            typesets=3,
        ),
    )

    assert (
        "Typesets: 3\nYour font configuration:" in config.build_error_details()
    )
    assert "Unicode font(s): Noto Sans Symbols 2 (custom font(s))" in (
        config.build_error_details()
    )


def test_build_doc_config_defaults_to_no_gutter_for_digital_mode() -> None:
    config = build_doc_config(
        mode="digital",
        paper="letter",
        dark=False,
        gutter=None,
        font_size=None,
    )

    assert config.gutter is False


def test_build_doc_config_defaults_to_gutter_for_print_mode() -> None:
    config = build_doc_config(
        mode="print",
        paper="letter",
        dark=False,
        gutter=None,
        font_size=None,
    )

    assert config.gutter is True


def test_build_doc_config_uses_explicit_gutter_override() -> None:
    config = build_doc_config(
        mode="digital",
        paper="letter",
        dark=False,
        gutter=True,
        font_size=None,
    )

    assert config.gutter is True


def test_pdf_content_selection_rejects_conflicting_selectors() -> None:
    try:
        PDFContentSelection(only_toc=True, only_chapter="GuidedTour")
    except ValueError as exc:
        assert "Use either --only-toc or --only-chapter" in str(exc)
    else:
        raise AssertionError("Expected conflicting PDF content selection")


def test_build_content_selection_strips_empty_chapter_value() -> None:
    selection = build_content_selection(only_toc=False, only_chapter="  ")

    assert selection == PDFContentSelection()
