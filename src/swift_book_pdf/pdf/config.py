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

"""Shared PDF build configuration."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from swift_book_pdf.core.config.models import BaseBuildConfig
from swift_book_pdf.core.output import OutputFormat


class RenderingMode(StrEnum):
    DIGITAL = "digital"
    PRINT = "print"


class Appearance(StrEnum):
    LIGHT = "light"
    DARK = "dark"


class PaperSize(StrEnum):
    A4 = "a4"
    LETTER = "letter"
    LEGAL = "legal"


class EngineKind(StrEnum):
    LATEX = "latex"


DEFAULT_RENDERING_MODE = RenderingMode.DIGITAL
DEFAULT_PAPER_SIZE = PaperSize.LETTER
DEFAULT_GUTTER = True
DEFAULT_BODY_FONT_SIZE = 9.0
DEFAULT_APPEARANCE = Appearance.LIGHT


@dataclass(frozen=True)
class PDFDocumentConfig:
    """Resolved PDF document options.

    Attributes:
        mode: PDF rendering mode.
        paper_size: Output paper size.
        gutter: Whether the book gutter should be rendered.
        font_size: Base paragraph font size in points.
        appearance: Light or dark rendering appearance.
    """

    mode: RenderingMode = DEFAULT_RENDERING_MODE
    """PDF rendering mode."""

    paper_size: PaperSize = DEFAULT_PAPER_SIZE
    """Output paper size."""

    gutter: bool = DEFAULT_GUTTER
    """Whether the book gutter should be rendered."""

    font_size: float = DEFAULT_BODY_FONT_SIZE
    """Base paragraph font size in points."""

    appearance: Appearance = DEFAULT_APPEARANCE
    """Light or dark rendering appearance."""

    def __post_init__(self) -> None:
        """Validate the resolved document configuration.

        Raises:
            ValueError: If `font_size` is not positive.
        """
        if self.font_size <= 0:
            raise ValueError("Font size must be a positive number.")


@dataclass(frozen=True, kw_only=True)
class PDFConfig(BaseBuildConfig, ABC):
    """Resolved configuration for PDF builds.

    Attributes:
        doc_config: PDF document layout configuration.
        engine_kind: PDF engine implementation.
        override_version: Optional Swift version override.
    """

    doc_config: PDFDocumentConfig
    engine_kind: EngineKind
    override_version: str | None = None

    output_format: ClassVar[OutputFormat] = OutputFormat.PDF

    def diagnostic_details(self) -> str:
        """Format resolved PDF build details for debug diagnostics."""
        doc_config = self.doc_config
        return "\n".join(
            [
                f"Rendering mode: {doc_config.mode}",
                f"Paper size: {doc_config.paper_size}",
                f"Appearance: {doc_config.appearance}",
                f"Book Gutter: {doc_config.gutter}",
                f"Font size: {doc_config.font_size}pt",
            ]
        )

    @abstractmethod
    def build_error_details(self) -> str:
        """Format backend-specific details for unexpected build errors."""
