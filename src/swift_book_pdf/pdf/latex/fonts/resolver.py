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

"""LaTeX font resolution."""

import logging
import shutil
import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

from swift_book_pdf.pdf.latex.templating import load_latex_template

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
CHECK_FONTS_TEMPLATE = load_latex_template("check_fonts.tex")


@dataclass(frozen=True)
class LaTeXFontConfig:
    """Resolved font names used by the LaTeX backend."""

    main_font: str
    mono_font: str
    emoji_font: str
    unicode_fonts: tuple[str, ...]
    header_footer_font: str

    def __str__(self) -> str:
        return self.diagnostic_details()

    def diagnostic_details(self) -> str:
        """Format a resolved font config with LaTeX default-font context."""
        unicode_context = (
            "default font"
            if all(font in UNICODE_FONT_LIST for font in self.unicode_fonts)
            else "custom font(s)"
        )
        return (
            "Your font configuration:\n"
            f"Main font: {self.main_font} "
            f"({_font_context(self.main_font, MAIN_FONT_LIST)})\n"
            f"Monospace font: {self.mono_font} "
            f"({_font_context(self.mono_font, MONO_FONT_LIST)})\n"
            f"Emoji font: {self.emoji_font} "
            f"({_font_context(self.emoji_font, EMOJI_FONT_LIST)})\n"
            f"Unicode font(s): {', '.join(self.unicode_fonts)} "
            f"({unicode_context})\n"
            f"Header/Footer font: {self.header_footer_font} "
            f"({_font_context(self.header_footer_font, HEADER_FOOTER_FONT_LIST)})\n"
        )


def resolve_for_latex(
    options: Mapping[str, Any] | None = None,
) -> LaTeXFontConfig:
    """Resolve a concrete font configuration for LuaLaTeX."""
    options = options or {}
    main_font_override = _optional_str(options, "main")
    mono_font_override = _optional_str(options, "mono")
    emoji_font_override = _optional_str(options, "emoji")
    header_footer_font_override = _optional_str(options, "header_footer")
    unicode_fonts_custom_list = list(_string_tuple(options, "unicode"))
    logger.info("Configuring fonts...")
    logger.debug("Custom fonts provided:")
    logger.debug(f"Main font: {main_font_override}")
    logger.debug(f"Monospace font: {mono_font_override}")
    logger.debug(f"Emoji font: {emoji_font_override}")
    logger.debug(f"Unicode font(s): {', '.join(unicode_fonts_custom_list)}")
    logger.debug(f"Header/Footer font: {header_footer_font_override}")

    latex_font_cache = _gather_candidate_fonts(
        (
            main_font_override,
            mono_font_override,
            emoji_font_override,
            header_footer_font_override,
        ),
        (
            unicode_fonts_custom_list,
            MAIN_FONT_LIST,
            MONO_FONT_LIST,
            EMOJI_FONT_LIST,
            UNICODE_FONT_LIST,
            HEADER_FOOTER_FONT_LIST,
        ),
    )
    main_font = _resolve_font_config_value(
        "main text",
        main_font_override,
        MAIN_FONT_LIST,
        latex_font_cache,
        "Custom main font",
    )
    mono_font = _resolve_font_config_value(
        "monospace text",
        mono_font_override,
        MONO_FONT_LIST,
        latex_font_cache,
        "Custom monospace font",
    )
    emoji_font = _resolve_font_config_value(
        "emojis",
        emoji_font_override,
        EMOJI_FONT_LIST,
        latex_font_cache,
        "Custom emoji font",
    )
    resolved_unicode_font_list = _resolve_unicode_font_list(
        unicode_fonts_custom_list,
        UNICODE_FONT_LIST,
        latex_font_cache,
    )
    header_footer_font = _resolve_font_config_value(
        "header/footer text",
        header_footer_font_override,
        HEADER_FOOTER_FONT_LIST,
        latex_font_cache,
        "Custom header/footer font",
    )

    logger.debug("Font configuration:")
    logger.debug(f"MAIN: {main_font}")
    logger.debug(f"MONO: {mono_font}")
    logger.debug(f"EMOJI: {emoji_font}")
    logger.debug(f"UNICODE: {', '.join(resolved_unicode_font_list)}")
    logger.debug(f"HEADER/FOOTER: {header_footer_font}")

    return LaTeXFontConfig(
        main_font=main_font,
        mono_font=mono_font,
        emoji_font=emoji_font,
        unicode_fonts=tuple(resolved_unicode_font_list),
        header_footer_font=header_footer_font,
    )


def _optional_str(options: Mapping[str, Any], key: str) -> str | None:
    value = options.get(key)
    return value if isinstance(value, str) else None


