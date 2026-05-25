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

"""Color palettes for LaTeX PDF rendering."""

from dataclasses import dataclass

from swift_book_pdf.pdf.config import Appearance, RenderingMode


@dataclass(frozen=True)
class DocumentColors:
    """RGB color substitutions used by the LaTeX preamble."""

    background: str
    """Page background color."""

    text: str
    """Primary text color."""

    header_background: str
    """Running header background color."""

    header_text: str
    """Running header text color."""

    hero_background: str
    """Chapter hero background color."""

    hero_text: str
    """Chapter hero text color."""

    link: str
    """Hyperlink text color."""

    aside_background: str
    """Aside box background color."""

    aside_border: str
    """Aside box border color."""

    aside_text: str
    """Aside box text color."""

    table_border: str
    """Table rule color."""

    code_border: str
    """Code box border color."""

    code_background: str
    """Code box background color."""

    code_style: str
    """Pygments style name for code highlighting."""


def get_document_colors(
    rendering_mode: RenderingMode,
    appearance: Appearance,
) -> DocumentColors:
    """Return the PDF color palette for the requested appearance.

    Args:
        rendering_mode: PDF rendering mode.
        appearance: PDF color appearance.

    Returns:
        Resolved document colors.

    Raises:
        ValueError: If `appearance` is unsupported.
    """
    match appearance:
        case Appearance.LIGHT:
            return light_colors(rendering_mode)
        case Appearance.DARK:
            return dark_colors(rendering_mode)
        case _:
            raise ValueError(f"Invalid appearance: {appearance}")


def light_colors(rendering_mode: RenderingMode) -> DocumentColors:
    """Return the light PDF palette.

    Args:
        rendering_mode: PDF rendering mode.

    Returns:
        Light-mode document colors.
    """
    return DocumentColors(
        background="255, 255, 255",
        text="0, 0, 0",
        header_background="51, 51, 51",
        header_text="255, 255, 255",
        hero_background="240, 240, 240",
        hero_text="0, 0, 0",
        link="51, 102, 255"
        if rendering_mode == RenderingMode.DIGITAL
        else "0, 0, 0",
        aside_background="245, 245, 245",
        aside_text="0, 0, 0",
        aside_border="102, 102, 102",
        table_border="240, 240, 240",
        code_border="204, 204, 204",
        code_background="247, 247, 247",
        code_style="swift_book_style",
    )


def dark_colors(rendering_mode: RenderingMode) -> DocumentColors:
    """Return the dark PDF palette.

    Args:
        rendering_mode: PDF rendering mode.

    Returns:
        Dark-mode document colors.
    """
    return DocumentColors(
        background="0, 0, 0",
        text="255, 255, 255",
        header_background="51, 51, 51",
        header_text="255, 255, 255",
        hero_background="51, 51, 51",
        hero_text="255, 255, 255",
        link="0, 153, 255"
        if rendering_mode == RenderingMode.DIGITAL
        else "255, 255, 255",
        aside_background="34, 34, 34",
        aside_text="255, 255, 255",
        aside_border="176, 176, 176",
        table_border="66, 66, 66",
        code_border="87, 87, 87",
        code_background="22, 22, 22",
        code_style="swift_book_dark_style",
    )
