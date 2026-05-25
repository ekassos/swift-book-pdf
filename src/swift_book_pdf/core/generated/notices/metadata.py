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

"""Backend-neutral metadata for the generated notices chapter."""

from swift_book_pdf.core.source import ChapterMetadata

NOTICES_DOC_TAG = "CopyrightAndNotices"
NOTICES_DOC_KEY = NOTICES_DOC_TAG.lower()
NOTICES_DOC_TITLE = "Acknowledgments"
NOTICES_DOC_SUBTITLE = "Review notices about this edition."
NOTICES_SECTION_TITLE = "About This Edition"
NOTICES_DOC_FILE_NAME = "Trademarks.xhtml"
NOTICES_SECTION_ID = "copyright-and-notices"


def build_notices_chapter_metadata() -> ChapterMetadata:
    """Build generated chapter metadata for notices content.

    Returns:
        Metadata entry used by TOC consumers when notices are included.
    """
    return ChapterMetadata(
        file_path=None,
        header_line=NOTICES_DOC_TITLE,
        subtitle_line=NOTICES_DOC_SUBTITLE,
    )


def build_notices_toc_lines(
    *, include_section_heading: bool = False
) -> list[str]:
    """Build generated TOC lines that append the notices document.

    Args:
        include_section_heading: Whether to add the notices section heading
            before the document link. PDF needs this heading for its rendered
            table of contents; EPUB navigation handles the section elsewhere.

    Returns:
        Markdown lines that can be appended to the source TOC.
    """
    lines = ["\n"]
    if include_section_heading:
        lines.extend([f"### {NOTICES_SECTION_TITLE}\n", "\n"])
    lines.append(f"- <doc:{NOTICES_DOC_TAG}>\n")
    return lines
