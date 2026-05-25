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

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from swift_book_pdf.epub.constants import (
    EPUB_IDENTIFIER_ID,
)
from swift_book_pdf.epub.package.manifest import (
    build_manifest_items,
    render_manifest_items,
)
from swift_book_pdf.epub.package.metadata import render_metadata
from swift_book_pdf.epub.package.workspace import write_text

if TYPE_CHECKING:
    from pathlib import Path

    from swift_book_pdf.core.document import DocumentEntry
    from swift_book_pdf.epub.assets import ImageAsset
    from swift_book_pdf.epub.config import EPUBConfig


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
    modified = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest_xml = render_manifest_items(build_manifest_items(package_input))
    metadata_xml = render_metadata(package_input, modified)
    spine_items = _render_spine_items(package_input)
    content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" xml:lang="en"
 prefix="ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"
 xmlns:epub="http://www.idpf.org/2007/ops"
 xmlns:ibooks="http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"
 unique-identifier="{EPUB_IDENTIFIER_ID}">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf"
        xmlns:dc="http://purl.org/dc/elements/1.1/">
{metadata_xml}</metadata>
  <manifest>
{manifest_xml}
  </manifest>
  <spine toc="ncx" page-progression-direction="ltr">
{spine_items}
  </spine>
</package>
"""
    write_text(workspace, "content.opf", content_opf)


def _render_spine_items(package_input: OPFPackageInput) -> str:
    return "\n".join(
        f'    <itemref idref="epub-doc-{index}" />'
        for index, _ in enumerate(package_input.documents)
    )
