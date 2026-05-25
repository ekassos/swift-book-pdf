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

from pathlib import Path


class AssetCatalog:
    def __init__(self, asset_path: Path) -> None:
        self._assets = self._build_asset_pairs(asset_path)

    def resolve(self, image_name: str) -> tuple[Path, Path | None]:
        key = normalize_asset_key(Path(image_name).stem)
        asset_pair = self._assets.get(key)
        if asset_pair is None:
            raise FileNotFoundError(f"Missing image asset: {image_name}")
        return asset_pair

    def _build_asset_pairs(
        self, asset_path: Path
    ) -> dict[str, tuple[Path, Path | None]]:
        asset_pairs: dict[str, tuple[Path, Path | None]] = {}
        for asset in asset_path.iterdir():
            if not asset.is_file():
                continue
            key = normalize_asset_key(asset.stem)
            light_asset, dark_asset = asset_pairs.get(key, (None, None))
            if "~dark" in asset.stem:
                dark_asset = asset
            else:
                light_asset = asset
            if light_asset is not None:
                asset_pairs[key] = (light_asset, dark_asset)
        return asset_pairs


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
