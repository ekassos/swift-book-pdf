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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


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
