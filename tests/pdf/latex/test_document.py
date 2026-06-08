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

from pathlib import Path
from unittest.mock import Mock

import pytest

from swift_book_pdf.core.config import ResolvedBuildSource
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.pdf.config import PDFContentSelection, PDFDocumentConfig
from swift_book_pdf.pdf.latex import document as latex_document
from swift_book_pdf.pdf.latex.config import LaTeXConfig, LaTeXPDFConfig
from swift_book_pdf.pdf.latex.fonts.resolver import LaTeXFontConfig
from swift_book_pdf.pdf.latex.renderer import LaTeXRenderer


def test_write_latex_document_can_render_only_toc(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    toc = _create_toc(tmp_path)
    config = _config(tmp_path, PDFContentSelection(only_toc=True))
    renderer = Mock(spec=LaTeXRenderer)
    output_path = tmp_path / "inner_content.tex"
    monkeypatch.setattr(latex_document, "generate_preamble", _fake_preamble)
    monkeypatch.setattr(
        latex_document,
        "generate_toc_latex",
        lambda _toc, _renderer: "TOC",
    )

    latex_document.write_latex_document(
        config,
        toc,
        renderer,
        output_path,
    )

    assert output_path.read_text(encoding="utf-8") == (
        "PREAMBLE\nTOC\n\\end{document}"
    )
    renderer.render_file.assert_not_called()


def test_write_latex_document_can_render_one_chapter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    toc = _create_toc(tmp_path)
    config = _config(tmp_path, PDFContentSelection(only_chapter="GuidedTour"))
    renderer = Mock(spec=LaTeXRenderer)
    renderer.render_file.return_value = "GUIDED TOUR"
    output_path = tmp_path / "inner_content.tex"
    monkeypatch.setattr(latex_document, "generate_preamble", _fake_preamble)

    latex_document.write_latex_document(
        config,
        toc,
        renderer,
        output_path,
    )

    assert output_path.read_text(encoding="utf-8") == (
        "PREAMBLE\nGUIDED TOUR\n\\end{document}"
    )
    renderer.render_file.assert_called_once_with(
        str(
            tmp_path
            / "swift-book"
            / "TSPL.docc"
            / "GuidedTour"
            / "GuidedTour.md"
        )
    )


def test_write_latex_document_fails_for_unknown_explicit_chapter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    toc = _create_toc(tmp_path)
    config = _config(tmp_path, PDFContentSelection(only_chapter="NotAChapter"))
    output_path = tmp_path / "inner_content.tex"
    monkeypatch.setattr(latex_document, "generate_preamble", _fake_preamble)

    with pytest.raises(ValueError, match="Couldn't find chapter"):
        latex_document.write_latex_document(
            config,
            toc,
            Mock(spec=LaTeXRenderer),
            output_path,
        )


def _fake_preamble(_config: LaTeXPDFConfig) -> str:
    return "PREAMBLE\n"


def _config(
    tmp_path: Path,
    selection: PDFContentSelection,
) -> LaTeXPDFConfig:
    docc_root = tmp_path / "swift-book" / "TSPL.docc"
    return LaTeXPDFConfig(
        source=ResolvedBuildSource(
            temp_dir=str(tmp_path),
            root_dir=str(docc_root),
            toc_file_path=str(docc_root / "The-Swift-Programming-Language.md"),
            assets_dir=str(docc_root / "Assets"),
            original_work_copyright_year_range=(2014, 2026),
        ),
        output_path=str(tmp_path / "book.pdf"),
        doc_config=PDFDocumentConfig(),
        content_selection=selection,
        latex_config=LaTeXConfig(
            font_config=LaTeXFontConfig(
                main_font="New York",
                mono_font="Berkeley Mono",
                emoji_font="Apple Color Emoji",
                unicode_fonts=("Noto Sans Symbols 2",),
                header_footer_font="SF Pro",
            ),
            typesets=1,
        ),
    )


def _create_toc(tmp_path: Path) -> TableOfContents:
    docc_root = tmp_path / "swift-book" / "TSPL.docc"
    for directory in (
        "GuidedTour",
        "LanguageGuide",
        "ReferenceManual",
        "RevisionHistory",
    ):
        (docc_root / directory).mkdir(parents=True, exist_ok=True)

    (docc_root / "GuidedTour" / "GuidedTour.md").write_text(
        "# Guided Tour\n\nA quick start.\n",
        encoding="utf-8",
    )
    toc_path = docc_root / "The-Swift-Programming-Language.md"
    toc_path.write_text(
        "# The Swift Programming Language (6.2)\n\n"
        "## About\n\n"
        "### Guided Tour\n\n"
        "- <doc:GuidedTour>\n",
        encoding="utf-8",
    )
    return TableOfContents(str(docc_root), str(toc_path), str(tmp_path))
