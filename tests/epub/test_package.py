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

import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from swift_book_pdf.core.document import DocumentEntry, PartEntry
from swift_book_pdf.epub.cover.png import write_cover_asset
from swift_book_pdf.epub.package.nav import FrontBackMatter, write_nav_file
from swift_book_pdf.epub.package.ncx import write_toc_ncx_file
from swift_book_pdf.epub.package.opf import (
    OPFPackageInput,
    write_content_opf_file,
)
from swift_book_pdf.epub.package.static import (
    EPUB_FONT_FILE_NAMES,
    write_static_files,
)
from swift_book_pdf.epub.package.workspace import prepare_workspace, write_text

if TYPE_CHECKING:
    from swift_book_pdf.epub.config import EPUBConfig


def _write_content_opf_file(
    workspace: Path,
    config: "EPUBConfig",
    documents: list[DocumentEntry],
    publication_identifier: str,
) -> None:
    write_content_opf_file(
        workspace,
        OPFPackageInput(
            config=config,
            book_title="The Swift Programming Language",
            documents=documents,
            image_assets={},
            publication_identifier=publication_identifier,
            has_cover_asset=False,
        ),
    )


def test_content_opf_includes_ibooks_version_metadata_when_configured(
    tmp_path: Path,
) -> None:
    config = cast(
        "EPUBConfig",
        SimpleNamespace(
            temp_dir=str(tmp_path),
            output_path=str(tmp_path / "swift_book.epub"),
            publisher=None,
            contributor=None,
            ibooks_version="1.1",
        ),
    )
    workspace = prepare_workspace(config)

    _write_content_opf_file(
        workspace,
        config,
        [],
        "urn:uuid:test-book",
    )

    content_opf = (workspace / "OEBPS" / "content.opf").read_text(
        encoding="utf-8"
    )

    assert '<meta property="ibooks:version">1.1</meta>' in content_opf


def test_content_opf_omits_ibooks_version_metadata_by_default(
    tmp_path: Path,
) -> None:
    config = cast(
        "EPUBConfig",
        SimpleNamespace(
            temp_dir=str(tmp_path),
            output_path=str(tmp_path / "swift_book.epub"),
            publisher=None,
            contributor=None,
            ibooks_version=None,
        ),
    )
    workspace = prepare_workspace(config)

    _write_content_opf_file(
        workspace,
        config,
        [],
        "urn:uuid:test-book",
    )

    content_opf = (workspace / "OEBPS" / "content.opf").read_text(
        encoding="utf-8"
    )

    assert 'property="ibooks:version"' not in content_opf


def test_content_opf_escapes_package_data_and_parses_as_xml(
    tmp_path: Path,
) -> None:
    config = cast(
        "EPUBConfig",
        SimpleNamespace(
            temp_dir=str(tmp_path),
            output_path=str(tmp_path / "swift_book.epub"),
            publisher="Swift & Friends",
            contributor="Docs <Team>",
            ibooks_version="6 & 7",
        ),
    )
    workspace = prepare_workspace(config)
    document = DocumentEntry(
        key="operators",
        title="Operators",
        subtitle=None,
        href="Basics/Operators&Symbols.xhtml",
        directory="Basics",
    )

    write_content_opf_file(
        workspace,
        OPFPackageInput(
            config=config,
            book_title="Swift <Guide> & Reference",
            documents=[document],
            image_assets={},
            publication_identifier="urn:uuid:test&book",
            has_cover_asset=True,
        ),
    )

    content_opf = (workspace / "OEBPS" / "content.opf").read_text(
        encoding="utf-8"
    )

    ET.fromstring(content_opf)  # noqa: S314 - parses generated test output
    assert "Swift &lt;Guide&gt; &amp; Reference" in content_opf
    assert "Swift &amp; Friends" in content_opf
    assert "Docs &lt;Team&gt;" in content_opf
    assert "urn:uuid:test&amp;book" in content_opf
    assert 'href="Basics/Operators&amp;Symbols.xhtml"' in content_opf
    assert '<meta property="ibooks:version">6 &amp; 7</meta>' in content_opf
    assert '<meta name="cover" content="epub-cover"/>' in content_opf


def test_content_opf_marks_cover_document_as_svg(
    tmp_path: Path,
) -> None:
    config = cast(
        "EPUBConfig",
        SimpleNamespace(
            temp_dir=str(tmp_path),
            output_path=str(tmp_path / "swift_book.epub"),
            publisher=None,
            contributor=None,
            ibooks_version=None,
        ),
    )
    workspace = prepare_workspace(config)

    _write_content_opf_file(
        workspace,
        config,
        [
            DocumentEntry(
                key="cover",
                title="Cover",
                subtitle=None,
                href="cover.xhtml",
                directory=None,
            )
        ],
        "urn:uuid:test-book",
    )

    content_opf = (workspace / "OEBPS" / "content.opf").read_text(
        encoding="utf-8"
    )

    assert (
        '<item id="epub-doc-0" href="cover.xhtml" '
        'media-type="application/xhtml+xml" properties="svg" />' in content_opf
    )


