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

"""Path helpers for EPUB workspace and package hrefs."""

from __future__ import annotations

import posixpath
from pathlib import Path, PurePosixPath

from swift_book_pdf.epub.constants import OEBPS_DIR_NAME


def relative_href(current_href: str, target_href: str) -> str:
    """Return a POSIX relative href from one package document to another."""
    current_parent = PurePosixPath(current_href).parent
    current_parent_str = (
        "." if str(current_parent) == "." else str(current_parent)
    )
    return posixpath.relpath(target_href, current_parent_str)


def oebps_workspace_path(workspace: Path, relative_path: str) -> Path:
    """Return the filesystem path for an OEBPS-relative package path."""
    return workspace / OEBPS_DIR_NAME / PurePosixPath(relative_path)
