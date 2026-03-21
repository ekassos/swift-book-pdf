# Copyright 2025 Evangelos Kassos
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

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .schema import SwiftBookRepoFilePaths

logger = logging.getLogger(__name__)


def get_file_name(file_path: str) -> str:
    return Path(file_path).stem


def find_or_clone_swift_book_repo(
    temp: str,
    input_path: Optional[str] = None,
) -> SwiftBookRepoFilePaths:
    """
    Clone the Swift book repository.

    Args:
        temp: The temporary directory to clone the repository
        input_path: The path to the local copy of the swift-book repo, if available
    """
    if input_path:
        root_dir = Path(input_path) / "TSPL.docc"
        toc_file_path = root_dir / "The-Swift-Programming-Language.md"
        assets_dir = root_dir / "Assets"
        if not root_dir.exists():
            raise FileNotFoundError(
                f"The specified input path {input_path} does not contain the Swift book repository.",
            )
        if not toc_file_path.exists():
            raise FileNotFoundError(
                f"Couldn't find the Table of Contents file (The-Swift-Programming-Language.md) in {root_dir}.",
            )
        if not assets_dir.exists():
            raise FileNotFoundError(
                f"Couldn't find the Assets directory ({assets_dir}).",
            )
        logger.info("Using local TSPL files...")
        return SwiftBookRepoFilePaths(
            toc_file_path=str(toc_file_path),
            root_dir=str(root_dir),
            assets_dir=str(assets_dir),
        )

    logger.info("Downloading TSPL files...")
    repo_url = "https://github.com/swiftlang/swift-book.git"
    clone_dir = Path(temp) / "swift-book"
    git_executable = shutil.which("git")
    if git_executable is None:
        raise RuntimeError("Git is not installed or not in PATH.")

    is_debug = logging.getLogger().isEnabledFor(logging.DEBUG)

    subprocess.run(  # noqa: S603
        [git_executable, "clone", repo_url, str(clone_dir)],
        check=True,
        stdout=None if is_debug else subprocess.DEVNULL,
        stderr=None if is_debug else subprocess.DEVNULL,
    )

    root_dir = clone_dir / "TSPL.docc"
    toc_file_path = root_dir / "The-Swift-Programming-Language.md"
    if not toc_file_path.exists():
        raise FileNotFoundError(
            f"Couldn't find the Table of Contents file (The-Swift-Programming-Language.md) in {root_dir}.",
        )

    assets_dir = root_dir / "Assets"
    if not assets_dir.exists():
        raise FileNotFoundError(f"Couldn't find the Assets directory ({assets_dir}).")
    return SwiftBookRepoFilePaths(
        toc_file_path=str(toc_file_path),
        root_dir=str(root_dir),
        assets_dir=str(assets_dir),
    )


def validate_output_path(output_path: str) -> str:
    output_path_obj = Path(output_path)
    output_dir = output_path_obj.parent if output_path_obj.parent != Path() else Path()

    if output_path_obj.is_dir():
        output_path_obj = _resolve_directory_output_path(output_path_obj)
    else:
        _ensure_pdf_output_path(output_path_obj)
        _ensure_directory_exists(output_dir)

    _verify_output_permissions(output_path_obj, output_dir)

    logger.debug(f"Will save file to: {output_path_obj}")

    return str(output_path_obj)


def _resolve_directory_output_path(output_path_obj: Path) -> Path:
    _ensure_directory_exists(output_path_obj)
    resolved_path = output_path_obj / "swift_book.pdf"
    logger.debug(f"Output path is a directory, will save to: {resolved_path}")
    return resolved_path


def _ensure_pdf_output_path(output_path_obj: Path) -> None:
    if output_path_obj.suffix.lower() != ".pdf":
        raise ValueError(f"Output path is not a PDF file: {output_path_obj}")


def _ensure_directory_exists(path: Path) -> None:
    if path.exists():
        return

    try:
        path.mkdir(parents=True)
        logger.debug(f"Created output directory: {path}")
    except OSError as e:
        raise ValueError(f"Cannot create output directory {path}: {e}") from e


def _verify_output_permissions(output_path_obj: Path, output_dir: Path) -> None:
    if not os.access(output_dir, os.W_OK):
        raise ValueError(f"Cannot write to output directory: {output_dir}")

    if output_path_obj.exists():
        if not os.access(output_path_obj, os.W_OK):
            raise ValueError(f"Cannot overwrite existing file: {output_path_obj}")
        logger.debug(f"Will overwrite existing file: {output_path_obj}")
