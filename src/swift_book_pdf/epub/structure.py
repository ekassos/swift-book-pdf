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
from pathlib import Path
from typing import TYPE_CHECKING

from swift_book_pdf.core.blocks.models import NoteBlock
from swift_book_pdf.core.blocks.parser import parse_blocks
from swift_book_pdf.core.document import (
    DocumentEntry,
    PartEntry,
    SourceDocument,
)
from swift_book_pdf.core.generated.notices.metadata import (
    NOTICES_DOC_FILE_NAME,
    NOTICES_DOC_KEY,
    NOTICES_DOC_TITLE,
)
from swift_book_pdf.core.markdown import (
    convert_markdown_links,
    remove_directives,
    remove_multiline_comments,
)

from .anchors import anchor_for_heading, make_unique_anchor
from .constants import (
    DOC_TAG_LINE_PATTERN,
    EPUB_COVER_DOC_FILE_NAME,
    EPUB_COVER_DOC_TITLE,
    HEADING_PATTERN,
    PART_HEADING_PATTERN,
    SUMMARY_DOC_FILE_NAME,
    SUMMARY_DOC_KEY,
)
from .render.grammar import extract_grammar_terms, grammar_anchor_fragment

if TYPE_CHECKING:
    from swift_book_pdf.core.navigation.toc import TableOfContents
    from swift_book_pdf.epub.config import EPUBConfig


@dataclass(frozen=True)
class EPUBStructure:
    parts: list[PartEntry]
    source_documents: dict[str, SourceDocument]
    cover_document: DocumentEntry | None
    notices_document: DocumentEntry | None
    documents: list[DocumentEntry]
    grammar_targets: dict[str, str]


class EPUBStructureCollector:
    def __init__(
        self,
        config: EPUBConfig,
        toc: TableOfContents,
        *,
        has_cover_asset: bool,
    ) -> None:
        self.config = config
        self.toc = toc
        self.has_cover_asset = has_cover_asset
        self.source_documents: dict[str, SourceDocument] = {}

    def collect(self) -> EPUBStructure:
        parts = self._build_parts()
        cover_document = self._build_cover_document()
        notices_document = (
            None
            if self.config.dangerously_skip_legal_notices
            else self._build_notices_document()
        )
        documents = self._flatten_documents(
            cover_document, parts, notices_document
        )
        return EPUBStructure(
            parts=parts,
            source_documents=self.source_documents,
            cover_document=cover_document,
            notices_document=notices_document,
            documents=documents,
            grammar_targets=self._build_grammar_target_map(parts),
        )

    def _build_parts(self) -> list[PartEntry]:
        parts: list[PartEntry] = []
        for title, tags in self._parse_toc_sections():
            documents = [self._get_source_document(tag).entry for tag in tags]
            if not documents:
                continue
            directory = documents[0].directory
            if directory is None:
                raise RuntimeError(
                    f"Cannot determine EPUB directory for {title}."
                )
            parts.append(
                PartEntry(
                    title=title,
                    href=f"{directory}/{directory}Part.xhtml",
                    directory=directory,
                    children=documents,
                )
            )
        return parts

    def _get_source_document(self, tag: str) -> SourceDocument:
        key = tag.lower()
        cached = self.source_documents.get(key)
        if cached is not None:
            return cached

        metadata = self.toc.chapter_metadata.get(key)
        if metadata is None or metadata.file_path is None:
            raise FileNotFoundError(
                f"Missing source metadata for chapter {tag}."
            )

        source_path = Path(metadata.file_path)
        lines = self._load_source_lines(source_path, metadata.subtitle_line)
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
            heading_map=self._extract_heading_map(lines),
        )
        source_document = SourceDocument(
            entry=entry,
            lines=lines,
            blocks=parse_blocks(lines),
        )
        self.source_documents[key] = source_document
        return source_document

    def _build_cover_document(self) -> DocumentEntry | None:
        if not self.has_cover_asset:
            return None

        return DocumentEntry(
            key="cover",
            title=EPUB_COVER_DOC_TITLE,
            subtitle=None,
            href=EPUB_COVER_DOC_FILE_NAME,
            directory=None,
        )

    def _build_notices_document(self) -> DocumentEntry:
        return DocumentEntry(
            key=NOTICES_DOC_KEY,
            title=NOTICES_DOC_TITLE,
            subtitle=None,
            href=NOTICES_DOC_FILE_NAME,
            directory=None,
        )

    def _flatten_documents(
        self,
        cover: DocumentEntry | None,
        parts: list[PartEntry],
        notices: DocumentEntry | None,
    ) -> list[DocumentEntry]:
        documents: list[DocumentEntry] = []
        if cover is not None:
            documents.append(cover)
        for part in parts:
            documents.append(
                DocumentEntry(
                    key=anchor_for_heading(part.title).lower(),
                    title=part.title,
                    subtitle=None,
                    href=part.href,
                    directory=part.directory,
                )
            )
            documents.extend(part.children)
        if notices is not None:
            documents.append(notices)
        return documents

    def _parse_toc_sections(self) -> list[tuple[str, list[str]]]:
        sections: list[tuple[str, list[str]]] = []
        current_title: str | None = None
        current_tags: list[str] = []

        for raw_line in self.toc.file_content:
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

    def _build_grammar_target_map(
        self, parts: list[PartEntry]
    ) -> dict[str, str]:
        grammar_targets: dict[str, str] = {}
        for part in parts:
            for document in part.children:
                source_document = self.source_documents[document.key]
                for block in source_document.blocks:
                    if not isinstance(block, NoteBlock):
                        continue
                    if not block.label.lower().startswith("grammar of "):
                        continue
                    for term in extract_grammar_terms(block):
                        grammar_targets.setdefault(
                            term,
                            f"{document.href}#grammar_{grammar_anchor_fragment(term)}",
                        )
        return grammar_targets

    def _extract_heading_map(self, lines: list[str]) -> dict[str, str]:
        heading_map: dict[str, str] = {}
        seen_anchors: dict[str, int] = {}
        for raw_line in lines:
            match = HEADING_PATTERN.match(raw_line.strip())
            if not match:
                continue
            title = match.group(2).strip()
            anchor = make_unique_anchor(
                anchor_for_heading(title), seen_anchors
            )
            heading_map[anchor] = title
        return heading_map

    def _load_source_lines(
        self, source_path: Path, subtitle: str | None
    ) -> list[str]:
        file_content = source_path.read_text(encoding="utf-8").splitlines()
        processed_lines = remove_multiline_comments(file_content)
        processed_lines = remove_directives(processed_lines)
        processed_lines = convert_markdown_links(processed_lines)
        processed_lines = [line.rstrip("\n") for line in processed_lines]
        return self._strip_title_and_subtitle(processed_lines, subtitle)

    def _strip_title_and_subtitle(
        self, lines: list[str], subtitle: str | None
    ) -> list[str]:
        remaining_lines = list(lines)
        while remaining_lines and not remaining_lines[0].strip():
            remaining_lines.pop(0)

        if remaining_lines and remaining_lines[0].startswith("# "):
            remaining_lines.pop(0)

        while remaining_lines and not remaining_lines[0].strip():
            remaining_lines.pop(0)

        if (
            subtitle
            and remaining_lines
            and remaining_lines[0].strip() == subtitle
        ):
            remaining_lines.pop(0)

        while remaining_lines and not remaining_lines[0].strip():
            remaining_lines.pop(0)

        return remaining_lines
