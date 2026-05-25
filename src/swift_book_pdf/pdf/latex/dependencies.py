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

"""LaTeX runtime dependency checks."""

import logging
import re
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

from swift_book_pdf.pdf.latex.fonts import check_for_missing_font_logs

logger = logging.getLogger(__name__)

REQUIRED_LATEX_PACKAGES = (
    "fontspec",
    "xcolor",
    "graphicx",
    "fancyhdr",
    "geometry",
    "adjustbox",
    "ifoddpage",
    "enumitem",
    "listings",
    "minted",
    "tcolorbox",
    "tikz",
    "needspace",
    "textcomp",
    "hyperref",
    "parskip",
    "tabulary",
    "ragged2e",
    "footmisc",
    "lua-ul",
)
MISSING_TEX_FILE_PATTERN = re.compile(
    r"! LaTeX Error: File [`'](?P<filename>[^`']+)['`] not found\."
)


def parse_version(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version))


def get_installed_latexminted_version() -> str | None:
    try:
        return metadata.version("latexminted")
    except metadata.PackageNotFoundError:
        return None


def get_installed_minted_sty_version() -> str | None:
    kpsewhich = shutil.which("kpsewhich")
    if kpsewhich is None:
        return None

    try:
        minted_sty_path = subprocess.run(  # noqa: S603
            [kpsewhich, "minted.sty"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        return None

    content = Path(minted_sty_path).read_text(encoding="utf-8")
    match = re.search(r"\[[0-9]{4}/[0-9]{2}/[0-9]{2} v([0-9.]+) ", content)
    return match.group(1) if match else None


def check_minted_runtime_compatibility() -> None:
    latexminted_executable = shutil.which("latexminted")
    latexminted_version = get_installed_latexminted_version()
    minted_sty_version = get_installed_minted_sty_version()

    if latexminted_executable is None or latexminted_version is None:
        raise RuntimeError(
            "latexminted is not installed or not available on PATH. "
            "Install the project dependencies before generating PDFs.",
        )

    if sys.version_info >= (3, 14) and parse_version(latexminted_version) < (
        0,
        7,
        1,
    ):
        raise RuntimeError(
            f"latexminted {latexminted_version} is incompatible with Python "
            f"{sys.version_info.major}.{sys.version_info.minor}. "
            "Use Python 3.13 or earlier, or install latexminted >= 0.7.1.",
        )

    if (
        minted_sty_version is not None
        and parse_version(latexminted_version) >= (0, 7, 1)
        and parse_version(minted_sty_version) < (3, 8, 0)
    ):
        raise RuntimeError(
            f"latexminted {latexminted_version} requires minted.sty >= 3.8.0, "
            f"but TeX provides minted.sty {minted_sty_version}. "
            "Upgrade TeX Live/minted or use Python 3.13 or earlier so the "
            "project can install latexminted 0.6.x instead.",
        )


def _format_missing_latex_packages_error(
    package_names: list[str], *, from_logs: bool = False
) -> str:
    unique_package_names = list(dict.fromkeys(package_names))
    if len(unique_package_names) == 1:
        package_list = (
            f"the required LaTeX package '{unique_package_names[0]}'"
        )
        install_hint = f"Install it with your TeX package manager (for TeX Live: tlmgr install {unique_package_names[0]})."
    else:
        package_list = "required LaTeX packages: " + ", ".join(
            f"'{package_name}'" for package_name in unique_package_names
        )
        install_hint = (
            "Install them with your TeX package manager "
            f"(for TeX Live: tlmgr install {' '.join(unique_package_names)})."
        )

    detection_hint = (
        "TeX reported that it could not find "
        if from_logs
        else "Your TeX installation is missing "
    )

    return (
        f"{detection_hint}{package_list} "
        f"{install_hint} On MiKTeX, install the missing package(s) from "
        "MiKTeX Console or install a fuller TeX distribution."
    )


def _extract_missing_latex_package_name(log_line: str) -> str | None:
    match = MISSING_TEX_FILE_PATTERN.search(log_line)
    if not match:
        return None

    missing_file = match.group("filename")
    if missing_file.endswith(".sty"):
        return missing_file.removesuffix(".sty")

    return missing_file


def check_for_missing_latex_package_logs(log_line: str) -> None:
    package_name = _extract_missing_latex_package_name(log_line)
    if package_name:
        raise RuntimeError(
            _format_missing_latex_packages_error(
                [package_name], from_logs=True
            )
        )


def check_required_latex_packages_installed() -> None:
    kpsewhich = shutil.which("kpsewhich")
    if kpsewhich is None:
        logger.debug(
            "kpsewhich is not available; skipping LaTeX package preflight check."
        )
        return

    missing_packages: list[str] = []
    for package_name in REQUIRED_LATEX_PACKAGES:
        result = subprocess.run(  # noqa: S603
            [kpsewhich, f"{package_name}.sty"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            missing_packages.append(package_name)

    if missing_packages:
        raise RuntimeError(
            _format_missing_latex_packages_error(missing_packages)
        )


def check_for_missing_dependency_logs(log_line: str) -> None:
    check_for_missing_font_logs(log_line)
    check_for_missing_latex_package_logs(log_line)
