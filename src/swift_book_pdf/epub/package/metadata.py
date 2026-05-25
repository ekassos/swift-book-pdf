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

"""OPF metadata construction."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from swift_book_pdf.epub.constants import EPUB_IDENTIFIER_ID

if TYPE_CHECKING:
    from swift_book_pdf.epub.package.opf import OPFPackageInput

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PackageMetadata:
    """Structured OPF metadata for a generated EPUB."""

    language: str
    """BCP 47 language tag for the publication."""

    book_title: str
    """Effective EPUB book title."""

    creator: str
    """Primary creator metadata value."""

    publisher: str | None
    """Optional publisher metadata value."""

    contributor: str | None
    """Optional contributor metadata value."""

    identifier_id: str
    """ID used by the OPF unique-identifier attribute."""

    publication_identifier: str
    """Stable EPUB publication identifier."""

    ibooks_version: str | None
    """Optional Apple Books version metadata value."""

    modified: str
    """UTC `dcterms:modified` timestamp."""

    has_cover_asset: bool
    """Whether `_static/cover.png` is in the package."""


def build_metadata(
    package_input: OPFPackageInput,
    modified: str,
) -> PackageMetadata:
    """Build structured OPF metadata for a generated EPUB.

    Args:
        package_input: Inputs shared by OPF package writers.
        modified: UTC `dcterms:modified` timestamp.

    Returns:
        Metadata object ready for template rendering.
    """
    config = package_input.config
    return PackageMetadata(
        language="en",
        book_title=package_input.book_title,
        creator="The Swift project authors",
        publisher=config.publisher,
        contributor=config.contributor,
        identifier_id=EPUB_IDENTIFIER_ID,
        publication_identifier=package_input.publication_identifier,
        ibooks_version=config.ibooks_version,
        modified=modified,
        has_cover_asset=package_input.has_cover_asset,
    )


def build_publication_identifier(
    version_info: str | None,
    source_revision: str | None,
    publication_identifier_seed: str | None = None,
) -> str:
    """Build a stable UUID URN for the EPUB package.

    Args:
        version_info: Swift version string detected from source.
        source_revision: Source repository revision when available.
        publication_identifier_seed: Optional explicit pre-hash seed.

    Returns:
        Stable UUID5 URN when a seed is available, otherwise a random UUID4
        URN.
    """
    seed = publication_identifier_seed
    if seed is None:
        seed = source_revision
    if seed is None and version_info is not None:
        normalized_version = " ".join(version_info.split())
        if normalized_version:
            seed = f"version:{normalized_version}"
    if seed is None:
        logger.debug(
            "EPUB publication identifier seed unavailable; generating random UUID4"
        )
        return f"urn:uuid:{uuid.uuid4()}"
    logger.debug(
        f"EPUB publication identifier pre-hash seed: swift-book:{seed}"
    )
    return f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, f'swift-book:{seed}')}"
