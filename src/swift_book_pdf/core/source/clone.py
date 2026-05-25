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

"""Clone and checkout helpers for the Swift Book source repository."""

import logging
import shutil
import subprocess
from pathlib import Path

from swift_book_pdf.core.source import SwiftBookRepoFilePaths
from swift_book_pdf.core.source.messages import (
    MISSING_ASSETS,
    MISSING_GIT,
    MISSING_TOC,
    SOURCE_REF_IGNORED,
)

logger = logging.getLogger(__name__)

SWIFT_BOOK_REPO_URL = "https://github.com/swiftlang/swift-book.git"


def clone_swift_book_repo(
    temp: str,
    source_ref: str | None = None,
    source_sha: str | None = None,
) -> SwiftBookRepoFilePaths:
    """Clone swift-book into a temp directory and optionally check out a ref.

    Args:
        temp: Temporary directory where the repository will be cloned.
        source_ref: Optional branch or tag to check out after cloning.
        source_sha: Optional commit SHA to check out after cloning. Takes
            precedence over `source_ref`.

    Returns:
        Paths to the cloned table of contents, DocC root, and assets directory.
    Raises:
        RuntimeError: If `git` is unavailable.
        FileNotFoundError: If the cloned repository does not contain expected
            Swift Book files.
        subprocess.CalledProcessError: If `git clone` or `git checkout` fails.
    """
    logger.info("Downloading TSPL files...")
    clone_dir = Path(temp) / "swift-book"
    git_executable = shutil.which("git")
    if git_executable is None:
        raise RuntimeError(MISSING_GIT)

    is_debug = logging.getLogger().isEnabledFor(logging.DEBUG)

    subprocess.run(  # noqa: S603
        [git_executable, "clone", SWIFT_BOOK_REPO_URL, str(clone_dir)],
        check=True,
        stdout=None if is_debug else subprocess.DEVNULL,
        stderr=None if is_debug else subprocess.DEVNULL,
    )

    _checkout_swift_book_source(
        git_executable,
        clone_dir,
        source_ref=source_ref,
        source_sha=source_sha,
        is_debug=is_debug,
    )

    return _resolve_cloned_repo_paths(clone_dir)


def _resolve_cloned_repo_paths(clone_dir: Path) -> SwiftBookRepoFilePaths:
    """Validate and return required paths from a freshly cloned repository."""
    root_dir = clone_dir / "TSPL.docc"
    toc_file_path = root_dir / "The-Swift-Programming-Language.md"
    if not toc_file_path.exists():
        raise FileNotFoundError(MISSING_TOC.format(root_dir=root_dir))

    assets_dir = root_dir / "Assets"
    if not assets_dir.exists():
        raise FileNotFoundError(MISSING_ASSETS.format(assets_dir=assets_dir))
    return SwiftBookRepoFilePaths(
        toc_file_path=str(toc_file_path),
        root_dir=str(root_dir),
        assets_dir=str(assets_dir),
    )


def _checkout_swift_book_source(
    git_executable: str,
    clone_dir: Path,
    source_ref: str | None,
    source_sha: str | None,
    is_debug: bool,
) -> None:
    """Check out the requested source ref or SHA inside a cloned repository.

    Args:
        git_executable: Resolved path to the `git` executable.
        clone_dir: Path to the cloned repository.
        source_ref: Optional branch or tag requested by the caller.
        source_sha: Optional commit SHA requested by the caller.
        is_debug: Whether git output should be shown directly.

    Raises:
        subprocess.CalledProcessError: If checkout fails.
    """
    target = source_sha or source_ref
    if target is None:
        return

    if source_sha and source_ref:
        logger.warning(SOURCE_REF_IGNORED, source_ref, source_sha)

    label = "commit SHA" if source_sha is not None else "source ref"
    logger.info("Checking out swift-book %s %s...", label, target)
    subprocess.run(  # noqa: S603
        [git_executable, "checkout", "--detach", target],
        cwd=clone_dir,
        check=True,
        stdout=None if is_debug else subprocess.DEVNULL,
        stderr=None if is_debug else subprocess.DEVNULL,
    )
