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

from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.contracts import PDFBackend, PDFEngine
from swift_book_pdf.pdf.options import EngineKind


def select_backend(engine_kind: EngineKind) -> PDFBackend:
    """Select the configured PDF backend."""
    match engine_kind:
        case EngineKind.LATEX:
            from swift_book_pdf.pdf.latex.backend import LaTeXBackend

            return LaTeXBackend()
        case _:
            raise ValueError(f"Unsupported PDF engine: {engine_kind}")


def select_engine(config: PDFConfig) -> PDFEngine:
    """Select the configured PDF engine."""
    match config.engine_kind:
        case EngineKind.LATEX:
            from swift_book_pdf.pdf.latex.engine import LaTeXEngine

            return LaTeXEngine()
        case _:
            raise ValueError(f"Unsupported PDF engine: {config.engine_kind}")
