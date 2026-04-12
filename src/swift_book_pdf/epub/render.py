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

from __future__ import annotations

import html
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import SwiftLexer

from swift_book_pdf.notices import render_notices_xhtml
from swift_book_pdf.schema import (
    Block,
    CodeBlock,
    DocumentEntry,
    Header2Block,
    Header3Block,
    Header4Block,
    ImageAsset,
    ImageBlock,
    NoteBlock,
    OrderedListBlock,
    ParagraphBlock,
    PartEntry,
    SourceDocument,
    TableBlock,
    TermListBlock,
    UnorderedListBlock,
)

from .constants import (
    CODE_PLACEHOLDER_PATTERN,
    DOC_LINK_PATTERN,
    EMPHASIS_PATTERN,
    EPUB_COVER_LOGO_DARK_FILE_NAME,
    EPUB_COVER_LOGO_FILE_NAME,
    STRONG_PATTERN,
)
from .helpers import (
    anchor_for_heading,
    cover_edition_text,
    image_destination_name,
    media_type_for_path,
    normalize_asset_key,
    part_section_id,
    relative_href,
)

logger = logging.getLogger(__name__)

MARKDOWN_WRAPPED_TERM_LENGTH = 2
WRAPPING_PLACEHOLDER_MIN_LENGTH = 28
INLINE_CODE_PADDING_LENGTH = 2

if TYPE_CHECKING:
    from collections.abc import Callable


class AssetCatalog:
    def __init__(self, asset_path: Path) -> None:
        self._assets = self._build_asset_pairs(asset_path)

    def resolve(self, image_name: str) -> tuple[Path, Path | None]:
        key = normalize_asset_key(Path(image_name).stem)
        asset_pair = self._assets.get(key)
        if asset_pair is None:
            raise FileNotFoundError(f"Missing image asset: {image_name}")
        return asset_pair

    def _build_asset_pairs(
        self, asset_path: Path
    ) -> dict[str, tuple[Path, Path | None]]:
        asset_pairs: dict[str, tuple[Path, Path | None]] = {}
        for asset in asset_path.iterdir():
            if not asset.is_file():
                continue
            key = normalize_asset_key(asset.stem)
            light_asset, dark_asset = asset_pairs.get(key, (None, None))
            if "~dark" in asset.stem:
                dark_asset = asset
            else:
                light_asset = asset
            if light_asset is not None:
                asset_pairs[key] = (light_asset, dark_asset)
        return asset_pairs


class LinkResolver:
    def __init__(self, documents: list[DocumentEntry]) -> None:
        self.documents = {document.key: document for document in documents}

    def render_doc_link(self, current_href: str, target: str) -> str:
        chapter_key, _, fragment = target.partition("#")
        document = self.documents.get(chapter_key.lower())
        if document is None:
            return html.escape(target)

        if fragment:
            link_text = document.heading_map.get(
                fragment, fragment.replace("-", " ")
            )
            href = f"{document.href}#{fragment}"
        else:
            link_text = document.title
            href = document.href

        return (
            f'<a href="{html.escape(relative_href(current_href, href))}">'
            f"{html.escape(link_text)}</a>"
        )


