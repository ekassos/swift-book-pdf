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
import subprocess

logger = logging.getLogger(__name__)

MAIN_FONT_LIST = [
    "Helvetica Neue",
    "Helvetica",
    "SF Pro",
    "Arial",
    "Segoe UI",
    "Liberation Sans",
    "DejaVu Sans",
]
MONO_FONT_LIST = [
    "Menlo",
    "SF Mono",
    "Courier",
    "Monaco",
    "Consolas",
    "Courier New",
    "DejaVu Sans Mono",
    "Ubuntu Mono",
]
EMOJI_FONT_LIST = ["Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji"]
UNICODE_FONT_LIST = [
    "Arial Unicode MS",
    "Noto Sans CJK",
    "Noto Serif CJK",
]
HEADER_FOOTER_FONT_LIST = [
    "SF Compact Display",
    "SF Pro Display",
    "SF Compact",
    "SF Pro",
    "Helvetica Neue",
    "Helvetica",
    "Arial",
    "Segoe UI",
    "Liberation Sans",
    "DejaVu Sans",
]
FONT_TROUBLESHOOTING_URL = (
    "https://github.com/ekassos/swift-book-pdf/wiki/Troubleshooting"
)


def find_font(font_list: list[str], available_fonts: str):
    """Return the first font from font_list that's available, or None otherwise."""
    for font in font_list:
        if font.lower() in available_fonts:
            logger.debug(f'Font "{font}" is accessible by LuaTeX.')
            return font
        else:
            logger.debug(f'Font "{font}" is not accessible by LuaTeX.')
    return None


class FontConfig:
    def __init__(
        self,
        main_font_list: list[str] = MAIN_FONT_LIST,
        mono_font_list: list[str] = MONO_FONT_LIST,
        emoji_font_list: list[str] = EMOJI_FONT_LIST,
        unicode_font_list: list[str] = UNICODE_FONT_LIST,
        header_footer_font_list: list[str] = HEADER_FOOTER_FONT_LIST,
    ):
        result = subprocess.run(
            ["luaotfload-tool", "--list=*"], capture_output=True, text=True
        )
        logger.debug(f"Available fonts:\n{result.stdout}")
        available_fonts = result.stdout.lower()

        main_font = find_font(main_font_list, available_fonts)
        if not main_font:
            raise ValueError(
                f"Couldn't find any of the following fonts for the main text: {', '.join(main_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}"
            )
        self.main_font = main_font

        mono_font = find_font(mono_font_list, available_fonts)
        if not mono_font:
            raise ValueError(
                f"Couldn't find any of the following fonts for monospace text: {', '.join(mono_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}"
            )
        self.mono_font = mono_font

        emoji_font = find_font(emoji_font_list, available_fonts)
        if not emoji_font:
            raise ValueError(
                f"Couldn't find any of the following fonts for emojis: {', '.join(emoji_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}"
            )
        self.emoji_font = emoji_font

        unicode_font = find_font(unicode_font_list, available_fonts)
        if not unicode_font:
            raise ValueError(
                f"Couldn't find any of the following fonts for unicode text: {', '.join(unicode_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}"
            )
        self.unicode_font = unicode_font

        header_footer_font = find_font(header_footer_font_list, available_fonts)
        if not header_footer_font:
            raise ValueError(
                f"Couldn't find any of the following fonts for header/footer text: {', '.join(header_footer_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}"
            )
        self.header_footer_font = header_footer_font

        logger.debug("Font configuration:")
        logger.debug(f"MAIN: {self.main_font}")
        logger.debug(f"MONO: {self.mono_font}")
        logger.debug(f"EMOJI: {self.emoji_font}")
        logger.debug(f"UNICODE: {self.unicode_font}")
        logger.debug(f"HEADER/FOOTER: {self.header_footer_font}")
