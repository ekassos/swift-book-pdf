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

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

from swift_book_pdf.blocks import parse_blocks
from swift_book_pdf.contents import (
    remove_directives,
    replace_and_extract_version,
)
from swift_book_pdf.files import get_swift_book_repository_revision
from swift_book_pdf.markdown_helpers import (
    convert_markdown_links,
    remove_multiline_comments,
)
from swift_book_pdf.schema import (
    DocumentEntry,
    ImageAsset,
    NoteBlock,
    PartEntry,
    SourceDocument,
)

from .constants import (
    DEFAULT_BOOK_TITLE,
    DOC_TAG_LINE_PATTERN,
    EPUB_COVER_DOC_FILE_NAME,
    EPUB_COVER_DOC_TITLE,
    HEADING_PATTERN,
    NOTICES_DOC_FILE_NAME,
    NOTICES_DOC_TITLE,
    PART_HEADING_PATTERN,
    SUMMARY_DOC_FILE_NAME,
    SUMMARY_DOC_KEY,
)
from .helpers import (
    anchor_for_heading,
    build_publication_identifier,
    make_unique_anchor,
)
from .package import EPUBPackageWriter
from .render import EPUBRenderer, LinkResolver, extract_grammar_terms

if TYPE_CHECKING:
    from swift_book_pdf.config import EPUBConfig
    from swift_book_pdf.toc import TableOfContents

logger = logging.getLogger(__name__)


class EPUBBuilder:
    def __init__(self, config: EPUBConfig, toc: TableOfContents) -> None:
        self.config = config
        self.toc = toc
        self.asset_path = Path(config.assets_dir)
        self.source_documents: dict[str, SourceDocument] = {}

    def build(self) -> None:
        logger.info("Creating EPUB...")
        writer = EPUBPackageWriter(self.config)
        workspace = writer.prepare_workspace()

        version_info = self._extract_version_info()
        source_revision = get_swift_book_repository_revision(
            self.config.root_dir
        )
        publication_identifier = build_publication_identifier(
            version_info,
            source_revision,
        )
        writer.publication_identifier = publication_identifier
        book_title = (
            f"{DEFAULT_BOOK_TITLE} (Swift {version_info})"
            if version_info
            else DEFAULT_BOOK_TITLE
        )
        parts = self._build_parts()
        notices = self._build_notices_document()

        writer.write_container_file(workspace)
        writer.write_static_files(workspace)
        writer.write_cover_asset(workspace, version_info)
        if self.config.export_cover_image:
            cover_output_path = writer.export_cover_asset(workspace)
            if cover_output_path is not None:
                logger.info(f"Cover image saved to {cover_output_path}")

        cover_document = self._build_cover_document(writer, workspace)
        documents = self._flatten_documents(cover_document, parts, notices)
        renderer = EPUBRenderer(
            self.asset_path,
            self._build_grammar_target_map(parts),
        )
        link_resolver = LinkResolver(documents)
        image_assets: dict[str, ImageAsset] = {}

        if cover_document is not None:
            writer.write_text(
                workspace,
                cover_document.href,
                renderer.render_cover_page(
                    cover_document, book_title, version_info
                ),
            )

        for part in parts:
            writer.write_text(
                workspace,
                part.href,
                renderer.render_part_page(part),
            )
            for document in part.children:
                writer.write_text(
                    workspace,
                    document.href,
                    renderer.render_chapter_page(
                        self.source_documents[document.key],
                        link_resolver,
                        image_assets,
                    ),
                )

        writer.write_text(
            workspace,
            notices.href,
            renderer.render_notices_page(notices),
        )
        writer.copy_image_assets(workspace, image_assets)
        writer.write_nav_file(workspace, cover_document, parts, notices)
        writer.write_toc_ncx_file(
            workspace,
            cover_document,
            parts,
            notices,
            book_title,
        )
        writer.write_content_opf_file(
            workspace,
            book_title,
            documents,
            image_assets,
            publication_identifier,
        )
        writer.package_epub(workspace)
        logger.info(f"EPUB saved to {self.config.output_path}")

    def _extract_version_info(self) -> str | None:
        _, version_info = replace_and_extract_version(self.toc.file_content)
        return version_info

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

    def _build_notices_document(self) -> DocumentEntry:
        return DocumentEntry(
            key="copyright-and-notices",
            title=NOTICES_DOC_TITLE,
            subtitle=None,
            href=NOTICES_DOC_FILE_NAME,
            directory=None,
        )

    def _build_cover_document(
        self,
        writer: EPUBPackageWriter,
        workspace: Path,
    ) -> DocumentEntry | None:
        if not writer.has_cover_asset(workspace):
            return None

        return DocumentEntry(
            key="cover",
            title=EPUB_COVER_DOC_TITLE,
            subtitle=None,
            href=EPUB_COVER_DOC_FILE_NAME,
            directory=None,
        )

    def _flatten_documents(
        self,
        cover: DocumentEntry | None,
        parts: list[PartEntry],
        notices: DocumentEntry,
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
                            f"{document.href}#grammar_{_grammar_anchor_fragment(term)}",
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


def _grammar_anchor_fragment(term: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", term.strip()).strip("-")
