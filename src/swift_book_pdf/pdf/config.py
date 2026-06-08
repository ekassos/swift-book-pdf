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
from dataclasses import dataclass, field
from enum import StrEnum
from typing import ClassVar

from swift_book_pdf.core.config.models import BaseBuildConfig
from swift_book_pdf.core.output import OutputFormat


class RenderingMode(StrEnum):
    """PDF layout modes optimized for digital or printed reading."""

    DIGITAL = "digital"
    """Render hyperlinks and navigation for screen reading."""

    PRINT = "print"
    """Render references and navigation for printed output."""


class Appearance(StrEnum):
    """PDF color appearances."""

    LIGHT = "light"
    """Render the light color palette."""

    DARK = "dark"
    """Render the dark color palette."""


class PaperSize(StrEnum):
    """Paper sizes supported by the PDF backend."""

    A4 = "a4"
    """A4 paper."""

    LETTER = "letter"
    """US Letter paper."""

    LEGAL = "legal"
    """US Legal paper."""


class EngineKind(StrEnum):
    """PDF rendering engine identifiers."""

    LATEX = "latex"
    """Render PDFs through the LaTeX backend."""


DEFAULT_RENDERING_MODE = RenderingMode.DIGITAL
DEFAULT_PAPER_SIZE = PaperSize.LETTER
DEFAULT_GUTTER = True
DEFAULT_BODY_FONT_SIZE = 9.5625
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
        code_font_size: Optional fenced code listing font size in points.
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

    code_font_size: float | None = None
    """Optional fenced code listing font size in points."""

    def __post_init__(self) -> None:
        """Validate the resolved document configuration.

        Raises:
            ValueError: If a font size is not positive.
        """
        if self.font_size <= 0:
            raise ValueError("Font size must be a positive number.")
        if self.code_font_size is not None and self.code_font_size <= 0:
            raise ValueError("Code font size must be a positive number.")


@dataclass(frozen=True)
class PDFContentSelection:
    """Subset of book content to render for a PDF build.

    Attributes:
        only_toc: Whether to render only the table of contents page.
        only_chapter: Optional document tag or file stem for one chapter.
    """

    only_toc: bool = False
    """Whether to render only the table of contents page."""

    only_chapter: str | None = None
    """Optional document tag or file stem for one chapter."""

    def __post_init__(self) -> None:
        """Validate the requested content subset.

        Raises:
            ValueError: If incompatible content selectors are set.
        """
        if self.only_toc and self.only_chapter is not None:
            raise ValueError(
                "Use either --only-toc or --only-chapter, not both."
            )


@dataclass(frozen=True, kw_only=True)
class PDFConfig(BaseBuildConfig, ABC):
    """Resolved configuration for PDF builds.

    Attributes:
        doc_config: PDF document layout configuration.
        engine_kind: PDF engine implementation.
        override_version: Optional Swift version override.
    """

    doc_config: PDFDocumentConfig
    """PDF document layout configuration."""

    engine_kind: EngineKind
    """PDF engine implementation."""

    override_version: str | None = None
    """Optional Swift version override."""

    content_selection: PDFContentSelection = field(
        default_factory=PDFContentSelection
    )
    """Subset of book content to render."""

    save_tex: bool = False
    """Whether to save LaTeX source instead of compiling a PDF."""

    intermediates_path: str | None = None
    """Optional destination directory for build intermediates."""

    output_format: ClassVar[OutputFormat] = OutputFormat.PDF
    """Artifact format produced by PDF builders."""

    def diagnostic_details(self) -> str:
        """Format resolved PDF build details for debug diagnostics.

        Returns:
            Human-readable diagnostic details.
        """
        doc_config = self.doc_config
        return "\n".join(
            [
                f"Rendering mode: {doc_config.mode}",
                f"Paper size: {doc_config.paper_size}",
                f"Appearance: {doc_config.appearance}",
                f"Book Gutter: {doc_config.gutter}",
                f"Font size: {doc_config.font_size}pt",
                f"Code font size: {doc_config.code_font_size}pt"
                if doc_config.code_font_size is not None
                else "Code font size: scaled",
                f"Content: {format_content_selection(self.content_selection)}",
                f"Build target: {'tex' if self.save_tex else 'pdf'}",
                f"Build files: {self.intermediates_path or 'temporary'}",
            ]
        )

    @abstractmethod
    def build_error_details(self) -> str:
        """Format backend-specific details for unexpected build errors.

        Returns:
            Human-readable backend details.
        """


def format_content_selection(selection: PDFContentSelection) -> str:
    """Format a PDF content selection for diagnostics.

    Args:
        selection: Requested content subset.

    Returns:
        Human-readable content selector.
    """
    if selection.only_toc:
        return "toc"
    if selection.only_chapter is not None:
        return f"chapter:{selection.only_chapter}"
    return "full"
