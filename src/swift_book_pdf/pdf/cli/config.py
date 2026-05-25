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

from swift_book_pdf.cli.source import resolve_cli_build_source
from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.doc import DocConfig
from swift_book_pdf.pdf.fonts import FontConfig
from swift_book_pdf.pdf.options import PaperSize, RenderingMode


def build_font_config(
    *,
    main: str | None,
    mono: str | None,
    unicode: list[str],
    emoji: str | None,
    header_footer: str | None,
) -> FontConfig:
    """Build PDF font configuration from CLI options.

    Args:
        main: Optional main text font.
        mono: Optional code font.
        unicode: Optional fallback fonts for unsupported characters.
        emoji: Optional emoji font.
        header_footer: Optional header and footer font.

    Returns:
        PDF font configuration.
    """
    return FontConfig(
        main_font_custom=main,
        mono_font_custom=mono,
        unicode_fonts_custom_list=unicode,
        emoji_font_custom=emoji,
        header_footer_font_custom=header_footer,
    )


def build_doc_config(  # noqa: PLR0913
    *,
    mode: str,
    paper: str,
    typesets: int,
    dark: bool,
    gutter: bool | None,
    font_size: float | None,
) -> DocConfig:
    """Build PDF document layout configuration from CLI options.

    Args:
        mode: Rendering mode option value.
        paper: Paper size option value.
        typesets: Number of typesetting passes.
        dark: Whether dark mode should be rendered.
        gutter: Optional gutter override.
        font_size: Optional base paragraph font size.

    Returns:
        PDF document layout configuration.
    """
    return DocConfig(
        RenderingMode(mode),
        PaperSize(paper),
        typesets,
        dark,
        gutter,
        font_size,
    )


def build_pdf_config(  # noqa: PLR0913
    temp_dir: str,
    output_path: str,
    *,
    font_config: FontConfig,
    doc_config: DocConfig,
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
        font_config: PDF font configuration.
        doc_config: PDF document layout configuration.
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
    return PDFConfig(
        source=source,
        output_path=output_path,
        dangerously_skip_legal_notices=dangerously_skip_legal_notices,
        font_config=font_config,
        doc_config=doc_config,
        override_version=override_version,
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
    return f"\n{config.font_config}"
