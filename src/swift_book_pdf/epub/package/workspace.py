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

"""Filesystem workspace helpers for EPUB packaging."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

from swift_book_pdf.epub.paths import oebps_workspace_path

if TYPE_CHECKING:
    from swift_book_pdf.epub.assets import ImageAsset
    from swift_book_pdf.epub.config import EPUBConfig


def prepare_workspace(config: EPUBConfig) -> Path:
    """Create and return the temporary EPUB workspace directory."""
    workspace = Path(config.temp_dir) / "epub"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def write_text(workspace: Path, relative_path: str, content: str) -> None:
    """Write UTF-8 text to an OEBPS-relative path."""
    path = oebps_workspace_path(workspace, relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_container_file(workspace: Path) -> None:
    """Write the EPUB mimetype and container metadata files."""
    _write_text_file(workspace / "mimetype", "application/epub+zip")
    _write_text_file(
        workspace / "META-INF" / "container.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
""",
    )


def copy_image_assets(
    workspace: Path, image_assets: dict[str, ImageAsset]
) -> None:
    """Copy rendered document image assets into the EPUB workspace."""
    for asset in image_assets.values():
        destination = oebps_workspace_path(workspace, asset.href)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(asset.source_path, destination)


def package_epub(config: EPUBConfig, workspace: Path) -> None:
    """Zip the EPUB workspace and move the archive to the output path."""
    output_path = Path(config.output_path)
    archive_path = Path(config.temp_dir) / output_path.name
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.write(
            workspace / "mimetype",
            "mimetype",
            compress_type=zipfile.ZIP_STORED,
        )
        for file_path in sorted(workspace.rglob("*")):
            if file_path.is_dir() or file_path.name == "mimetype":
                continue
            archive.write(
                file_path,
                file_path.relative_to(workspace).as_posix(),
                compress_type=zipfile.ZIP_DEFLATED,
            )

    shutil.move(str(archive_path), config.output_path)


def _write_text_file(path: Path, content: str) -> None:
    """Write UTF-8 text to a concrete filesystem path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
