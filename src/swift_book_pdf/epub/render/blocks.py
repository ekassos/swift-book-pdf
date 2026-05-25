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

"""Backend-neutral block rendering to EPUB XHTML."""

from __future__ import annotations

import html
from dataclasses import dataclass
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
from swift_book_pdf.epub.anchors import anchor_for_heading
from swift_book_pdf.epub.grammar_rules import is_grammar_note_label

from .code_blocks import render_code_block
from .grammar import render_grammar_block
from .images import render_image_block
from .inline import render_inline

if TYPE_CHECKING:
    from swift_book_pdf.epub.assets import AssetCatalog, ImageAsset
    from swift_book_pdf.epub.render.links import LinkResolver


@dataclass
class RenderContext:
    """State shared while rendering one EPUB document.

    Attributes:
        current_href: Href of the document currently being rendered.
        link_resolver: Resolver for `<doc:...>` links.
        image_assets: Mutable collection of image assets referenced so far.
        asset_catalog: Source asset lookup table.
        grammar_targets: Map from grammar terms to target hrefs.
        grammar_anchor_counts: Per-document grammar anchor counters.
    """

    current_href: str
    link_resolver: LinkResolver
    image_assets: dict[str, ImageAsset]
    asset_catalog: AssetCatalog
    grammar_targets: dict[str, str]
    grammar_anchor_counts: dict[str, int]


class BlockRenderer:
    """Render parsed Swift Book blocks into XHTML snippets."""

    def __init__(self, context: RenderContext) -> None:
        """Create a renderer with document-local rendering context."""
        self.context = context

    def render_blocks(
        self,
        blocks: list[Block],
        initial_level: int,
    ) -> list[str]:
        """Render block sequence and close nested heading sections."""
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
                    '<div class="section" '
                    f'id="{html.escape(anchor_for_heading(heading_title))}">'
                )
                rendered.append(
                    f'<h{target_level} class="section-title">'
                    f"{html.escape(heading_title)}</h{target_level}>"
                )
                current_level = target_level
                continue

            rendered.append(self._render_block(block))

        while current_level > initial_level:
            rendered.append("</div>")
            current_level -= 1

        return rendered

    def _render_block(self, block: Block) -> str:
        """Dispatch one parsed block to the matching EPUB renderer."""
        if isinstance(block, ParagraphBlock):
            rendered_block = self._render_paragraph_block(block)
        elif isinstance(block, CodeBlock):
            rendered_block = render_code_block(block.lines)
        elif isinstance(block, ImageBlock):
            rendered_block = render_image_block(
                block,
                self.context.current_href,
                self.context.image_assets,
                self.context.asset_catalog,
            )
        elif isinstance(block, OrderedListBlock):
            rendered_block = self._render_ordered_list_block(block)
        elif isinstance(block, UnorderedListBlock):
            rendered_block = self._render_unordered_list_block(block)
        elif isinstance(block, TermListBlock):
            rendered_block = self._render_term_list_block(block)
        elif isinstance(block, TableBlock):
            rendered_block = self._render_table_block(block)
        elif isinstance(block, NoteBlock):
            rendered_block = self._render_note_block(block)
        else:
            raise ValueError(f"Unsupported EPUB block type: {block.type}")
        return rendered_block

    def _render_paragraph_block(self, block: ParagraphBlock) -> str:
        """Render a paragraph block."""
        return (
            "<p>"
            + render_inline(
                " ".join(block.lines),
                self.context.current_href,
                self.context.link_resolver,
            )
            + "</p>"
        )

    def _render_ordered_list_block(self, block: OrderedListBlock) -> str:
        """Render a flat ordered-list block."""
        items = "".join(
            "<li><p>"
            + render_inline(
                item,
                self.context.current_href,
                self.context.link_resolver,
            )
            + "</p></li>"
            for item in block.items
        )
        return f'<ol class="arabic simple">{items}</ol>'

    def _render_unordered_list_block(self, block: UnorderedListBlock) -> str:
        """Render an unordered list with nested block content."""
        list_items: list[str] = []
        for item_blocks in block.items:
            item_html = "".join(
                self._render_block(sub_block) for sub_block in item_blocks
            )
            list_items.append(f"<li>{item_html}</li>")
        return '<ul class="simple">' + "".join(list_items) + "</ul>"

    def _render_term_list_block(self, block: TermListBlock) -> str:
        """Render a Swift grammar term-list block."""
        items = "".join(
            (
                "<dt>"
                + render_inline(
                    item.label,
                    self.context.current_href,
                    self.context.link_resolver,
                )
                + "</dt><dd><p>"
                + render_inline(
                    item.content,
                    self.context.current_href,
                    self.context.link_resolver,
                )
                + "</p></dd>"
            )
            for item in block.items
        )
        return f'<dl class="simple">{items}</dl>'

    def _render_table_block(self, block: TableBlock) -> str:
        """Render a Markdown table block."""
        header_cells = "".join(
            "<th>"
            + render_inline(
                cell,
                self.context.current_href,
                self.context.link_resolver,
            )
            + "</th>"
            for cell in block.rows[0]
        )
        body_rows = "".join(
            "<tr>"
            + "".join(
                "<td>"
                + render_inline(
                    cell,
                    self.context.current_href,
                    self.context.link_resolver,
                )
                + "</td>"
                for cell in row
            )
            + "</tr>"
            for row in block.rows[1:]
        )
        return (
            '<table class="book-table">'
            f"<thead><tr>{header_cells}</tr></thead>"
            f"<tbody>{body_rows}</tbody></table>"
        )

    def _render_note_block(self, block: NoteBlock) -> str:
        """Render a Swift Book aside or grammar block."""
        if is_grammar_note_label(block.label):
            return render_grammar_block(
                block,
                self.context.current_href,
                self.context.grammar_targets,
                self.context.grammar_anchor_counts,
            )

        body = "".join(
            self._render_block(sub_block) for sub_block in block.blocks
        )
        return (
            '<div class="aside note">'
            f'<p class="aside-title">{html.escape(block.label)}</p>'
            f"{body}</div>"
        )


def _heading_level(block: Block) -> int | None:
    """Return the EPUB heading level represented by a heading block."""
    if isinstance(block, Header2Block):
        return 2
    if isinstance(block, Header3Block):
        return 3
    if isinstance(block, Header4Block):
        return 4
    return None


def _heading_text(block: Header2Block | Header3Block | Header4Block) -> str:
    """Return display text from a heading block."""
    return block.content
