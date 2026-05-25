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
from dataclasses import dataclass
from typing import TYPE_CHECKING

from swift_book_pdf.epub.constants import (
    EPUB_COVER_DOC_FILE_NAME,
    NAV_DOC_FILE_NAME,
    NCX_FILE_NAME,
)
from swift_book_pdf.epub.package.static import (
    EPUB_FONT_DIR_NAME,
    EPUB_FONT_FILE_NAMES,
)

if TYPE_CHECKING:
    from swift_book_pdf.epub.package.opf import OPFPackageInput


@dataclass(frozen=True)
class ManifestItem:
    item_id: str
    href: str
    media_type: str
    properties: str | None = None


def build_manifest_items(package_input: OPFPackageInput) -> list[ManifestItem]:
    manifest = [
        ManifestItem(
            item_id="ncx",
            href=NCX_FILE_NAME,
            media_type="application/x-dtbncx+xml",
        ),
        ManifestItem(
            item_id="nav",
            href=NAV_DOC_FILE_NAME,
            media_type="application/xhtml+xml",
            properties="nav",
        ),
    ]
    manifest.extend(_document_manifest_items(package_input))
    manifest.extend(_image_manifest_items(package_input))
    manifest.extend(_static_manifest_items())
    if package_input.has_cover_asset:
        manifest.append(
            ManifestItem(
                item_id="epub-cover",
                href="_static/cover.png",
                media_type="image/png",
                properties="cover-image",
            )
        )
    return manifest


def render_manifest_items(items: list[ManifestItem]) -> str:
    return "\n".join(_format_manifest_item(item) for item in items)


def _document_manifest_items(
    package_input: OPFPackageInput,
) -> list[ManifestItem]:
    return [
        ManifestItem(
            item_id=f"epub-doc-{index}",
            href=document.href,
            media_type="application/xhtml+xml",
            properties=(
                "svg" if document.href == EPUB_COVER_DOC_FILE_NAME else None
            ),
        )
        for index, document in enumerate(package_input.documents)
    ]


def _image_manifest_items(
    package_input: OPFPackageInput,
) -> list[ManifestItem]:
    return [
        ManifestItem(
            item_id=f"epub-image-{index}",
            href=asset.href,
            media_type=asset.media_type,
        )
        for index, asset in enumerate(
            sorted(
                package_input.image_assets.values(),
                key=lambda item: item.href,
            )
        )
    ]


def _static_manifest_items() -> list[ManifestItem]:
    manifest = [
        ManifestItem(
            item_id="epub-style",
            href="_static/epub.css",
            media_type="text/css",
        ),
        ManifestItem(
            item_id="epub-pygments",
            href="_static/pygments.css",
            media_type="text/css",
        ),
    ]
    manifest.extend(
        ManifestItem(
            item_id=f"epub-font-{index}",
            href=f"{EPUB_FONT_DIR_NAME}/{font_file_name}",
            media_type="font/ttf",
        )
        for index, font_file_name in enumerate(EPUB_FONT_FILE_NAMES)
    )
    return manifest


def _format_manifest_item(item: ManifestItem) -> str:
    properties = (
        f' properties="{html.escape(item.properties)}"'
        if item.properties is not None
        else ""
    )
    return (
        f'    <item id="{html.escape(item.item_id)}"'
        f' href="{html.escape(item.href)}"'
        f' media-type="{html.escape(item.media_type)}"{properties} />'
    )