def test_static_files_include_bundled_ibm_plex_fonts(
    tmp_path: Path,
) -> None:
    config = cast(
        "EPUBConfig",
        SimpleNamespace(
            temp_dir=str(tmp_path),
            output_path=str(tmp_path / "swift_book.epub"),
            publisher=None,
            contributor=None,
            ibooks_version=None,
        ),
    )
    workspace = prepare_workspace(config)

    write_static_files(workspace)
    _write_content_opf_file(
        workspace,
        config,
        [],
        "urn:uuid:test-book",
    )

    for font_file_name in EPUB_FONT_FILE_NAMES:
        assert (
            workspace / "OEBPS" / "_static" / "fonts" / font_file_name
        ).exists()

    content_opf = (workspace / "OEBPS" / "content.opf").read_text(
        encoding="utf-8"
    )
    assert 'href="_static/fonts/IBMPlexSans-Medium.ttf"' in content_opf
    assert 'media-type="font/ttf"' in content_opf


def test_write_cover_asset_uses_bundled_ibm_plex_fonts(
    tmp_path: Path,
) -> None:
    config = cast(
        "EPUBConfig",
        SimpleNamespace(
            temp_dir=str(tmp_path),
            output_path=str(tmp_path / "swift_book.epub"),
            base_cover_image=None,
            cover_template_paths={},
            cover_variant=None,
            cover_footer_line="Updated for Swift 6.3",
        ),
    )
    workspace = prepare_workspace(config)

    write_cover_asset(config, workspace, "6.3")

    assert (workspace / "OEBPS" / "_static" / "cover.png").exists()


def test_nav_and_ncx_omit_acknowledgments_when_notices_are_skipped(
    tmp_path: Path,
) -> None:
    config = cast(
        "EPUBConfig",
        SimpleNamespace(
            temp_dir=str(tmp_path),
            output_path=str(tmp_path / "swift_book.epub"),
            publisher=None,
            contributor=None,
            ibooks_version=None,
        ),
    )
    workspace = prepare_workspace(config)
    cover = DocumentEntry(
        key="cover",
        title="Cover",
        subtitle=None,
        href="cover.xhtml",
        directory=None,
    )
    write_text(workspace, "Edition.xhtml", "<html></html>")

    front_back_matter = FrontBackMatter(cover, None)
    write_nav_file(workspace, front_back_matter, [])
    write_toc_ncx_file(
        workspace,
        "urn:uuid:test-book",
        front_back_matter,
        [],
        "The Swift Programming Language",
    )

    nav = (workspace / "OEBPS" / "toc.xhtml").read_text(encoding="utf-8")
    ncx = (workspace / "OEBPS" / "toc.ncx").read_text(encoding="utf-8")

    assert 'epub:type="frontmatter"' not in nav
    assert '<a href="Edition.xhtml">About This Edition</a>' not in nav
    assert "<text>About This Edition</text>" not in ncx
    assert "Acknowledgments" not in nav
    assert 'epub:type="acknowledgements"' not in nav
    assert "Acknowledgments" not in ncx


def test_nav_file_escapes_titles_and_parses_as_xhtml(tmp_path: Path) -> None:
    config = cast(
        "EPUBConfig",
        SimpleNamespace(
            temp_dir=str(tmp_path),
            output_path=str(tmp_path / "swift_book.epub"),
        ),
    )
    workspace = prepare_workspace(config)
    part = DocumentEntry(
        key="generics",
        title="Generics <T> & Operators",
        subtitle=None,
        href="Basics/Operators&Symbols.xhtml",
        directory="Basics",
    )
    parts = [
        PartEntry(
            title="Language & Runtime",
            href="Basics/BasicsPart.xhtml",
            directory="Basics",
            children=[part],
        )
    ]

    write_nav_file(workspace, FrontBackMatter(None, None), parts)

    nav = (workspace / "OEBPS" / "toc.xhtml").read_text(encoding="utf-8")

    ET.fromstring(nav)  # noqa: S314 - parses generated test output
    assert "Language &amp; Runtime" in nav
    assert "Generics &lt;T&gt; &amp; Operators" in nav
    assert 'href="Basics/Operators&amp;Symbols.xhtml"' in nav


def test_ncx_file_escapes_titles_and_parses_as_xml(tmp_path: Path) -> None:
    config = cast(
        "EPUBConfig",
        SimpleNamespace(
            temp_dir=str(tmp_path),
            output_path=str(tmp_path / "swift_book.epub"),
        ),
    )
    workspace = prepare_workspace(config)
    child = DocumentEntry(
        key="operators",
        title="Operators <T> & Symbols",
        subtitle=None,
        href="Basics/Operators&Symbols.xhtml",
        directory="Basics",
    )
    parts = [
        PartEntry(
            title="Language & Runtime",
            href="Basics/BasicsPart.xhtml",
            directory="Basics",
            children=[child],
        )
    ]

    write_toc_ncx_file(
        workspace,
        "urn:uuid:test-book",
        FrontBackMatter(None, None),
        parts,
        "The Swift Programming Language",
    )

    ncx = (workspace / "OEBPS" / "toc.ncx").read_text(encoding="utf-8")

    ET.fromstring(ncx)  # noqa: S314 - parses generated test output
    assert "Language &amp; Runtime" in ncx
    assert "Operators &lt;T&gt; &amp; Symbols" in ncx
    assert 'src="Basics/Operators&amp;Symbols.xhtml"' in ncx
    assert 'id="navPoint1" playOrder="1"' in ncx
    assert 'id="navPoint2" playOrder="2"' in ncx
