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

import os
import subprocess

from swift_book_pdf.config import Config
from swift_book_pdf.fonts import check_for_missing_font_logs
from swift_book_pdf.log import run_process_with_logs


class PDFConverter:
    def __init__(self, config: Config):
        self.local_assets_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets"
        )
        self.config = config

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
            ["lualatex", "--shell-escape", latex_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=self.config.temp_dir,
            env=env,
            bufsize=1,
        )

        run_process_with_logs(process, log_check_func=check_for_missing_font_logs)
