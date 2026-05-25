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
    from swift_book_pdf.epub.config import EPUBConfig
    from swift_book_pdf.epub.models import ImageAsset

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


class EPUBBuilder:
    def __init__(self, config: EPUBConfig, toc: TableOfContents) -> None:
        self.config = config
        self.toc = toc
        self.asset_path = Path(config.assets_dir)

    def build(self) -> None:
        logger.info("Creating EPUB...")
        workspace = prepare_workspace(self.config)
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

        write_container_file(workspace)
        write_static_files(workspace)
        write_cover_asset(self.config, workspace, version_info)
        if self.config.export_cover_image:
            cover_output_path = export_cover_asset(
                workspace, Path(self.config.output_path)
            )
            if cover_output_path is not None:
                logger.info(f"Cover image saved to {cover_output_path}")

        structure = EPUBStructureCollector(
            self.config,
            self.toc,
            has_cover_asset=has_cover_asset(workspace),
        ).collect()
        renderer = EPUBRenderer(
            self.asset_path,
            structure.grammar_targets,
            self.config.original_work_copyright_year_range,
        )
        link_resolver = LinkResolver(structure.documents)
        image_assets: dict[str, ImageAsset] = {}

        if structure.cover_document is not None:
            cover_banner = resolve_cover_banner(
                self.config.cover_banner_text,
                self.config.cover_banner_color,
                version_info,
                self.config.cover_variant,
            )
            write_text(
                workspace,
                structure.cover_document.href,
                render_cover_page(
                    structure.cover_document,
                    version_info,
                    CoverPageOptions(
                        book_title=book_title,
                        cover_banner=cover_banner,
                        cover_footer_line=self.config.cover_footer_line,
                        compiled_by_name=self.config.contributor,
                        cover_variant=self.config.cover_variant,
                    ),
                ),
            )

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

        if structure.notices_document is not None:
            write_text(
                workspace,
                structure.notices_document.href,
                renderer.render_notices_page(structure.notices_document),
            )
        copy_image_assets(workspace, image_assets)
        front_back_matter = FrontBackMatter(
            structure.cover_document, structure.notices_document
        )
        write_nav_file(workspace, front_back_matter, structure.parts)
        write_toc_ncx_file(
            workspace,
            publication_identifier,
            front_back_matter,
            structure.parts,
            book_title,
        )
        write_content_opf_file(
            workspace,
            OPFPackageInput(
                config=self.config,
                book_title=book_title,
                documents=structure.documents,
                image_assets=image_assets,
                publication_identifier=publication_identifier,
                has_cover_asset=has_cover_asset(workspace),
            ),
        )
        package_epub(self.config, workspace)
        logger.info(f"EPUB saved to {self.config.output_path}")

    def _version_info(self) -> str:
        return resolve_version_info(
            self.toc.file_content, self.config.override_version
        )
