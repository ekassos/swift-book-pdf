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

"""PDF backend contracts and registry."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from swift_book_pdf.core.config import ResolvedBuildSource
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.pdf.config import EngineKind, PDFConfig, PDFDocumentConfig
from swift_book_pdf.pdf.latex.backend import LaTeXBackend
from swift_book_pdf.pdf.latex.engine import LaTeXEngine

DEFAULT_ENGINE = EngineKind.LATEX


@dataclass(frozen=True)
class PDFBuildContext:
    """Shared PDF build inputs passed to a concrete engine."""

    config: PDFConfig
    toc: TableOfContents


@dataclass(frozen=True)
class PDFBackendConfigInput:
    """Shared inputs used to build a concrete backend config."""

    source: ResolvedBuildSource
    output_path: str
    doc_config: PDFDocumentConfig
    override_version: str | None
    dangerously_skip_legal_notices: bool
    backend_options: Mapping[str, Any]


class PDFEngine(Protocol):
    """Engine interface for producing a temporary PDF artifact."""

    def build(self, context: PDFBuildContext) -> Path:
        """Render and compile a PDF, returning the temporary PDF path."""


class PDFBackend(Protocol):
    """Backend contract for engine-specific PDF config behavior."""

    kind: EngineKind

    def build_config(self, config_input: PDFBackendConfigInput) -> PDFConfig:
        """Build the concrete backend config for a PDF build."""


@dataclass(frozen=True)
class PDFBackendRegistration:
    """Factories for a registered PDF backend and its build engine."""

    backend_factory: Callable[[], PDFBackend]
    engine_factory: Callable[[], PDFEngine]


PDF_BACKENDS: dict[EngineKind, PDFBackendRegistration] = {
    EngineKind.LATEX: PDFBackendRegistration(
        backend_factory=LaTeXBackend,
        engine_factory=LaTeXEngine,
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
