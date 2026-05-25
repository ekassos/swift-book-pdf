# Copyright 2025 Evangelos Kassos
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

import logging

from swift_book_pdf.pdf.latex.fonts.candidates import (
    EMOJI_FONT_LIST,
    HEADER_FOOTER_FONT_LIST,
    MAIN_FONT_LIST,
    MONO_FONT_LIST,
    UNICODE_FONT_LIST,
)
from swift_book_pdf.pdf.latex.fonts.discovery import gather_all_candidate_fonts
from swift_book_pdf.pdf.latex.fonts.resolution import (
    resolve_font_config_value,
    resolve_unicode_font_list,
)

logger = logging.getLogger(__name__)


class FontConfig:
    def __init__(  # noqa: PLR0913
        self,
        main_font_custom: str | None = None,
        mono_font_custom: str | None = None,
        emoji_font_custom: str | None = None,
        unicode_fonts_custom_list: list[str] | None = None,
        header_footer_font_custom: str | None = None,
        main_font_list: list[str] = MAIN_FONT_LIST,
        mono_font_list: list[str] = MONO_FONT_LIST,
        emoji_font_list: list[str] = EMOJI_FONT_LIST,
        unicode_font_list: list[str] = UNICODE_FONT_LIST,
        header_footer_font_list: list[str] = HEADER_FOOTER_FONT_LIST,
    ) -> None:
        unicode_fonts_custom_list = unicode_fonts_custom_list or []
        logger.info("Configuring fonts...")
        logger.debug("Custom fonts provided:")
        logger.debug(f"Main font: {main_font_custom}")
        logger.debug(f"Monospace font: {mono_font_custom}")
        logger.debug(f"Emoji font: {emoji_font_custom}")
        logger.debug(
            f"Unicode font(s): {', '.join(unicode_fonts_custom_list)}"
        )
        logger.debug(f"Header/Footer font: {header_footer_font_custom}")

        latex_font_cache = gather_all_candidate_fonts(
            [
                main_font_custom,
                mono_font_custom,
                emoji_font_custom,
                header_footer_font_custom,
            ],
            [
                unicode_fonts_custom_list,
                main_font_list,
                mono_font_list,
                emoji_font_list,
                unicode_font_list,
                header_footer_font_list,
            ],
        )
        self.main_font = resolve_font_config_value(
            "main text",
            main_font_custom,
            main_font_list,
            latex_font_cache,
            "Custom main font",
        )
        self.mono_font = resolve_font_config_value(
            "monospace text",
            mono_font_custom,
            mono_font_list,
            latex_font_cache,
            "Custom monospace font",
        )
        self.emoji_font = resolve_font_config_value(
            "emojis",
            emoji_font_custom,
            emoji_font_list,
            latex_font_cache,
            "Custom emoji font",
        )
        self.unicode_font_list = resolve_unicode_font_list(
            unicode_fonts_custom_list,
            unicode_font_list,
            latex_font_cache,
        )
        self.header_footer_font = resolve_font_config_value(
            "header/footer text",
            header_footer_font_custom,
            header_footer_font_list,
            latex_font_cache,
            "Custom header/footer font",
        )

        logger.debug("Font configuration:")
        logger.debug(f"MAIN: {self.main_font}")
        logger.debug(f"MONO: {self.mono_font}")
        logger.debug(f"EMOJI: {self.emoji_font}")
        logger.debug(f"UNICODE: {', '.join(self.unicode_font_list)}")
        logger.debug(f"HEADER/FOOTER: {self.header_footer_font}")

    def __str__(self) -> str:
        return (
            "Your font configuration:\n"
            f"Main font: {self.main_font} ({'default font' if self.main_font in MAIN_FONT_LIST else 'custom font'})\n"
            f"Monospace font: {self.mono_font} ({'default font' if self.mono_font in MONO_FONT_LIST else 'custom font'})\n"
            f"Emoji font: {self.emoji_font} ({'default font' if self.emoji_font in EMOJI_FONT_LIST else 'custom font'})\n"
            f"Unicode font(s): {', '.join(self.unicode_font_list)} ({'default font' if all(font in UNICODE_FONT_LIST for font in self.unicode_font_list) else 'custom font(s)'})\n"
            f"Header/Footer font: {self.header_footer_font} ({'default font' if self.header_footer_font in HEADER_FOOTER_FONT_LIST else 'custom font'})\n"
        )
