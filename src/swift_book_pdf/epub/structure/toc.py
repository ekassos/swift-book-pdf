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

"""Parse Swift Book TOC sections for EPUB part grouping."""

from swift_book_pdf.epub.patterns import (
    DOC_TAG_LINE_PATTERN,
    PART_HEADING_PATTERN,
)


def parse_toc_sections(toc_lines: list[str]) -> list[tuple[str, list[str]]]:
    """Return TOC part titles with their ordered document tags.

    Args:
        toc_lines: Raw lines from `The-Swift-Programming-Language.md`.

    Returns:
        Pairs of part title and ordered DocC tags. Empty parts are skipped
        because EPUB spine generation cannot render a part without children.
    """
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_tags: list[str] = []

    for raw_line in toc_lines:
        line = raw_line.strip()
        heading_match = PART_HEADING_PATTERN.match(line)
        if heading_match:
            if current_title and current_tags:
                sections.append((current_title, current_tags))
            current_title = heading_match.group(1).strip()
            current_tags = []
            continue

        tag_match = DOC_TAG_LINE_PATTERN.match(line)
        if tag_match and current_title:
            current_tags.append(tag_match.group(1))

    if current_title and current_tags:
        sections.append((current_title, current_tags))
    return sections
