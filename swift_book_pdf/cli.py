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

import importlib
from typing import Optional
import click
import logging

from tempfile import TemporaryDirectory

from swift_book_pdf.book import Book
from swift_book_pdf.config import Config
from swift_book_pdf.doc import DocConfig
from swift_book_pdf.files import validate_output_path
from swift_book_pdf.fonts import FontConfig
from swift_book_pdf.log import configure_logging
from swift_book_pdf.schema import PaperSize, RenderingMode


@click.group()
def cli() -> None:
    pass


@cli.command("run")
@click.argument(
    "output_path",
    type=click.Path(resolve_path=True),
    default="./swift-book.pdf",
    required=False,
)
@click.option(
    "--mode",
    type=click.Choice([mode.value for mode in RenderingMode], case_sensitive=False),
    default=RenderingMode.DIGITAL.value,
    help="Rendering mode",
    show_default="digital",
)
@click.option(
    "--paper",
    type=click.Choice(
        [paper_size.value for paper_size in PaperSize], case_sensitive=False
    ),
    default=PaperSize.LETTER.value,
    help="Paper size for the document",
    show_default="letter",
)
@click.option(
    "--typesets",
    type=int,
    default=4,
    help="Number of typeset passes to use",
    show_default="4",
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
@click.option("--dark", is_flag=True, help="Render the book in dark mode")
@click.option(
    "--input-path",
    "-i",
    help="Path to the root of a local copy of the swift-book repo. If not provided,\
        the repository will be cloned from GitHub.",
    type=click.Path(resolve_path=True),
    required=False,
)
@click.option(
    "--gutter/--no-gutter",
    " /-G",
    required=False,
    default=None,
    help="Enable or disable the book gutter",
)
@click.option("--verbose", is_flag=True)
@click.option("--version", is_flag=True)
def run(
    output_path: str,
    mode: str,
    verbose: bool,
    typesets: int,
    paper: str,
    main: Optional[str],
    mono: Optional[str],
    unicode: list[str],
    emoji: Optional[str],
    header_footer: Optional[str],
    dark: bool,
    version: bool,
    gutter: bool | None = None,
    input_path: Optional[str] = None,
) -> None:
    if version:
        current_version = importlib.metadata.version("swift-book-pdf")
        click.echo(f"swift-book-pdf {current_version}")
        return

    configure_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        output_path = validate_output_path(output_path)
        font_config = FontConfig(
            main_font_custom=main,
            mono_font_custom=mono,
            unicode_fonts_custom_list=unicode,
            emoji_font_custom=emoji,
            header_footer_font_custom=header_footer,
        )
        doc_config = DocConfig(
            RenderingMode(mode), PaperSize(paper), typesets, dark, gutter
        )
    except ValueError as e:
        logger.error(str(e))
        return

    with TemporaryDirectory() as temp:
        config = Config(temp, output_path, font_config, doc_config, input_path)
        try:
            Book(config).process()
        except Exception as e:
            logger.error(
                f"Couldn't build The Swift Programming Language book: {e}\n{font_config}"
            )


if __name__ == "__main__":
    cli()
