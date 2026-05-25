# Copyright 2025 Evangelos Kassos
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

"""PDF document layout configuration."""

from dataclasses import dataclass

from swift_book_pdf.pdf.options import Appearance, PaperSize, RenderingMode

DEFAULT_RENDERING_MODE = RenderingMode.DIGITAL
DEFAULT_PAPER_SIZE = PaperSize.LETTER
DEFAULT_GUTTER = True
DEFAULT_BODY_FONT_SIZE = 9.0
DEFAULT_APPEARANCE = Appearance.LIGHT


@dataclass(frozen=True)
class PDFDocumentConfig:
    """Resolved PDF document layout options.

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
        """Validate the resolved layout configuration.

        Raises:
            ValueError: If `font_size` is not positive.
        """
        if self.font_size <= 0:
            raise ValueError("Font size must be a positive number.")

    def __str__(self) -> str:
        """Format the resolved layout configuration for diagnostics."""
        return "\n".join(
            [
                f"Rendering mode: {self.mode}",
                f"Paper size: {self.paper_size}",
                f"Appearance: {self.appearance}",
                f"Book Gutter: {self.gutter}",
                f"Font size: {self.font_size}pt",
            ]
        )
