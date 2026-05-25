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

"""Shared PDF backend and engine contracts."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from swift_book_pdf.core.config import ResolvedBuildSource
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.layout import PDFDocumentConfig
from swift_book_pdf.pdf.options import EngineKind

OptionTarget = Callable[..., object]


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
    """Backend contract for engine-specific PDF CLI and config behavior."""

    kind: EngineKind

    def build_options(self, func: OptionTarget) -> OptionTarget:
        """Decorate the PDF command with backend build options."""

    def command_options(self, func: OptionTarget) -> OptionTarget:
        """Decorate the PDF command with backend-specific CLI options."""

    def build_config(self, config_input: PDFBackendConfigInput) -> PDFConfig:
        """Build the concrete backend config for a PDF build."""
