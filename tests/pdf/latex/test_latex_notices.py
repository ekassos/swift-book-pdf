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

from swift_book_pdf.core.generated.notices.content import (
    SWIFT_BOOK_PDF_REPO_URL,
    SWIFT_BOOK_REPO_URL,
    SWIFT_CONTRIBUTORS_URL,
    SWIFT_DOCC_RENDER_NOTICE_TEXT,
    SWIFT_LICENSE_URL,
)
from swift_book_pdf.core.generated.notices.metadata import NOTICES_DOC_KEY
from swift_book_pdf.pdf.config import RenderingMode
from swift_book_pdf.pdf.latex.render.notices import render_notices_latex


def test_render_notices_latex_uses_detected_year_range() -> None:
    latex = render_notices_latex(RenderingMode.DIGITAL, (2014, 2026))

    assert f"{{{NOTICES_DOC_KEY}}}" in latex
    assert r"\begin{DocCCodeListingPlainBox}" in latex
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
