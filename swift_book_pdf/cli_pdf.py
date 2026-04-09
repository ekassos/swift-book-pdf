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

import click

from swift_book_pdf.book import build_pdf
from swift_book_pdf.cli import (
    common_options,
    output_path_argument,
    run_build,
    version_option,
)
from swift_book_pdf.config import PDFConfig
from swift_book_pdf.doc import DocConfig
from swift_book_pdf.fonts import FontConfig
from swift_book_pdf.schema import OutputFormat, PaperSize, RenderingMode

DEFAULT_TYPESETS = 4


@click.command(name="swift-book-pdf")
@output_path_argument
@click.option(
    "--mode",
    type=click.Choice(
        [mode.value for mode in RenderingMode], case_sensitive=False
    ),
    default=RenderingMode.DIGITAL.value,
    help="Rendering mode",
    show_default="digital",
)
@click.option(
    "--paper",
    type=click.Choice(
        [paper_size.value for paper_size in PaperSize],
        case_sensitive=False,
    ),
    default=PaperSize.LETTER.value,
    help="Paper size for the document",
    show_default="letter",
)
@click.option(
    "--typesets",
    type=int,
    default=DEFAULT_TYPESETS,
    help="Number of typeset passes to use",
    show_default=str(DEFAULT_TYPESETS),
)
@click.option(
    "--main",
    type=str,
    default=None,
    help="Font for the main text",
)
@click.option(
    "--mono",
    type=str,
    default=None,
    help="Font for code blocks",
)
@click.option(
    "--unicode",
    type=str,
    default=None,
    help="Font(s) for characters not supported by the main font",
    multiple=True,
)
@click.option(
    "--emoji",
    type=str,
    default=None,
    help="Font for emoji",
)
@click.option(
    "--header-footer",
    type=str,
    default=None,
    help="Font for text in the header and footer",
)
@click.option(
    "--font-size",
    type=float,
    default=None,
    help="Base paragraph font size in points. All other font sizes scale proportionally",
    show_default="9",
)
@click.option("--dark", is_flag=True, help="Render the book in dark mode")
@click.option(
    "--dangerously-skip-legal-notices",
    is_flag=True,
    help=(
        "Omit the generated legal notices chapter. This may remove "
        "attribution, licensing, trademark, and non-affiliation "
        "disclaimers that can be required for redistribution."
    ),
)
@click.option(
    "--gutter/--no-gutter",
    " /-G",
    required=False,
    default=None,
    help="Enable or disable the book gutter",
)
@common_options
@version_option("Swift-Book-PDF")
def pdf(  # noqa: PLR0913
    output_path: str,
    mode: str,
    paper: str,
    typesets: int,
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
    font_config = _build_font_config(
        main=main,
        mono=mono,
        unicode=unicode,
        emoji=emoji,
        header_footer=header_footer,
    )
    doc_config = _build_doc_config(
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
        config_builder=lambda temp_dir, validated_output_path: PDFConfig(
            temp_dir,
            validated_output_path,
            font_config,
            doc_config,
            source_ref=source_ref,
            source_sha=source_sha,
            input_path=input_path,
            dangerously_skip_legal_notices=dangerously_skip_legal_notices,
        ),
        builder=build_pdf,
    )


def _build_font_config(
    *,
    main: str | None,
    mono: str | None,
    unicode: list[str],
    emoji: str | None,
    header_footer: str | None,
) -> FontConfig:
    return FontConfig(
        main_font_custom=main,
        mono_font_custom=mono,
        unicode_fonts_custom_list=unicode,
        emoji_font_custom=emoji,
        header_footer_font_custom=header_footer,
    )


def _build_doc_config(  # noqa: PLR0913
    *,
    mode: str,
    paper: str,
    typesets: int,
    dark: bool,
    gutter: bool | None,
    font_size: float | None,
) -> DocConfig:
    return DocConfig(
        RenderingMode(mode),
        PaperSize(paper),
        typesets,
        dark,
        gutter,
        font_size,
    )


if __name__ == "__main__":
    pdf()
