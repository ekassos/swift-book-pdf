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

"""Validation for a user-provided local Swift Book checkout."""

import logging
from pathlib import Path

from swift_book_pdf.core.source import SwiftBookRepoFilePaths
from swift_book_pdf.core.source.messages import (
    MISSING_ASSETS,
    MISSING_REPOSITORY,
    MISSING_TOC,
)

logger = logging.getLogger(__name__)


def resolve_local_swift_book_repo(input_path: str) -> SwiftBookRepoFilePaths:
    """Resolve required source paths from an existing Swift Book clone.

    Args:
        input_path: Path to a local `swift-book` checkout. The function expects
            `TSPL.docc` to live directly under this directory.

    Returns:
        Paths to the table of contents, DocC root, and assets directory.
    Raises:
        FileNotFoundError: If the checkout, TOC file, or assets directory is
            missing.
    """
    root_dir = Path(input_path) / "TSPL.docc"
    toc_file_path = root_dir / "The-Swift-Programming-Language.md"
    assets_dir = root_dir / "Assets"
    if not root_dir.exists():
        raise FileNotFoundError(
            MISSING_REPOSITORY.format(input_path=input_path)
        )
    if not toc_file_path.exists():
        raise FileNotFoundError(MISSING_TOC.format(root_dir=root_dir))
    if not assets_dir.exists():
        raise FileNotFoundError(MISSING_ASSETS.format(assets_dir=assets_dir))
    logger.info("Using local TSPL files...")
    return SwiftBookRepoFilePaths(
        toc_file_path=str(toc_file_path),
        root_dir=str(root_dir),
        assets_dir=str(assets_dir),
    )
