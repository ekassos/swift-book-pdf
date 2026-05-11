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

from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from swift_book_pdf.epub.constants import EPUB_FONT_FILE_NAMES
from swift_book_pdf.epub.package import EPUBPackageWriter, NavigationDocuments
from swift_book_pdf.schema import DocumentEntry

if TYPE_CHECKING:
    from swift_book_pdf.config import EPUBConfig


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
    writer = EPUBPackageWriter(config)
    workspace = writer.prepare_workspace()

    writer.write_content_opf_file(
        workspace,
        "The Swift Programming Language",
        [],
        {},
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
    writer = EPUBPackageWriter(config)
    workspace = writer.prepare_workspace()

    writer.write_content_opf_file(
        workspace,
        "The Swift Programming Language",
        [],
        {},
        "urn:uuid:test-book",
    )

    content_opf = (workspace / "OEBPS" / "content.opf").read_text(
        encoding="utf-8"
    )

    assert 'property="ibooks:version"' not in content_opf


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
    writer = EPUBPackageWriter(config)
    workspace = writer.prepare_workspace()

    writer.write_content_opf_file(
        workspace,
        "The Swift Programming Language",
        [
            DocumentEntry(
                key="cover",
                title="Cover",
                subtitle=None,
                href="cover.xhtml",
                directory=None,
            )
        ],
        {},
        "urn:uuid:test-book",
    )

    content_opf = (workspace / "OEBPS" / "content.opf").read_text(
        encoding="utf-8"
    )

    assert (
        '<item id="epub-doc-0" href="cover.xhtml" '
        'media-type="application/xhtml+xml" properties="svg" />' in content_opf
    )


def test_content_opf_can_place_edition_notice_between_cover_and_body(
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
    writer = EPUBPackageWriter(config)
    workspace = writer.prepare_workspace()

    writer.write_content_opf_file(
        workspace,
        "The Swift Programming Language",
        [
            DocumentEntry(
                key="cover",
                title="Cover",
                subtitle=None,
                href="cover.xhtml",
                directory=None,
            ),
            DocumentEntry(
                key="editionnotice",
                title="About This Edition",
                subtitle=None,
                href="Edition.xhtml",
                directory=None,
            ),
            DocumentEntry(
                key="guidedtour",
                title="Guided Tour",
                subtitle=None,
                href="GuidedTour/GuidedTour.xhtml",
                directory="GuidedTour",
            ),
        ],
        {},
        "urn:uuid:test-book",
    )

    content_opf = (workspace / "OEBPS" / "content.opf").read_text(
        encoding="utf-8"
    )

    assert content_opf.index('href="cover.xhtml"') < content_opf.index(
        'href="Edition.xhtml"'
    )
    assert content_opf.index('href="Edition.xhtml"') < content_opf.index(
        'href="GuidedTour/GuidedTour.xhtml"'
    )
    assert '<itemref idref="epub-doc-0" />' in content_opf
    assert '<itemref idref="epub-doc-1" />' in content_opf
    assert '<itemref idref="epub-doc-2" />' in content_opf


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
    writer = EPUBPackageWriter(config)
    workspace = writer.prepare_workspace()

    writer.write_static_files(workspace)
    writer.write_content_opf_file(
        workspace,
        "The Swift Programming Language",
        [],
        {},
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
    writer = EPUBPackageWriter(config)
    workspace = writer.prepare_workspace()

    writer.write_cover_asset(workspace, "6.3")

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
    writer = EPUBPackageWriter(config)
    workspace = writer.prepare_workspace()
    cover = DocumentEntry(
        key="cover",
        title="Cover",
        subtitle=None,
        href="cover.xhtml",
        directory=None,
    )
    writer.write_text(workspace, "Edition.xhtml", "<html></html>")

    navigation_documents = NavigationDocuments(cover, None, None)
    writer.write_nav_file(workspace, navigation_documents, [])
    writer.write_toc_ncx_file(
        workspace,
        navigation_documents,
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


def test_nav_and_ncx_include_edition_notice_when_configured(
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
    writer = EPUBPackageWriter(config)
    workspace = writer.prepare_workspace()
    cover = DocumentEntry(
        key="cover",
        title="Cover",
        subtitle=None,
        href="cover.xhtml",
        directory=None,
    )
    edition_notice = DocumentEntry(
        key="editionnotice",
        title="About This Edition",
        subtitle=None,
        href="Edition.xhtml",
        directory=None,
    )

    navigation_documents = NavigationDocuments(cover, edition_notice, None)
    writer.write_nav_file(workspace, navigation_documents, [])
    writer.write_toc_ncx_file(
        workspace,
        navigation_documents,
        [],
        "The Swift Programming Language",
    )

    nav = (workspace / "OEBPS" / "toc.xhtml").read_text(encoding="utf-8")
    ncx = (workspace / "OEBPS" / "toc.ncx").read_text(encoding="utf-8")

    assert '<a href="Edition.xhtml">About This Edition</a>' in nav
    assert "<text>About This Edition</text>" in ncx
