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

"""Cover edition variant selection and derived cover text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from swift_book_pdf.epub.cover.constants import (
    COVER_BETA_TEMPLATE_PATH,
    COVER_BETA_TEXT_FILL,
    COVER_CURRENT_TEMPLATE_PATH,
    COVER_CURRENT_TEXT_FILL,
    COVER_NIGHTLY_TEMPLATE_PATH,
    COVER_NIGHTLY_TEXT_FILL,
    COVER_TEMPLATE_PATH,
    COVER_TEXT_FILL,
)

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class CoverVariant:
    """Cover art, label, and color for one edition variant.

    Attributes:
        banner_text: Default inner-cover banner text.
        color: Primary cover text and banner color.
        template_path: Bundled PNG template for the outer cover.
    """

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


def cover_version_label(
    version_info: str | None,
    cover_variant: str | None = None,
) -> str | None:
    """Return the normalized version label shown on the cover.

    Args:
        version_info: Effective Swift version string.
        cover_variant: Optional explicit cover variant name.

    Returns:
        Version label without a leading `Swift` or trailing `Edition`, or
        `None` when no label should be rendered. Beta suffixes are hidden for
        release/current covers but preserved for nightly covers.
    """
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
    """Return the cover variant selected by version text and overrides.

    Args:
        version_info: Effective Swift version string.
        cover_variant: Optional explicit cover variant name.

    Returns:
        Cover variant configuration.
    """
    return COVER_VARIANTS[
        resolve_cover_variant_name(version_info, cover_variant)
    ]


def resolve_cover_variant_name(
    version_info: str | None,
    cover_variant: str | None = None,
) -> str:
    """Resolve a cover variant name and validate explicit overrides.

    Args:
        version_info: Effective Swift version string.
        cover_variant: Optional explicit cover variant name.

    Returns:
        Cover variant key.

    Raises:
        ValueError: If an explicit variant is not registered.
    """
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
    """Return the PNG cover version-label fill color.

    Args:
        version_info: Effective Swift version string.
        cover_variant: Optional explicit cover variant name.

    Returns:
        Hex color used for the outer cover version label.
    """
    return resolve_cover_variant(version_info, cover_variant).color


def cover_png_version_text(
    version_info: str | None,
    cover_variant: str | None = None,
) -> str | None:
    """Return the PNG cover version-label text.

    Args:
        version_info: Effective Swift version string.
        cover_variant: Optional explicit cover variant name.

    Returns:
        Normalized cover version label, or `None`.
    """
    return cover_version_label(version_info, cover_variant)


def cover_template_path(
    version_info: str | None,
    base_cover_image: Path | None = None,
    cover_variant: str | None = None,
    cover_template_paths: dict[str, Path] | None = None,
) -> Path:
    """Return the cover template path after overrides and variant fallback.

    Args:
        version_info: Effective Swift version string.
        base_cover_image: Optional global cover image override.
        cover_variant: Optional explicit cover variant name.
        cover_template_paths: Optional per-variant template overrides.

    Returns:
        Cover template path. The broad base override wins first; otherwise the
        selected variant can be overridden individually before bundled assets
        are used.
    """
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
    """Return effective inner-cover banner text and color.

    Args:
        banner_text: Optional explicit banner label.
        banner_color: Optional explicit banner color.
        version_info: Effective Swift version string.
        cover_variant: Optional explicit cover variant name.

    Returns:
        Banner text and color, using variant defaults for omitted values.
    """
    variant = resolve_cover_variant(version_info, cover_variant)
    text = banner_text.strip() if banner_text else ""
    color = banner_color or variant.color
    return text or variant.banner_text, color
