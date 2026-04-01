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
from swift_book_pdf.files import (
    find_or_clone_swift_book_repo,
    find_swift_book_copyright_year_range,
)
from swift_book_pdf.fonts import FontConfig
from swift_book_pdf.schema import OutputFormat

logger = logging.getLogger(__name__)


class Config:
    output_format: OutputFormat

    def __init__(
        self,
        temp_dir_path: str,
        output_path: str,
        source_ref: str | None = None,
        source_sha: str | None = None,
        input_path: str | None = None,
    ) -> None:
        if not shutil.which("git"):
            raise RuntimeError("Git is not installed or not in PATH.")

        self.temp_dir = temp_dir_path

        file_paths = find_or_clone_swift_book_repo(
            temp_dir_path,
            input_path,
            source_ref=source_ref,
            source_sha=source_sha,
        )

        self.root_dir = file_paths.root_dir
        self.toc_file_path = file_paths.toc_file_path
        self.assets_dir = file_paths.assets_dir
        self.output_path = output_path
        self.original_work_copyright_year_range = (
            find_swift_book_copyright_year_range(self.root_dir)
        )
        logger.debug(f"Swift book repository directory: {self.root_dir}")
        logger.debug(f"Assets directory: {self.assets_dir}")
        logger.debug(f"Output path: {self.output_path}")
        logger.debug(f"Temporary directory: {self.temp_dir}")
        logger.debug(f"Table of contents file path: {self.toc_file_path}")
        logger.debug(
            "Swift book copyright year range: %s",
            self.original_work_copyright_year_range,
        )


class PDFConfig(Config):
    output_format = OutputFormat.PDF

    def __init__(  # noqa: PLR0913
        self,
        temp_dir_path: str,
        output_path: str,
        font_config: FontConfig,
        doc_config: DocConfig,
        source_ref: str | None = None,
        source_sha: str | None = None,
        input_path: str | None = None,
    ) -> None:
        super().__init__(
            temp_dir_path,
            output_path,
            source_ref=source_ref,
            source_sha=source_sha,
            input_path=input_path,
        )
        self.font_config = font_config
        self.doc_config = doc_config
        logger.debug(f"Output format: {self.output_format}")
        logger.debug(f"Font configuration: {self.font_config}")
        logger.debug(f"Document configuration: {self.doc_config}")


class EPUBConfig(Config):
    output_format = OutputFormat.EPUB

    def __init__(  # noqa: PLR0913
        self,
        temp_dir_path: str,
        output_path: str,
        input_path: str | None = None,
        export_cover_image: bool = False,
        cover_footer_line: str | None = None,
        override_version: str | None = None,
        ibooks_version: str | None = None,
        publisher: str | None = None,
        contributor: str | None = None,
        source_ref: str | None = None,
        source_sha: str | None = None,
    ) -> None:
        super().__init__(
            temp_dir_path,
            output_path,
            source_ref=source_ref,
            source_sha=source_sha,
            input_path=input_path,
        )
        self.export_cover_image = export_cover_image
        self.cover_footer_line = cover_footer_line
        self.override_version = override_version
        self.ibooks_version = ibooks_version
        self.publisher = publisher
        self.contributor = contributor
        logger.debug(f"Output format: {self.output_format}")
        logger.debug(
            f"Save generated cover image as separate file: {export_cover_image}"
        )
        logger.debug(f"Cover footer line: {cover_footer_line}")
        logger.debug(f"Version override: {override_version}")
        logger.debug(f"Apple Books version metadata: {ibooks_version}")
        logger.debug(f"Publisher: {publisher}")
        logger.debug(f"Contributor: {contributor}")
