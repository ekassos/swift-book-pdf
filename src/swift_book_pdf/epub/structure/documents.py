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

"""Build parsed source documents for EPUB rendering."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from swift_book_pdf.core.blocks.parser import parse_blocks
from swift_book_pdf.core.document import DocumentEntry, SourceDocument
from swift_book_pdf.core.markdown import (
    convert_markdown_links,
    remove_directives,
    remove_multiline_comments,
)
from swift_book_pdf.epub.anchors import anchor_for_heading, make_unique_anchor
from swift_book_pdf.epub.constants import (
    SUMMARY_DOC_FILE_NAME,
    SUMMARY_DOC_KEY,
)
from swift_book_pdf.epub.patterns import HEADING_PATTERN

if TYPE_CHECKING:
    from swift_book_pdf.core.source import ChapterMetadata


def build_source_document(
    key: str,
    metadata: ChapterMetadata,
) -> SourceDocument:
    """Build one parsed source document from chapter metadata."""
    if metadata.file_path is None:
        raise FileNotFoundError(f"Missing source metadata for chapter {key}.")

    source_path = Path(metadata.file_path)
    lines = load_source_lines(source_path, metadata.subtitle_line)
    file_name = (
        SUMMARY_DOC_FILE_NAME
        if key == SUMMARY_DOC_KEY
        else f"{source_path.stem}.xhtml"
    )
    entry = DocumentEntry(
        key=key,
        title=metadata.header_line or source_path.stem,
        subtitle=metadata.subtitle_line,
        href=f"{source_path.parent.name}/{file_name}",
        directory=source_path.parent.name,
        source_path=source_path,
        heading_map=extract_heading_map(lines),
    )
    return SourceDocument(
        entry=entry,
        lines=lines,
        blocks=parse_blocks(lines),
    )


def load_source_lines(source_path: Path, subtitle: str | None) -> list[str]:
    """Load and preprocess source Markdown lines for EPUB rendering."""
    file_content = source_path.read_text(encoding="utf-8").splitlines()
    processed_lines = remove_multiline_comments(file_content)
    processed_lines = remove_directives(processed_lines)
    processed_lines = convert_markdown_links(processed_lines)
    processed_lines = [line.rstrip("\n") for line in processed_lines]
    return strip_title_and_subtitle(processed_lines, subtitle)


def strip_title_and_subtitle(
    lines: list[str], subtitle: str | None
) -> list[str]:
    """Remove leading title and optional subtitle lines from source Markdown."""
    remaining_lines = _drop_leading_blank_lines(list(lines))

    if remaining_lines and remaining_lines[0].startswith("# "):
        remaining_lines.pop(0)

    remaining_lines = _drop_leading_blank_lines(remaining_lines)

    if subtitle and remaining_lines and remaining_lines[0].strip() == subtitle:
        remaining_lines.pop(0)

    return _drop_leading_blank_lines(remaining_lines)


def extract_heading_map(lines: list[str]) -> dict[str, str]:
    """Map generated heading anchors back to display heading text."""
    heading_map: dict[str, str] = {}
    seen_anchors: dict[str, int] = {}
    for raw_line in lines:
        match = HEADING_PATTERN.match(raw_line.strip())
        if not match:
            continue
        title = match.group(2).strip()
        anchor = make_unique_anchor(anchor_for_heading(title), seen_anchors)
        heading_map[anchor] = title
    return heading_map


def _drop_leading_blank_lines(lines: list[str]) -> list[str]:
    """Return `lines` after removing leading blank lines in place."""
    while lines and not lines[0].strip():
        lines.pop(0)
    return lines
