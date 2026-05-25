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

"""PDF engine selection and shared engine contract."""

# ruff: noqa: PLC0415

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.options import EngineKind


@dataclass(frozen=True)
class PDFBuildContext:
    """Shared PDF build inputs passed to a concrete engine."""

    config: PDFConfig
    toc: TableOfContents
    version_info: str


class PDFEngine(Protocol):
    """Engine interface for producing a temporary PDF artifact."""

    def build(self, context: PDFBuildContext) -> Path:
        """Render and compile a PDF, returning the temporary PDF path."""


def select_engine(config: PDFConfig) -> PDFEngine:
    """Select the configured PDF engine.

    Args:
        config: Resolved PDF build configuration.

    Returns:
        The engine implementation for the configured engine kind.

    Raises:
        ValueError: If the configured engine is unsupported.
    """
    match config.engine_kind:
        case EngineKind.LATEX:
            from swift_book_pdf.pdf.latex.engine import (
                LaTeXEngine,
            )

            return LaTeXEngine()
        case _:
            raise ValueError(f"Unsupported PDF engine: {config.engine_kind}")
