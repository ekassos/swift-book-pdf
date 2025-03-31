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

    def get_latex_command(self) -> list[str]:
        command = ["lualatex"]

        pattern = r"(TeX Live|MiKTeX) (\d{2,4})"

        result = subprocess.run(
            ["lualatex", "--version"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to get LaTeX version: {result.stderr}")

        match = re.search(pattern, result.stdout)
        if match:
            tex_distribution = match.group(1)
            tex_version = match.group(2)

            if tex_distribution == "TeX Live":
                if int(tex_version) < 2024:
                    command.append("--shell-escape")
                    command.append("--enable-write18")
            elif tex_distribution == "MiKTeX":
                command.append("--shell-escape")
                command.append("--enable-write18")
            else:
                raise RuntimeError(
                    f"Unsupported LaTeX distribution: {tex_distribution}"
                )
        else:
            raise RuntimeError(f"Failed to get LaTeX version: {result.stderr}")
        logger.debug(
            f"Using LaTeX distribution: {tex_distribution}, version: {tex_version}"
        )
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
