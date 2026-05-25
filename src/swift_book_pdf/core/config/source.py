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

"""Resolve Swift Book source inputs into build-ready paths."""

import logging
import shutil

from swift_book_pdf.core.config.models import (
    BuildSourceConfig,
    ResolvedBuildSource,
)
from swift_book_pdf.core.source.copyright import (
    find_swift_book_copyright_year_range,
)
from swift_book_pdf.core.source.repository import (
    find_or_clone_swift_book_repo,
)

logger = logging.getLogger(__name__)


def resolve_build_source(config: BuildSourceConfig) -> ResolvedBuildSource:
    """Resolve user-selected Swift Book source inputs.

    Args:
        config: User-selected source inputs from the CLI or caller.

    Returns:
        Resolved source paths and derived copyright metadata.

    Raises:
        RuntimeError: If Git is unavailable.
        FileNotFoundError: If the selected local or cloned source is invalid.
    """
    if not shutil.which("git"):
        raise RuntimeError("Git is not installed or not in PATH.")

    file_paths = find_or_clone_swift_book_repo(
        config.temp_dir,
        config.input_path,
        source_ref=config.source_ref,
        source_sha=config.source_sha,
    )
    copyright_year_range = find_swift_book_copyright_year_range(
        file_paths.root_dir
    )

    logger.debug("Swift book repository directory: %s", file_paths.root_dir)
    logger.debug("Assets directory: %s", file_paths.assets_dir)
    logger.debug("Temporary directory: %s", config.temp_dir)
    logger.debug("Table of contents file path: %s", file_paths.toc_file_path)
    logger.debug(
        "Swift book copyright year range: %s",
        copyright_year_range,
    )

    return ResolvedBuildSource(
        temp_dir=config.temp_dir,
        root_dir=file_paths.root_dir,
        toc_file_path=file_paths.toc_file_path,
        assets_dir=file_paths.assets_dir,
        original_work_copyright_year_range=copyright_year_range,
    )
