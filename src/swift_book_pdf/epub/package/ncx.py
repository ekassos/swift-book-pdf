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

from swift_book_pdf.epub.constants import NCX_FILE_NAME
from swift_book_pdf.epub.package.workspace import write_text

if TYPE_CHECKING:
    from pathlib import Path

    from swift_book_pdf.core.document import PartEntry
    from swift_book_pdf.epub.package.nav import FrontBackMatter


def write_toc_ncx_file(
    workspace: Path,
    publication_identifier: str,
    front_back_matter: FrontBackMatter,
    parts: list[PartEntry],
    book_title: str,
) -> None:
    cover = front_back_matter.cover
    notices = front_back_matter.notices
    part_navpoints: list[str] = []
    navpoint_index = 1
    if cover is not None:
        cover_navpoint, navpoint_index = _build_ncx_navpoint_tree(
            navpoint_index,
            cover.title,
            cover.href,
        )
        part_navpoints.append(cover_navpoint)
    for part in parts:
        part_navpoint, navpoint_index = _build_ncx_navpoint_tree(
            navpoint_index,
            part.title,
            part.href,
            [(child.title, child.href) for child in part.children],
        )
        part_navpoints.append(part_navpoint)
    if notices is not None:
        notices_navpoint, _ = _build_ncx_navpoint_tree(
            navpoint_index,
            notices.title,
            notices.href,
        )
        part_navpoints.append(notices_navpoint)
    write_text(
        workspace,
        NCX_FILE_NAME,
        """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content=\""""
        + html.escape(publication_identifier)
        + """\"/>
    <meta name="dtb:depth" content="2"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>"""
        + html.escape(book_title)
        + """</text>
  </docTitle>
  <navMap>
"""
        + "\n".join(part_navpoints)
        + """
  </navMap>
</ncx>
""",
    )


def _build_ncx_navpoint_tree(
    index: int,
    title: str,
    href: str,
    children: list[tuple[str, str]] | None = None,
) -> tuple[str, int]:
    current_index = index
    next_index = index + 1
    child_navpoints: list[str] = []
    for child_title, child_href in children or []:
        child_navpoint, next_index = _build_ncx_navpoint_tree(
            next_index,
            child_title,
            child_href,
        )
        child_navpoints.append(child_navpoint)

    child_lines = "".join(child_navpoints)
    navpoint = (
        f'    <navPoint id="navPoint{current_index}" playOrder="{current_index}">\n'
        "      <navLabel>\n"
        f"        <text>{html.escape(title)}</text>\n"
        "      </navLabel>\n"
        f'      <content src="{html.escape(href)}" />\n'
        f"{child_lines}"
        "    </navPoint>"
    )
    return navpoint, next_index
