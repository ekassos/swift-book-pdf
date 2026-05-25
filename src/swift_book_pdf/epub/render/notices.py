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

from __future__ import annotations

from dataclasses import dataclass

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
from swift_book_pdf.epub.templating import render_epub_template


@dataclass(frozen=True)
class NoticesTemplateData:
    """Structured data for the generated notices body template."""

    title: str
    """Notices page title."""

    section_id: str
    """Generated notices section anchor."""

    swift_book_pdf_repo_url: str
    """Repository URL for this generator."""

    swift_book_repo_url: str
    """Repository URL for the upstream Swift book."""

    swift_license_url: str
    """Swift project license URL."""

    swift_contributors_url: str
    """Swift project contributors URL."""

    original_work_years: str
    """Formatted original-work copyright years, or an empty string."""

    apache_license_text: str
    """Bundled Apache license text."""

    ibm_plex_ofl_text: str
    """Bundled IBM Plex font license text."""


def render_notices_xhtml(
    title: str,
    year_range: tuple[int, int] | None = None,
) -> str:
    """Render the generated notices body for an EPUB XHTML document.

    Args:
        title: Notices page title.
        year_range: Optional original-work copyright year range.

    Returns:
        XHTML body fragment for the generated legal notices page.
    """
    return render_epub_template(
        "notices-body.xhtml.j2",
        {
            "notices": NoticesTemplateData(
                title=title,
                section_id=NOTICES_SECTION_ID,
                swift_book_pdf_repo_url=SWIFT_BOOK_PDF_REPO_URL,
                swift_book_repo_url=SWIFT_BOOK_REPO_URL,
                swift_license_url=SWIFT_LICENSE_URL,
                swift_contributors_url=SWIFT_CONTRIBUTORS_URL,
                original_work_years=format_copyright_year_range(year_range),
                apache_license_text=APACHE_LICENSE_V2_TEXT,
                ibm_plex_ofl_text=IBM_PLEX_OFL_TEXT,
            )
        },
    )
