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

"""Copy bundled static EPUB assets into a workspace."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from swift_book_pdf.epub.assets import REFERENCE_STATIC_DIR
from swift_book_pdf.epub.paths import oebps_workspace_path

if TYPE_CHECKING:
    from pathlib import Path

EPUB_FONT_DIR_NAME = "_static/fonts"
EPUB_FONT_FILE_NAMES = (
    "IBMPlexSans-Medium.ttf",
    "IBMPlexSerif-Italic.ttf",
    "IBMPlexSerif-Medium.ttf",
    "IBMPlexSerif-Regular.ttf",
)


def write_static_files(workspace: Path) -> None:
    """Copy bundled CSS and font files into the EPUB workspace.

    Args:
        workspace: Temporary EPUB workspace root.
    """
    _copy_reference_static_asset("epub.css", workspace)
    _copy_reference_static_asset("pygments.css", workspace)
    for font_file_name in EPUB_FONT_FILE_NAMES:
        _copy_reference_static_asset(f"fonts/{font_file_name}", workspace)


def _copy_reference_static_asset(name: str, workspace: Path) -> None:
    """Copy one bundled reference static asset into OEBPS.

    Args:
        name: Reference asset path relative to `epub_reference`.
        workspace: Temporary EPUB workspace root.
    """
    source = REFERENCE_STATIC_DIR / name
    destination = oebps_workspace_path(workspace, f"_static/{name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