class EPUBRenderer:
    def __init__(
        self,
        asset_path: Path,
        grammar_targets: dict[str, str],
        original_work_copyright_year_range: tuple[int, int] | None = None,
    ) -> None:
        self.asset_catalog = AssetCatalog(asset_path)
        self.grammar_targets = grammar_targets
        self._grammar_anchor_counts: dict[str, int] = {}
        self.original_work_copyright_year_range = (
            original_work_copyright_year_range
        )

    def render_part_page(self, part: PartEntry) -> str:
        section_id = part_section_id(part.title)
        body = (
            f'  <div class="section part-page" id="{html.escape(section_id)}">\n'
            f"<h1>{html.escape(part.title)}</h1>\n"
            "</div>\n"
        )
        return self._wrap_xhtml_document(part.title, part.href, body)

    def render_cover_page(
        self,
        document: DocumentEntry,
        book_title: str,
        version_info: str | None,
    ) -> str:
        edition_text = cover_edition_text(version_info)
        logo_light_href = html.escape(
            relative_href(document.href, EPUB_COVER_LOGO_FILE_NAME)
        )
        logo_dark_href = html.escape(
            relative_href(document.href, EPUB_COVER_LOGO_DARK_FILE_NAME)
        )
        subtitle_html = (
            f'      <h2 id="title3">{html.escape(edition_text)}</h2>\n'
            if edition_text
            else ""
        )
        return f"""<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head>
    <meta charset="utf-8" />
    <title>{html.escape(book_title)}</title>
    <link rel="stylesheet" href="{html.escape(relative_href(document.href, "_static/epub.css"))}" type="text/css" />
  </head>
  <body class="coverpage" id="coverpage">
    <div class="cover-shell">
      <div class="theme-image cover-logo-wrap">
        <img class="align-center image-light cover-logo" src="{logo_light_href}" alt="Swift logo" />
        <img class="align-center image-dark cover-logo" src="{logo_dark_href}" alt="Swift logo" />
      </div>
      <div class="titleContainer">
        <h1 id="title1a">The Swift</h1>
        <h1 id="title1b">Programming</h1>
        <h1 id="title1c">Language</h1>
{subtitle_html}      </div>
    </div>
  </body>
</html>
"""

    def render_chapter_page(
        self,
        source_document: SourceDocument,
        link_resolver: LinkResolver,
        image_assets: dict[str, ImageAsset],
    ) -> str:
        self._grammar_anchor_counts = {}
        document = source_document.entry
        body_parts = [
            f'  <div class="section" id="{html.escape(part_section_id(document.title))}">',
            f"<h1>{html.escape(document.title)}</h1>",
        ]
        body_parts.extend(
            self._render_blocks(
                source_document.blocks,
                1,
                document.href,
                link_resolver,
                image_assets,
            )
        )
        body_parts.append("</div>\n")
        return self._wrap_xhtml_document(
            document.title,
            document.href,
            "\n".join(body_parts),
        )

    def render_notices_page(self, document: DocumentEntry) -> str:
        body = render_notices_xhtml(
            document.title, self.original_work_copyright_year_range
        )
        return self._wrap_xhtml_document(document.title, document.href, body)

    def _wrap_xhtml_document(
        self, title: str, href: str, body_html: str
    ) -> str:
        css_href = html.escape(relative_href(href, "_static/epub.css"))
        pygments_href = html.escape(
            relative_href(href, "_static/pygments.css")
        )
        return f"""<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head>
    <meta charset="utf-8" />
    <title>{html.escape(title)}</title>
    <link rel="stylesheet" href="{css_href}" type="text/css" />
    <link rel="stylesheet" href="{pygments_href}" type="text/css" />
  </head>
  <body>
    <main class="book-root" role="main">
{body_html}
    </main>
  </body>
</html>
"""

    def _render_blocks(
        self,
        blocks: list[Block],
        initial_level: int,
        current_href: str,
        link_resolver: LinkResolver,
        image_assets: dict[str, ImageAsset],
    ) -> list[str]:
        rendered: list[str] = []
        current_level = initial_level

        for block in blocks:
            target_level = _heading_level(block)
            if target_level is not None:
                heading_title = _heading_text(block)
                while current_level >= target_level:
                    rendered.append("</div>")
                    current_level -= 1
                rendered.append(
                    f'<div class="section" id="{html.escape(anchor_for_heading(heading_title))}">'
                )
                rendered.append(
                    f'<h{target_level} class="section-title">{html.escape(heading_title)}</h{target_level}>'
                )
                current_level = target_level
                continue

            rendered.append(
                self._render_block(
                    block, current_href, link_resolver, image_assets
                )
            )

        while current_level > initial_level:
            rendered.append("</div>")
            current_level -= 1

        return rendered

    def _render_block(
        self,
        block: Block,
        current_href: str,
        link_resolver: LinkResolver,
        image_assets: dict[str, ImageAsset],
    ) -> str:
        rendered_block: str
        if isinstance(block, ParagraphBlock):
            rendered_block = (
                "<p>"
                + _render_inline(
                    " ".join(block.lines), current_href, link_resolver
                )
                + "</p>"
            )
        elif isinstance(block, CodeBlock):
            rendered_block = self._render_code_block(block.lines)
        elif isinstance(block, ImageBlock):
            rendered_block = self._render_image_block(
                block, current_href, image_assets
            )
        elif isinstance(block, OrderedListBlock):
            items = "".join(
                "<li><p>"
                + _render_inline(item, current_href, link_resolver)
                + "</p></li>"
                for item in block.items
            )
            rendered_block = f'<ol class="arabic simple">{items}</ol>'
        elif isinstance(block, UnorderedListBlock):
            list_items: list[str] = []
            for item_blocks in block.items:
                item_html = "".join(
                    self._render_block(
                        sub_block,
                        current_href,
                        link_resolver,
                        image_assets,
                    )
                    for sub_block in item_blocks
                )
                list_items.append(f"<li>{item_html}</li>")
            rendered_block = (
                '<ul class="simple">' + "".join(list_items) + "</ul>"
            )
        elif isinstance(block, TermListBlock):
            items = "".join(
                (
                    "<dt>"
                    + _render_inline(item.label, current_href, link_resolver)
                    + "</dt><dd><p>"
                    + _render_inline(item.content, current_href, link_resolver)
                    + "</p></dd>"
                )
                for item in block.items
            )
            rendered_block = f'<dl class="simple">{items}</dl>'
        elif isinstance(block, TableBlock):
            header_cells = "".join(
                f"<th>{_render_inline(cell, current_href, link_resolver)}</th>"
                for cell in block.rows[0]
            )
            body_rows = "".join(
                "<tr>"
                + "".join(
                    f"<td>{_render_inline(cell, current_href, link_resolver)}</td>"
                    for cell in row
                )
                + "</tr>"
                for row in block.rows[1:]
            )
            rendered_block = (
                '<table class="book-table">'
                f"<thead><tr>{header_cells}</tr></thead>"
                f"<tbody>{body_rows}</tbody></table>"
            )
        elif isinstance(block, NoteBlock):
            rendered_block = self._render_note_block(
                block, current_href, link_resolver, image_assets
            )
        else:
            raise ValueError(f"Unsupported EPUB block type: {block.type}")
        return rendered_block

    def _render_code_block(self, code_lines: list[str]) -> str:
        has_placeholders = any(
            CODE_PLACEHOLDER_PATTERN.search(line) for line in code_lines
        )
        if has_placeholders:
            highlighted_lines = [
                _render_outline_code_line(line) for line in code_lines
            ]
        else:
            highlighted_lines = highlight(
                "\n".join(code_lines),
                SwiftLexer(),
                HtmlFormatter(nowrap=True),
            ).splitlines()
        if not highlighted_lines:
            highlighted_lines = [""]
        items = "".join(
            f"<li>{line or ' '}</li>" for line in highlighted_lines
        )
        block_class = "code-block code-block--outline"
        if not has_placeholders:
            block_class = "code-block"
        return (
            f'<div class="{block_class}">'
            '<div class="code-block__shell"><div class="code-block__frame highlight">'
            f'<ol class="code-block__lines">{items}</ol>'
            "</div></div></div>"
        )

    def _render_image_block(
        self,
        block: ImageBlock,
        current_href: str,
        image_assets: dict[str, ImageAsset],
    ) -> str:
        asset, dark_asset = self.asset_catalog.resolve(block.imgname)
        image_href = self._register_asset(asset, image_assets)
        width = _image_display_width(asset, Path(image_href).name)
        width_attr = (
            f' style="width: {width:.1f}px;"' if width is not None else ""
        )
        alt = html.escape(block.alt or block.imgname)
        if dark_asset is None:
            return (
                f'<img alt="{alt}" class="align-center" '
                f'src="{html.escape(relative_href(current_href, image_href))}"{width_attr} />'
            )

        dark_image_href = self._register_asset(dark_asset, image_assets)
        return (
            '<div class="theme-image">'
            f'<img alt="{alt}" class="align-center image-light" '
            f'src="{html.escape(relative_href(current_href, image_href))}"{width_attr} />'
            f'<img alt="{alt}" class="align-center image-dark" '
            f'src="{html.escape(relative_href(current_href, dark_image_href))}"{width_attr} />'
            "</div>"
        )

    def _register_asset(
        self, asset: Path, image_assets: dict[str, ImageAsset]
    ) -> str:
        href = f"_images/{image_destination_name(asset)}"
        if href not in image_assets:
            image_assets[href] = ImageAsset(
                source_path=asset,
                href=href,
                media_type=media_type_for_path(asset),
            )
        return href

    def _render_note_block(
        self,
        block: NoteBlock,
        current_href: str,
        link_resolver: LinkResolver,
        image_assets: dict[str, ImageAsset],
    ) -> str:
        if block.label.lower().startswith("grammar of "):
            return self._render_grammar_block(block, current_href)

        body = "".join(
            self._render_block(
                sub_block, current_href, link_resolver, image_assets
            )
            for sub_block in block.blocks
        )
        return (
            '<div class="aside note">'
            f'<p class="aside-title">{html.escape(block.label)}</p>'
            f"{body}</div>"
        )

    def _render_grammar_block(
        self, block: NoteBlock, current_href: str
    ) -> str:
        groups: list[str] = []
        for sub_block in block.blocks:
            if not isinstance(sub_block, ParagraphBlock):
                continue
            syntax_lines = [
                self._render_grammar_line(line, current_href)
                for line in sub_block.lines
                if line.strip()
            ]
            if syntax_lines:
                groups.append(
                    '<div class="grammar-group">'
                    + "".join(syntax_lines)
                    + "</div>"
                )

        return (
            '<div class="aside grammar">'
            f'<p class="first aside-title">{html.escape(block.label)}</p>'
            + "".join(groups)
            + "</div>"
        )

    def _render_grammar_line(self, line: str, current_href: str) -> str:
        clean_line = line.strip()
        if clean_line.endswith("\\"):
            clean_line = clean_line[:-1].rstrip()
        if "→" not in clean_line:
            return f"<p>{_render_grammar_fragment(clean_line, current_href, self.grammar_targets)}</p>"

        left, right = (part.strip() for part in clean_line.split("→", 1))
        if _is_wrapped_markdown_term(left):
            left = left[1:-1]
        anchor_id = self._next_grammar_anchor_id(left)
        return (
            '<p class="grammar-rule">'
            f'<span class="grammar-term"><a id="{html.escape(anchor_id)}"></a>{html.escape(left)}</span>'
            '<span class="arrow"> → </span>'
            f"{_render_grammar_fragment(right, current_href, self.grammar_targets)}</p>"
        )

    def _next_grammar_anchor_id(self, term: str) -> str:
        fragment = _grammar_anchor_fragment(term)
        count = self._grammar_anchor_counts.get(fragment, 0) + 1
        self._grammar_anchor_counts[fragment] = count
        if count == 1:
            return f"grammar_{fragment}"
        return f"grammar_{fragment}_{count}"


