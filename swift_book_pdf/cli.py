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
    "--size",
    type=click.Choice([size.value for size in PaperSize], case_sensitive=False),
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
@click.option("--verbose", is_flag=True)
def run(output_path: str, mode: str, verbose: bool, typesets: int, size: str) -> None:
    configure_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        output_path = validate_output_path(output_path)
        font_config = FontConfig()
        font_config.check_font_availability()
        doc_config = DocConfig(RenderingMode(mode), PaperSize(size), typesets)
    except ValueError as e:
        logger.error(str(e))
        return

    with TemporaryDirectory() as temp:
        config = Config(temp, output_path, doc_config)
        Book(config).process()


if __name__ == "__main__":
    cli()
