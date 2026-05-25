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

"""Render the generated notices chapter as EPUB XHTML."""

import html

from swift_book_pdf.core.generated.notices.content import (
    APACHE_LICENSE_V2_TEXT,
    IBM_PLEX_OFL_TEXT,
    SWIFT_BOOK_PDF_REPO_URL,
    SWIFT_BOOK_REPO_URL,
    SWIFT_CONTRIBUTORS_URL,
    SWIFT_LICENSE_URL,
    format_copyright_year_range,
)
from swift_book_pdf.core.generated.notices.metadata import NOTICES_SECTION_ID


def render_notices_xhtml(
    title: str,
    year_range: tuple[int, int] | None = None,
) -> str:
    """Render the generated notices body for an EPUB XHTML document."""
    return (
        f'  <div class="section" id="{html.escape(NOTICES_SECTION_ID)}">\n'
        f"<h1>{html.escape(title)}</h1>\n"
        "<p>This edition of <em>The Swift Programming Language</em> was generated using "
        f'<a href="{html.escape(SWIFT_BOOK_PDF_REPO_URL)}"><em>swift-book-pdf</em></a>. '
        "This publication includes styling and supporting assets derived from <em>swift-book-pdf</em>. "
        "These materials are Copyright &#169; 2026 Evangelos Kassos and are licensed under the Apache License, Version 2.0.</p>"
        "<p>This edition is derived from the <em>swift-book</em> source and is a modified version "
        "of the original work, converted and formatted for distribution.</p>\n"
        "<p>The <em>swift-book</em> "
        f'<a href="{html.escape(SWIFT_BOOK_REPO_URL)}">repository</a> '
        "is part of the Swift.org open source project. The <em>swift-book</em> source is licensed under the Apache License, Version 2.0 with Runtime Library Exception. "
        f'See <a href="{html.escape(SWIFT_LICENSE_URL)}">{html.escape(SWIFT_LICENSE_URL)}</a> for details. '
        f"{_build_original_work_copyright_sentence(year_range)} The Swift project authors are credited at "
        f'<a href="{html.escape(SWIFT_CONTRIBUTORS_URL)}">{html.escape(SWIFT_CONTRIBUTORS_URL)}</a>.</p>\n'
        "<p>Swift is a trademark of Apple Inc. "
        "This edition is not published by, endorsed by, or affiliated with Apple Inc. or the Swift.org open source project.</p>\n"
        "<p>This edition uses IBM Plex Sans and IBM Plex Serif, Copyright &#169; 2017 IBM Corp. "
        'with Reserved Font Name "Plex", licensed under the SIL Open Font License 1.1.</p>\n'
        "<h2>Apache License 2.0</h2>\n"
        f"<pre>{html.escape(APACHE_LICENSE_V2_TEXT)}</pre>\n"
        "<h2>IBM Plex Font License</h2>\n"
        f"<pre>{html.escape(IBM_PLEX_OFL_TEXT)}</pre>\n"
        "</div>\n"
    )


def _build_original_work_copyright_sentence(
    year_range: tuple[int, int] | None,
) -> str:
    year_text = format_copyright_year_range(year_range)
    if year_text:
        return (
            "The original work is Copyright &#169; "
            f"{year_text} Apple Inc. and the Swift project authors."
        )
    return (
        "The original work is Copyright &#169; Apple Inc. "
        "and the Swift project authors."
    )
