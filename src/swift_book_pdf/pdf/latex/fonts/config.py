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

from swift_book_pdf.pdf.fonts.config import FontConfig, FontOverrides
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
class LaTeXFontCandidates:
    """Candidate font names used to resolve LaTeX font defaults."""

    main_fonts: list[str] | None = None
    mono_fonts: list[str] | None = None
    emoji_fonts: list[str] | None = None
    unicode_fonts: list[str] | None = None
    header_footer_fonts: list[str] | None = None


def format_for_latex(font_config: FontConfig) -> str:
    """Format a resolved font config with LaTeX default-font context."""
    return (
        "Your font configuration:\n"
        f"Main font: {font_config.main_font} ({'default font' if font_config.main_font in MAIN_FONT_LIST else 'custom font'})\n"
        f"Monospace font: {font_config.mono_font} ({'default font' if font_config.mono_font in MONO_FONT_LIST else 'custom font'})\n"
        f"Emoji font: {font_config.emoji_font} ({'default font' if font_config.emoji_font in EMOJI_FONT_LIST else 'custom font'})\n"
        f"Unicode font(s): {', '.join(font_config.unicode_font_list)} ({'default font' if all(font in UNICODE_FONT_LIST for font in font_config.unicode_font_list) else 'custom font(s)'})\n"
        f"Header/Footer font: {font_config.header_footer_font} ({'default font' if font_config.header_footer_font in HEADER_FOOTER_FONT_LIST else 'custom font'})\n"
    )


def resolve_for_latex(
    overrides: FontOverrides | None = None,
    candidates: LaTeXFontCandidates | None = None,
) -> FontConfig:
    overrides = overrides or FontOverrides()
    candidates = candidates or LaTeXFontCandidates()
    main_font_list = (
        MAIN_FONT_LIST
        if candidates.main_fonts is None
        else candidates.main_fonts
    )
    mono_font_list = (
        MONO_FONT_LIST
        if candidates.mono_fonts is None
        else candidates.mono_fonts
    )
    emoji_font_list = (
        EMOJI_FONT_LIST
        if candidates.emoji_fonts is None
        else candidates.emoji_fonts
    )
    unicode_font_list = (
        UNICODE_FONT_LIST
        if candidates.unicode_fonts is None
        else candidates.unicode_fonts
    )
    header_footer_font_list = (
        HEADER_FOOTER_FONT_LIST
        if candidates.header_footer_fonts is None
        else candidates.header_footer_fonts
    )
    unicode_fonts_custom_list = list(overrides.unicode_fonts)
    logger.info("Configuring fonts...")
    logger.debug("Custom fonts provided:")
    logger.debug(f"Main font: {overrides.main_font}")
    logger.debug(f"Monospace font: {overrides.mono_font}")
    logger.debug(f"Emoji font: {overrides.emoji_font}")
    logger.debug(f"Unicode font(s): {', '.join(unicode_fonts_custom_list)}")
    logger.debug(f"Header/Footer font: {overrides.header_footer_font}")

    latex_font_cache = gather_all_candidate_fonts(
        [
            overrides.main_font,
            overrides.mono_font,
            overrides.emoji_font,
            overrides.header_footer_font,
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
        overrides.main_font,
        main_font_list,
        latex_font_cache,
        "Custom main font",
    )
    mono_font = resolve_font_config_value(
        "monospace text",
        overrides.mono_font,
        mono_font_list,
        latex_font_cache,
        "Custom monospace font",
    )
    emoji_font = resolve_font_config_value(
        "emojis",
        overrides.emoji_font,
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
        overrides.header_footer_font,
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

    return FontConfig(
        main_font=main_font,
        mono_font=mono_font,
        emoji_font=emoji_font,
        unicode_font_list=tuple(resolved_unicode_font_list),
        header_footer_font=header_footer_font,
    )
