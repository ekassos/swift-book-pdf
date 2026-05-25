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

from dataclasses import dataclass
from typing import TYPE_CHECKING

from swift_book_pdf.epub.constants import DEFAULT_BOOK_TITLE, NAV_DOC_FILE_NAME
from swift_book_pdf.epub.package.workspace import write_text
from swift_book_pdf.epub.paths import relative_href
from swift_book_pdf.epub.templating import render_epub_template

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


@dataclass(frozen=True)
class NavItem:
    """A visible table-of-contents item for the EPUB nav document."""

    href: str
    """Navigation-document-relative href for the item target."""

    title: str
    """Display title for the item link."""

    children: tuple[NavItem, ...] = ()
    """Nested child items displayed under this item."""


@dataclass(frozen=True)
class LandmarkItem:
    """A landmark entry for EPUB reader navigation."""

    epub_type: str
    """EPUB semantic type for the landmark link."""

    href: str
    """Navigation-document-relative href for the landmark target."""

    title: str
    """Display title for the landmark link."""


def write_nav_file(
    workspace: Path,
    front_back_matter: FrontBackMatter,
    parts: list[PartEntry],
) -> None:
    """Write the EPUB 3 navigation document to the workspace.

    The navigation document contains both the visible table of contents and
    Apple Books landmarks. Reader start falls back from the first body part to
    notices, then cover, then the nav document itself for degenerate builds.

    Args:
        workspace: Root temporary EPUB workspace.
        front_back_matter: Optional generated cover and notices documents.
        parts: Top-level book parts and their child chapter entries.
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
    toc_items = _build_toc_items(front_back_matter, parts)
    landmarks = _build_landmarks(
        front_back_matter,
        parts,
        reader_start_relative_href,
        cover_relative_href,
    )
    rendered = render_epub_template(
        "nav.xhtml.j2",
        {
            "toc_items": toc_items,
            "landmarks": landmarks,
        },
    )
    write_text(workspace, NAV_DOC_FILE_NAME, rendered)


def _build_toc_items(
    front_back_matter: FrontBackMatter,
    parts: list[PartEntry],
) -> tuple[NavItem, ...]:
    """Build visible table-of-contents items for the nav template.

    Args:
        front_back_matter: Optional generated cover and notices documents.
        parts: Top-level bodymatter parts and their child chapter entries.

    Returns:
        Ordered nav items containing cover, bodymatter, and notices entries.
    """
    cover = front_back_matter.cover
    notices = front_back_matter.notices
    items: list[NavItem] = []
    if cover is not None:
        items.append(
            NavItem(
                href=relative_href(NAV_DOC_FILE_NAME, cover.href),
                title=cover.title,
            )
        )
    items.extend(
        (
            NavItem(
                href=relative_href(NAV_DOC_FILE_NAME, part.href),
                title=part.title,
                children=tuple(
                    NavItem(
                        href=relative_href(NAV_DOC_FILE_NAME, child.href),
                        title=child.title,
                    )
                    for child in part.children
                ),
            )
        )
        for part in parts
    )
    if notices is not None:
        items.append(
            NavItem(
                href=relative_href(NAV_DOC_FILE_NAME, notices.href),
                title=notices.title,
            )
        )
    return tuple(items)


def _build_landmarks(
    front_back_matter: FrontBackMatter,
    parts: list[PartEntry],
    reader_start_relative_href: str,
    cover_relative_href: str | None,
) -> tuple[LandmarkItem, ...]:
    """Build EPUB landmarks for reader navigation.

    Args:
        front_back_matter: Optional generated cover and notices documents.
        parts: Top-level bodymatter parts, used to label the bodymatter entry.
        reader_start_relative_href: Navigation-document-relative start href.
        cover_relative_href: Navigation-document-relative cover href, if any.

    Returns:
        Ordered landmark entries for reader start, cover, bodymatter, and
        acknowledgments when available.
    """
    notices = front_back_matter.notices
    items = [
        LandmarkItem(
            epub_type="ibooks:reader-start-page",
            href=reader_start_relative_href,
            title="Start Reading",
        )
    ]
    if cover_relative_href is not None:
        items.append(
            LandmarkItem(
                epub_type="cover",
                href=cover_relative_href,
                title="Cover",
            )
        )
    items.append(
        LandmarkItem(
            epub_type="bodymatter",
            href=reader_start_relative_href,
            title=parts[0].title if parts else DEFAULT_BOOK_TITLE,
        )
    )
    if notices is not None:
        items.append(
            LandmarkItem(
                epub_type="acknowledgements",
                href=relative_href(NAV_DOC_FILE_NAME, notices.href),
                title="Acknowledgments",
            )
        )
    return tuple(items)
