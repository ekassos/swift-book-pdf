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

"""minted and latexminted compatibility checks."""

import re
import shutil
import subprocess
import sys
from functools import cache
from importlib import metadata
from pathlib import Path


def parse_version(version: str) -> tuple[int, ...]:
    """Parse a version string into comparable numeric components.

    Args:
        version: Version text that may include nonnumeric separators.

    Returns:
        Numeric version components.
    """
    return tuple(int(part) for part in re.findall(r"\d+", version))


@cache
def get_installed_latexminted_version() -> str | None:
    """Return the installed `latexminted` Python package version.

    Returns:
        Installed package version, or `None` when `latexminted` is absent.
    """
    try:
        return metadata.version("latexminted")
    except metadata.PackageNotFoundError:
        return None


@cache
def get_installed_minted_sty_version() -> str | None:
    """Return the installed TeX `minted.sty` package version.

    Returns:
        Detected `minted.sty` version, or `None` when it cannot be found or
        parsed.
    """
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


@cache
def check_minted_runtime_compatibility() -> None:
    """Validate that the installed minted runtime can run with this Python.

    Raises:
        RuntimeError: If `latexminted` is missing or the installed
            `latexminted` and `minted.sty` versions are incompatible.
    """
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