def _heading_level(block: Block) -> int | None:
    if isinstance(block, Header2Block):
        return 2
    if isinstance(block, Header3Block):
        return 3
    if isinstance(block, Header4Block):
        return 4
    return None


def _heading_text(block: Header2Block | Header3Block | Header4Block) -> str:
    return block.content


def _render_inline(
    text: str, current_href: str, link_resolver: LinkResolver
) -> str:
    placeholders: dict[str, str] = {}
    placeholder_index = 0

    def store(value: str) -> str:
        nonlocal placeholder_index
        token = f"@@INLINE{placeholder_index}@@"
        placeholders[token] = value
        placeholder_index += 1
        return token

    text = DOC_LINK_PATTERN.sub(
        lambda match: store(
            link_resolver.render_doc_link(current_href, match.group(1))
        ),
        text,
    )
    text = _replace_markdown_links(
        text,
        lambda label, href: store(
            '<a href="'
            + html.escape(href)
            + '">'
            + _render_inline_styles(label)
            + "</a>"
        ),
    )
    text = _replace_inline_code_spans(
        text,
        lambda code: store(
            '<code class="inline-code">' + html.escape(code) + "</code>"
        ),
    )
    text = _normalize_prose_punctuation(text)
    text = html.escape(text)
    text = STRONG_PATTERN.sub(r"<strong>\1</strong>", text)
    text = EMPHASIS_PATTERN.sub(r"<em>\1</em>", text)

    for token, value in placeholders.items():
        text = text.replace(html.escape(token), value)

    return text


