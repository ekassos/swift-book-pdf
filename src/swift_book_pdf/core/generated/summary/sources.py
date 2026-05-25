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

"""Resolve source chapters for generated grammar summaries."""

import logging
from pathlib import Path

from swift_book_pdf.core.generated.summary.constants import (
    SUMMARY_FALLBACK_SOURCE_PATHS,
)
from swift_book_pdf.core.generated.summary.messages import (
    FALLBACK_CHAPTERS_MISSING,
    GENERATE_GRAMMAR_PARSE_FAILED,
    PUBLISH_BOOK_PARSE_FAILED,
    SUMMARY_SCRIPT_MISSING,
)

logger = logging.getLogger(__name__)


def resolve_summary_source_paths(
    repo_root: Path,
    publish_book_script: Path,
    generate_grammar_script: Path,
    publish_book_source_paths: list[Path],
) -> list[Path] | None:
    """Return configured grammar sources or a validated fallback source list.

    Args:
        repo_root: Path to the `swift-book` repository root.
        publish_book_script: Path to `bin/publish-book`.
        generate_grammar_script: Path to `bin/generate-grammar`.
        publish_book_source_paths: Source paths parsed from upstream scripts.

    Returns:
        Source chapter paths to use for grammar extraction, or `None` when the
        fallback list contains missing files.
    """
    if publish_book_source_paths:
        return publish_book_source_paths

    if generate_grammar_script.exists():
        logger.warning(GENERATE_GRAMMAR_PARSE_FAILED)
    elif publish_book_script.exists():
        logger.warning(PUBLISH_BOOK_PARSE_FAILED)
    else:
        logger.warning(SUMMARY_SCRIPT_MISSING)

    fallback_paths = [
        repo_root / path for path in SUMMARY_FALLBACK_SOURCE_PATHS
    ]
    missing_paths = [str(path) for path in fallback_paths if not path.exists()]
    if missing_paths:
        logger.warning(FALLBACK_CHAPTERS_MISSING, ", ".join(missing_paths))
        return None
    return fallback_paths
