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

"""PDF backend helpers for the Click command surface."""

from collections.abc import Callable

import click

from swift_book_pdf.cli.options import OptionTarget, apply_options
from swift_book_pdf.pdf.backend import (
    DEFAULT_ENGINE,
    PDFBackend,
    registered_backends,
    registered_engine_kinds,
)
from swift_book_pdf.pdf.config import EngineKind
from swift_book_pdf.pdf.latex.config import DEFAULT_TYPESETS

OptionDecorator = Callable[[OptionTarget], OptionTarget]

BACKENDS = registered_backends()
BACKENDS_BY_KIND = {backend.kind: backend for backend in BACKENDS}


def engine_choices() -> list[str]:
    """Return registered engine choices for Click.

    Returns:
        Registered engine values accepted by Click.
    """
    return [engine.value for engine in registered_engine_kinds()]


def default_engine_value() -> str:
    """Return the default PDF engine value for Click.

    Returns:
        Default engine value accepted by Click.
    """
    return DEFAULT_ENGINE.value


def apply_backend_build_options(func: OptionTarget) -> OptionTarget:
    """Add build options for every registered PDF backend.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    return apply_options(func, _backend_build_options())


def apply_backend_command_options(func: OptionTarget) -> OptionTarget:
    """Add command options for every registered PDF backend.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    return apply_options(func, _backend_command_options())


def select_backend_for_cli(engine: EngineKind) -> PDFBackend:
    """Select a backend and convert registry misses into Click errors.

    Args:
        engine: Requested PDF engine.

    Returns:
        Backend adapter for the requested engine.

    Raises:
        click.ClickException: If the engine is not registered.
    """
    try:
        return BACKENDS_BY_KIND[engine]
    except KeyError as exc:
        raise click.ClickException(
            f"Unsupported PDF engine: {engine.value}"
        ) from exc


def _backend_build_options() -> tuple[OptionDecorator, ...]:
    """Return CLI build options for registered PDF engines.

    Returns:
        Build option decorators for all registered engines.
    """
    decorators: list[OptionDecorator] = []
    for engine in registered_engine_kinds():
        if engine is EngineKind.LATEX:
            decorators.extend(_latex_build_options())
    return tuple(decorators)


def _backend_command_options() -> tuple[OptionDecorator, ...]:
    """Return CLI command options for registered PDF engines.

    Returns:
        Command option decorators for all registered engines.
    """
    decorators: list[OptionDecorator] = []
    for engine in registered_engine_kinds():
        if engine is EngineKind.LATEX:
            decorators.extend(_latex_command_options())
    return tuple(decorators)


def _latex_build_options() -> tuple[OptionDecorator, ...]:
    """Return LaTeX-specific build options for the Click command.

    Returns:
        LaTeX build option decorators.
    """
    return (
        click.option(
            "--typesets",
            type=int,
            default=DEFAULT_TYPESETS,
            help="Number of typeset passes to use",
            show_default=str(DEFAULT_TYPESETS),
        ),
    )


def _latex_command_options() -> tuple[OptionDecorator, ...]:
    """Return LaTeX-specific command options for the Click command.

    Returns:
        LaTeX command option decorators.
    """
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
