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

"""Backend-neutral generated notices text and references."""

from importlib.resources import files

SWIFT_LICENSE_URL = "https://swift.org/LICENSE.txt"
SWIFT_CONTRIBUTORS_URL = "https://swift.org/CONTRIBUTORS.txt"
SWIFT_BOOK_REPO_URL = "https://github.com/swiftlang/swift-book"
SWIFT_DOCC_RENDER_REPO_URL = "https://github.com/swiftlang/swift-docc-render"
SWIFT_BOOK_PDF_REPO_URL = "https://github.com/ekassos/swift-book-pdf"


def _read_notice_text(resource_path: str) -> str:
    """Read bundled notice text with normalized line endings.

    Args:
        resource_path: Package-relative path under `swift_book_pdf`.

    Returns:
        Text content with CRLF line endings normalized to LF.
    """
    return (
        files("swift_book_pdf")
        .joinpath(resource_path)
        .read_text(encoding="utf-8")
        .replace("\r\n", "\n")
    )


APACHE_LICENSE_V2_TEXT = _read_notice_text(
    "assets/notices/Apache-License-2.0-with-Runtime-Exception.txt"
)
SWIFT_DOCC_RENDER_NOTICE_TEXT = _read_notice_text(
    "assets/notices/Swift-DocC-Render-NOTICE.txt"
)
IBM_PLEX_OFL_TEXT = _read_notice_text("assets/notices/IBM-Plex-OFL.txt")


def format_copyright_year_range(year_range: tuple[int, int] | None) -> str:
    """Format an optional inclusive copyright year range.

    Args:
        year_range: Inclusive `(start_year, end_year)` range, or `None` when
            no source copyright years were detected.

    Returns:
        An empty string for `None`, one year when both years match, or a
        hyphenated range.
    """
    if year_range is None:
        return ""
    start_year, end_year = year_range
    if start_year == end_year:
        return str(start_year)
    return f"{start_year}-{end_year}"
