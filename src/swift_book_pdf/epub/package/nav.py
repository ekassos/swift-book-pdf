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

"""EPUB navigation document rendering."""

from __future__ import annotations

import html
from dataclasses import dataclass
from typing import TYPE_CHECKING

from swift_book_pdf.epub.constants import DEFAULT_BOOK_TITLE, NAV_DOC_FILE_NAME
from swift_book_pdf.epub.package.workspace import write_text
from swift_book_pdf.epub.paths import relative_href

if TYPE_CHECKING:
    from pathlib import Path

    from swift_book_pdf.core.document import DocumentEntry, PartEntry


@dataclass(frozen=True)
class FrontBackMatter:
    """Optional front and back matter documents.

    Attributes:
        cover: Optional generated cover document.
        notices: Optional generated notices document.
    """

    cover: DocumentEntry | None
    notices: DocumentEntry | None


def write_nav_file(
    workspace: Path,
    front_back_matter: FrontBackMatter,
    parts: list[PartEntry],
) -> None:
    """Write the EPUB 3 navigation document to the workspace.

    The navigation document contains both the visible table of contents and
    Apple Books landmarks. Reader start falls back from the first body part to
    notices, then cover, then the nav document itself for degenerate builds.
    """
    cover = front_back_matter.cover
    notices = front_back_matter.notices
    reader_start_href = (
        parts[0].href
        if parts
        else notices.href
        if notices is not None
        else cover.href
        if cover is not None
        else NAV_DOC_FILE_NAME
    )
    reader_start_relative_href = relative_href(
        NAV_DOC_FILE_NAME, reader_start_href
    )
    cover_relative_href = (
        relative_href(NAV_DOC_FILE_NAME, cover.href)
        if cover is not None
        else None
    )
    items = []
    if cover is not None:
        items.append(
            "        <li>\n"
            f'          <a href="{html.escape(cover_relative_href or "")}">{html.escape(cover.title)}</a>\n'
            "        </li>"
        )
    for part in parts:
        chapter_items = "\n".join(
            (
                "            <li>\n"
                f'              <a href="{html.escape(relative_href(NAV_DOC_FILE_NAME, child.href))}">{html.escape(child.title)}</a>\n'
                "            </li>"
            )
            for child in part.children
        )
        items.append(
            "        <li>\n"
            f'          <a href="{html.escape(relative_href(NAV_DOC_FILE_NAME, part.href))}">{html.escape(part.title)}</a>\n'
            "          <ol>\n"
            f"{chapter_items}\n"
            "          </ol>\n"
            "        </li>"
        )
    if notices is not None:
        items.append(
            "        <li>\n"
            f'          <a href="{html.escape(relative_href(NAV_DOC_FILE_NAME, notices.href))}">{html.escape(notices.title)}</a>\n'
            "        </li>"
        )
    write_text(
        workspace,
        NAV_DOC_FILE_NAME,
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      xmlns:ibooks="http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0"
      epub:prefix="ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"
      lang="en" xml:lang="en">
  <head>
    <title>Table of Contents</title>
    <link rel="stylesheet" href="_static/epub.css" type="text/css" />
  </head>
  <body>
    <section>
      <header>
        <h1>Table of Contents</h1>
      </header>
      <nav epub:type="toc" id="toc">
        <ol>
"""
        + "\n".join(items)
        + """
        </ol>
      </nav>
      <nav epub:type="landmarks">
        <h1>Guide</h1>
        <ol>
        <li>
          <a epub:type="ibooks:reader-start-page" href=\""""
        + html.escape(reader_start_relative_href)
        + """\">Start Reading</a>
        </li>
"""
        + (
            """        <li>
          <a epub:type="cover" href=\""""
            + html.escape(cover_relative_href)
            + """\">Cover</a>
        </li>
"""
            if cover_relative_href is not None
            else ""
        )
        + """        <li>
          <a epub:type="bodymatter" href=\""""
        + html.escape(reader_start_relative_href)
        + """\">"""
        + html.escape(parts[0].title if parts else DEFAULT_BOOK_TITLE)
        + """</a>
        </li>
"""
        + (
            """        <li>
          <a epub:type="acknowledgements" href=\""""
            + html.escape(relative_href(NAV_DOC_FILE_NAME, notices.href))
            + """\">Acknowledgments</a>
        </li>
"""
            if notices is not None
            else ""
        )
        + """
        </ol>
      </nav>
    </section>
  </body>
</html>
""",
    )
