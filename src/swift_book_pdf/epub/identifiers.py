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

"""EPUB publication identifier generation."""

from __future__ import annotations

import logging
import uuid

logger = logging.getLogger(__name__)


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
