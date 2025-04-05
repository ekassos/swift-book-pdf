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
import subprocess
from typing import Optional

from .schema import SwiftBookRepoFilePaths

logger = logging.getLogger(__name__)


def get_file_name(file_path: str) -> str:
    return os.path.basename(file_path).replace(".md", "")


def find_or_clone_swift_book_repo(
    temp: str, input_path: Optional[str] = None
) -> SwiftBookRepoFilePaths:
    """
    Clone the Swift book repository.

    Args:
        temp: The temporary directory to clone the repository
        input_path: The path to the local copy of the swift-book repo, if available
    """
    if input_path:
        root_dir = os.path.join(input_path, "TSPL.docc/")
        toc_file_path = os.path.join(root_dir, "The-Swift-Programming-Language.md")
        assets_dir = os.path.join(root_dir, "Assets/")
        if not os.path.exists(root_dir):
            raise FileNotFoundError(
                f"The specified input path {input_path} does not contain the Swift book repository."
            )
        elif not os.path.exists(toc_file_path):
            raise FileNotFoundError(
                f"Couldn't find the Table of Contents file (The-Swift-Programming-Language.md) in {root_dir}."
            )
        elif not os.path.exists(assets_dir):
            raise FileNotFoundError(
                f"Couldn't find the Assets directory ({assets_dir})."
            )
        else:
            logger.info("Using local TSPL files...")
            return SwiftBookRepoFilePaths(
                toc_file_path=toc_file_path,
                root_dir=root_dir,
                assets_dir=assets_dir,
            )

    logger.info("Downloading TSPL files...")
    repo_url = "https://github.com/swiftlang/swift-book.git"
    clone_dir = os.path.join(temp, "swift-book")

    is_debug = logging.getLogger().isEnabledFor(logging.DEBUG)

    subprocess.run(
        ["git", "clone", repo_url, clone_dir],
        check=True,
        stdout=None if is_debug else subprocess.DEVNULL,
        stderr=None if is_debug else subprocess.DEVNULL,
    )

    root_dir = os.path.join(clone_dir, "TSPL.docc/")
    toc_file_path = os.path.join(root_dir, "The-Swift-Programming-Language.md")
    if not os.path.exists(toc_file_path):
        raise FileNotFoundError(
            f"Couldn't find the Table of Contents file (The-Swift-Programming-Language.md) in {root_dir}."
        )

    assets_dir = os.path.join(root_dir, "Assets/")
    if not os.path.exists(assets_dir):
        raise FileNotFoundError(f"Couldn't find the Assets directory ({assets_dir}).")
    return SwiftBookRepoFilePaths(
        toc_file_path=toc_file_path,
        root_dir=root_dir,
        assets_dir=assets_dir,
    )


def validate_output_path(output_path: str) -> str:
    output_dir = os.path.dirname(output_path) or "."  # Default to current directory

    if os.path.isdir(output_path):
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
                logger.debug(f"Created output directory: {output_path}")
            except OSError as e:
                raise ValueError(f"Cannot create output directory {output_path}: {e}")

        # If it's a directory, use default filename in that directory
        output_path = os.path.join(output_path, "swift_book.pdf")
        logger.debug(f"Output path is a directory, will save to: {output_path}")
    elif os.path.exists(output_path):
        # If the path exists but is not a directory
        _, ext = os.path.splitext(output_path)
        if ext.lower() != ".pdf":
            raise ValueError(f"Output path is not a PDF file: {output_path}")
    else:
        # If path doesn't exist, ensure it has .pdf extension
        _, ext = os.path.splitext(output_path)
        if ext.lower() != ".pdf":
            raise ValueError(f"Output path is not a PDF file: {output_path}")

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                logger.debug(f"Created output directory: {output_dir}")
            except OSError as e:
                raise ValueError(f"Cannot create output directory {output_dir}: {e}")

    # Verify write permissions
    if not os.access(output_dir, os.W_OK):
        raise ValueError(f"Cannot write to output directory: {output_dir}")

    # Check if the file already exists and if we can overwrite it
    if os.path.exists(output_path):
        if not os.access(output_path, os.W_OK):
            raise ValueError(f"Cannot overwrite existing file: {output_path}")
        logger.debug(f"Will overwrite existing file: {output_path}")

    logger.debug(f"Will save file to: {output_path}")

    return output_path
