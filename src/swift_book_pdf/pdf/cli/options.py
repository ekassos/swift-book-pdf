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
from swift_book_pdf.pdf.config import (
    DEFAULT_BODY_FONT_SIZE,
    DEFAULT_PAPER_SIZE,
    DEFAULT_RENDERING_MODE,
    PaperSize,
    RenderingMode,
)

GUTTER_FLAG_OPTIONS = ("--gutter/--no-gutter", " /-G")


def pdf_document_options(func: OptionTarget) -> OptionTarget:
    """Add PDF document options to the command callback.

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
            default=DEFAULT_RENDERING_MODE.value,
            help="Rendering mode",
            show_default=DEFAULT_RENDERING_MODE.value,
        ),
        click.option(
            "--paper",
            type=click.Choice(
                [paper_size.value for paper_size in PaperSize],
                case_sensitive=False,
            ),
            default=DEFAULT_PAPER_SIZE.value,
            help="Paper size for the document",
            show_default=DEFAULT_PAPER_SIZE.value,
        ),
    )
    return apply_options(func, decorators)


def pdf_output_options(func: OptionTarget) -> OptionTarget:
    """Add PDF output artifact options to the command callback.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    decorators = (
        click.option(
            "--save-tex",
            is_flag=True,
            help="Save the generated LaTeX source instead of compiling a PDF",
        ),
    )
    return apply_options(func, decorators)


def pdf_typography_options(func: OptionTarget) -> OptionTarget:
    """Add PDF typography options to the command callback.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    decorators = (
        click.option(
            "--font-size",
            type=float,
            default=None,
            help="Base paragraph font size in points. All other font sizes scale proportionally",
            show_default=f"{DEFAULT_BODY_FONT_SIZE:g}",
        ),
    )
    return apply_options(func, decorators)


def pdf_appearance_options(func: OptionTarget) -> OptionTarget:
    """Add PDF appearance options to the command callback.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    decorators = (
        click.option(
            "--dark", is_flag=True, help="Render the book in dark mode"
        ),
    )
    return apply_options(func, decorators)


def pdf_gutter_option(func: OptionTarget) -> OptionTarget:
    """Add the PDF gutter toggle to the command callback.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    decorators = (
        click.option(
            *GUTTER_FLAG_OPTIONS,
            required=False,
            default=None,
            help="Enable or disable the book gutter",
        ),
    )
    return apply_options(func, decorators)
