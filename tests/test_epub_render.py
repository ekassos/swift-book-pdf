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

from pathlib import Path

from swift_book_pdf.epub.render import (
    CoverPageOptions,
    CoverTextSpan,
    CoverTextStyle,
    EPUBRenderer,
    LinkResolver,
    _normalize_prose_punctuation,
    _render_cover_text,
    _render_inline,
)
from swift_book_pdf.schema import DocumentEntry

EPUB_REFERENCE_DIR = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "swift_book_pdf"
    / "assets"
    / "epub_reference"
)


def test_normalize_prose_punctuation_converts_triple_hyphen_to_em_dash() -> (
    None
):
    assert _normalize_prose_punctuation("before --- after") == "before—after"


def test_normalize_prose_punctuation_converts_double_hyphen_to_en_dash() -> (
    None
):
    assert (
        _normalize_prose_punctuation("Swift 5.9--6.0") == "Swift 5.9\u20136.0"
    )


def test_render_inline_keeps_markdown_like_code_spans_literal() -> None:
    rendered = _render_inline(
        (
            "Alternatively, you can create an empty array of a certain type "
            "using explicit initializer syntax, by writing the element type "
            "in square brackets followed by parentheses---for example, "
            "`[Int]()` in the following:"
        ),
        "CollectionTypes.xhtml",
        LinkResolver([]),
    )

    assert "@@INLINE" not in rendered
    assert '<code class="inline-code">[Int]()</code>' in rendered


def test_render_inline_supports_code_inside_markdown_link_labels() -> None:
    rendered = _render_inline(
        "Read [`Array`](https://example.com) first.",
        "CollectionTypes.xhtml",
        LinkResolver([]),
    )

    assert (
        '<a href="https://example.com">'
        '<code class="inline-code">Array</code></a>' in rendered
    )


def test_render_cover_text_emits_configured_letter_spacing() -> None:
    rendered = _render_cover_text(
        "Swift",
        x=104.81,
        y=335.69,
        style=CoverTextStyle(
            font_family="IBM Plex Serif",
            font_size=208.333,
            fill="#33519e",
            font_weight="500",
            letter_spacing=-2,
        ),
    )

    assert 'letter-spacing="-2"' in rendered
    assert ">Swift</text>" in rendered


def test_render_cover_text_accepts_spans_with_letter_spacing() -> None:
    rendered = _render_cover_text(
        [
            CoverTextSpan("Swift", letter_spacing=-2),
            CoverTextSpan(" 6.3", letter_spacing=-0.8),
        ],
        x=104.81,
        y=335.69,
        style=CoverTextStyle(
            font_family="IBM Plex Serif",
            font_size=208.333,
            fill="#33519e",
            font_weight="500",
        ),
    )

    assert (
        '<tspan dominant-baseline="text-before-edge" '
        'letter-spacing="-2">Swift</tspan>' in rendered
    )
    assert (
        '<tspan dominant-baseline="text-before-edge" '
        'letter-spacing="-0.8"> 6.3</tspan>' in rendered
    )


def test_render_cover_text_accepts_spans_with_dx() -> None:
    rendered = _render_cover_text(
        (
            CoverTextSpan("Swift", dx=4),
            CoverTextSpan(" 6.3", dx=-1.5),
        ),
        x=104.81,
        y=335.69,
        style=CoverTextStyle(
            font_family="IBM Plex Serif",
            font_size=208.333,
            fill="#33519e",
            font_weight="500",
        ),
    )

    assert (
        '<tspan dominant-baseline="text-before-edge" '
        'dx="4">Swift</tspan>' in rendered
    )
    assert (
        '<tspan dominant-baseline="text-before-edge" '
        'dx="-1.5"> 6.3</tspan>' in rendered
    )


