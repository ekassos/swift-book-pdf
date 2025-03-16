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
from swift_book_pdf.doc import DocConfig
from swift_book_pdf.files import clone_swift_book_repo
from swift_book_pdf.fonts import FontConfig

logger = logging.getLogger(__name__)


class Config:
    def __init__(
        self,
        input_path: str,
        output_path: str,
        font_config: FontConfig,
        doc_config: DocConfig,
    ):
        if not shutil.which("git"):
            raise RuntimeError("Git is not installed or not in PATH.")

        self.temp_dir = input_path

        logger.info("Downloading TSPL files...")
        clone_swift_book_repo(input_path)
        self.root_dir = os.path.join(input_path, "swift-book/TSPL.docc/")

        self.toc_file_path = os.path.join(
            self.root_dir, "The-Swift-Programming-Language.md"
        )
        if not os.path.exists(self.toc_file_path):
            raise FileNotFoundError(
                f"Couldn't find the Table of Contents file (The-Swift-Programming-Language.md) in {self.root_dir}."
            )

        self.assets_dir = os.path.join(self.root_dir, "Assets/")
        if not os.path.exists(self.assets_dir):
            raise FileNotFoundError(
                f"Couldn't find the Assets directory ({self.assets_dir})."
            )

        self.output_path = output_path
        self.font_config = font_config
        self.doc_config = doc_config
