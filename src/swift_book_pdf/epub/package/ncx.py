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

"""EPUB 2 NCX table-of-contents rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from swift_book_pdf.epub.constants import NCX_FILE_NAME
from swift_book_pdf.epub.package.workspace import write_text
from swift_book_pdf.epub.templating import render_epub_template

if TYPE_CHECKING:
    from pathlib import Path

    from swift_book_pdf.core.document import PartEntry
    from swift_book_pdf.epub.package.nav import FrontBackMatter


@dataclass(frozen=True)
class NavPoint:
    """An NCX navPoint entry."""

    play_order: int
    """One-based NCX play order."""

    title: str
    """Display title for this navPoint."""

    href: str
    """Package href for this navPoint target."""

    children: tuple[NavPoint, ...] = ()
    """Nested child navPoints."""

    @property
    def navpoint_id(self) -> str:
        """ID derived from the NCX play order."""
        return f"navPoint{self.play_order}"


def write_toc_ncx_file(
    workspace: Path,
    publication_identifier: str,
    front_back_matter: FrontBackMatter,
    parts: list[PartEntry],
    book_title: str,
) -> None:
    """Write the NCX table-of-contents file to the workspace.

    Args:
        workspace: Temporary EPUB workspace root.
        publication_identifier: Identifier mirrored from OPF metadata.
        front_back_matter: Optional generated cover and notices documents.
        parts: Top-level book parts and their child chapters.
        book_title: Effective title for the NCX document title.
    """
    navpoints = _build_ncx_navpoints(front_back_matter, parts)
    rendered = render_epub_template(
        "toc.ncx.j2",
        {
            "publication_identifier": publication_identifier,
            "book_title": book_title,
            "navpoints": navpoints,
        },
    )
    write_text(
        workspace,
        NCX_FILE_NAME,
        rendered,
    )


def _build_ncx_navpoints(
    front_back_matter: FrontBackMatter,
    parts: list[PartEntry],
) -> tuple[NavPoint, ...]:
    """Build top-level NCX navPoints.

    Args:
        front_back_matter: Optional generated cover and notices documents.
        parts: Top-level book parts and their child chapter entries.

    Returns:
        Ordered NCX navPoints with stable one-based play orders.
    """
    cover = front_back_matter.cover
    notices = front_back_matter.notices
    navpoints: list[NavPoint] = []
    navpoint_index = 1
    if cover is not None:
        cover_navpoint, navpoint_index = _build_ncx_navpoint_tree(
            navpoint_index,
            cover.title,
            cover.href,
        )
        navpoints.append(cover_navpoint)
    for part in parts:
        part_navpoint, navpoint_index = _build_ncx_navpoint_tree(
            navpoint_index,
            part.title,
            part.href,
            tuple((child.title, child.href) for child in part.children),
        )
        navpoints.append(part_navpoint)
    if notices is not None:
        notices_navpoint, _ = _build_ncx_navpoint_tree(
            navpoint_index,
            notices.title,
            notices.href,
        )
        navpoints.append(notices_navpoint)
    return tuple(navpoints)


def _build_ncx_navpoint_tree(
    play_order: int,
    title: str,
    href: str,
    children: tuple[tuple[str, str], ...] = (),
) -> tuple[NavPoint, int]:
    """Build one NCX navPoint subtree.

    Args:
        play_order: Current one-based NCX play order.
        title: Display title for this navPoint.
        href: Package href for this navPoint.
        children: Optional child navPoint titles and hrefs.

    Returns:
        Built navPoint and the next available play order.
    """
    next_play_order = play_order + 1
    child_navpoints: list[NavPoint] = []
    for child_title, child_href in children:
        child_navpoint, next_index = _build_ncx_navpoint_tree(
            next_play_order,
            child_title,
            child_href,
        )
        child_navpoints.append(child_navpoint)
        next_play_order = next_index

    navpoint = NavPoint(
        play_order=play_order,
        title=title,
        href=href,
        children=tuple(child_navpoints),
    )
    return navpoint, next_play_order
