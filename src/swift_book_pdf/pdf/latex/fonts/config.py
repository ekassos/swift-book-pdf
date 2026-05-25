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
from dataclasses import dataclass

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


@dataclass(frozen=True)
class FontConfig:
    main_font: str
    mono_font: str
    emoji_font: str
    unicode_font_list: tuple[str, ...]
    header_footer_font: str

    @classmethod
    def resolve(  # noqa: PLR0913
        cls,
        main_font_custom: str | None = None,
        mono_font_custom: str | None = None,
        emoji_font_custom: str | None = None,
        unicode_fonts_custom_list: list[str] | None = None,
        header_footer_font_custom: str | None = None,
        main_font_list: list[str] | None = None,
        mono_font_list: list[str] | None = None,
        emoji_font_list: list[str] | None = None,
        unicode_font_list: list[str] | None = None,
        header_footer_font_list: list[str] | None = None,
    ) -> "FontConfig":
        main_font_list = (
            MAIN_FONT_LIST if main_font_list is None else main_font_list
        )
        mono_font_list = (
            MONO_FONT_LIST if mono_font_list is None else mono_font_list
        )
        emoji_font_list = (
            EMOJI_FONT_LIST if emoji_font_list is None else emoji_font_list
        )
        unicode_font_list = (
            UNICODE_FONT_LIST
            if unicode_font_list is None
            else unicode_font_list
        )
        header_footer_font_list = (
            HEADER_FOOTER_FONT_LIST
            if header_footer_font_list is None
            else header_footer_font_list
        )
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
        main_font = resolve_font_config_value(
            "main text",
            main_font_custom,
            main_font_list,
            latex_font_cache,
            "Custom main font",
        )
        mono_font = resolve_font_config_value(
            "monospace text",
            mono_font_custom,
            mono_font_list,
            latex_font_cache,
            "Custom monospace font",
        )
        emoji_font = resolve_font_config_value(
            "emojis",
            emoji_font_custom,
            emoji_font_list,
            latex_font_cache,
            "Custom emoji font",
        )
        resolved_unicode_font_list = resolve_unicode_font_list(
            unicode_fonts_custom_list,
            unicode_font_list,
            latex_font_cache,
        )
        header_footer_font = resolve_font_config_value(
            "header/footer text",
            header_footer_font_custom,
            header_footer_font_list,
            latex_font_cache,
            "Custom header/footer font",
        )

        logger.debug("Font configuration:")
        logger.debug(f"MAIN: {main_font}")
        logger.debug(f"MONO: {mono_font}")
        logger.debug(f"EMOJI: {emoji_font}")
        logger.debug(f"UNICODE: {', '.join(resolved_unicode_font_list)}")
        logger.debug(f"HEADER/FOOTER: {header_footer_font}")

        return cls(
            main_font=main_font,
            mono_font=mono_font,
            emoji_font=emoji_font,
            unicode_font_list=tuple(resolved_unicode_font_list),
            header_footer_font=header_footer_font,
        )

    def __str__(self) -> str:
        return (
            "Your font configuration:\n"
            f"Main font: {self.main_font} ({'default font' if self.main_font in MAIN_FONT_LIST else 'custom font'})\n"
            f"Monospace font: {self.mono_font} ({'default font' if self.mono_font in MONO_FONT_LIST else 'custom font'})\n"
            f"Emoji font: {self.emoji_font} ({'default font' if self.emoji_font in EMOJI_FONT_LIST else 'custom font'})\n"
            f"Unicode font(s): {', '.join(self.unicode_font_list)} ({'default font' if all(font in UNICODE_FONT_LIST for font in self.unicode_font_list) else 'custom font(s)'})\n"
            f"Header/Footer font: {self.header_footer_font} ({'default font' if self.header_footer_font in HEADER_FOOTER_FONT_LIST else 'custom font'})\n"
        )
