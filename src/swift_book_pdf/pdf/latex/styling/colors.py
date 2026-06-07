# Copyright 2025 Evangelos Kassos
#
# Portions derived from swift-docc-render:
#   Copyright (c) 2021-2025 Apple Inc. and the Swift project authors
#   Licensed under Apache License v2.0 with Runtime Library Exception
#
#   See https://swift.org/LICENSE.txt for details.
#   The Swift project authors are credited at https://swift.org/CONTRIBUTORS.txt.
#   See THIRD-PARTY-NOTICES.txt for details.
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
    """DocC Render CSS colors used by the LaTeX preamble."""

    color_text_background: str
    """DocC `--color-text-background` color."""

    color_text: str
    """DocC `--color-text` color."""

    color_article_background: str
    """DocC `--color-article-background` color."""

    color_header_footer_background: str
    """PDF running header and footer background color."""

    color_header_footer_text: str
    """PDF running header and footer text color."""

    color_link: str
    """DocC `--color-link` color."""

    color_grid: str
    """DocC `--color-grid` color."""

    color_code_background: str
    """DocC `--color-code-background` color."""

    color_code_plain: str
    """DocC `--color-code-plain` color."""

    color_aside_note_background: str
    """DocC `--color-aside-note-background` color."""

    color_aside_note_border: str
    """DocC `--color-aside-note-border` color."""

    color_aside_note: str
    """DocC `--color-aside-note` color."""

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
        color_text_background="255, 255, 255",
        color_text="0, 0, 0",
        color_article_background="240, 240, 240",
        color_header_footer_background="51, 51, 51",
        color_header_footer_text="255, 255, 255",
        color_link="51, 102, 255"
        if rendering_mode == RenderingMode.DIGITAL
        else "0, 0, 0",
        color_grid="204, 204, 204",
        color_code_background="247, 247, 247",
        color_code_plain="0, 0, 0",
        color_aside_note_background="245, 245, 245",
        color_aside_note_border="102, 102, 102",
        color_aside_note="0, 0, 0",
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
        color_text_background="0, 0, 0",
        color_text="255, 255, 255",
        color_article_background="42, 42, 42",
        color_header_footer_background="51, 51, 51",
        color_header_footer_text="255, 255, 255",
        color_link="0, 153, 255"
        if rendering_mode == RenderingMode.DIGITAL
        else "255, 255, 255",
        color_grid="87, 87, 87",
        color_code_background="22, 22, 22",
        color_code_plain="255, 255, 255",
        color_aside_note_background="34, 34, 34",
        color_aside_note_border="176, 176, 176",
        color_aside_note="255, 255, 255",
        code_style="swift_book_dark_style",
    )
