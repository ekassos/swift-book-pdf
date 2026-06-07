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

"""PDF config assembly for CLI commands."""

from collections.abc import Mapping
from typing import Any

from swift_book_pdf.cli.source import resolve_cli_build_source
from swift_book_pdf.pdf.backend import PDFBackend, PDFBackendConfigInput
from swift_book_pdf.pdf.config import (
    DEFAULT_BODY_FONT_SIZE,
    DEFAULT_GUTTER,
    Appearance,
    PaperSize,
    PDFConfig,
    PDFContentSelection,
    PDFDocumentConfig,
    RenderingMode,
)


def build_doc_config(
    *,
    mode: str,
    paper: str,
    dark: bool,
    gutter: bool | None,
    font_size: float | None,
) -> PDFDocumentConfig:
    """Build PDF document layout configuration from CLI options.

    Args:
        mode: Rendering mode option value.
        paper: Paper size option value.
        dark: Whether dark mode should be rendered.
        gutter: Optional gutter override.
        font_size: Optional base paragraph font size.

    Returns:
        PDF document layout configuration.
    """
    return PDFDocumentConfig(
        mode=RenderingMode(mode),
        paper_size=PaperSize(paper),
        gutter=DEFAULT_GUTTER if gutter is None else gutter,
        font_size=(DEFAULT_BODY_FONT_SIZE if font_size is None else font_size),
        appearance=Appearance.DARK if dark else Appearance.LIGHT,
    )


def build_content_selection(
    *,
    only_toc: bool,
    only_chapter: str | None,
) -> PDFContentSelection:
    """Build the PDF content selection from CLI options.

    Args:
        only_toc: Whether to render only the table of contents page.
        only_chapter: Optional document tag or file stem for one chapter.

    Returns:
        PDF content selection.
    """
    chapter = only_chapter.strip() if only_chapter is not None else None
    return PDFContentSelection(
        only_toc=only_toc,
        only_chapter=chapter or None,
    )


def build_pdf_config(  # noqa: PLR0913
    temp_dir: str,
    output_path: str,
    *,
    backend: PDFBackend,
    doc_config: PDFDocumentConfig,
    content_selection: PDFContentSelection,
    save_tex: bool,
    intermediates_path: str | None,
    backend_options: Mapping[str, Any],
    override_version: str | None,
    source_ref: str | None,
    source_sha: str | None,
    input_path: str | None,
    dangerously_skip_legal_notices: bool,
) -> PDFConfig:
    """Build the PDF configuration from normalized CLI options.

    Args:
        temp_dir: Temporary build directory.
        output_path: Validated PDF output path.
        backend: PDF backend adapter.
        doc_config: PDF document layout configuration.
        content_selection: Requested content subset.
        save_tex: Whether to save LaTeX source instead of compiling a PDF.
        intermediates_path: Optional destination directory for build
            intermediates.
        backend_options: Backend-specific CLI option values.
        override_version: Optional Swift version override.
        source_ref: Optional Swift Book Git ref.
        source_sha: Optional Swift Book commit SHA.
        input_path: Optional local Swift Book repository path.
        dangerously_skip_legal_notices: Whether notices should be omitted.

    Returns:
        PDF builder configuration.
    """
    source = resolve_cli_build_source(
        temp_dir=temp_dir,
        input_path=input_path,
        source_ref=source_ref,
        source_sha=source_sha,
    )
    return backend.build_config(
        PDFBackendConfigInput(
            source=source,
            output_path=output_path,
            dangerously_skip_legal_notices=dangerously_skip_legal_notices,
            doc_config=doc_config,
            content_selection=content_selection,
            save_tex=save_tex,
            intermediates_path=intermediates_path,
            override_version=override_version,
            backend_options=backend_options,
        )
    )


def format_pdf_build_details(config: PDFConfig | None) -> str:
    """Format PDF-specific diagnostic details for unexpected build errors.

    Args:
        config: Partially or fully constructed PDF config.

    Returns:
        Extra log text appended to unexpected build failures.
    """
    if config is None:
        return ""
    details = config.build_error_details()
    return f"\n{details}" if details else ""
