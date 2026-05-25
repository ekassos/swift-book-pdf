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

import logging
import os
from pathlib import Path

from swift_book_pdf.core.output import OutputFormat

logger = logging.getLogger(__name__)


def validate_output_path(output_path: str, output_format: OutputFormat) -> str:
    """Resolve and validate the path for a generated book artifact.

    Args:
        output_path: User-provided output file or directory path.
        output_format: Expected artifact format, used for the default file name
            and suffix validation.

    Returns:
        A string path to the concrete output file.
    Raises:
        ValueError: If the suffix is wrong, the destination directory cannot be
            created, or the file cannot be written.
    """
    output_path_obj = Path(output_path)
    output_dir = (
        output_path_obj.parent if output_path_obj.parent != Path() else Path()
    )

    if output_path_obj.is_dir():
        output_path_obj = _resolve_directory_output_path(
            output_path_obj, output_format
        )
    else:
        _ensure_output_path(output_path_obj, output_format)
        _ensure_directory_exists(output_dir)

    _verify_output_permissions(output_path_obj, output_dir)

    logger.debug(f"Will save file to: {output_path_obj}")

    return str(output_path_obj)


def _resolve_directory_output_path(
    output_path_obj: Path, output_format: OutputFormat
) -> Path:
    """Turn a directory output target into `swift_book.<format>`."""
    _ensure_directory_exists(output_path_obj)
    resolved_path = output_path_obj / f"swift_book.{output_format.value}"
    logger.debug(f"Output path is a directory, will save to: {resolved_path}")
    return resolved_path


def _ensure_output_path(
    output_path_obj: Path, output_format: OutputFormat
) -> None:
    """Reject file paths that do not match the selected output format.

    Raises:
        ValueError: If `output_path_obj` does not have the expected suffix.
    """
    expected_suffix = f".{output_format.value}"
    if output_path_obj.suffix.lower() != expected_suffix:
        raise ValueError(
            f"Output path is not a {output_format.value.upper()} file: {output_path_obj}"
        )


def _ensure_directory_exists(path: Path) -> None:
    """Create an output directory when needed.

    Raises:
        ValueError: If the directory cannot be created.
    """
    if path.exists():
        return

    try:
        path.mkdir(parents=True)
        logger.debug(f"Created output directory: {path}")
    except OSError as e:
        raise ValueError(f"Cannot create output directory {path}: {e}") from e


def _verify_output_permissions(
    output_path_obj: Path, output_dir: Path
) -> None:
    """Ensure the output directory and existing target are writable.

    Raises:
        ValueError: If the directory is not writable or an existing output file
            cannot be overwritten.
    """
    if not os.access(output_dir, os.W_OK):
        raise ValueError(f"Cannot write to output directory: {output_dir}")

    if output_path_obj.exists():
        if not os.access(output_path_obj, os.W_OK):
            raise ValueError(
                f"Cannot overwrite existing file: {output_path_obj}"
            )
        logger.debug(f"Will overwrite existing file: {output_path_obj}")
