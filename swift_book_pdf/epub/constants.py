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

import re
from pathlib import Path

DOC_LINK_PATTERN = re.compile(r"<doc:([^>]+)>")
STRONG_PATTERN = re.compile(r"\*\*(.+?)\*\*")
EMPHASIS_PATTERN = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
HEADING_PATTERN = re.compile(r"^(#{1,4})\s+(.*)$")
DOC_TAG_LINE_PATTERN = re.compile(r"^-\s+<doc:(.*?)>\s*$")
PART_HEADING_PATTERN = re.compile(r"^###\s+(.*)$")
CODE_PLACEHOLDER_PATTERN = re.compile(r"<#(.*?)#>")

SUMMARY_DOC_KEY = "summaryofthegrammar"
SUMMARY_DOC_FILE_NAME = "zzSummaryOfTheGrammar.xhtml"
NOTICES_DOC_TITLE = "Acknowledgments"
NOTICES_DOC_FILE_NAME = "Trademarks.xhtml"
EPUB_COVER_DOC_TITLE = "Cover"
EPUB_COVER_DOC_FILE_NAME = "cover.xhtml"
DEFAULT_BOOK_TITLE = "The Swift Programming Language"
EPUB_IDENTIFIER_ID = "publication-id"
OEBPS_DIR_NAME = "OEBPS"
NAV_DOC_FILE_NAME = "toc.xhtml"
NCX_FILE_NAME = "toc.ncx"
SWIFT_LICENSE_URL = "https://swift.org/LICENSE.txt"
SWIFT_CONTRIBUTORS_URL = "https://swift.org/CONTRIBUTORS.txt"
SWIFT_BOOK_REPO_URL = "https://github.com/swiftlang/swift-book"
SWIFT_BOOK_PDF_REPO_URL = "https://github.com/ekassos/swift-book-pdf"

LOCAL_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
REFERENCE_STATIC_DIR = LOCAL_ASSETS_DIR / "epub_reference"
SWIFT_LOGO_PNG_PATH = LOCAL_ASSETS_DIR / "Swift_logo_color_epub.png"
SWIFT_LOGO_WHITE_PNG_PATH = LOCAL_ASSETS_DIR / "Swift_logo_white.png"
EPUB_COVER_LOGO_FILE_NAME = "_static/swift-logo.png"
EPUB_COVER_LOGO_DARK_FILE_NAME = "_static/swift-logo-dark.png"
COVER_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover.png"
COVER_BETA_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover-beta.png"
COVER_DPI = 300
COVER_TEXT_X = 292.5
COVER_TEXT_Y = 1604.99
COVER_TEXT_WIDTH = 855.0
COVER_TEXT_SIZE_PT = 30
COVER_TEXT_SIZE = round(COVER_TEXT_SIZE_PT * COVER_DPI / 72)
COVER_TEXT_TRACKING = 0.2
COVER_TEXT_VERTICAL_SCALE = 0.9
COVER_TEXT_FILL = "#2B2B2B"
COVER_FOOTER_TEXT_SIZE_PT = 14
COVER_FOOTER_TEXT_SIZE = round(COVER_FOOTER_TEXT_SIZE_PT * COVER_DPI / 72)
COVER_FOOTER_TEXT_Y = 1978
COVER_FOOTER_TEXT_FILL = "#6F6F6F"
