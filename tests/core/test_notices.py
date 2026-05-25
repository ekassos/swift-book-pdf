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

from swift_book_pdf.core.generated.notices.metadata import (
    NOTICES_DOC_KEY,
    NOTICES_DOC_TAG,
    NOTICES_SECTION_TITLE,
    build_notices_toc_lines,
)
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.core.source.copyright import (
    find_swift_book_copyright_year_range,
)


def test_find_swift_book_copyright_year_range_uses_earliest_and_latest_years(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "swift-book"
    docc_root = repo_root / "TSPL.docc"
    docc_root.mkdir(parents=True)

    (docc_root / "one.md").write_text(
        "Copyright (c) 2014 Apple Inc. and the Swift project authors\n",
        encoding="utf-8",
    )
    (docc_root / "two.md").write_text(
        "Copyright (c) 2020-2026 Apple Inc. and the Swift project authors\n",
        encoding="utf-8",
    )

    assert find_swift_book_copyright_year_range(docc_root) == (2014, 2026)


def test_toc_tracks_notices_as_final_generated_chapter(
    tmp_path: Path,
) -> None:
    toc_path = _create_minimal_swift_book_checkout(tmp_path)

    toc = TableOfContents(
        str(toc_path.parent),
        str(toc_path),
        str(tmp_path / "temp"),
    )

    assert toc.doc_tags[-1] == NOTICES_DOC_TAG
    assert (
        toc.chapter_metadata[NOTICES_DOC_KEY].header_line == "Acknowledgments"
    )


def test_notices_toc_lines_include_section_heading_only_when_requested() -> (
    None
):
    assert build_notices_toc_lines() == ["\n", f"- <doc:{NOTICES_DOC_TAG}>\n"]
    assert build_notices_toc_lines(include_section_heading=True) == [
        "\n",
        f"### {NOTICES_SECTION_TITLE}\n",
        "\n",
        f"- <doc:{NOTICES_DOC_TAG}>\n",
    ]


def test_toc_can_skip_notices_chapter(
    tmp_path: Path,
) -> None:
    toc_path = _create_minimal_swift_book_checkout(tmp_path)

    toc = TableOfContents(
        str(toc_path.parent),
        str(toc_path),
        str(tmp_path / "temp"),
        include_notices=False,
    )

    assert NOTICES_DOC_TAG not in toc.doc_tags
    assert NOTICES_DOC_KEY not in toc.chapter_metadata


def _create_minimal_swift_book_checkout(tmp_path: Path) -> Path:
    docc_root = tmp_path / "swift-book" / "TSPL.docc"
    for directory in (
        "GuidedTour",
        "LanguageGuide",
        "ReferenceManual",
        "RevisionHistory",
    ):
        (docc_root / directory).mkdir(parents=True, exist_ok=True)

    (docc_root / "GuidedTour" / "GuidedTour.md").write_text(
        "# Guided Tour\n\nA quick start.\n",
        encoding="utf-8",
    )
    toc_path = docc_root / "The-Swift-Programming-Language.md"
    toc_path.write_text(
        "# The Swift Programming Language (6.2)\n\n"
        "## About\n\n"
        "### Guided Tour\n\n"
        "- <doc:GuidedTour>\n",
        encoding="utf-8",
    )
    return toc_path
