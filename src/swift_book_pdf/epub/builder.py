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

"""Top-level orchestration for building EPUB artifacts."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from swift_book_pdf.core.markdown import resolve_version_info
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.core.source.repository import (
    get_swift_book_repository_revision,
)

from .constants import DEFAULT_BOOK_TITLE
from .cover import CoverPageOptions, render_cover_page, resolve_cover_banner
from .cover.png import (
    export_cover_asset,
    has_cover_asset,
    write_cover_asset,
)
from .identifiers import build_publication_identifier
from .package.nav import FrontBackMatter, write_nav_file
from .package.ncx import write_toc_ncx_file
from .package.opf import OPFPackageInput, write_content_opf_file
from .package.static import write_static_files
from .package.workspace import (
    copy_image_assets,
    package_epub,
    prepare_workspace,
    write_container_file,
    write_text,
)
from .render import EPUBRenderer, LinkResolver
from .structure import EPUBStructureCollector

if TYPE_CHECKING:
    from swift_book_pdf.epub.assets import ImageAsset
    from swift_book_pdf.epub.config import EPUBConfig
    from swift_book_pdf.epub.structure import EPUBStructure

logger = logging.getLogger(__name__)


def build_epub(config: EPUBConfig) -> None:
    """Build the EPUB artifact from resolved configuration.

    Args:
        config: Resolved EPUB build configuration.
    """
    toc = TableOfContents(
        config.root_dir,
        config.toc_file_path,
        config.temp_dir,
        include_notices=not config.dangerously_skip_legal_notices,
    )
    EPUBBuilder(config, toc).build()


@dataclass(frozen=True)
class PublicationMetadata:
    """Metadata derived once and reused across EPUB package writers.

    Attributes:
        version_info: Swift version string detected from the source.
        source_revision: Source repository revision when available.
        publication_identifier: Stable EPUB publication identifier.
        book_title: Display title written into EPUB metadata.
    """

    version_info: str
    source_revision: str | None
    publication_identifier: str
    book_title: str


class EPUBBuilder:
    """Build an EPUB workspace, render documents, and package the archive."""

    def __init__(self, config: EPUBConfig, toc: TableOfContents) -> None:
        """Create a builder from resolved config and a loaded source TOC."""
        self.config = config
        self.toc = toc
        self.asset_path = Path(config.assets_dir)

    def build(self) -> None:
        """Render and package the EPUB described by the builder config."""
        logger.info("Creating EPUB...")
        workspace = prepare_workspace(self.config)
        metadata = self._build_publication_metadata()

        write_container_file(workspace)
        write_static_files(workspace)
        self._write_cover_assets(workspace, metadata.version_info)

        structure = self._collect_structure(has_cover_asset(workspace))
        image_assets = self._render_documents(workspace, structure, metadata)
        copy_image_assets(workspace, image_assets)
        self._write_package_files(workspace, structure, image_assets, metadata)
        package_epub(self.config, workspace)
        logger.info(f"EPUB saved to {self.config.output_path}")

    def _build_publication_metadata(self) -> PublicationMetadata:
        """Resolve publication metadata shared by rendered and package files."""
        version_info = self._version_info()
        source_revision = get_swift_book_repository_revision(
            self.config.root_dir
        )
        publication_identifier = build_publication_identifier(
            version_info,
            source_revision,
            self.config.publication_identifier_seed,
        )
        book_title = (
            f"{DEFAULT_BOOK_TITLE} (Swift {version_info})"
            if version_info
            else DEFAULT_BOOK_TITLE
        )
        return PublicationMetadata(
            version_info=version_info,
            source_revision=source_revision,
            publication_identifier=publication_identifier,
            book_title=book_title,
        )

    def _write_cover_assets(
        self, workspace: Path, version_info: str | None
    ) -> None:
        """Write the package cover asset and optional exported cover image."""
        write_cover_asset(self.config, workspace, version_info)
        if not self.config.export_cover_image:
            return
        cover_output_path = export_cover_asset(
            workspace, Path(self.config.output_path)
        )
        if cover_output_path is not None:
            logger.info(f"Cover image saved to {cover_output_path}")

    def _collect_structure(self, cover_asset_exists: bool) -> EPUBStructure:
        """Collect book structure from the source TOC and build config."""
        return EPUBStructureCollector(
            self.config,
            self.toc,
            has_cover_asset=cover_asset_exists,
        ).collect()

    def _render_documents(
        self,
        workspace: Path,
        structure: EPUBStructure,
        metadata: PublicationMetadata,
    ) -> dict[str, ImageAsset]:
        """Render XHTML documents and collect image assets they reference."""
        renderer = EPUBRenderer(
            self.asset_path,
            structure.grammar_targets,
            self.config.original_work_copyright_year_range,
        )
        link_resolver = LinkResolver(structure.documents)
        image_assets: dict[str, ImageAsset] = {}

        self._render_cover_document(workspace, structure, metadata)
        self._render_part_documents(
            workspace,
            structure,
            renderer,
            link_resolver,
            image_assets,
        )
        self._render_notices_document(workspace, structure, renderer)
        return image_assets

    def _render_cover_document(
        self,
        workspace: Path,
        structure: EPUBStructure,
        metadata: PublicationMetadata,
    ) -> None:
        """Render the generated cover XHTML document when a cover exists."""
        if structure.cover_document is None:
            return

        cover_banner = resolve_cover_banner(
            self.config.cover_banner_text,
            self.config.cover_banner_color,
            metadata.version_info,
            self.config.cover_variant,
        )
        write_text(
            workspace,
            structure.cover_document.href,
            render_cover_page(
                structure.cover_document,
                metadata.version_info,
                CoverPageOptions(
                    book_title=metadata.book_title,
                    cover_banner=cover_banner,
                    cover_footer_line=self.config.cover_footer_line,
                    compiled_by_name=self.config.contributor,
                    cover_variant=self.config.cover_variant,
                ),
            ),
        )

    def _render_part_documents(
        self,
        workspace: Path,
        structure: EPUBStructure,
        renderer: EPUBRenderer,
        link_resolver: LinkResolver,
        image_assets: dict[str, ImageAsset],
    ) -> None:
        """Render part pages and their child chapter documents."""
        for part in structure.parts:
            write_text(
                workspace,
                part.href,
                renderer.render_part_page(part),
            )
            for document in part.children:
                write_text(
                    workspace,
                    document.href,
                    renderer.render_chapter_page(
                        structure.source_documents[document.key],
                        link_resolver,
                        image_assets,
                    ),
                )

    def _render_notices_document(
        self,
        workspace: Path,
        structure: EPUBStructure,
        renderer: EPUBRenderer,
    ) -> None:
        """Render the generated notices document when it is enabled."""
        if structure.notices_document is not None:
            write_text(
                workspace,
                structure.notices_document.href,
                renderer.render_notices_page(structure.notices_document),
            )

    def _write_package_files(
        self,
        workspace: Path,
        structure: EPUBStructure,
        image_assets: dict[str, ImageAsset],
        metadata: PublicationMetadata,
    ) -> None:
        """Write navigation, NCX, and OPF package files."""
        front_back_matter = FrontBackMatter(
            structure.cover_document, structure.notices_document
        )
        write_nav_file(workspace, front_back_matter, structure.parts)
        write_toc_ncx_file(
            workspace,
            metadata.publication_identifier,
            front_back_matter,
            structure.parts,
            metadata.book_title,
        )
        write_content_opf_file(
            workspace,
            OPFPackageInput(
                config=self.config,
                book_title=metadata.book_title,
                documents=structure.documents,
                image_assets=image_assets,
                publication_identifier=metadata.publication_identifier,
                has_cover_asset=structure.has_cover_asset,
            ),
        )

    def _version_info(self) -> str:
        """Resolve the Swift version string for this build."""
        return resolve_version_info(
            self.toc.file_content, self.config.override_version
        )
