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
from pathlib import Path

from tqdm import trange

from swift_book_pdf.config import Config, EPUBConfig, PDFConfig
from swift_book_pdf.latex import LaTeXConverter
from swift_book_pdf.pdf import PDFConverter
from swift_book_pdf.preamble import generate_preamble
from swift_book_pdf.toc import TableOfContents

logger = logging.getLogger(__name__)


class Book:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.toc = TableOfContents(
            config.root_dir,
            config.toc_file_path,
            config.temp_dir,
        )

    def process_files_in_order(
        self,
        converter: LaTeXConverter,
        config: PDFConfig,
        latex_file_path: str,
    ) -> None:
        latex = generate_preamble(config)
        # TODO: Use the version to generate a cover page
        toc_latex, _ = self.toc.generate_toc_latex(converter=converter)
        latex += toc_latex + "\n"
        for tag in self.toc.doc_tags:
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

    def process(self) -> None:
        if isinstance(self.config, EPUBConfig):
            from swift_book_pdf.epub import EPUBBuilder

            EPUBBuilder(self.config, self.toc).build()
            return

        if not isinstance(self.config, PDFConfig):
            raise TypeError("Book requires a PDFConfig or EPUBConfig.")
        self._process_pdf(self.config)

    def _process_pdf(self, config: PDFConfig) -> None:
        converter = LaTeXConverter(config)
        latex_file_path = Path(config.temp_dir) / "inner_content.tex"
        self.process_files_in_order(converter, config, str(latex_file_path))
        logger.info(
            f"Creating PDF in {config.doc_config.mode.value} ({config.doc_config.appearance}) mode...",
        )
        pdf_converter = PDFConverter(config)
        for _ in trange(config.doc_config.typesets, leave=False):
            pdf_converter.convert_to_pdf(str(latex_file_path))

        temp_pdf_path = Path(config.temp_dir) / "inner_content.pdf"
        if not temp_pdf_path.exists():
            logger.error(f"PDF file not found: {temp_pdf_path}")
            return

        try:
            shutil.move(str(temp_pdf_path), config.output_path)
            logger.info(f"PDF saved to {config.output_path}")
        except (OSError, shutil.Error) as e:
            logger.error(f"Failed to save PDF to {config.output_path}: {e}")