def _render_inline_styles(text: str) -> str:
    placeholders: dict[str, str] = {}
    placeholder_index = 0

    def store(value: str) -> str:
        nonlocal placeholder_index
        token = f"@@STYLE{placeholder_index}@@"
        placeholders[token] = value
        placeholder_index += 1
        return token

    text = _replace_inline_code_spans(
        text,
        lambda code: store(
            '<code class="inline-code">' + html.escape(code) + "</code>"
        ),
    )
    text = _normalize_prose_punctuation(text)
    text = html.escape(text)
    text = STRONG_PATTERN.sub(r"<strong>\1</strong>", text)
    text = EMPHASIS_PATTERN.sub(r"<em>\1</em>", text)

    for token, value in placeholders.items():
        text = text.replace(html.escape(token), value)

    return text


def _render_grammar_fragment(
    text: str,
    current_href: str,
    grammar_targets: dict[str, str],
) -> str:
    placeholders: dict[str, str] = {}
    placeholder_index = 0

    def store(value: str) -> str:
        nonlocal placeholder_index
        token = f"@@GRAMMAR{placeholder_index}@@"
        placeholders[token] = value
        placeholder_index += 1
        return token

    text = re.sub(
        r"\*\*``\s*(.*?)\s*``\*\*",
        lambda match: store(f"<code>{html.escape(match.group(1))}</code>"),
        text,
    )
    text = re.sub(
        r"\*\*`([^`]+)`\*\*",
        lambda match: store(f"<code>{html.escape(match.group(1))}</code>"),
        text,
    )
    text = _replace_inline_code_spans(
        text,
        lambda code: store(f"<code>{html.escape(code)}</code>"),
    )
    text = EMPHASIS_PATTERN.sub(
        lambda match: store(
            _render_grammar_category(
                match.group(1),
                current_href,
                grammar_targets,
            )
        ),
        text,
    )
    text = html.escape(text)
    text = text.replace(
        "_?_",
        '<span class="grammar-optional">?</span>',
    )

    for token, value in placeholders.items():
        text = text.replace(html.escape(token), value)

    return text


