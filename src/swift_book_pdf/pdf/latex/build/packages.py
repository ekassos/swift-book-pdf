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

"""Required LaTeX package checks."""

import logging
import re
import shutil
import subprocess
from functools import cache

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


def check_for_missing_latex_package_logs(log_line: str) -> None:
    package_name = _extract_missing_latex_package_name(log_line)
    if package_name:
        raise RuntimeError(
            _format_missing_latex_packages_error(
                [package_name], from_logs=True
            )
        )


@cache
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
