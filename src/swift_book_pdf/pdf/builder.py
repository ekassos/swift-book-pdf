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

from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.contracts import PDFBuildContext
from swift_book_pdf.pdf.registry import select_engine

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
    doc_config = config.doc_config
    logger.info(
        f"Creating PDF in {doc_config.mode.value} "
        f"({doc_config.appearance}) mode...",
    )
    logger.debug(f"\n{config.diagnostic_details()}")
    temp_pdf_path = select_engine(config).build(
        PDFBuildContext(config=config, toc=toc)
    )
    if not temp_pdf_path.exists():
        logger.error(f"PDF file not found: {temp_pdf_path}")
        return

    try:
        shutil.move(str(temp_pdf_path), config.output_path)
        logger.info(f"PDF saved to {config.output_path}")
    except (OSError, shutil.Error) as e:
        logger.error(f"Failed to save PDF to {config.output_path}: {e}")
