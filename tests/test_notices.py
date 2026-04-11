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

from swift_book_pdf.files import find_swift_book_copyright_year_range
from swift_book_pdf.notices import (
    NOTICES_DOC_KEY,
    NOTICES_DOC_TAG,
    NOTICES_SECTION_TITLE,
    SWIFT_BOOK_PDF_REPO_URL,
    SWIFT_BOOK_REPO_URL,
    SWIFT_CONTRIBUTORS_URL,
    SWIFT_DOCC_RENDER_NOTICE_TEXT,
    SWIFT_LICENSE_URL,
    build_notices_toc_lines,
    render_notices_latex,
    render_notices_xhtml,
)
from swift_book_pdf.schema import RenderingMode
from swift_book_pdf.toc import TableOfContents


def test_find_swift_book_copyright_year_range_uses_earliest_and_latest_years(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "swift-book"
    docc_root = repo_root / "TSPL.docc"
    docc_root.mkdir(parents=True)

    (docc_root / "one.md").write_text(
        "Copyright (c) 2014 Apple Inc. and the Swift project authors\n",
        encoding="utf-8",
    )
    (docc_root / "two.md").write_text(
        "Copyright (c) 2020-2026 Apple Inc. and the Swift project authors\n",
        encoding="utf-8",
    )

    assert find_swift_book_copyright_year_range(docc_root) == (2014, 2026)


def test_pdf_toc_tracks_notices_as_final_synthetic_chapter(
    tmp_path: Path,
) -> None:
    toc_path = _create_minimal_swift_book_checkout(tmp_path)

    toc = TableOfContents(
        str(toc_path.parent),
        str(toc_path),
        str(tmp_path / "temp"),
    )

    assert toc.pdf_doc_tags[-1] == NOTICES_DOC_TAG
    assert (
        toc.chapter_metadata[NOTICES_DOC_KEY].header_line == "Acknowledgments"
    )


def test_pdf_notices_toc_lines_include_section_heading_only_when_requested() -> (
    None
):
    assert build_notices_toc_lines() == ["\n", f"- <doc:{NOTICES_DOC_TAG}>\n"]
    assert build_notices_toc_lines(include_section_heading=True) == [
        "\n",
        f"### {NOTICES_SECTION_TITLE}\n",
        "\n",
        f"- <doc:{NOTICES_DOC_TAG}>\n",
    ]


def test_pdf_toc_can_skip_notices_chapter(
    tmp_path: Path,
) -> None:
    toc_path = _create_minimal_swift_book_checkout(tmp_path)

    toc = TableOfContents(
        str(toc_path.parent),
        str(toc_path),
        str(tmp_path / "temp"),
        include_notices=False,
    )

    assert NOTICES_DOC_TAG not in toc.pdf_doc_tags
    assert NOTICES_DOC_KEY not in toc.chapter_metadata


def test_render_notices_uses_detected_year_range_without_process_text() -> (
    None
):
    year_range = (2014, 2026)

    xhtml = render_notices_xhtml("Acknowledgments", year_range)
    latex = render_notices_latex(RenderingMode.DIGITAL, year_range)

    assert (
        "Copyright &#169; 2014-2026 Apple Inc. and the Swift project authors"
        in xhtml
    )
    assert "swift-book-pdf" in xhtml
    assert "supporting assets derived from <em>swift-book-pdf</em>." in xhtml
    assert "swift-docc-render project" not in xhtml
    assert f"{{{NOTICES_DOC_KEY}}}" in latex
    assert r"\begin{plainlistingbox}" in latex
    assert r"\textcopyright{} 2025-2026" in latex
    assert (
        r"\textcopyright{} 2014-2026 Apple Inc. and the Swift project authors"
        in latex
    )
    assert SWIFT_DOCC_RENDER_NOTICE_TEXT in latex


def test_print_notices_does_not_footnote_named_url_strings() -> None:
    latex = render_notices_latex(RenderingMode.PRINT, (2014, 2026))

    assert SWIFT_LICENSE_URL in latex
    assert SWIFT_CONTRIBUTORS_URL in latex
    assert r"\footnote{\url{https://swift.org/LICENSE.txt}}" not in latex
    assert r"\footnote{\url{https://swift.org/CONTRIBUTORS.txt}}" not in latex


def test_digital_notices_keeps_named_url_strings_as_links() -> None:
    latex = render_notices_latex(RenderingMode.DIGITAL, (2014, 2026))

    assert (
        rf"\href{{{SWIFT_BOOK_PDF_REPO_URL}}}{{\emph{{swift-book-pdf}}}}"
        in latex
    )
    assert rf"\href{{{SWIFT_BOOK_REPO_URL}}}{{\emph{{swift-book}}}}" in latex
    assert (
        r"\href{https://github.com/swiftlang/swift-docc-render}"
        r"{\emph{swift-docc-render}}" in latex
    )
    assert rf"\href{{{SWIFT_LICENSE_URL}}}{{{SWIFT_LICENSE_URL}}}" in latex
    assert (
        rf"\href{{{SWIFT_CONTRIBUTORS_URL}}}{{{SWIFT_CONTRIBUTORS_URL}}}"
        in latex
    )


def _create_minimal_swift_book_checkout(tmp_path: Path) -> Path:
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
    return toc_path
