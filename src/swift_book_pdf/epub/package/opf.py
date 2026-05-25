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
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from swift_book_pdf.epub.constants import (
    EPUB_COVER_DOC_FILE_NAME,
    EPUB_IDENTIFIER_ID,
    NAV_DOC_FILE_NAME,
    NCX_FILE_NAME,
)
from swift_book_pdf.epub.package.static import (
    EPUB_FONT_DIR_NAME,
    EPUB_FONT_FILE_NAMES,
)
from swift_book_pdf.epub.package.workspace import write_text

if TYPE_CHECKING:
    from pathlib import Path

    from swift_book_pdf.core.document import DocumentEntry
    from swift_book_pdf.epub.config import EPUBConfig
    from swift_book_pdf.epub.models import ImageAsset


@dataclass(frozen=True)
class ManifestItem:
    item_id: str
    href: str
    media_type: str
    properties: str | None = None


@dataclass(frozen=True)
class OPFPackageInput:
    config: EPUBConfig
    book_title: str
    documents: list[DocumentEntry]
    image_assets: dict[str, ImageAsset]
    publication_identifier: str
    has_cover_asset: bool


def write_content_opf_file(
    workspace: Path,
    package_input: OPFPackageInput,
) -> None:
    config = package_input.config
    documents = package_input.documents
    image_assets = package_input.image_assets
    has_cover_asset = package_input.has_cover_asset
    manifest: list[ManifestItem] = [
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
    for index, document in enumerate(documents):
        manifest.append(
            ManifestItem(
                item_id=f"epub-doc-{index}",
                href=document.href,
                media_type="application/xhtml+xml",
                properties=(
                    "svg"
                    if document.href == EPUB_COVER_DOC_FILE_NAME
                    else None
                ),
            )
        )

    for index, asset in enumerate(
        sorted(image_assets.values(), key=lambda item: item.href)
    ):
        manifest.append(
            ManifestItem(
                item_id=f"epub-image-{index}",
                href=asset.href,
                media_type=asset.media_type,
            )
        )

    manifest.extend(
        [
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
    )
    manifest.extend(
        ManifestItem(
            item_id=f"epub-font-{index}",
            href=f"{EPUB_FONT_DIR_NAME}/{font_file_name}",
            media_type="font/ttf",
        )
        for index, font_file_name in enumerate(EPUB_FONT_FILE_NAMES)
    )
    if has_cover_asset:
        manifest.append(
            ManifestItem(
                item_id="epub-cover",
                href="_static/cover.png",
                media_type="image/png",
                properties="cover-image",
            )
        )

    manifest_xml = "\n".join(_format_manifest_item(item) for item in manifest)
    spine_items = "\n".join(
        f'    <itemref idref="epub-doc-{index}" />'
        for index, _ in enumerate(documents)
    )
    modified = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    cover_meta = ""
    if has_cover_asset:
        cover_meta = '<meta name="cover" content="epub-cover"/>\n    '
    publisher_xml = ""
    if config.publisher is not None:
        publisher_xml = f"<dc:publisher>{html.escape(config.publisher)}</dc:publisher>\n    "
    contributor_xml = ""
    if config.contributor is not None:
        contributor_xml = f"<dc:contributor>{html.escape(config.contributor)}</dc:contributor>\n    "
    ibooks_version_xml = ""
    if config.ibooks_version is not None:
        ibooks_version_xml = (
            f'<meta property="ibooks:version">'
            f"{html.escape(config.ibooks_version)}</meta>\n    "
        )
    content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" xml:lang="en"
 prefix="ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"
 xmlns:epub="http://www.idpf.org/2007/ops"
 xmlns:ibooks="http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"
 unique-identifier="{EPUB_IDENTIFIER_ID}">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf"
        xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:language>en</dc:language>
    <dc:title>{html.escape(package_input.book_title)}</dc:title>
    <dc:creator>The Swift project authors</dc:creator>
    {publisher_xml}{contributor_xml}<dc:identifier id="{EPUB_IDENTIFIER_ID}">{html.escape(package_input.publication_identifier)}</dc:identifier>
    {ibooks_version_xml}<meta property="dcterms:modified">{modified}</meta>
    <meta property="ibooks:specified-fonts">true</meta>
    {cover_meta}</metadata>
  <manifest>
{manifest_xml}
  </manifest>
  <spine toc="ncx" page-progression-direction="ltr">
{spine_items}
  </spine>
</package>
"""
    write_text(workspace, "content.opf", content_opf)


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
