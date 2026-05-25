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

"""OPF metadata XML rendering."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING

from swift_book_pdf.epub.constants import EPUB_IDENTIFIER_ID

if TYPE_CHECKING:
    from swift_book_pdf.epub.package.opf import OPFPackageInput


def render_metadata(package_input: OPFPackageInput, modified: str) -> str:
    """Render the OPF metadata block for a generated EPUB."""
    config = package_input.config
    return (
        f"    <dc:language>en</dc:language>\n"
        f"    <dc:title>{html.escape(package_input.book_title)}</dc:title>\n"
        f"    <dc:creator>The Swift project authors</dc:creator>\n"
        f"    {_optional_publisher(config.publisher)}"
        f"{_optional_contributor(config.contributor)}"
        f'<dc:identifier id="{EPUB_IDENTIFIER_ID}">'
        f"{html.escape(package_input.publication_identifier)}</dc:identifier>\n"
        f"    {_optional_ibooks_version(config.ibooks_version)}"
        f'<meta property="dcterms:modified">{modified}</meta>\n'
        f'    <meta property="ibooks:specified-fonts">true</meta>\n'
        f"    {_optional_cover_meta(package_input.has_cover_asset)}"
    )


def _optional_publisher(publisher: str | None) -> str:
    """Render optional publisher metadata."""
    if publisher is None:
        return ""
    return f"<dc:publisher>{html.escape(publisher)}</dc:publisher>\n    "


def _optional_contributor(contributor: str | None) -> str:
    """Render optional contributor metadata."""
    if contributor is None:
        return ""
    return f"<dc:contributor>{html.escape(contributor)}</dc:contributor>\n    "


def _optional_ibooks_version(ibooks_version: str | None) -> str:
    """Render optional Apple Books version metadata."""
    if ibooks_version is None:
        return ""
    return (
        f'<meta property="ibooks:version">'
        f"{html.escape(ibooks_version)}</meta>\n    "
    )


def _optional_cover_meta(has_cover_asset: bool) -> str:
    """Render optional legacy cover metadata."""
    if not has_cover_asset:
        return ""
    return '<meta name="cover" content="epub-cover"/>\n    '
