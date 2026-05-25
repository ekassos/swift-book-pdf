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

"""Resolve requested font families against discovered availability."""

import logging

from swift_book_pdf.pdf.latex.fonts.candidates import (
    FONT_TROUBLESHOOTING_URL,
    NOTO_SANS_DOWNLOAD_URL,
)
from swift_book_pdf.pdf.latex.fonts.discovery import (
    find_all_fonts,
    find_font,
)

logger = logging.getLogger(__name__)


def resolve_font_config_value(
    font_role: str,
    custom_font: str | None,
    default_font_list: list[str],
    latex_font_cache: dict[str, bool],
    custom_warning_label: str,
) -> str:
    font = find_font(default_font_list, latex_font_cache)
    if custom_font:
        font = find_font([custom_font], latex_font_cache)
        if not font:
            logger.warning(
                f"{custom_warning_label} '{custom_font}' not found. Using default fonts.",
            )
            font = find_font(default_font_list, latex_font_cache)

    if font:
        return font

    raise ValueError(
        f"Couldn't find any of the following fonts for {font_role}: {', '.join(default_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}",
    )


def resolve_unicode_font_list(
    unicode_fonts_custom_list: list[str],
    unicode_font_list: list[str],
    latex_font_cache: dict[str, bool],
) -> list[str]:
    if unicode_fonts_custom_list:
        if find_all_fonts(unicode_fonts_custom_list, latex_font_cache):
            return unicode_fonts_custom_list
        logger.warning(
            f"Some of the provided unicode font(s) ('{', '.join(unicode_fonts_custom_list)}') not found. Using default fonts.",
        )

    unicode_font = find_font(unicode_font_list, latex_font_cache)
    if unicode_font:
        return [unicode_font]

    raise ValueError(
        f'Couldn\'t find any of the following fonts for unicode text: {", ".join(unicode_font_list)}. If you don\'t have access to any of the default unicode fonts, download ({NOTO_SANS_DOWNLOAD_URL}) and specify the following Noto Sans font families:\n\nswift_book_pdf --unicode "Noto Sans" --unicode "Noto Sans SC" --unicode "Noto Sans KR" --unicode "Noto Sans Thai"\n\nSee: {FONT_TROUBLESHOOTING_URL}',
    )