def _render_grammar_category(
    text: str,
    current_href: str,
    grammar_targets: dict[str, str],
) -> str:
    target_href = grammar_targets.get(text)
    if target_href is None:
        return '<span class="grammar-ref">' + html.escape(text) + "</span>"

    return (
        '<span class="grammar-ref">'
        f'<a href="{html.escape(relative_href(current_href, target_href))}">{html.escape(text)}</a>'
        "</span>"
    )


def _render_outline_code_line(line: str) -> str:
    parts: list[str] = []
    last_index = 0

    for match in CODE_PLACEHOLDER_PATTERN.finditer(line):
        prefix = line[last_index : match.start()]
        if prefix:
            parts.append(_highlight_swift_fragment(prefix))
        parts.append(_render_outline_placeholder(match.group(1)))
        last_index = match.end()

    suffix = line[last_index:]
    if suffix:
        parts.append(_highlight_swift_fragment(suffix))

    return "".join(parts)


def extract_grammar_terms(block: NoteBlock) -> list[str]:
    terms: list[str] = []
    for sub_block in block.blocks:
        if not isinstance(sub_block, ParagraphBlock):
            continue
        for line in sub_block.lines:
            term = _extract_grammar_term(line)
            if term is not None:
                terms.append(term)
    return terms


def _extract_grammar_term(line: str) -> str | None:
    clean_line = line.strip()
    if clean_line.endswith("\\"):
        clean_line = clean_line[:-1].rstrip()
    if "→" not in clean_line:
        return None

    left, _ = (part.strip() for part in clean_line.split("→", 1))
    if _is_wrapped_markdown_term(left):
        left = left[1:-1]
    return left


