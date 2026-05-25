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
from pathlib import Path

from swift_book_pdf.core.assets import (
    IBM_PLEX_FONT_DIR,
    ICON_ASSETS_DIR,
    SWIFT_LOGO_ASSETS_DIR,
)
from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.latex.dependencies import (
    check_for_missing_dependency_logs,
    check_minted_runtime_compatibility,
    check_required_latex_packages_installed,
)
from swift_book_pdf.pdf.process import run_process_with_logs

logger = logging.getLogger(__name__)


class LuaLaTeXCompiler:
    def __init__(self, config: PDFConfig) -> None:
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
        self.local_assets_dir = self.local_asset_dirs[0]
        self.config = config

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