def test_render_cover_page_uses_release_cover_layers(
    tmp_path: Path,
) -> None:
    renderer = EPUBRenderer(tmp_path, {})
    rendered = renderer.render_cover_page(
        DocumentEntry(
            key="cover",
            title="Cover",
            subtitle=None,
            href="cover.xhtml",
            directory=None,
        ),
        "6.3",
        CoverPageOptions(
            book_title="The Swift Programming Language",
            cover_banner=("RELEASE VERSION", "#33519e"),
        ),
    )

    assert '<rect x="0" y="0" width="1440" height="153"' in rendered
    assert 'fill="#33519e"' in rendered
    assert 'x="114.12" y="37.47"' in rendered
    assert ">RELEASE VERSION</text>" in rendered
    assert 'x="107.81" y="233.67"' in rendered
    assert ">The</text>" in rendered
    assert 'x="104.81" y="355.69"' in rendered
    assert ">Swift</text>" in rendered
    assert 'x="108.81" y="567.77"' in rendered
    assert ">Programming</text>" in rendered
    assert 'x="108.81" y="740.77"' in rendered
    assert ">Language</text>" in rendered
    assert 'x="111.81" y="1003.95"' in rendered
    assert ">Swift 6.3</text>" in rendered


def test_render_cover_page_uses_beta_cover_color(tmp_path: Path) -> None:
    renderer = EPUBRenderer(tmp_path, {})
    rendered = renderer.render_cover_page(
        DocumentEntry(
            key="cover",
            title="Cover",
            subtitle=None,
            href="cover.xhtml",
            directory=None,
        ),
        "6.3 beta",
        CoverPageOptions(
            book_title="The Swift Programming Language",
            cover_banner=("BETA VERSION", "#d94a2b"),
        ),
    )

    assert ">BETA VERSION</text>" in rendered
    assert 'fill="#d94a2b"' in rendered
    assert 'fill="#d94a2b">Swift 6.3</text>' in rendered


def test_render_cover_page_keeps_lowercase_beta_for_nightly(
    tmp_path: Path,
) -> None:
    renderer = EPUBRenderer(tmp_path, {})
    rendered = renderer.render_cover_page(
        DocumentEntry(
            key="cover",
            title="Cover",
            subtitle=None,
            href="cover.xhtml",
            directory=None,
        ),
        "6.3 Beta",
        CoverPageOptions(
            book_title="The Swift Programming Language",
            cover_banner=("NIGHTLY EDITION", "#8e3fa9"),
            cover_variant="nightly",
        ),
    )

    assert ">NIGHTLY EDITION</text>" in rendered
    assert 'fill="#8e3fa9">Swift 6.3 beta</text>' in rendered


def test_render_cover_page_does_not_add_beta_for_nightly(
    tmp_path: Path,
) -> None:
    renderer = EPUBRenderer(tmp_path, {})
    rendered = renderer.render_cover_page(
        DocumentEntry(
            key="cover",
            title="Cover",
            subtitle=None,
            href="cover.xhtml",
            directory=None,
        ),
        "6.3",
        CoverPageOptions(
            book_title="The Swift Programming Language",
            cover_banner=("NIGHTLY EDITION", "#8e3fa9"),
            cover_variant="nightly",
        ),
    )

    assert 'fill="#8e3fa9">Swift 6.3</text>' in rendered
    assert "Swift 6.3 beta" not in rendered


def test_epub_css_does_not_override_svg_cover_colors() -> None:
    css = (EPUB_REFERENCE_DIR / "epub.css").read_text(encoding="utf-8")

    assert 'font-family: "IBM Plex Sans";' in css
    assert 'url("fonts/IBMPlexSans-Medium.ttf")' in css
    assert 'font-family: "IBM Plex Serif";' in css
    assert 'url("fonts/IBMPlexSerif-Regular.ttf")' in css
    assert 'url("fonts/IBMPlexSerif-Medium.ttf")' in css
    assert 'url("fonts/IBMPlexSerif-Italic.ttf")' in css
    assert ".edition-notice-page" in css
    assert ".cover-canvas-svg .cover-title-text" not in css
    assert ".cover-canvas-svg .cover-subtitle-text" not in css
