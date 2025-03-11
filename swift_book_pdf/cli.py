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

from tempfile import TemporaryDirectory
import click
import logging

from swift_book_pdf.book import Book
from swift_book_pdf.config import Config
from swift_book_pdf.files import validate_output_path
from swift_book_pdf.schema import RenderingMode

logger = logging.getLogger(__name__)


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
@click.option("--mode", type=click.Choice(["print", "digital"]), default="digital")
@click.option("--verbose", is_flag=True)
@click.option("--typesets", type=int, default=4)
def run(output_path: str, mode: str, verbose: bool, typesets: int) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO, format="%(message)s"
    )
    try:
        output_path = validate_output_path(output_path, logger)
    except ValueError as e:
        logger.error(str(e))
        return

    with TemporaryDirectory() as temp:
        config = Config(temp, output_path, RenderingMode(mode), logger, typesets)
        Book(config).process()


if __name__ == "__main__":
    cli()
