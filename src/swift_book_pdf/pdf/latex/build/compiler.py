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
import shutil
import subprocess
import tempfile
from functools import cache
from pathlib import Path

from swift_book_pdf.core.assets import (
    IBM_PLEX_FONT_DIR,
    ICON_ASSETS_DIR,
    SWIFT_LOGO_ASSETS_DIR,
)
from swift_book_pdf.core.process import run_process_with_logs
from swift_book_pdf.pdf.latex.build.minted import (
    check_minted_runtime_compatibility,
)
from swift_book_pdf.pdf.latex.build.packages import (
    check_for_missing_latex_package_logs,
    check_required_latex_packages_installed,
)
from swift_book_pdf.pdf.latex.config import LaTeXPDFConfig
from swift_book_pdf.pdf.latex.fonts.diagnostics import (
    check_for_missing_font_logs,
)
from swift_book_pdf.pdf.latex.templating import read_latex_template

logger = logging.getLogger(__name__)
CHECK_MINTED_TEMPLATE = read_latex_template("check_minted.tex")


def check_for_missing_dependency_logs(log_line: str) -> None:
    check_for_missing_font_logs(log_line)
    check_for_missing_latex_package_logs(log_line)


class LuaLaTeXCompiler:
    def __init__(self, config: LaTeXPDFConfig) -> None:
        lualatex_executable = shutil.which("lualatex")
        if lualatex_executable is None:
            raise RuntimeError("lualatex is not installed or not in PATH.")
        self.lualatex_executable = lualatex_executable
        check_required_latex_packages_installed()
        check_minted_runtime_compatibility()
        self.local_asset_dirs = (
            str(SWIFT_LOGO_ASSETS_DIR),
            str(ICON_ASSETS_DIR),
            str(IBM_PLEX_FONT_DIR),
        )
        self.config = config

    def get_latex_command(self) -> list[str]:
        command = [self.lualatex_executable, "--interaction=nonstopmode"]

        if _does_minted_need_shell_escape(self.lualatex_executable):
            command.append("--shell-escape")
            command.append("--enable-write18")

        logger.debug(f"LaTeX Command: {command}")
        return command

    def convert_to_pdf(self, latex_file_path: str) -> None:
        env = os.environ.copy()
        expected_pdf_path = Path(latex_file_path).with_suffix(".pdf")

        env["TEXINPUTS"] = os.pathsep.join(
            [
                "",
                *self.local_asset_dirs,
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
            process, log_check_func=check_for_missing_dependency_logs
        )

        if process.returncode and not expected_pdf_path.exists():
            raise RuntimeError(
                "lualatex failed while generating the PDF. "
                "Re-run with --verbose to inspect the full TeX output."
            )


@cache
def _does_minted_need_shell_escape(lualatex_executable: str) -> bool:
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_filename = "check_minted.tex"
        tex_file_path = Path(tmpdir) / tex_filename
        tex_file_path.write_text(CHECK_MINTED_TEMPLATE, encoding="utf-8")
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
            logger.debug(f"Batch minted shell escape check output:\n{output}")
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
