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
from typing import TYPE_CHECKING

from swift_book_pdf.core.blocks.models import (
    Block,
    CodeBlock,
    Header2Block,
    Header3Block,
    Header4Block,
    ImageBlock,
    NoteBlock,
    OrderedListBlock,
    ParagraphBlock,
    TableBlock,
    TermListBlock,
    UnorderedListBlock,
)
from swift_book_pdf.epub.anchors import anchor_for_heading, part_section_id
from swift_book_pdf.epub.paths import relative_href

from .code import render_code_block
from .grammar import render_grammar_block
from .images import AssetCatalog, render_image_block
from .inline import render_inline
from .notices import render_notices_xhtml

if TYPE_CHECKING:
    from pathlib import Path

    from swift_book_pdf.core.document import (
        DocumentEntry,
        PartEntry,
        SourceDocument,
    )
    from swift_book_pdf.epub.models import ImageAsset
    from swift_book_pdf.epub.render.links import LinkResolver


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
        return self._wrap_xhtml_document(
            part.title, part.href, body, body_class="part-body"
        )

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
        self,
        title: str,
        href: str,
        body_html: str,
        body_class: str | None = None,
    ) -> str:
        css_href = html.escape(relative_href(href, "_static/epub.css"))
        pygments_href = html.escape(
            relative_href(href, "_static/pygments.css")
        )
        body_attr = f' class="{html.escape(body_class)}"' if body_class else ""
        return f"""<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head>
    <meta charset="utf-8" />
    <title>{html.escape(title)}</title>
    <link rel="stylesheet" href="{css_href}" type="text/css" />
    <link rel="stylesheet" href="{pygments_href}" type="text/css" />
  </head>
  <body{body_attr}>
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
                + render_inline(
                    " ".join(block.lines), current_href, link_resolver
                )
                + "</p>"
            )
        elif isinstance(block, CodeBlock):
            rendered_block = render_code_block(block.lines)
        elif isinstance(block, ImageBlock):
            rendered_block = render_image_block(
                block,
                current_href,
                image_assets,
                self.asset_catalog,
            )
        elif isinstance(block, OrderedListBlock):
            items = "".join(
                "<li><p>"
                + render_inline(item, current_href, link_resolver)
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
                    + render_inline(item.label, current_href, link_resolver)
                    + "</dt><dd><p>"
                    + render_inline(item.content, current_href, link_resolver)
                    + "</p></dd>"
                )
                for item in block.items
            )
            rendered_block = f'<dl class="simple">{items}</dl>'
        elif isinstance(block, TableBlock):
            header_cells = "".join(
                f"<th>{render_inline(cell, current_href, link_resolver)}</th>"
                for cell in block.rows[0]
            )
            body_rows = "".join(
                "<tr>"
                + "".join(
                    f"<td>{render_inline(cell, current_href, link_resolver)}</td>"
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

    def _render_note_block(
        self,
        block: NoteBlock,
        current_href: str,
        link_resolver: LinkResolver,
        image_assets: dict[str, ImageAsset],
    ) -> str:
        if block.label.lower().startswith("grammar of "):
            return render_grammar_block(
                block,
                current_href,
                self.grammar_targets,
                self._grammar_anchor_counts,
            )

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
