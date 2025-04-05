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
import shutil
from swift_book_pdf.doc import DocConfig
from swift_book_pdf.files import find_or_clone_swift_book_repo
from swift_book_pdf.fonts import FontConfig

logger = logging.getLogger(__name__)


class Config:
    def __init__(
        self,
        temp_dir_path: str,
        output_path: str,
        font_config: FontConfig,
        doc_config: DocConfig,
        input_path: str | None = None,
    ):
        if not shutil.which("git"):
            raise RuntimeError("Git is not installed or not in PATH.")

        self.temp_dir = temp_dir_path

        file_paths = find_or_clone_swift_book_repo(temp_dir_path, input_path)

        self.root_dir = file_paths.root_dir
        self.toc_file_path = file_paths.toc_file_path
        self.assets_dir = file_paths.assets_dir
        self.output_path = output_path
        self.font_config = font_config
        self.doc_config = doc_config
        logger.debug(f"Swift book repository directory: {self.root_dir}")
        logger.debug(f"Assets directory: {self.assets_dir}")
        logger.debug(f"Output path: {self.output_path}")
        logger.debug(f"Font configuration: {self.font_config}")
        logger.debug(f"Document configuration: {self.doc_config}")
        logger.debug(f"Temporary directory: {self.temp_dir}")
        logger.debug(f"Table of contents file path: {self.toc_file_path}")
