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

"""LuaTeX-backed font discovery helpers."""

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from swift_book_pdf.pdf.latex.templating import load_latex_template

logger = logging.getLogger(__name__)

CHECK_FONTS_TEMPLATE = load_latex_template("check_fonts.tex")


def batch_check_fonts(font_names: list[str]) -> dict[str, bool]:
    """Check font availability in one LuaLaTeX run."""
    if not font_names:
        return {}

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
            return dict.fromkeys(font_names, False)

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

    return font_cache


def find_font(
    font_list: list[str], latex_font_cache: dict[str, bool]
) -> str | None:
    """Return the first available font from `font_list`."""
    for font in font_list:
        if latex_font_cache.get(font, False):
            logger.debug(f'Font "{font}" is accessible by LuaTeX.')
            return font
        logger.debug(f'Font "{font}" is not accessible by LuaTeX.')
    return None


def find_all_fonts(
    font_list: list[str], latex_font_cache: dict[str, bool]
) -> bool:
    """Return whether all fonts in `font_list` are available."""
    for font in font_list:
        if latex_font_cache.get(font, False):
            logger.debug(f'Font "{font}" is accessible by LuaTeX.')
        else:
            logger.info(f'Font "{font}" is not accessible by LuaTeX.')
            return False
    return True


def gather_all_candidate_fonts(
    custom_fonts: list[str | None],
    default_font_lists: list[list[str]],
) -> dict[str, bool]:
    """Collect custom and default font names, then batch-check them."""
    candidate_fonts: set[str] = set()
    for font in custom_fonts:
        if font:
            candidate_fonts.add(font)
    for font_list in default_font_lists:
        candidate_fonts.update(font_list)
    if candidate_fonts:
        return batch_check_fonts(list(candidate_fonts))
    return {}
