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
import subprocess
import tempfile

from swift_book_pdf.config import Config
from swift_book_pdf.fonts import check_for_missing_font_logs
from swift_book_pdf.log import run_process_with_logs

logger = logging.getLogger(__name__)


class PDFConverter:
    def __init__(self, config: Config):
        self.local_assets_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets"
        )
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

    def get_latex_command(self) -> list[str]:
        command = ["lualatex", "--interaction=nonstopmode"]

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
            ]
        )

        process = subprocess.Popen(
            self.get_latex_command() + [latex_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=self.config.temp_dir,
            env=env,
            bufsize=1,
        )

        run_process_with_logs(process, log_check_func=check_for_missing_font_logs)
