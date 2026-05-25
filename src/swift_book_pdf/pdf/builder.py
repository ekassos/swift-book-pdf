# Copyright 2026 Evangelos Kassos
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

"""Top-level orchestration for building PDF artifacts."""

import logging
import shutil

from swift_book_pdf.core.markdown import resolve_version_info
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.engine import PDFBuildContext, select_engine

logger = logging.getLogger(__name__)


def build_pdf(config: PDFConfig) -> None:
    """Build the PDF artifact from resolved configuration.

    Args:
        config: Resolved PDF build configuration.
    """
    toc = TableOfContents(
        config.root_dir,
        config.toc_file_path,
        config.temp_dir,
        include_notices=not config.dangerously_skip_legal_notices,
    )
    PDFBookBuilder(config, toc).build()


class PDFBookBuilder:
    """Build a PDF by delegating engine-specific rendering and compilation."""

    def __init__(self, config: PDFConfig, toc: TableOfContents) -> None:
        self.config = config
        self.toc = toc

    def build(self) -> None:
        """Render and compile the configured PDF artifact."""
        doc_config = self.config.doc_config
        logger.info(
            f"Creating PDF in {doc_config.mode.value} "
            f"({doc_config.appearance}) mode...",
        )
        logger.debug(f"\n{doc_config}")
        context = PDFBuildContext(
            config=self.config,
            toc=self.toc,
            version_info=resolve_version_info(
                self.toc.file_content, self.config.override_version
            ),
        )
        temp_pdf_path = select_engine(self.config).build(context)
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
