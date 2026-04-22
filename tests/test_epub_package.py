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
from typing import cast

from swift_book_pdf.config import EPUBConfig
from swift_book_pdf.epub.package import EPUBPackageWriter
from swift_book_pdf.schema import DocumentEntry


def test_content_opf_includes_ibooks_version_metadata_when_configured(
    tmp_path: Path,
) -> None:
    config = cast(
        EPUBConfig,
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
        EPUBConfig,
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
        EPUBConfig,
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


def test_nav_and_ncx_omit_acknowledgments_when_notices_are_skipped(
    tmp_path: Path,
) -> None:
    config = cast(
        EPUBConfig,
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

    writer.write_nav_file(workspace, cover, [], None)
    writer.write_toc_ncx_file(
        workspace,
        cover,
        [],
        None,
        "The Swift Programming Language",
    )

    nav = (workspace / "OEBPS" / "toc.xhtml").read_text(encoding="utf-8")
    ncx = (workspace / "OEBPS" / "toc.ncx").read_text(encoding="utf-8")

    assert "Acknowledgments" not in nav
    assert 'epub:type="acknowledgements"' not in nav
    assert "Acknowledgments" not in ncx
