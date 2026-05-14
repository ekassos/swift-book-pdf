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
import posixpath
import re
import uuid
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .constants import (
    COVER_BETA_TEMPLATE_PATH,
    COVER_BETA_TEXT_FILL,
    COVER_CURRENT_TEMPLATE_PATH,
    COVER_CURRENT_TEXT_FILL,
    COVER_NIGHTLY_TEMPLATE_PATH,
    COVER_NIGHTLY_TEXT_FILL,
    COVER_TEMPLATE_PATH,
    COVER_TEXT_FILL,
    OEBPS_DIR_NAME,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CoverVariant:
    banner_text: str
    color: str
    template_path: Path


COVER_VARIANTS = {
    "release": CoverVariant(
        "RELEASE VERSION",
        COVER_TEXT_FILL,
        COVER_TEMPLATE_PATH,
    ),
    "beta": CoverVariant(
        "BETA VERSION",
        COVER_BETA_TEXT_FILL,
        COVER_BETA_TEMPLATE_PATH,
    ),
    "current": CoverVariant(
        "CURRENT EDITION",
        COVER_CURRENT_TEXT_FILL,
        COVER_CURRENT_TEMPLATE_PATH,
    ),
    "nightly": CoverVariant(
        "NIGHTLY EDITION",
        COVER_NIGHTLY_TEXT_FILL,
        COVER_NIGHTLY_TEMPLATE_PATH,
    ),
}


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


def cover_png_version_text(
    version_info: str | None,
    cover_variant: str | None = None,
) -> str | None:
    if version_info is None:
        return None
    normalized_version = version_info.strip()
    if not normalized_version:
        return None
    normalized_version = re.sub(
        r"^Swift\s+",
        "",
        normalized_version,
        flags=re.IGNORECASE,
    ).strip()
    normalized_version = re.sub(
        r"\s+Edition$",
        "",
        normalized_version,
        flags=re.IGNORECASE,
    ).strip()
    if cover_variant == "nightly":
        normalized_version = re.sub(
            r"\bbeta\b", "beta", normalized_version, flags=re.IGNORECASE
        )
    else:
        normalized_version = re.sub(
            r"\s+beta(?:\s+\d+)?\b",
            "",
            normalized_version,
            flags=re.IGNORECASE,
        ).strip()
    if not normalized_version:
        return None
    return normalized_version


def resolve_cover_variant(
    version_info: str | None,
    cover_variant: str | None = None,
) -> CoverVariant:
    return COVER_VARIANTS[
        resolve_cover_variant_name(version_info, cover_variant)
    ]


def resolve_cover_variant_name(
    version_info: str | None,
    cover_variant: str | None = None,
) -> str:
    if cover_variant is not None:
        if cover_variant not in COVER_VARIANTS:
            known_variants = ", ".join(sorted(COVER_VARIANTS))
            raise ValueError(
                f"Unknown cover variant {cover_variant!r}. "
                f"Expected one of: {known_variants}."
            )
        return cover_variant
    if version_info is not None and "beta" in version_info.lower():
        return "beta"
    return "release"


def cover_png_version_fill(
    version_info: str | None,
    cover_variant: str | None = None,
) -> str:
    return resolve_cover_variant(version_info, cover_variant).color


def cover_template_path(
    version_info: str | None,
    base_cover_image: Path | None = None,
    cover_variant: str | None = None,
    cover_template_paths: dict[str, Path] | None = None,
) -> Path:
    if base_cover_image is not None:
        return base_cover_image
    variant_name = resolve_cover_variant_name(version_info, cover_variant)
    if (
        cover_template_paths is not None
        and variant_name in cover_template_paths
    ):
        return cover_template_paths[variant_name]
    return COVER_VARIANTS[variant_name].template_path


def resolve_cover_banner(
    banner_text: str | None,
    banner_color: str | None,
    version_info: str | None,
    cover_variant: str | None = None,
) -> tuple[str, str]:
    variant = resolve_cover_variant(version_info, cover_variant)
    text = banner_text.strip() if banner_text else ""
    color = banner_color or variant.color
    return text or variant.banner_text, color


def build_publication_identifier(
    version_info: str | None,
    source_revision: str | None,
    publication_identifier_seed: str | None = None,
) -> str:
    seed = publication_identifier_seed
    if seed is None:
        seed = source_revision
    if seed is None and version_info is not None:
        normalized_version = " ".join(version_info.split())
        if normalized_version:
            seed = f"version:{normalized_version}"
    if seed is None:
        logger.debug(
            "EPUB publication identifier seed unavailable; generating random UUID4"
        )
        return f"urn:uuid:{uuid.uuid4()}"
    logger.debug(
        f"EPUB publication identifier pre-hash seed: swift-book:{seed}"
    )
    return f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, f'swift-book:{seed}')}"
