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

"""PDF backend and engine registry."""

# ruff: noqa: PLC0415

from collections.abc import Callable
from dataclasses import dataclass

from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.contracts import PDFBackend, PDFEngine
from swift_book_pdf.pdf.options import EngineKind

DEFAULT_ENGINE = EngineKind.LATEX


@dataclass(frozen=True)
class PDFBackendRegistration:
    """Factories for a registered PDF backend and its build engine."""

    backend_factory: Callable[[], PDFBackend]
    engine_factory: Callable[[], PDFEngine]


def _latex_backend() -> PDFBackend:
    from swift_book_pdf.pdf.latex.backend import LaTeXBackend

    return LaTeXBackend()


def _latex_engine() -> PDFEngine:
    from swift_book_pdf.pdf.latex.engine import LaTeXEngine

    return LaTeXEngine()


PDF_BACKENDS: dict[EngineKind, PDFBackendRegistration] = {
    EngineKind.LATEX: PDFBackendRegistration(
        backend_factory=_latex_backend,
        engine_factory=_latex_engine,
    ),
}


def registered_engine_kinds() -> tuple[EngineKind, ...]:
    """Return all registered PDF engine kinds."""
    return tuple(PDF_BACKENDS)


def registered_backends() -> tuple[PDFBackend, ...]:
    """Return backend adapters for all registered PDF engines."""
    return tuple(
        registration.backend_factory()
        for registration in PDF_BACKENDS.values()
    )


def select_backend(engine_kind: EngineKind) -> PDFBackend:
    """Select the configured PDF backend."""
    try:
        return PDF_BACKENDS[engine_kind].backend_factory()
    except KeyError as exc:
        raise ValueError(f"Unsupported PDF engine: {engine_kind}") from exc


def select_engine(config: PDFConfig) -> PDFEngine:
    """Select the configured PDF engine."""
    try:
        return PDF_BACKENDS[config.engine_kind].engine_factory()
    except KeyError as exc:
        raise ValueError(
            f"Unsupported PDF engine: {config.engine_kind}"
        ) from exc
