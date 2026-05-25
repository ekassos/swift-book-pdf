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

"""PNG cover asset generation and export helpers."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from swift_book_pdf.epub.cover.constants import (
    COVER_FOOTER_TEXT_FILL,
    COVER_FOOTER_TEXT_SIZE,
    COVER_FOOTER_TEXT_Y,
    COVER_SANS_FONT_PATH,
    COVER_SERIF_ITALIC_FONT_PATH,
    COVER_TEXT_BASELINE_Y,
    COVER_TEXT_SIZE,
    COVER_TEXT_TRACKING,
    COVER_TEXT_X,
)
from swift_book_pdf.epub.cover.variants import (
    cover_png_version_fill,
    cover_png_version_text,
    cover_template_path,
)
from swift_book_pdf.epub.paths import oebps_workspace_path

if TYPE_CHECKING:
    from pathlib import Path

    from swift_book_pdf.epub.config import EPUBConfig

logger = logging.getLogger(__name__)

COVER_ASSET_HREF = "_static/cover.png"


@dataclass(frozen=True)
class _PNGTextStyle:
    """Pillow text style for rendered PNG cover labels.

    Attributes:
        font: Pillow font used to draw text.
        tracking: Extra pixels inserted between glyphs.
        fill: Text fill color.
    """

    font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    tracking: float
    fill: str


def write_cover_asset(
    config: EPUBConfig,
    workspace: Path,
    version_info: str | None,
) -> None:
    """Write the outer cover PNG into the EPUB workspace.

    Args:
        config: Resolved EPUB build configuration.
        workspace: Temporary EPUB workspace root.
        version_info: Effective Swift version string used for label and
            variant selection.
    """
    template_path = cover_template_path(
        version_info,
        config.base_cover_image,
        config.cover_variant,
        config.cover_template_paths,
    )
    if not template_path.exists():
        logger.warning(
            "Couldn't find cover template %s; skipping cover.",
            template_path,
        )
        return

    cover_destination = oebps_workspace_path(workspace, COVER_ASSET_HREF)
    cover_destination.parent.mkdir(parents=True, exist_ok=True)
    version_text = cover_png_version_text(
        version_info,
        config.cover_variant,
    )
    if version_text is None and not config.cover_footer_line:
        shutil.copy2(template_path, cover_destination)
        return

    cover_image = Image.open(template_path).convert("RGBA")
    if version_text is not None:
        style = _PNGTextStyle(
            font=ImageFont.truetype(
                str(COVER_SANS_FONT_PATH), COVER_TEXT_SIZE
            ),
            tracking=COVER_TEXT_TRACKING,
            fill=cover_png_version_fill(
                version_info,
                config.cover_variant,
            ),
        )
        _draw_cover_version_text(
            cover_image,
            version_text,
            style,
        )
    if config.cover_footer_line:
        footer_line_font = ImageFont.truetype(
            str(COVER_SERIF_ITALIC_FONT_PATH),
            COVER_FOOTER_TEXT_SIZE,
        )
        _draw_cover_footer_line(
            cover_image,
            config.cover_footer_line,
            footer_line_font,
        )
    cover_image.convert("RGB").save(cover_destination, format="PNG")


def export_cover_asset(workspace: Path, output_path: Path) -> Path | None:
    """Copy the generated cover PNG next to the output EPUB.

    Args:
        workspace: Temporary EPUB workspace root.
        output_path: Final EPUB output path.

    Returns:
        Exported cover image path, or `None` if no package cover was written.
    """
    source = oebps_workspace_path(workspace, COVER_ASSET_HREF)
    if not source.exists():
        return None

    destination = output_path.with_name(f"{output_path.stem}_cover.png")
    shutil.copy2(source, destination)
    return destination


def has_cover_asset(workspace: Path) -> bool:
    """Return whether the EPUB workspace contains an outer cover PNG.

    Args:
        workspace: Temporary EPUB workspace root.

    Returns:
        True when `_static/cover.png` exists in the staged package tree.
    """
    return oebps_workspace_path(workspace, COVER_ASSET_HREF).exists()


def _draw_cover_version_text(
    image: Image.Image,
    text: str,
    style: _PNGTextStyle,
) -> None:
    """Draw baseline-aligned tracked version text onto a cover image.

    Pillow positions text by bounding box, not typographic baseline. The
    overlay calculation compensates for the font's top offset so the version
    label stays aligned to the cover template coordinates.
    """
    text_width, text_height, bbox_left, bbox_top = _measure_tracked_text(
        text, style.font, style.tracking
    )
    padding = 12
    overlay_width = max(1, int(text_width + (padding * 2)))
    overlay_height = max(1, int(text_height + (padding * 2)))
    overlay = Image.new(
        "RGBA", (overlay_width, overlay_height), (255, 255, 255, 0)
    )
    overlay_draw = ImageDraw.Draw(overlay)
    _draw_tracked_text(
        overlay_draw,
        (padding - bbox_left, padding - bbox_top),
        text,
        style,
    )
    x = round(COVER_TEXT_X - padding)
    y = round(COVER_TEXT_BASELINE_Y - padding + bbox_top)
    image.alpha_composite(overlay, (x, y))


def _draw_cover_footer_line(
    image: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Draw a centered footer line onto a cover image.

    Args:
        image: Mutable cover image.
        text: Footer text to draw.
        font: Font used for footer rendering.
    """
    _draw_cover_centered_text(
        image,
        text,
        font,
        COVER_FOOTER_TEXT_Y,
        COVER_FOOTER_TEXT_FILL,
    )


def _measure_tracked_text(
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    tracking: float = COVER_TEXT_TRACKING,
) -> tuple[float, int, int, int]:
    """Measure text dimensions after applying manual glyph tracking.

    Args:
        text: Text to measure.
        font: Pillow font used to draw the text.
        tracking: Extra pixels between glyphs.

    Returns:
        Width, height, left bearing, and top bearing for the tracked text.
    """
    dummy = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
    draw = ImageDraw.Draw(dummy)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    width = float(right - left)
    if len(text) > 1:
        width += tracking * (len(text) - 1)
    return width, bottom - top, left, top


def _draw_tracked_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    style: _PNGTextStyle,
) -> None:
    """Draw text one glyph at a time when tracking is nonzero.

    Args:
        draw: Pillow drawing context.
        position: Top-left text position adjusted for glyph bearing.
        text: Text to draw.
        style: Font, tracking, and fill settings.
    """
    if style.tracking == 0:
        draw.text(position, text, fill=style.fill, font=style.font)
        return

    cursor_x, y = position
    for index, character in enumerate(text):
        draw.text(
            (cursor_x, y),
            character,
            fill=style.fill,
            font=style.font,
        )
        cursor_x += draw.textlength(character, font=style.font)
        if index < len(text) - 1:
            cursor_x += style.tracking


def _draw_cover_centered_text(
    image: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    top_y: float,
    fill: str,
) -> None:
    """Draw untracked text centered horizontally on a cover image."""
    text_width, text_height, bbox_left, bbox_top = _measure_tracked_text(
        text,
        font,
        tracking=0,
    )
    padding = 8
    overlay_width = max(1, int(text_width + (padding * 2)))
    overlay_height = max(1, int(text_height + (padding * 2)))
    overlay = Image.new(
        "RGBA", (overlay_width, overlay_height), (255, 255, 255, 0)
    )
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.text(
        (padding - bbox_left, padding - bbox_top),
        text,
        fill=fill,
        font=font,
    )

    x = round((image.width - overlay.width) / 2)
    y = round(top_y)
    image.alpha_composite(overlay, (x, y))
