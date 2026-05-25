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

"""EPUB asset discovery and media-type helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

LOCAL_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
"""Bundled package asset directory."""

REFERENCE_STATIC_DIR = LOCAL_ASSETS_DIR / "epub_reference"
"""Directory containing EPUB reference CSS, fonts, and cover art."""

REFERENCE_NOTICES_DIR = LOCAL_ASSETS_DIR / "notices"
"""Directory containing bundled notices text."""

IBM_PLEX_OFL_PATH = REFERENCE_NOTICES_DIR / "IBM-Plex-OFL.txt"
"""Path to the bundled IBM Plex Open Font License text."""


@dataclass(frozen=True)
class ImageAsset:
    """An image copied into the EPUB package.

    Attributes:
        source_path: Source image path on disk.
        href: EPUB package href where the image is written.
        media_type: Manifest media type for the image.
    """

    source_path: Path
    href: str
    media_type: str


class AssetCatalog:
    """Lookup table for source image assets and optional dark variants.

    Swift Book image references are not always byte-for-byte file stems. The
    catalog indexes normalized stems so `@2x`, `_2x`, and `~dark` variants can
    be paired before EPUB rendering decides which files to copy.
    """

    def __init__(self, asset_path: Path) -> None:
        """Index image assets from an upstream Swift Book asset directory.

        Args:
            asset_path: Directory containing image files from the source book.
        """
        self._assets = self._build_asset_pairs(asset_path)

    def resolve(self, image_name: str) -> tuple[Path, Path | None]:
        """Resolve an image reference to light and optional dark assets.

        Args:
            image_name: Raw Markdown image target from the source document.

        Returns:
            Light image path and an optional dark-mode variant.

        Raises:
            FileNotFoundError: If the source asset directory has no matching
                normalized light asset.
        """
        key = normalize_asset_key(Path(image_name).stem)
        asset_pair = self._assets.get(key)
        if asset_pair is None:
            raise FileNotFoundError(f"Missing image asset: {image_name}")
        return asset_pair

    def _build_asset_pairs(
        self, asset_path: Path
    ) -> dict[str, tuple[Path, Path | None]]:
        """Index light/dark image variants by normalized asset key.

        Args:
            asset_path: Directory containing source image files.

        Returns:
            Mapping from normalized image stem to light and dark asset paths.
        """
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
    """Strip scale and dark-mode suffixes from an image stem.

    Args:
        stem: File stem without extension.

    Returns:
        Stem used to match source Markdown image names with concrete asset
        files, independent of Retina or dark-mode suffixes.
    """
    normalized = stem.replace("~dark", "")
    normalized = normalized.replace("@2x", "")
    if normalized.endswith("_2x"):
        normalized = normalized.removesuffix("_2x")
    return normalized


def image_destination_name(asset_path: Path) -> str:
    """Return the normalized EPUB file name for a source image asset."""
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
    """Return the EPUB manifest media type for a supported image path.

    Args:
        path: Image file path whose suffix determines the media type.

    Returns:
        OPF manifest media type.

    Raises:
        ValueError: If the image suffix is not supported by the EPUB pipeline.
    """
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".svg":
        return "image/svg+xml"
    raise ValueError(f"Unsupported EPUB media type for asset: {path}")
