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

from swift_book_pdf.epub.anchors import part_section_id
from swift_book_pdf.epub.assets import AssetCatalog
from swift_book_pdf.epub.paths import relative_href

from .blocks import BlockRenderer, RenderContext
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
        document = source_document.entry
        context = RenderContext(
            current_href=document.href,
            link_resolver=link_resolver,
            image_assets=image_assets,
            asset_catalog=self.asset_catalog,
            grammar_targets=self.grammar_targets,
            grammar_anchor_counts={},
        )
        body_parts = [
            f'  <div class="section" id="{html.escape(part_section_id(document.title))}">',
            f"<h1>{html.escape(document.title)}</h1>",
        ]
        body_parts.extend(
            BlockRenderer(context).render_blocks(source_document.blocks, 1)
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
