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

"""LaTeX source document assembly."""

import logging
from pathlib import Path

from swift_book_pdf.core.generated.notices.metadata import NOTICES_DOC_KEY
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.latex.preamble import generate_preamble
from swift_book_pdf.pdf.latex.render.notices import render_notices_latex
from swift_book_pdf.pdf.latex.render.toc import generate_toc_latex
from swift_book_pdf.pdf.latex.renderer import LaTeXRenderer

logger = logging.getLogger(__name__)


def write_latex_document(
    config: PDFConfig,
    toc: TableOfContents,
    renderer: LaTeXRenderer,
    output_path: Path,
) -> None:
    """Write the complete LaTeX source file for a PDF build.

    Args:
        config: Resolved PDF build configuration.
        toc: Loaded Swift Book table of contents.
        renderer: Chapter renderer for source Markdown files.
        output_path: Destination ``.tex`` file path.
    """
    latex = generate_preamble(config)
    toc_latex, _ = generate_toc_latex(toc, renderer)
    latex += toc_latex + "\n"

    for tag in toc.doc_tags:
        if tag.lower() == NOTICES_DOC_KEY:
            latex += render_notices_latex(
                config.doc_config.mode,
                config.original_work_copyright_year_range,
            )
            latex += "\n"
            continue

        chapter_metadata = toc.chapter_metadata.get(tag.lower())
        if chapter_metadata is None or chapter_metadata.file_path is None:
            logger.warning(
                f"Warning: No file found for tag <doc:{tag}>, skipping...",
            )
            continue

        latex += renderer.render_file(chapter_metadata.file_path) + "\n"

    latex += r"\end{document}"
    output_path.write_text(latex, encoding="utf-8")
