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

"""OPF package document rendering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from swift_book_pdf.epub.package.manifest import build_manifest_items
from swift_book_pdf.epub.package.metadata import build_metadata
from swift_book_pdf.epub.package.workspace import write_text
from swift_book_pdf.epub.templating import render_epub_template

if TYPE_CHECKING:
    from pathlib import Path

    from swift_book_pdf.core.document import DocumentEntry
    from swift_book_pdf.epub.assets import ImageAsset
    from swift_book_pdf.epub.config import EPUBConfig


@dataclass(frozen=True)
class OPFPackageInput:
    """Inputs needed to render the OPF package document.

    Attributes:
        config: Resolved EPUB build configuration.
        book_title: Effective book title.
        documents: Rendered documents in spine order.
        image_assets: Source image assets copied into the package.
        publication_identifier: EPUB publication identifier.
        has_cover_asset: Whether the package includes an outer cover image.
    """

    config: EPUBConfig
    book_title: str
    documents: list[DocumentEntry]
    image_assets: dict[str, ImageAsset]
    publication_identifier: str
    has_cover_asset: bool


@dataclass(frozen=True)
class SpineItem:
    """One OPF spine item."""

    idref: str
    """Manifest item ID referenced by the spine."""


def write_content_opf_file(
    workspace: Path,
    package_input: OPFPackageInput,
) -> None:
    """Write `content.opf` to the EPUB workspace.

    Args:
        workspace: Temporary EPUB workspace root.
        package_input: Data needed to render metadata, manifest, and spine.
    """
    modified = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    content_opf = render_epub_template(
        "content.opf.j2",
        {
            "metadata": build_metadata(package_input, modified),
            "manifest_items": build_manifest_items(package_input),
            "spine_items": _build_spine_items(package_input),
        },
    )
    write_text(workspace, "content.opf", content_opf)


def _build_spine_items(
    package_input: OPFPackageInput,
) -> tuple[SpineItem, ...]:
    """Build OPF spine entries for package documents.

    Args:
        package_input: Inputs containing documents in spine order.

    Returns:
        Spine items whose idrefs match document manifest IDs.
    """
    return tuple(
        SpineItem(idref=f"epub-doc-{index}")
        for index, _ in enumerate(package_input.documents)
    )
