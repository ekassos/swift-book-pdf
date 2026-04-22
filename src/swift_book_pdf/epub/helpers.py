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

from __future__ import annotations

import html
import posixpath
import re
import uuid
from pathlib import Path, PurePosixPath

from .constants import (
    COVER_BETA_TEMPLATE_PATH,
    COVER_TEMPLATE_PATH,
    OEBPS_DIR_NAME,
)


def relative_href(current_href: str, target_href: str) -> str:
    current_parent = PurePosixPath(current_href).parent
    current_parent_str = (
        "." if str(current_parent) == "." else str(current_parent)
    )
    return posixpath.relpath(target_href, current_parent_str)


def anchor_for_heading(title: str) -> str:
    cleaned = re.sub(r"[*`]", "", title).strip()
    cleaned = re.sub("[()/:,.!?'\\u2019]", "", cleaned)
    cleaned = re.sub(r"\s+", "-", cleaned)
    return re.sub(r"-{2,}", "-", cleaned)


def make_unique_anchor(anchor: str, seen: dict[str, int]) -> str:
    count = seen.get(anchor, 0)
    seen[anchor] = count + 1
    if count == 0:
        return anchor
    return f"{anchor}-{count + 1}"


def part_section_id(title: str) -> str:
    return anchor_for_heading(title).lower()


def normalize_asset_key(stem: str) -> str:
    normalized = stem.replace("~dark", "")
    normalized = normalized.replace("@2x", "")
    if normalized.endswith("_2x"):
        normalized = normalized.removesuffix("_2x")
    return normalized


def image_destination_name(asset_path: Path) -> str:
    key = normalize_asset_key(asset_path.stem)
    suffix = asset_path.suffix.lower()
    scale_suffix = (
        "_2x"
        if "@2x" in asset_path.stem or asset_path.stem.endswith("_2x")
        else ""
    )
    dark_suffix = "~dark" if "~dark" in asset_path.stem else ""
    return f"{key}{dark_suffix}{scale_suffix}{suffix}"


def media_type_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".svg":
        return "image/svg+xml"
    raise ValueError(f"Unsupported EPUB media type for asset: {path}")


def strip_html_tags(text: str) -> str:
    stripped = re.sub(r"<[^>]+>", "", text)
    return html.unescape(" ".join(stripped.split()))


def oebps_workspace_path(workspace: Path, relative_path: str) -> Path:
    return workspace / OEBPS_DIR_NAME / PurePosixPath(relative_path)


def cover_edition_text(version_info: str | None) -> str | None:
    if version_info is None:
        return None
    normalized_version = version_info.strip()
    if not normalized_version:
        return None
    normalized_version = re.sub(
        r"\s+beta(?:\s+\d+)?\b",
        "",
        normalized_version,
        flags=re.IGNORECASE,
    ).strip()
    if normalized_version.lower().endswith("edition"):
        return normalized_version
    return f"Swift {normalized_version} Edition"


def cover_template_path(
    version_info: str | None,
    base_cover_image: Path | None = None,
) -> Path:
    if base_cover_image is not None:
        return base_cover_image
    if version_info is not None and "beta" in version_info.lower():
        return COVER_BETA_TEMPLATE_PATH
    return COVER_TEMPLATE_PATH


def build_publication_identifier(
    version_info: str | None,
    source_revision: str | None,
) -> str:
    seed = source_revision
    if seed is None and version_info is not None:
        normalized_version = " ".join(version_info.split())
        if normalized_version:
            seed = f"version:{normalized_version}"
    if seed is None:
        return f"urn:uuid:{uuid.uuid4()}"
    return f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, f'swift-book:{seed}')}"
