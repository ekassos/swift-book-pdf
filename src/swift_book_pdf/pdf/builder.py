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
from swift_book_pdf.pdf.backend import PDFBuildContext, select_engine
from swift_book_pdf.pdf.config import PDFConfig

logger = logging.getLogger(__name__)


def build_pdf(config: PDFConfig) -> None:
    """Build the PDF artifact from resolved configuration.

    Args:
        config: Resolved PDF build configuration.

    Raises:
        FileNotFoundError: If the selected engine does not produce the
            expected temporary artifact.
        RuntimeError: If the generated artifact cannot be moved to the
            requested output path.
    """
    toc = TableOfContents(
        config.root_dir,
        config.toc_file_path,
        config.temp_dir,
        include_notices=not config.dangerously_skip_legal_notices,
    )
    doc_config = config.doc_config
    artifact_label = "TeX" if config.save_tex else "PDF"
    logger.info(
        f"Creating {artifact_label} in {doc_config.mode.value} "
        f"({doc_config.appearance}) mode...",
    )
    logger.debug(f"\n{config.diagnostic_details()}")
    temp_artifact_path = select_engine(config).build(
        PDFBuildContext(config=config, toc=toc)
    )
    if not temp_artifact_path.exists():
        raise FileNotFoundError(
            f"{artifact_label} file not found: {temp_artifact_path}"
        )

    try:
        shutil.move(str(temp_artifact_path), config.output_path)
        logger.info(f"{artifact_label} saved to {config.output_path}")
    except (OSError, shutil.Error) as e:
        raise RuntimeError(
            f"Failed to save {artifact_label} to {config.output_path}"
        ) from e
