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
from collections.abc import Callable
from tempfile import TemporaryDirectory

import click

from swift_book_pdf.book import Book
from swift_book_pdf.config import Config, EPUBConfig, PDFConfig
from swift_book_pdf.doc import DocConfig
from swift_book_pdf.files import validate_output_path
from swift_book_pdf.fonts import FontConfig
from swift_book_pdf.log import configure_logging
from swift_book_pdf.schema import (
    OutputFormat,
    PaperSize,
    RenderingMode,
    RunOptions,
)

DEFAULT_TYPESETS = 4


EPUB_UNSUPPORTED_OPTION_CHECKS: tuple[
    tuple[str, Callable[[RunOptions], bool]], ...
] = (
    ("--mode", lambda options: options.mode != RenderingMode.DIGITAL.value),
    ("--paper", lambda options: options.paper != PaperSize.LETTER.value),
    ("--typesets", lambda options: options.typesets != DEFAULT_TYPESETS),
    ("--main", lambda options: options.main is not None),
    ("--mono", lambda options: options.mono is not None),
    ("--unicode", lambda options: bool(options.unicode)),
    ("--emoji", lambda options: options.emoji is not None),
    (
        "--header-footer",
        lambda options: options.header_footer is not None,
    ),
    ("--font-size", lambda options: options.font_size is not None),
    ("--dark", lambda options: options.dark),
    ("--gutter/--no-gutter", lambda options: options.gutter is not None),
)

PDF_UNSUPPORTED_OPTION_CHECKS: tuple[
    tuple[str, Callable[[RunOptions], bool]], ...
] = (
    ("--export-cover-image", lambda options: options.export_cover_image),
    (
        "--cover-footer-line",
        lambda options: options.cover_footer_line is not None,
    ),
    (
        "--override-version",
        lambda options: options.override_version is not None,
    ),
    ("--publisher", lambda options: options.publisher is not None),
)


@click.group()
def cli() -> None:
    pass


@cli.command("run")
@click.argument(
    "output_path",
    type=click.Path(resolve_path=True),
    default=".",
    required=False,
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(
        [output_format.value for output_format in OutputFormat],
        case_sensitive=False,
    ),
    default=OutputFormat.PDF.value,
    help="Output format",
    show_default="pdf",
)
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
    "--gutter/--no-gutter",
    " /-G",
    required=False,
    default=None,
    help="Enable or disable the book gutter",
)
@click.option(
    "--input-path",
    "-i",
    help="Path to the root of a local copy of the swift-book repo. If not provided, the repository will be cloned from GitHub.",
    type=click.Path(resolve_path=True),
    required=False,
)
@click.option(
    "--export-cover-image",
    "-e",
    is_flag=True,
    help="When generating an EPUB, also save the generated cover image as a separate file in the output directory",
)
@click.option(
    "--cover-footer-line",
    type=str,
    default=None,
    help="When generating an EPUB, include the specified text in the cover image footer. If not provided, no footer text will be included.",
)
@click.option(
    "--override-version",
    type=str,
    default=None,
    help='When generating an EPUB, override the version number. Include "beta" for beta versions. If not provided, the version will be determined by parsing the table of contents.',
)
@click.option(
    "--publisher",
    type=str,
    default=None,
    help="When generating an EPUB, set the publisher metadata field to the specified value. If not provided, the publisher will not be set.",
)
@click.option(
    "--contributor",
    type=str,
    default=None,
    help="When generating an EPUB, include a contributor in the metadata with the specified value. If not provided, this field will not be included.",
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
@click.version_option(
    prog_name="Swift-Book-PDF",
    message="\033[1m%(prog)s\033[0m (version \033[36m%(version)s\033[0m)",
)
def run(  # noqa: PLR0913
    output_path: str,
    output_format: str,
    mode: str,
    verbose: bool,
    typesets: int,
    paper: str,
    main: str | None,
    mono: str | None,
    unicode: list[str],
    emoji: str | None,
    header_footer: str | None,
    font_size: float | None,
    dark: bool,
    gutter: bool | None,
    input_path: str | None,
    export_cover_image: bool,
    cover_footer_line: str | None,
    override_version: str | None,
    publisher: str | None,
    contributor: str | None,
) -> None:
    configure_logging(verbose)
    logger = logging.getLogger(__name__)
    options = RunOptions(
        mode=mode,
        paper=paper,
        typesets=typesets,
        main=main,
        mono=mono,
        unicode=tuple(unicode),
        emoji=emoji,
        header_footer=header_footer,
        font_size=font_size,
        dark=dark,
        gutter=gutter,
        export_cover_image=export_cover_image,
        cover_footer_line=cover_footer_line,
        override_version=override_version,
        publisher=publisher,
        contributor=contributor,
    )

    try:
        selected_output_format = OutputFormat(output_format)
        output_path = validate_output_path(output_path, selected_output_format)
    except ValueError as e:
        logger.error(str(e))
        return

    with TemporaryDirectory() as temp:
        config: Config | None = None
        try:
            config = _build_config(
                temp,
                output_path,
                selected_output_format,
                options,
                input_path,
            )
            Book(config).process()
        except ValueError as e:
            logger.error(str(e))
        except Exception as e:
            details = _format_build_details(config)
            logger.error(
                f"Couldn't build The Swift Programming Language book: {e}{details}",
            )


def _build_config(
    temp_dir: str,
    output_path: str,
    output_format: OutputFormat,
    options: RunOptions,
    input_path: str | None,
) -> Config:
    if output_format == OutputFormat.PDF:
        unsupported_options = _find_unsupported_pdf_options(options)
        if unsupported_options:
            raise ValueError(
                "The following options are only supported for EPUB output: "
                + ", ".join(unsupported_options)
            )
        return PDFConfig(
            temp_dir,
            output_path,
            _build_font_config(options),
            _build_doc_config(options),
            input_path,
        )

    unsupported_options = _find_unsupported_epub_options(options)
    if unsupported_options:
        raise ValueError(
            "The following options are only supported for PDF output: "
            + ", ".join(unsupported_options)
        )
    return EPUBConfig(
        temp_dir,
        output_path,
        input_path,
        export_cover_image=options.export_cover_image,
        cover_footer_line=options.cover_footer_line,
        override_version=options.override_version,
        publisher=options.publisher,
        contributor=options.contributor,
    )


def _build_font_config(options: RunOptions) -> FontConfig:
    return FontConfig(
        main_font_custom=options.main,
        mono_font_custom=options.mono,
        unicode_fonts_custom_list=list(options.unicode),
        emoji_font_custom=options.emoji,
        header_footer_font_custom=options.header_footer,
    )


def _build_doc_config(options: RunOptions) -> DocConfig:
    return DocConfig(
        RenderingMode(options.mode),
        PaperSize(options.paper),
        options.typesets,
        options.dark,
        options.gutter,
        options.font_size,
    )


def _find_unsupported_epub_options(options: RunOptions) -> list[str]:
    return [
        option_name
        for option_name, check in EPUB_UNSUPPORTED_OPTION_CHECKS
        if check(options)
    ]


def _find_unsupported_pdf_options(options: RunOptions) -> list[str]:
    return [
        option_name
        for option_name, check in PDF_UNSUPPORTED_OPTION_CHECKS
        if check(options)
    ]


def _format_build_details(config: Config | None) -> str:
    if isinstance(config, PDFConfig):
        return f"\n{config.font_config}"
    return ""


if __name__ == "__main__":
    cli()
