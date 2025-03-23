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
import os
import re
import subprocess
import tempfile

from typing import Optional

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
    "Monaco",
    "Consolas",
    "DejaVu Sans Mono",
    "Ubuntu Mono",
    "Courier New",
]
EMOJI_FONT_LIST = ["Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji"]
UNICODE_FONT_LIST = ["Arial Unicode MS"]
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
NOTO_SANS_DOWNLOAD_URL = "https://fonts.google.com/noto"


def batch_check_fonts(font_names: list[str]) -> dict[str, bool]:
    """
    Given an iterable of font names, check (in one lualatex run) whether each
    font is available to fontspec.
    """
    if not font_names:
        return {}

    font_cache = {}

    # Build LaTeX code that produces output like:
    #   FONTCHECK:<fontname>:FOUND
    #   FONTCHECK:<fontname>:MISSING
    font_checks = "\n".join(
        rf"""\IfFontExistsTF{{{font}}}{{\typeout{{FONTCHECK:{font}:FOUND}}}}{{\typeout{{FONTCHECK:{font}:MISSING}}}}"""
        for font in font_names
    )

    tex_code = rf"""
    \documentclass{{article}}
    \usepackage{{fontspec}}
    \begin{{document}}
    {font_checks}
    \end{{document}}
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_filename = "check_fonts.tex"
        tex_file_path = os.path.join(tmpdir, tex_filename)
        with open(tex_file_path, "w", encoding="utf-8") as tex_file:
            tex_file.write(tex_code)
        try:
            result = subprocess.run(
                ["lualatex", "--interaction=nonstopmode", tex_filename],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )
            output = result.stdout + "\n" + result.stderr
            logger.debug(f"Batch font check output:\n{output}")
        except Exception as e:
            logger.error(
                "Error occurred while running lualatex for batch font check", exc_info=e
            )
            # On error, mark all as missing.
            for font in font_names:
                font_cache[font] = False
            return font_cache

    for line in output.splitlines():
        if "FONTCHECK:" in line:
            try:
                # Expecting a line: "FONTCHECK:<font>:FOUND" or "FONTCHECK:<font>:MISSING"
                marker = line.split("FONTCHECK:", 1)[1]
                font, status = marker.split(":", 1)
                font_cache[font.strip()] = status.strip() == "FOUND"
            except Exception as parse_e:
                logger.warning(
                    f"Cannot parse font status from line: {line}. Error: {parse_e}"
                )

    return font_cache


def find_font(font_list: list[str], latex_font_cache: dict[str, bool]) -> Optional[str]:
    """
    Return the first font in font_list that is available, or None if none are found.
    """
    for font in font_list:
        if latex_font_cache.get(font, False):
            logger.debug(f'Font "{font}" is accessible by LuaTeX.')
            return font
        else:
            logger.debug(f'Font "{font}" is not accessible by LuaTeX.')
    return None


def find_all_fonts(font_list: list[str], latex_font_cache: dict[str, bool]) -> bool:
    """
    Return True if all fonts in font_list are available, or False if any are not found.
    """
    for font in font_list:
        if latex_font_cache.get(font, False):
            logger.debug(f'Font "{font}" is accessible by LuaTeX.')
        else:
            logger.info(f'Font "{font}" is not accessible by LuaTeX.')
            return False
    return True


def gather_all_candidate_fonts(
    custom_fonts: list[Optional[str]], default_font_lists: list[list[str]]
) -> dict[str, bool]:
    """
    Gathers all custom fonts (if provided) and all default fonts from the provided lists,
    then batch-checks them using LuaTeX.
    """
    candidate_fonts = set()
    for font in custom_fonts:
        if font:
            candidate_fonts.add(font)
    for font_list in default_font_lists:
        candidate_fonts.update(font_list)
    if candidate_fonts:
        return batch_check_fonts(list(candidate_fonts))
    else:
        return {}


class FontConfig:
    def __init__(
        self,
        main_font_custom: Optional[str] = None,
        mono_font_custom: Optional[str] = None,
        emoji_font_custom: Optional[str] = None,
        unicode_fonts_custom_list: list[str] = [],
        header_footer_font_custom: Optional[str] = None,
        main_font_list: list[str] = MAIN_FONT_LIST,
        mono_font_list: list[str] = MONO_FONT_LIST,
        emoji_font_list: list[str] = EMOJI_FONT_LIST,
        unicode_font_list: list[str] = UNICODE_FONT_LIST,
        header_footer_font_list: list[str] = HEADER_FOOTER_FONT_LIST,
    ):
        logger.info("Configuring fonts...")
        logger.debug("Custom fonts provided:")
        logger.debug(f"Main font: {main_font_custom}")
        logger.debug(f"Monospace font: {mono_font_custom}")
        logger.debug(f"Emoji font: {emoji_font_custom}")
        logger.debug(f"Unicode font(s): {', '.join(unicode_fonts_custom_list)}")
        logger.debug(f"Header/Footer font: {header_footer_font_custom}")

        LATEX_FONT_CACHE = gather_all_candidate_fonts(
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

        if main_font_custom:
            main_font = find_font([main_font_custom], LATEX_FONT_CACHE)
            if not main_font:
                logger.warning(
                    f"Custom main font '{main_font_custom}' not found. Using default fonts."
                )
                main_font = find_font(main_font_list, LATEX_FONT_CACHE)
        else:
            main_font = find_font(main_font_list, LATEX_FONT_CACHE)
        if not main_font:
            raise ValueError(
                f"Couldn't find any of the following fonts for the main text: {', '.join(main_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}"
            )
        self.main_font = main_font

        if mono_font_custom:
            mono_font = find_font([mono_font_custom], LATEX_FONT_CACHE)
            if not mono_font:
                logger.warning(
                    f"Custom monospace font '{mono_font_custom}' not found. Using default fonts."
                )
                mono_font = find_font(mono_font_list, LATEX_FONT_CACHE)
        else:
            mono_font = find_font(mono_font_list, LATEX_FONT_CACHE)
        if not mono_font:
            raise ValueError(
                f"Couldn't find any of the following fonts for monospace text: {', '.join(mono_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}"
            )
        self.mono_font = mono_font

        if emoji_font_custom:
            emoji_font = find_font([emoji_font_custom], LATEX_FONT_CACHE)
            if not emoji_font:
                logger.warning(
                    f"Custom emoji font '{emoji_font_custom}' not found. Using default fonts."
                )
                emoji_font = find_font(emoji_font_list, LATEX_FONT_CACHE)
        else:
            emoji_font = find_font(emoji_font_list, LATEX_FONT_CACHE)
        if not emoji_font:
            raise ValueError(
                f"Couldn't find any of the following fonts for emojis: {', '.join(emoji_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}"
            )
        self.emoji_font = emoji_font

        has_valid_custom_unicode_fonts = False
        custom_unicode_fonts: list[str] = []
        unicode_font = None
        if unicode_fonts_custom_list:
            has_valid_custom_unicode_fonts = find_all_fonts(
                unicode_fonts_custom_list, LATEX_FONT_CACHE
            )
            if not has_valid_custom_unicode_fonts:
                logger.warning(
                    f"Some of the provided unicode font(s) ('{', '.join(unicode_fonts_custom_list)}') not found. Using default fonts."
                )
                unicode_font = find_font(unicode_font_list, LATEX_FONT_CACHE)
            else:
                custom_unicode_fonts = unicode_fonts_custom_list
        else:
            unicode_font = find_font(unicode_font_list, LATEX_FONT_CACHE)
        if has_valid_custom_unicode_fonts and custom_unicode_fonts:
            self.unicode_font_list = custom_unicode_fonts
        elif unicode_font:
            self.unicode_font_list = [unicode_font]
        else:
            raise ValueError(
                f'Couldn\'t find any of the following fonts for unicode text: {", ".join(unicode_font_list)}. If you don\'t have access to any of the default unicode fonts, download ({NOTO_SANS_DOWNLOAD_URL}) and specify the following Noto Sans font families:\n\nswift_book_pdf --unicode "Noto Sans" --unicode "Noto Sans SC" --unicode "Noto Sans KR" --unicode "Noto Sans Thai"\n\nSee: {FONT_TROUBLESHOOTING_URL}'
            )

        if header_footer_font_custom:
            header_footer_font = find_font(
                [header_footer_font_custom], LATEX_FONT_CACHE
            )
            if not header_footer_font:
                logger.warning(
                    f"Custom header/footer font '{header_footer_font_custom}' not found. Using default fonts."
                )
                header_footer_font = find_font(
                    header_footer_font_list, LATEX_FONT_CACHE
                )
        else:
            header_footer_font = find_font(header_footer_font_list, LATEX_FONT_CACHE)
        if not header_footer_font:
            raise ValueError(
                f"Couldn't find any of the following fonts for header/footer text: {', '.join(header_footer_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}"
            )
        self.header_footer_font = header_footer_font

        logger.debug("Font configuration:")
        logger.debug(f"MAIN: {self.main_font}")
        logger.debug(f"MONO: {self.mono_font}")
        logger.debug(f"EMOJI: {self.emoji_font}")
        logger.debug(f"UNICODE: {', '.join(self.unicode_font_list)}")
        logger.debug(f"HEADER/FOOTER: {self.header_footer_font}")

    def __str__(self):
        return (
            "Your font configuration:\n"
            f"Main font: {self.main_font} ({'default font' if self.main_font in MAIN_FONT_LIST else 'custom font'})\n"
            f"Monospace font: {self.mono_font} ({'default font' if self.mono_font in MONO_FONT_LIST else 'custom font'})\n"
            f"Emoji font: {self.emoji_font} ({'default font' if self.emoji_font in EMOJI_FONT_LIST else 'custom font'})\n"
            f"Unicode font(s): {', '.join(self.unicode_font_list)} ({'default font' if all(font in UNICODE_FONT_LIST for font in self.unicode_font_list) else 'custom font(s)'})\n"
            f"Header/Footer font: {self.header_footer_font} ({'default font' if self.header_footer_font in HEADER_FOOTER_FONT_LIST else 'custom font'})\n"
        )


def check_for_missing_font_logs(log_line: str):
    """Check for missing font logs in the given log line.
    If a missing font is detected, raise a ValueError with a message
    indicating the font name and the character that is missing.
    Args:
        log_line (str): The log line to check.
    Raises:
        ValueError: If a missing font is detected.
    """
    pattern = re.compile(
        r"Missing character: There is no (?P<char>\S+) "
        r"\((?P<code>U\+\w+)\) in font name:"
    )

    match = pattern.search(log_line)
    if match:
        missing_char = match.group("char")
        unicode_code = match.group("code")
        raise ValueError(
            f"The fonts you specified do not support character {missing_char} ({unicode_code}).\nIf you are using a custom font, please ensure that it supports the character set you are trying to use.\nOtherwise, see {FONT_TROUBLESHOOTING_URL} for more information."
        )
