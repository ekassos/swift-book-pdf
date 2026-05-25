# Copyright 2025-2026 Evangelos Kassos
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

from swift_book_pdf.config import Config, EPUBConfig, PDFConfig
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.epub import EPUBBuilder
from swift_book_pdf.pdf.builder import PDFBookBuilder


def build_pdf(config: PDFConfig) -> None:
    PDFBookBuilder(config).build()


def build_epub(config: EPUBConfig) -> None:
    toc = _build_table_of_contents(config)
    EPUBBuilder(config, toc).build()


def _build_table_of_contents(config: Config) -> TableOfContents:
    return TableOfContents(
        config.root_dir,
        config.toc_file_path,
        config.temp_dir,
        include_notices=not config.dangerously_skip_legal_notices,
    )
