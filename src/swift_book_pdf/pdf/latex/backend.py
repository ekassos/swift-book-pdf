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

"""LaTeX PDF backend CLI and configuration adapter."""

from collections.abc import Callable, Mapping
from typing import Any

import click

from swift_book_pdf.cli.options import OptionTarget, apply_options
from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.contracts import PDFBackendConfigInput
from swift_book_pdf.pdf.fonts import FontOverrides
from swift_book_pdf.pdf.latex.config import (
    DEFAULT_TYPESETS,
    LaTeXConfig,
    LaTeXPDFConfig,
)
from swift_book_pdf.pdf.latex.fonts.config import resolve_for_latex
from swift_book_pdf.pdf.options import EngineKind

OptionDecorator = Callable[[OptionTarget], OptionTarget]


class LaTeXBackend:
    """LaTeX backend adapter for the generic PDF command."""

    kind = EngineKind.LATEX

    def build_options(self, func: OptionTarget) -> OptionTarget:
        """Add LaTeX build options."""
        return apply_options(func, _latex_options())

    def command_options(self, func: OptionTarget) -> OptionTarget:
        """Add LaTeX font options."""
        return apply_options(func, _font_options())

    def build_config(self, config_input: PDFBackendConfigInput) -> PDFConfig:
        """Build a LaTeX-backed PDF configuration."""
        backend_options = config_input.backend_options
        font_config = resolve_for_latex(
            FontOverrides(
                main_font=_optional_str(backend_options, "main"),
                mono_font=_optional_str(backend_options, "mono"),
                unicode_fonts=tuple(backend_options.get("unicode", ())),
                emoji_font=_optional_str(backend_options, "emoji"),
                header_footer_font=_optional_str(
                    backend_options, "header_footer"
                ),
            ),
        )
        latex_config = LaTeXConfig(
            font_config=font_config,
            typesets=int(backend_options["typesets"]),
        )
        return LaTeXPDFConfig(
            source=config_input.source,
            output_path=config_input.output_path,
            dangerously_skip_legal_notices=(
                config_input.dangerously_skip_legal_notices
            ),
            doc_config=config_input.doc_config,
            latex_config=latex_config,
            override_version=config_input.override_version,
        )


def _latex_options() -> tuple[OptionDecorator, ...]:
    return (
        click.option(
            "--typesets",
            type=int,
            default=DEFAULT_TYPESETS,
            help="Number of typeset passes to use",
            show_default=str(DEFAULT_TYPESETS),
        ),
    )


def _font_options() -> tuple[OptionDecorator, ...]:
    return (
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


def _optional_str(options: Mapping[str, Any], key: str) -> str | None:
    value = options.get(key)
    return value if isinstance(value, str) else None