def _grammar_anchor_fragment(term: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", term.strip()).strip("-")


def _render_outline_placeholder(text: str) -> str:
    class_name = "gi"
    if _needs_wrapping_placeholder(text):
        class_name = "gi gi-wrap"
    return f'<span class="{class_name}">{html.escape(text)}</span>'


def _needs_wrapping_placeholder(text: str) -> bool:
    normalized = text.strip()
    return (
        len(normalized) > WRAPPING_PLACEHOLDER_MIN_LENGTH and " " in normalized
    )


def _highlight_swift_fragment(fragment: str) -> str:
    return highlight(
        fragment, SwiftLexer(), HtmlFormatter(nowrap=True)
    ).rstrip("\n")


def _replace_inline_code_spans(text: str, render: Callable[[str], str]) -> str:
    output: list[str] = []
    index = 0

    while index < len(text):
        if (
            text[index] == "\\"
            and index + 1 < len(text)
            and text[index + 1] == "`"
        ):
            output.append("`")
            index += 2
            continue

        if text[index] != "`":
            output.append(text[index])
            index += 1
            continue

        fence_end = index
        while fence_end < len(text) and text[fence_end] == "`":
            fence_end += 1

        fence = text[index:fence_end]
        closing_index = text.find(fence, fence_end)
        if closing_index == -1:
            output.append(fence)
            index = fence_end
            continue

        code = text[fence_end:closing_index]
        if (
            len(code) >= INLINE_CODE_PADDING_LENGTH
            and code[0] == " "
            and code[-1] == " "
            and any(character != " " for character in code)
        ):
            code = code[1:-1]

        output.append(render(code))
        index = closing_index + len(fence)

    return "".join(output)


def _replace_markdown_links(
    text: str, render: Callable[[str, str], str]
) -> str:
    output: list[str] = []
    index = 0

    while index < len(text):
        label_start = text.find("[", index)
        if label_start == -1:
            output.append(text[index:])
            break

        output.append(text[index:label_start])
        label_end = text.find("]", label_start + 1)
        if (
            label_end == -1
            or label_end + 1 >= len(text)
            or text[label_end + 1] != "("
        ):
            output.append(text[label_start])
            index = label_start + 1
            continue

        href_start = label_end + 2
        href_end = href_start
        depth = 1
        while href_end < len(text):
            character = text[href_end]
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0:
                    break
            href_end += 1

        if href_end >= len(text) or depth != 0:
            output.append(text[label_start])
            index = label_start + 1
            continue

        output.append(
            render(
                text[label_start + 1 : label_end], text[href_start:href_end]
            )
        )
        index = href_end + 1

    return "".join(output)


def _normalize_prose_punctuation(text: str) -> str:
    text = re.sub(r"\s*---\s*", "\u2014", text)
    return re.sub(r"--", "\u2013", text)


def _image_display_width(path: Path, file_name: str) -> float | None:
    try:
        with Image.open(path) as image:
            width = image.width
    except OSError:
        logger.warning("Couldn't read image dimensions for %s", path)
        return None

    if "_2x" in file_name or "@2x" in path.stem:
        return width / 2
    return float(width)


def _is_wrapped_markdown_term(text: str) -> bool:
    return (
        text.startswith("*")
        and text.endswith("*")
        and len(text) > MARKDOWN_WRAPPED_TERM_LENGTH
    )
