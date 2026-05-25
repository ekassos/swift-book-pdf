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
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

from swift_book_pdf.epub.assets import (
    image_destination_name,
    media_type_for_path,
    normalize_asset_key,
)
from swift_book_pdf.epub.models import ImageAsset
from swift_book_pdf.epub.paths import relative_href

if TYPE_CHECKING:
    from swift_book_pdf.core.blocks.models import ImageBlock

logger = logging.getLogger(__name__)


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


def render_image_block(
    block: ImageBlock,
    current_href: str,
    image_assets: dict[str, ImageAsset],
    asset_catalog: AssetCatalog,
) -> str:
    asset, dark_asset = asset_catalog.resolve(block.imgname)
    image_href = _register_asset(asset, image_assets)
    width = _image_display_width(asset, Path(image_href).name)
    width_attr = f' style="width: {width:.1f}px;"' if width is not None else ""
    alt = html.escape(block.alt or block.imgname)
    if dark_asset is None:
        return (
            f'<img alt="{alt}" class="align-center" '
            f'src="{html.escape(relative_href(current_href, image_href))}"{width_attr} />'
        )

    dark_image_href = _register_asset(dark_asset, image_assets)
    return (
        '<div class="theme-image">'
        f'<img alt="{alt}" class="align-center image-light" '
        f'src="{html.escape(relative_href(current_href, image_href))}"{width_attr} />'
        f'<img alt="{alt}" class="align-center image-dark" '
        f'src="{html.escape(relative_href(current_href, dark_image_href))}"{width_attr} />'
        "</div>"
    )


def _register_asset(asset: Path, image_assets: dict[str, ImageAsset]) -> str:
    href = f"_images/{image_destination_name(asset)}"
    if href not in image_assets:
        image_assets[href] = ImageAsset(
            source_path=asset,
            href=href,
            media_type=media_type_for_path(asset),
        )
    return href


def _image_display_width(path: Path, file_name: str) -> float | None:
    try:
        with Image.open(path) as image:
            width = image.width
    except OSError:
        logger.warning("Couldn't read image dimensions for %s", path)
        return None

    if "_2x" in file_name or "@2x" in path.stem:
        return width / 2
    return float(width)
