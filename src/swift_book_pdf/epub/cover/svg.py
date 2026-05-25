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

"""SVG/XHTML inner-cover rendering."""

from __future__ import annotations

import html
from dataclasses import dataclass
from typing import TYPE_CHECKING

from swift_book_pdf.epub.cover.constants import (
    COVER_DPI,
    COVER_FOOTER_TEXT_FILL,
    COVER_FOOTER_TEXT_SIZE_PT,
)
from swift_book_pdf.epub.cover.variants import cover_version_label
from swift_book_pdf.epub.paths import relative_href

if TYPE_CHECKING:
    from swift_book_pdf.core.document import DocumentEntry

COVER_SERIF_FONT_FAMILY = (
    "'IBM Plex Serif', Georgia, 'Times New Roman', Times, serif"
)
COVER_SANS_FONT_FAMILY = (
    "'IBM Plex Sans', 'SF Pro Display', 'SF Compact', 'SF Pro', "
    "'Helvetica Neue', Helvetica, Arial, 'Segoe UI', "
    "'Liberation Sans', 'DejaVu Sans', sans-serif"
)


@dataclass(frozen=True)
class CoverPageOptions:
    """Inputs used to render the generated inner-cover XHTML.

    Attributes:
        book_title: EPUB book title for the XHTML `<title>`.
        cover_banner: Effective banner text and color.
        cover_footer_line: Optional custom footer line.
        compiled_by_name: Optional compiler credit fallback.
        cover_variant: Optional cover variant name used for version labels.
    """

    book_title: str
    cover_banner: tuple[str, str]
    cover_footer_line: str | None = None
    compiled_by_name: str | None = None
    cover_variant: str | None = None


@dataclass(frozen=True)
class SVGTextStyle:
    """SVG text styling used by cover title layers.

    Attributes:
        font_family: CSS font-family value.
        font_size: Font size in SVG user units.
        fill: Text fill color.
        font_weight: CSS font-weight value.
        font_style: CSS font-style value.
        letter_spacing: Base SVG letter-spacing value.
    """

    font_family: str
    font_size: float
    fill: str
    font_weight: str = "400"
    font_style: str = "normal"
    letter_spacing: float = 0


@dataclass(frozen=True)
class CoverTextSpan:
    """A text span with optional per-span spacing overrides.

    Attributes:
        text: Span text content.
        letter_spacing: Optional SVG letter-spacing for this span.
        dx: Optional SVG horizontal offset for this span.
    """

    text: str
    letter_spacing: float | None = None
    dx: float | None = None


CoverTextContent = str | tuple[CoverTextSpan, ...] | list[CoverTextSpan]


def render_cover_page(
    document: DocumentEntry,
    version_info: str | None,
    options: CoverPageOptions,
) -> str:
    """Render the complete generated cover XHTML document.

    Args:
        document: Generated cover document entry.
        version_info: Effective Swift version string.
        options: Inner-cover rendering options.

    Returns:
        XHTML document containing the generated SVG cover.
    """
    version_label = cover_version_label(version_info, options.cover_variant)
    css_href = html.escape(relative_href(document.href, "_static/epub.css"))
    banner_text, banner_color = options.cover_banner
    banner_color = html.escape(banner_color)

    layers = [
        _render_banner_layer(banner_text, banner_color),
        *_render_title_layers(version_label, banner_color),
    ]
    footer_layer = _render_footer_layer(options)
    if footer_layer is not None:
        layers.append(footer_layer)

    svg_body = "".join(layers)
    accessible_title = _build_accessible_title(options, version_label)
    return _wrap_cover_xhtml(options, css_href, accessible_title, svg_body)


def _render_banner_layer(banner_text: str, banner_color: str) -> str:
    """Render the colored edition banner SVG layer.

    Args:
        banner_text: Effective banner label.
        banner_color: Effective banner fill color.

    Returns:
        SVG markup for the fixed-position banner rectangle and text.
    """
    return (
        f'        <rect x="0" y="1029" width="1440" height="153" '
        f'fill="{banner_color}"/>\n'
        f'        <text class="cover-banner-text" x="114.48" '
        f'y="1066.47" font-family="{COVER_SANS_FONT_FAMILY}" '
        f'font-weight="500" font-size="58.333" letter-spacing="-0.7" '
        f'dominant-baseline="text-before-edge" '
        f'font-kerning="normal" text-rendering="optimizeLegibility" '
        f'fill="#ffffff">'
        f"{html.escape(banner_text.upper())}</text>\n"
    )


