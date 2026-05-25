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

"""PDF Click command entrypoint."""

from functools import partial

import click

import swift_book_pdf.pdf.cli.config as pdf_config
from swift_book_pdf.cli.common import run_build
from swift_book_pdf.cli.legal_notices import legal_notices_option
from swift_book_pdf.cli.options import (
    output_path_argument,
    override_version_option,
    source_options,
    version_option,
)
from swift_book_pdf.core.output import OutputFormat
from swift_book_pdf.pdf.builder import build_pdf
from swift_book_pdf.pdf.cli.options import pdf_font_options, pdf_options


@click.command(name="swift-book-pdf")
@output_path_argument
@pdf_options
@override_version_option
@pdf_font_options
@legal_notices_option
@source_options
@version_option("Swift-Book-PDF")
def pdf(  # noqa: PLR0913
    output_path: str,
    mode: str,
    paper: str,
    typesets: int,
    override_version: str | None,
    main: str | None,
    mono: str | None,
    unicode: list[str],
    emoji: str | None,
    header_footer: str | None,
    font_size: float | None,
    dark: bool,
    dangerously_skip_legal_notices: bool,
    gutter: bool | None,
    input_path: str | None,
    source_ref: str | None,
    source_sha: str | None,
    verbose: bool,
) -> None:
    """Build the PDF command from parsed Click options.

    Args:
        output_path: User-provided output path.
        mode: Rendering mode option value.
        paper: Paper size option value.
        typesets: Number of typesetting passes.
        override_version: Optional Swift version override.
        main: Optional main text font.
        mono: Optional code font.
        unicode: Optional fallback fonts for unsupported characters.
        emoji: Optional emoji font.
        header_footer: Optional header and footer font.
        font_size: Optional base paragraph font size.
        dark: Whether dark mode should be rendered.
        dangerously_skip_legal_notices: Whether generated notices are omitted.
        gutter: Optional gutter override.
        input_path: Optional local Swift Book repository path.
        source_ref: Optional Swift Book Git ref.
        source_sha: Optional Swift Book commit SHA.
        verbose: Whether debug logging should be enabled.
    """
    font_config = pdf_config.build_font_config(
        main=main,
        mono=mono,
        unicode=unicode,
        emoji=emoji,
        header_footer=header_footer,
    )
    doc_config = pdf_config.build_doc_config(
        mode=mode,
        paper=paper,
        typesets=typesets,
        dark=dark,
        gutter=gutter,
        font_size=font_size,
    )

    run_build(
        verbose=verbose,
        output_path=output_path,
        output_format=OutputFormat.PDF,
        config_builder=partial(
            pdf_config.build_pdf_config,
            font_config=font_config,
            doc_config=doc_config,
            override_version=override_version,
            source_ref=source_ref,
            source_sha=source_sha,
            input_path=input_path,
            dangerously_skip_legal_notices=dangerously_skip_legal_notices,
        ),
        builder=build_pdf,
        error_details=pdf_config.format_pdf_build_details,
    )


if __name__ == "__main__":
    pdf()
