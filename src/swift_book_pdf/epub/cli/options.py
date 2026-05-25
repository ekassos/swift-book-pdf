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

"""EPUB-specific Click option decorators."""

from pathlib import Path

import click

from swift_book_pdf.cli.options import OptionTarget, apply_options
from swift_book_pdf.epub.cli.validators import validate_hex_color


def epub_cover_options(func: OptionTarget) -> OptionTarget:
    """Add EPUB cover-generation options to the command callback.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    image_path = click.Path(exists=True, dir_okay=False, path_type=Path)
    decorators = (
        click.option(
            "--export-cover-image",
            "-e",
            is_flag=True,
            help="Also save the generated cover image as a separate file in the output directory",
        ),
        click.option(
            "--base-cover-image",
            type=image_path,
            default=None,
            help=(
                "Use the specified base cover image file instead of selecting "
                "one from the version string."
            ),
        ),
        click.option(
            "--release-cover-image",
            type=image_path,
            default=None,
            hidden=True,
        ),
        click.option(
            "--beta-cover-image",
            type=image_path,
            default=None,
            hidden=True,
        ),
        click.option(
            "--current-cover-image",
            type=image_path,
            default=None,
            hidden=True,
        ),
        click.option(
            "--nightly-cover-image",
            type=image_path,
            default=None,
            hidden=True,
        ),
        click.option(
            "--cover-footer-line",
            type=str,
            default=None,
            help="Include the specified text in the cover image footer",
        ),
        click.option(
            "--cover-banner-text",
            type=str,
            default=None,
            help=(
                "Override the banner text at the top of the inner cover. "
                'Defaults to "RELEASE VERSION" or "BETA VERSION".'
            ),
        ),
        click.option(
            "--cover-banner-color",
            type=str,
            default=None,
            callback=validate_hex_color,
            help=(
                "Background color of the inner-cover banner as a hex string "
                "(e.g. #33519e). Defaults to the selected release or beta cover color."
            ),
        ),
        click.option("--current-edition", is_flag=True, hidden=True),
        click.option("--nightly-edition", is_flag=True, hidden=True),
    )
    return apply_options(func, decorators)


def epub_metadata_options(func: OptionTarget) -> OptionTarget:
    """Add EPUB metadata override options to the command callback.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    decorators = (
        click.option(
            "--publication-identifier-seed",
            type=str,
            default=None,
            help=(
                "Override the pre-hash seed used for the EPUB publication "
                "identifier. This bypasses the default source-revision or "
                "version-derived seed."
            ),
        ),
        click.option(
            "--ibooks-version",
            type=str,
            default=None,
            help="Set the ibooks:version metadata value in the generated EPUB",
        ),
        click.option(
            "--publisher",
            type=str,
            default=None,
            help="Set the publisher metadata field to the specified value",
        ),
        click.option(
            "--contributor",
            type=str,
            default=None,
            help="Include a contributor in the metadata with the specified value",
        ),
    )
    return apply_options(func, decorators)
