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
import shutil
import subprocess
import sys
import tempfile
from importlib import metadata
from pathlib import Path

from swift_book_pdf.config import Config
from swift_book_pdf.fonts import check_for_missing_font_logs
from swift_book_pdf.log import run_process_with_logs

logger = logging.getLogger(__name__)


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


class PDFConverter:
    def __init__(self, config: Config) -> None:
        check_minted_runtime_compatibility()
        self.local_assets_dir = str(Path(__file__).resolve().parent / "assets")
        self.config = config
        lualatex_executable = shutil.which("lualatex")
        if lualatex_executable is None:
            raise RuntimeError("lualatex is not installed or not in PATH.")
        self.lualatex_executable = lualatex_executable

    def does_minted_need_shell_escape(self) -> bool:
        """
        Check if minted package needs shell escape by running a test LaTeX document.
        Returns True if shell escape is needed, False otherwise.
        """
        tex_code = r"""
        \documentclass{article}
        \usepackage{minted}
        \usepackage[svgnames]{xcolor}
        \begin{document}
        \begin{minted}[bgcolor=Beige, bgcolorpadding=0.5em]{c}
        int main() {
        printf("hello, world");
        return 0;
        }
        \end{minted}
        \end{document}
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_filename = "check_minted.tex"
            tex_file_path = Path(tmpdir) / tex_filename
            with tex_file_path.open("w", encoding="utf-8") as tex_file:
                tex_file.write(tex_code)
            try:
                result = subprocess.run(  # noqa: S603
                    [
                        self.lualatex_executable,
                        "--interaction=nonstopmode",
                        tex_filename,
                    ],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                output = result.stdout + "\n" + result.stderr
                logger.debug(
                    f"Batch minted shell escape check output:\n{output}"
                )
            except Exception as e:
                logger.error(
                    "Error occurred while running lualatex for minted shell escape check",
                    exc_info=e,
                )
                return True

        if (
            "Package minted Error: You must invoke LaTeX with the -shell-escape flag."
            in output
        ):
            logger.debug("Minted package requires shell escape.")
            return True
        logger.debug("Minted package does not require shell escape.")
        return False

    def get_latex_command(self) -> list[str]:
        command = [self.lualatex_executable, "--interaction=nonstopmode"]

        if self.does_minted_need_shell_escape():
            command.append("--shell-escape")
            command.append("--enable-write18")

        logger.debug(f"LaTeX Command: {command}")
        return command

    def convert_to_pdf(self, latex_file_path: str) -> None:
        env = os.environ.copy()

        env["TEXINPUTS"] = os.pathsep.join(
            [
                "",
                self.local_assets_dir,
                env.get("TEXINPUTS", ""),
            ],
        )

        process = subprocess.Popen(  # noqa: S603
            [*self.get_latex_command(), latex_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=self.config.temp_dir,
            env=env,
            bufsize=1,
        )

        run_process_with_logs(
            process, log_check_func=check_for_missing_font_logs
        )