def _render_title_layers(
    version_label: str | None, banner_color: str
) -> list[str]:
    """Render the fixed title and version SVG text layers."""
    swift_version_text = [
        CoverTextSpan("S", letter_spacing=-5.0),
        CoverTextSpan("w", letter_spacing=-3.2),
        CoverTextSpan("i", letter_spacing=-4),
        CoverTextSpan("f", letter_spacing=0),
        CoverTextSpan("t ", letter_spacing=-0.5),
    ]
    if version_label:
        swift_version_text.append(
            CoverTextSpan(version_label, letter_spacing=-2.5)
        )

    return [
        render_cover_text(
            "The",
            x=107.81,
            y=57.67,
            style=SVGTextStyle(
                font_family=COVER_SERIF_FONT_FAMILY,
                font_size=133.333,
                fill="#1f1f1f",
                font_style="italic",
            ),
        ),
        render_cover_text(
            "Swift",
            x=104.81,
            y=176.69,
            style=SVGTextStyle(
                font_family=COVER_SERIF_FONT_FAMILY,
                font_size=208.333,
                fill=banner_color,
                font_weight="500",
                letter_spacing=-1.8,
            ),
        ),
        render_cover_text(
            "Programming",
            x=108.81,
            y=383.77,
            style=SVGTextStyle(
                font_family=COVER_SERIF_FONT_FAMILY,
                font_size=176,
                fill="#1f1f1f",
                letter_spacing=-3.5,
            ),
        ),
        render_cover_text(
            "Language",
            x=108.81,
            y=556.77,
            style=SVGTextStyle(
                font_family=COVER_SERIF_FONT_FAMILY,
                font_size=176,
                fill="#1f1f1f",
                letter_spacing=-3.8,
            ),
        ),
        render_cover_text(
            swift_version_text,
            x=111.81,
            y=843.95,
            style=SVGTextStyle(
                font_family=COVER_SANS_FONT_FAMILY,
                font_size=116.667,
                fill=banner_color,
                font_weight="500",
            ),
        ),
    ]


def _render_footer_layer(options: CoverPageOptions) -> str | None:
    """Render the optional footer or compiler-credit SVG layer.

    Args:
        options: Inner-cover rendering options.

    Returns:
        SVG footer layer, compiler-credit layer, or `None`.
    """
    if options.cover_footer_line:
        return (
            f'        <text class="cover-footer-text" x="720" y="2023" '
            f'text-anchor="middle" '
            f'font-family="{COVER_SERIF_FONT_FAMILY}" '
            f'font-weight="400" font-style="italic" '
            f'font-size="{COVER_FOOTER_TEXT_SIZE_PT * COVER_DPI / 72:g}" '
            f'letter-spacing="0" '
            f'font-kerning="normal" font-optical-sizing="auto" '
            f'text-rendering="optimizeLegibility" '
            f'fill="{COVER_FOOTER_TEXT_FILL}">'
            f"{html.escape(options.cover_footer_line)}</text>\n"
        )
    if options.compiled_by_name:
        return (
            f'        <text class="cover-compiler-label" x="115.81" '
            f'y="1991.09" font-family="{COVER_SERIF_FONT_FAMILY}" '
            f'font-weight="400" font-style="italic" '
            f'font-size="{11 * COVER_DPI / 72:g}" letter-spacing="-0.8" '
            f'font-kerning="normal" font-optical-sizing="auto" '
            f'dominant-baseline="text-before-edge" '
            f'text-rendering="optimizeLegibility" '
            f'fill="{COVER_FOOTER_TEXT_FILL}">Compiled by:</text>\n'
            f'        <text class="cover-compiler-name" x="115.81" '
            f'y="2043.55" font-family="{COVER_SERIF_FONT_FAMILY}" '
            f'font-weight="500" font-style="normal" '
            f'font-size="{12 * COVER_DPI / 72:g}" letter-spacing="-0.7" '
            f'font-kerning="normal" font-optical-sizing="auto" '
            f'dominant-baseline="text-before-edge" '
            f'text-rendering="optimizeLegibility" '
            f'fill="{COVER_FOOTER_TEXT_FILL}">'
            f"{html.escape(options.compiled_by_name)}</text>\n"
        )
    return None