def _string_tuple(options: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = options.get(key, ())
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(item for item in value if isinstance(item, str))


def _gather_candidate_fonts(
    custom_fonts: tuple[str | None, ...],
    default_font_lists: tuple[list[str], ...],
) -> dict[str, bool]:
    candidate_fonts: set[str] = set()
    for font in custom_fonts:
        if font:
            candidate_fonts.add(font)
    for font_list in default_font_lists:
        candidate_fonts.update(font_list)
    return _font_cache_for(candidate_fonts)


def _font_cache_for(font_names: set[str]) -> dict[str, bool]:
    if not font_names:
        return {}

    checked_fonts = tuple(sorted(font_names))
    return dict(_check_fonts(checked_fonts))


@cache
def _check_fonts(font_names: tuple[str, ...]) -> tuple[tuple[str, bool], ...]:
    font_cache: dict[str, bool] = {}
    font_checks = "\n".join(
        rf"""\IfFontExistsTF{{{font}}}{{\typeout{{FONTCHECK:{font}:FOUND}}}}{{\typeout{{FONTCHECK:{font}:MISSING}}}}"""
        for font in font_names
    )
    tex_code = CHECK_FONTS_TEMPLATE.substitute(font_checks=font_checks)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_filename = "check_fonts.tex"
        tex_file_path = Path(tmpdir) / tex_filename
        lualatex_executable = shutil.which("lualatex")
        if lualatex_executable is None:
            raise RuntimeError("lualatex is not installed or not in PATH.")
        tex_file_path.write_text(tex_code, encoding="utf-8")
        try:
            result = subprocess.run(  # noqa: S603
                [
                    lualatex_executable,
                    "--interaction=nonstopmode",
                    tex_filename,
                ],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout + "\n" + result.stderr
            logger.debug(f"Batch font check output:\n{output}")
        except Exception as e:
            logger.error(
                "Error occurred while running lualatex for batch font check",
                exc_info=e,
            )
            return tuple((font, False) for font in font_names)

    for line in output.splitlines():
        if "FONTCHECK:" in line:
            try:
                marker = line.split("FONTCHECK:", 1)[1]
                font, status = marker.split(":", 1)
                font_cache[font.strip()] = status.strip() == "FOUND"
            except Exception as parse_e:
                logger.warning(
                    f"Cannot parse font status from line: {line}. Error: {parse_e}",
                )

    return tuple(font_cache.items())


def _resolve_font_config_value(
    font_role: str,
    custom_font: str | None,
    default_font_list: list[str],
    latex_font_cache: dict[str, bool],
    custom_warning_label: str,
) -> str:
    font = _first_available(default_font_list, latex_font_cache)
    if custom_font:
        font = _first_available([custom_font], latex_font_cache)
        if not font:
            logger.warning(
                f"{custom_warning_label} '{custom_font}' not found. Using default fonts.",
            )
            font = _first_available(default_font_list, latex_font_cache)

    if font:
        return font

    raise ValueError(
        f"Couldn't find any of the following fonts for {font_role}: {', '.join(default_font_list)}. Install one of these fonts to continue. See: {FONT_TROUBLESHOOTING_URL}",
    )


def _resolve_unicode_font_list(
    unicode_fonts_custom_list: list[str],
    unicode_font_list: list[str],
    latex_font_cache: dict[str, bool],
) -> list[str]:
    if unicode_fonts_custom_list:
        if all(
            latex_font_cache.get(font, False)
            for font in unicode_fonts_custom_list
        ):
            return unicode_fonts_custom_list
        logger.warning(
            f"Some of the provided unicode font(s) ('{', '.join(unicode_fonts_custom_list)}') not found. Using default fonts.",
        )

    unicode_font = _first_available(unicode_font_list, latex_font_cache)
    if unicode_font:
        return [unicode_font]

    raise ValueError(
        f'Couldn\'t find any of the following fonts for unicode text: {", ".join(unicode_font_list)}. If you don\'t have access to any of the default unicode fonts, download ({NOTO_SANS_DOWNLOAD_URL}) and specify the following Noto Sans font families:\n\nswift_book_pdf --unicode "Noto Sans" --unicode "Noto Sans SC" --unicode "Noto Sans KR" --unicode "Noto Sans Thai"\n\nSee: {FONT_TROUBLESHOOTING_URL}',
    )


def _first_available(
    font_list: list[str], latex_font_cache: dict[str, bool]
) -> str | None:
    for font in font_list:
        if latex_font_cache.get(font, False):
            logger.debug(f'Font "{font}" is accessible by LuaTeX.')
            return font
        logger.debug(f'Font "{font}" is not accessible by LuaTeX.')
    return None


def _font_context(font: str, default_fonts: list[str]) -> str:
    return "default font" if font in default_fonts else "custom font"
