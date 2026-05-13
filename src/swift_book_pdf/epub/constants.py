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
EPUB_COVER_DOC_TITLE = "Cover"
EPUB_COVER_DOC_FILE_NAME = "cover.xhtml"
DEFAULT_BOOK_TITLE = "The Swift Programming Language"
EPUB_IDENTIFIER_ID = "publication-id"
OEBPS_DIR_NAME = "OEBPS"
NAV_DOC_FILE_NAME = "toc.xhtml"
NCX_FILE_NAME = "toc.ncx"

LOCAL_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
REFERENCE_STATIC_DIR = LOCAL_ASSETS_DIR / "epub_reference"
EPUB_FONT_DIR_NAME = "_static/fonts"
EPUB_FONT_FILE_NAMES = (
    "IBMPlexSans-Medium.ttf",
    "IBMPlexSerif-Italic.ttf",
    "IBMPlexSerif-Medium.ttf",
    "IBMPlexSerif-Regular.ttf",
)
EPUB_FONT_DIR = REFERENCE_STATIC_DIR / "fonts"
COVER_SANS_FONT_PATH = EPUB_FONT_DIR / "IBMPlexSans-Medium.ttf"
COVER_SERIF_ITALIC_FONT_PATH = EPUB_FONT_DIR / "IBMPlexSerif-Italic.ttf"
IBM_PLEX_OFL_PATH = EPUB_FONT_DIR / "IBM-Plex-OFL.txt"
COVER_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover.png"
COVER_BETA_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover-beta.png"
COVER_CURRENT_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover-current.png"
COVER_NIGHTLY_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover-nightly.png"
COVER_DPI = 300
COVER_TEXT_X = 404
COVER_TEXT_BASELINE_Y = 982
COVER_TEXT_SIZE_PT = 28
COVER_TEXT_SIZE = round(COVER_TEXT_SIZE_PT * COVER_DPI / 72)
COVER_TEXT_TRACKING = -2.5
COVER_TEXT_FILL = "#33519e"
COVER_BETA_TEXT_FILL = "#d94a2b"
COVER_CURRENT_TEXT_FILL = "#19733c"
COVER_NIGHTLY_TEXT_FILL = "#8e3fa9"
COVER_FOOTER_TEXT_SIZE_PT = 11
COVER_FOOTER_TEXT_SIZE = round(COVER_FOOTER_TEXT_SIZE_PT * COVER_DPI / 72)
COVER_FOOTER_TEXT_Y = 1978
COVER_FOOTER_TEXT_FILL = "#1e1c1d"
