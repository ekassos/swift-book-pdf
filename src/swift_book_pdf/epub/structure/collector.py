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

"""Collect source TOC data into EPUB document structure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

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
from swift_book_pdf.epub.anchors import anchor_for_heading
from swift_book_pdf.epub.constants import (
    EPUB_COVER_DOC_FILE_NAME,
    EPUB_COVER_DOC_TITLE,
)

from .documents import build_source_document
from .grammar import build_grammar_target_map
from .toc import parse_toc_sections

if TYPE_CHECKING:
    from swift_book_pdf.core.navigation.toc import TableOfContents
    from swift_book_pdf.epub.config import EPUBConfig


@dataclass(frozen=True)
class EPUBStructure:
    """Collected structure needed by EPUB renderers and package writers.

    Attributes:
        parts: Top-level book parts and their child documents.
        source_documents: Parsed source documents keyed by document key.
        cover_document: Optional generated cover document.
        notices_document: Optional generated notices document.
        documents: Flattened package document list in spine order.
        grammar_targets: Grammar term target hrefs for cross-linking.
        has_cover_asset: Whether the package includes an outer cover image.
    """

    parts: list[PartEntry]
    source_documents: dict[str, SourceDocument]
    cover_document: DocumentEntry | None
    notices_document: DocumentEntry | None
    documents: list[DocumentEntry]
    grammar_targets: dict[str, str]
    has_cover_asset: bool


class EPUBStructureCollector:
    """Build the EPUB document tree from a loaded Swift Book TOC."""

    def __init__(
        self,
        config: EPUBConfig,
        toc: TableOfContents,
        *,
        has_cover_asset: bool,
    ) -> None:
        """Create a collector for one EPUB build.

        Args:
            config: Resolved EPUB build configuration.
            toc: Loaded Swift Book table of contents.
            has_cover_asset: Whether a cover image exists in the workspace.
        """
        self.config = config
        self.toc = toc
        self.has_cover_asset = has_cover_asset
        self.source_documents: dict[str, SourceDocument] = {}

    def collect(self) -> EPUBStructure:
        """Collect parts, generated documents, and grammar targets.

        Returns:
            Complete structure used by renderers and package writers.
        """
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
            grammar_targets=build_grammar_target_map(
                parts, self.source_documents
            ),
            has_cover_asset=self.has_cover_asset,
        )

    def _build_parts(self) -> list[PartEntry]:
        """Build top-level book parts from TOC sections.

        Returns:
            Part entries with source document children in TOC order.

        Raises:
            RuntimeError: If a part cannot infer a source directory from its
                first child document.
        """
        parts: list[PartEntry] = []
        for title, tags in parse_toc_sections(self.toc.file_content):
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
        """Load or return the cached source document for a doc tag.

        Args:
            tag: DocC document tag from the Swift Book TOC.

        Returns:
            Parsed source document for the tag.

        Raises:
            FileNotFoundError: If TOC metadata has no source file for the tag.
        """
        key = tag.lower()
        cached = self.source_documents.get(key)
        if cached is not None:
            return cached

        metadata = self.toc.chapter_metadata.get(key)
        if metadata is None or metadata.file_path is None:
            raise FileNotFoundError(
                f"Missing source metadata for chapter {tag}."
            )

        source_document = build_source_document(key, metadata)
        self.source_documents[key] = source_document
        return source_document

    def _build_cover_document(self) -> DocumentEntry | None:
        """Build the generated cover document entry when a cover exists.

        Returns:
            Cover front-matter document, or `None` when the outer cover PNG was
            not generated.
        """
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
        """Build the generated notices document entry.

        Returns:
            Generated legal notices back-matter document.
        """
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
        """Flatten front matter, parts, chapters, and notices in spine order.

        Part entries become generated spine pages before their child chapters.
        The resulting document order must stay aligned with OPF manifest IDs
        and spine itemrefs, which are generated by list index.
        """
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
