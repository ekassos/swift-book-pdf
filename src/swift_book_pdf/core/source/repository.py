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

"""Public entry points for resolving Swift Book source files."""

from swift_book_pdf.core.source import SwiftBookRepoFilePaths
from swift_book_pdf.core.source.clone import clone_swift_book_repo
from swift_book_pdf.core.source.local import resolve_local_swift_book_repo
from swift_book_pdf.core.source.messages import INPUT_PATH_REVISION_CONFLICT
from swift_book_pdf.core.source.revision import (
    get_swift_book_repository_revision,
)


def find_or_clone_swift_book_repo(
    temp: str,
    input_path: str | None = None,
    source_ref: str | None = None,
    source_sha: str | None = None,
) -> SwiftBookRepoFilePaths:
    """Resolve Swift Book source paths from local input or a clone.

    Args:
        temp: Temporary directory used when cloning the upstream repository.
        input_path: Optional local `swift-book` checkout path.
        source_ref: Optional branch or tag to check out for cloned sources.
        source_sha: Optional commit SHA to check out for cloned sources.

    Returns:
        Paths to the table of contents, DocC root, and assets directory.
    Raises:
        ValueError: If revision options are combined with `input_path`.
        RuntimeError: If cloning is required but `git` is unavailable.
        FileNotFoundError: If required Swift Book source paths are missing.
        subprocess.CalledProcessError: If cloning or checkout fails.
    """
    if input_path:
        if source_ref is not None or source_sha is not None:
            raise ValueError(INPUT_PATH_REVISION_CONFLICT)
        return resolve_local_swift_book_repo(input_path)

    return clone_swift_book_repo(
        temp,
        source_ref=source_ref,
        source_sha=source_sha,
    )


__all__ = [
    "find_or_clone_swift_book_repo",
    "get_swift_book_repository_revision",
]