def _build_accessible_title(
    options: CoverPageOptions, version_label: str | None
) -> str:
    """Build the hidden accessible title for the cover image.

    Args:
        options: Inner-cover rendering options.
        version_label: Normalized visible version label.

    Returns:
        Descriptive label used by both hidden heading text and SVG ARIA.
    """
    accessible_parts: list[str] = [options.cover_banner[0]]
    accessible_parts.append("The Swift Programming Language")
    if version_label:
        accessible_parts.append(f"Swift {version_label}")
    if options.cover_footer_line:
        accessible_parts.append(options.cover_footer_line)
    elif options.compiled_by_name:
        accessible_parts.append(f"Compiled by: {options.compiled_by_name}")
    return " — ".join(accessible_parts)


def _wrap_cover_xhtml(
    options: CoverPageOptions,
    css_href: str,
    accessible_title: str,
    svg_body: str,
) -> str:
    """Wrap cover SVG markup in a complete XHTML document.

    Args:
        options: Inner-cover rendering options.
        css_href: Cover document relative href to the EPUB stylesheet.
        accessible_title: Accessible label for the cover image.
        svg_body: SVG child markup.

    Returns:
        Complete XHTML cover page.
    """
    return f"""<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head>
    <meta charset="utf-8" />
    <title>{html.escape(options.book_title)}</title>
    <link rel="stylesheet" href="{css_href}" type="text/css" />
  </head>
  <body class="coverpage" id="coverpage">
    <h1 class="visually-hidden">{html.escape(accessible_title)}</h1>
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" class="cover-canvas-svg" viewBox="0 0 1440 2160" preserveAspectRatio="xMidYMid meet" role="img" aria-label="{html.escape(accessible_title)}">
{svg_body}    </svg>
  </body>
</html>
"""


def render_cover_text(
    text: CoverTextContent,
    x: float,
    y: float,
    style: SVGTextStyle,
) -> str:
    """Render a positioned SVG cover text element.

    Args:
        text: Plain text or span sequence for the element body.
        x: SVG x coordinate.
        y: SVG y coordinate.
        style: Shared SVG text styling.

    Returns:
        SVG `<text>` element with escaped content.
    """
    text_content = _render_cover_text_content(text)
    return (
        f'        <text class="cover-title-text" x="{x:g}" y="{y:g}" '
        f'font-family="{style.font_family}" '
        f'font-weight="{style.font_weight}" '
        f'font-style="{style.font_style}" font-size="{style.font_size:g}" '
        f'letter-spacing="{style.letter_spacing:g}" '
        f'font-kerning="normal" dominant-baseline="text-before-edge" '
        f'fill="{html.escape(style.fill)}">'
        f"{text_content}</text>\n"
    )


def _render_cover_text_content(text: CoverTextContent) -> str:
    """Render plain text or span-based cover text content.

    Args:
        text: Plain text or span sequence.

    Returns:
        Escaped SVG text content.
    """
    if isinstance(text, str):
        return html.escape(text)
    return "".join(_render_cover_text_span(span) for span in text)


def _render_cover_text_span(span: CoverTextSpan) -> str:
    """Render a single SVG `<tspan>` for cover text.

    Args:
        span: Text span and optional positioning overrides.

    Returns:
        SVG `<tspan>` markup.
    """
    attributes = ['dominant-baseline="text-before-edge"']
    if span.letter_spacing is not None:
        attributes.append(f'letter-spacing="{span.letter_spacing:g}"')
    if span.dx is not None:
        attributes.append(f'dx="{span.dx:g}"')
    return f"<tspan {' '.join(attributes)}>{html.escape(span.text)}</tspan>"
