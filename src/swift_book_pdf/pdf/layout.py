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

import logging
from dataclasses import dataclass

from swift_book_pdf.pdf.options import Appearance, PaperSize, RenderingMode

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DocConfig:
    """PDF document layout options resolved from CLI input.

    Attributes:
        mode: PDF rendering mode.
        paper_size: Output paper size.
        typesets: Number of LaTeX typesetting passes.
        gutter: Whether the book gutter should be rendered.
        font_size: Base paragraph font size in points.
        appearance: Light or dark rendering appearance derived from
            `dark_mode`.
    """

    mode: RenderingMode
    """PDF rendering mode."""

    paper_size: PaperSize
    """Output paper size."""

    typesets: int
    """Number of LaTeX typesetting passes."""

    gutter: bool
    """Whether the book gutter should be rendered."""

    font_size: float
    """Base paragraph font size in points."""

    appearance: Appearance
    """Light or dark rendering appearance."""

    def __init__(  # noqa: PLR0913
        self,
        mode: RenderingMode = RenderingMode.DIGITAL,
        paper_size: PaperSize = PaperSize.LETTER,
        typesets: int = 4,
        dark_mode: bool = False,
        gutter: bool | None = None,
        font_size: float | None = None,
    ) -> None:
        """Create a normalized PDF document layout configuration.

        Args:
            mode: PDF rendering mode.
            paper_size: Output paper size.
            typesets: Number of LaTeX typesetting passes.
            dark_mode: Whether dark appearance should be selected.
            gutter: Optional gutter override. `None` keeps the default enabled
                gutter.
            font_size: Optional base paragraph font size in points.

        Raises:
            ValueError: If `font_size` is not positive.
        """
        normalized_font_size = font_size if font_size is not None else 9.0
        if normalized_font_size <= 0:
            raise ValueError("Font size must be a positive number.")

        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "paper_size", paper_size)
        object.__setattr__(self, "typesets", typesets)
        object.__setattr__(
            self,
            "appearance",
            Appearance.DARK if dark_mode else Appearance.LIGHT,
        )
        object.__setattr__(
            self,
            "gutter",
            True if gutter is None else gutter,
        )
        object.__setattr__(self, "font_size", normalized_font_size)

        logger.debug(f"Rendering mode: {self.mode}")
        logger.debug(f"Paper size: {self.paper_size}")
        logger.debug(f"Typesets: {self.typesets}")
        logger.debug(f"Appearance: {self.appearance}")
        logger.debug(f"Book Gutter: {self.gutter}")
        logger.debug(f"Font size: {self.font_size}pt")
