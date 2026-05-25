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

from swift_book_pdf.epub.constants import REFERENCE_STATIC_DIR

COVER_FONT_DIR = REFERENCE_STATIC_DIR / "fonts"
COVER_SANS_FONT_PATH = COVER_FONT_DIR / "IBMPlexSans-Medium.ttf"
COVER_SERIF_ITALIC_FONT_PATH = COVER_FONT_DIR / "IBMPlexSerif-Italic.ttf"
COVER_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover.png"
COVER_BETA_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover-beta.png"
COVER_CURRENT_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover-current.png"
COVER_NIGHTLY_TEMPLATE_PATH = REFERENCE_STATIC_DIR / "cover-nightly.png"
COVER_DPI = 300
COVER_TEXT_X = 404
COVER_TEXT_BASELINE_Y = 844
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
