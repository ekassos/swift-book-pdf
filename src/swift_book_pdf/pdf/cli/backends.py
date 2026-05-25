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

import click

from swift_book_pdf.cli.options import OptionTarget, apply_options
from swift_book_pdf.pdf.contracts import PDFBackend
from swift_book_pdf.pdf.options import EngineKind
from swift_book_pdf.pdf.registry import (
    DEFAULT_ENGINE,
    registered_backends,
    registered_engine_kinds,
)

BACKENDS = registered_backends()
BACKENDS_BY_KIND = {backend.kind: backend for backend in BACKENDS}


def engine_choices() -> list[str]:
    """Return registered engine choices for Click."""
    return [engine.value for engine in registered_engine_kinds()]


def default_engine_value() -> str:
    """Return the default PDF engine value for Click."""
    return DEFAULT_ENGINE.value


def apply_backend_build_options(func: OptionTarget) -> OptionTarget:
    """Add build options for every registered PDF backend."""
    return apply_options(
        func,
        tuple(backend.build_options for backend in BACKENDS),
    )


def apply_backend_command_options(func: OptionTarget) -> OptionTarget:
    """Add command options for every registered PDF backend."""
    return apply_options(
        func,
        tuple(backend.command_options for backend in BACKENDS),
    )


def select_backend_for_cli(engine: EngineKind) -> PDFBackend:
    """Select a backend and convert registry misses into Click errors."""
    try:
        return BACKENDS_BY_KIND[engine]
    except KeyError as exc:
        raise click.ClickException(
            f"Unsupported PDF engine: {engine.value}"
        ) from exc
