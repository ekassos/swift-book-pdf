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

import re
from pathlib import Path

import click

from swift_book_pdf.book import build_epub
from swift_book_pdf.cli import (
    common_options,
    output_path_argument,
    run_build,
    version_option,
)
from swift_book_pdf.config import EPUBConfig
from swift_book_pdf.schema import OutputFormat

_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


def _validate_hex_color(
    _ctx: click.Context, _param: click.Parameter, value: str | None
) -> str | None:
    if value is None:
        return None
    if not _HEX_COLOR_RE.match(value):
        raise click.BadParameter(
            f"{value!r} is not a valid hex color (expected #RGB or #RRGGBB)."
        )
    return value


@click.command(name="swift-book-epub")
@output_path_argument
@click.option(
    "--export-cover-image",
    "-e",
    is_flag=True,
    help="Also save the generated cover image as a separate file in the output directory",
)
@click.option(
    "--base-cover-image",
    type=click.Path(
        exists=True,
        dir_okay=False,
        path_type=Path,
    ),
    default=None,
    help=(
        "Use the specified base cover image file instead of selecting one "
        "from the version string."
    ),
)
@click.option(
    "--cover-footer-line",
    type=str,
    default=None,
    help="Include the specified text in the cover image footer",
)
@click.option(
    "--cover-banner-text",
    type=str,
    default=None,
    help=(
        "Add a banner at the top of the inner cover with the given text. "
        'When the version is beta and this flag is omitted, "beta" is used.'
    ),
)
@click.option(
    "--cover-banner-color",
    type=str,
    default=None,
    callback=_validate_hex_color,
    help=(
        "Background color of the inner-cover banner as a hex string "
        "(e.g. #a5aeb0). Defaults to #a5aeb0."
    ),
)
@click.option(
    "--override-version",
    type=str,
    default=None,
    help='Override the version number. Include "beta" for beta versions.',
)
@click.option(
    "--ibooks-version",
    type=str,
    default=None,
    help="Set the ibooks:version metadata value in the generated EPUB",
)
@click.option(
    "--publisher",
    type=str,
    default=None,
    help="Set the publisher metadata field to the specified value",
)
@click.option(
    "--contributor",
    type=str,
    default=None,
    help="Include a contributor in the metadata with the specified value",
)
@click.option(
    "--dangerously-skip-legal-notices",
    is_flag=True,
    help=(
        "Omit the generated legal notices chapter. This may remove "
        "attribution, licensing, trademark, and non-affiliation "
        "disclaimers that can be required for redistribution."
    ),
)
@common_options
@version_option("Swift-Book-EPUB")
def epub(  # noqa: PLR0913
    output_path: str,
    export_cover_image: bool,
    base_cover_image: Path | None,
    cover_footer_line: str | None,
    cover_banner_text: str | None,
    cover_banner_color: str | None,
    override_version: str | None,
    ibooks_version: str | None,
    publisher: str | None,
    contributor: str | None,
    dangerously_skip_legal_notices: bool,
    input_path: str | None,
    source_ref: str | None,
    source_sha: str | None,
    verbose: bool,
) -> None:
    run_build(
        verbose=verbose,
        output_path=output_path,
        output_format=OutputFormat.EPUB,
        config_builder=lambda temp_dir, validated_output_path: EPUBConfig(
            temp_dir,
            validated_output_path,
            input_path=input_path,
            export_cover_image=export_cover_image,
            base_cover_image=base_cover_image,
            cover_footer_line=cover_footer_line,
            cover_banner_text=cover_banner_text,
            cover_banner_color=cover_banner_color,
            override_version=override_version,
            ibooks_version=ibooks_version,
            publisher=publisher,
            contributor=contributor,
            source_ref=source_ref,
            source_sha=source_sha,
            dangerously_skip_legal_notices=dangerously_skip_legal_notices,
        ),
        builder=build_epub,
    )


if __name__ == "__main__":
    epub()
