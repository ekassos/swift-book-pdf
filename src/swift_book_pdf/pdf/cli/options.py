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

"""PDF-specific Click option decorators."""

import click

from swift_book_pdf.cli.options import OptionTarget, apply_options
from swift_book_pdf.pdf.options import PaperSize, RenderingMode

DEFAULT_TYPESETS = 4
GUTTER_FLAG_OPTIONS = ("--gutter/--no-gutter", " /-G")


def pdf_options(func: OptionTarget) -> OptionTarget:
    """Add PDF-specific rendering options to the command callback.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    decorators = (
        click.option(
            "--mode",
            type=click.Choice(
                [mode.value for mode in RenderingMode],
                case_sensitive=False,
            ),
            default=RenderingMode.DIGITAL.value,
            help="Rendering mode",
            show_default="digital",
        ),
        click.option(
            "--paper",
            type=click.Choice(
                [paper_size.value for paper_size in PaperSize],
                case_sensitive=False,
            ),
            default=PaperSize.LETTER.value,
            help="Paper size for the document",
            show_default="letter",
        ),
        click.option(
            "--typesets",
            type=click.IntRange(min=1),
            default=DEFAULT_TYPESETS,
            help="Number of typeset passes to use",
            show_default=str(DEFAULT_TYPESETS),
        ),
        click.option(
            "--dark", is_flag=True, help="Render the book in dark mode"
        ),
        click.option(
            *GUTTER_FLAG_OPTIONS,
            required=False,
            default=None,
            help="Enable or disable the book gutter",
        ),
        click.option(
            "--font-size",
            type=click.FloatRange(min=0, min_open=True),
            default=None,
            help="Base paragraph font size in points. All other font sizes scale proportionally",
            show_default="9",
        ),
    )
    return apply_options(func, decorators)


def pdf_font_options(func: OptionTarget) -> OptionTarget:
    """Add PDF font override options to the command callback.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    decorators = (
        click.option(
            "--main",
            type=str,
            default=None,
            help="Font for the main text",
        ),
        click.option(
            "--mono",
            type=str,
            default=None,
            help="Font for code blocks",
        ),
        click.option(
            "--unicode",
            type=str,
            default=None,
            help="Font(s) for characters not supported by the main font",
            multiple=True,
        ),
        click.option(
            "--emoji",
            type=str,
            default=None,
            help="Font for emoji",
        ),
        click.option(
            "--header-footer",
            type=str,
            default=None,
            help="Font for text in the header and footer",
        ),
    )
    return apply_options(func, decorators)
