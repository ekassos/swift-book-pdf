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

import logging
import shutil
from pathlib import Path

from tqdm import trange

from swift_book_pdf.config import Config, EPUBConfig, PDFConfig
from swift_book_pdf.epub import EPUBBuilder
from swift_book_pdf.latex import LaTeXConverter
from swift_book_pdf.notices import NOTICES_DOC_KEY, render_notices_latex
from swift_book_pdf.pdf import PDFConverter
from swift_book_pdf.preamble import generate_preamble
from swift_book_pdf.toc import TableOfContents

logger = logging.getLogger(__name__)


class PDFBookBuilder:
    def __init__(self, config: PDFConfig) -> None:
        self.config = config
        self.toc = _build_table_of_contents(config)

    def process_files_in_order(
        self,
        converter: LaTeXConverter,
        latex_file_path: str,
    ) -> None:
        latex = generate_preamble(self.config)
        # TODO: Use the version to generate a cover page
        toc_latex, _ = self.toc.generate_toc_latex(converter=converter)
        latex += toc_latex + "\n"
        for tag in self.toc.pdf_doc_tags:
            if tag.lower() == NOTICES_DOC_KEY:
                latex += render_notices_latex(
                    self.config.doc_config.mode,
                    self.config.original_work_copyright_year_range,
                )
                latex += "\n"
                continue
            file_path = None
            chapter_metadata = self.toc.chapter_metadata.get(tag.lower())
            if chapter_metadata:
                file_path = chapter_metadata.file_path
            if file_path:
                latex_content = converter.generate_latex(file_path)
                latex += latex_content + "\n"
            else:
                logger.warning(
                    f"Warning: No file found for tag <doc:{tag}>, skipping...",
                )
        latex += r"\end{document}"
        with Path(latex_file_path).open("w", encoding="utf-8") as f:
            f.write(latex)

    def build(self) -> None:
        converter = LaTeXConverter(self.config)
        latex_file_path = Path(self.config.temp_dir) / "inner_content.tex"
        self.process_files_in_order(converter, str(latex_file_path))
        logger.info(
            f"Creating PDF in {self.config.doc_config.mode.value} ({self.config.doc_config.appearance}) mode...",
        )
        pdf_converter = PDFConverter(self.config)
        for _ in trange(self.config.doc_config.typesets, leave=False):
            pdf_converter.convert_to_pdf(str(latex_file_path))

        temp_pdf_path = Path(self.config.temp_dir) / "inner_content.pdf"
        if not temp_pdf_path.exists():
            logger.error(f"PDF file not found: {temp_pdf_path}")
            return

        try:
            shutil.move(str(temp_pdf_path), self.config.output_path)
            logger.info(f"PDF saved to {self.config.output_path}")
        except (OSError, shutil.Error) as e:
            logger.error(
                f"Failed to save PDF to {self.config.output_path}: {e}"
            )


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
