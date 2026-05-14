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

from pathlib import Path

from swift_book_pdf.epub.constants import (
    COVER_CURRENT_TEMPLATE_PATH,
    COVER_NIGHTLY_TEMPLATE_PATH,
)
from swift_book_pdf.epub.helpers import (
    build_publication_identifier,
    cover_png_version_fill,
    cover_png_version_text,
    cover_template_path,
    resolve_cover_banner,
    resolve_cover_variant_name,
)


def test_cover_template_path_prefers_explicit_base_cover_image(
    tmp_path: Path,
) -> None:
    base_cover_image = tmp_path / "cover-custom.png"
    assert (
        cover_template_path("6.2 beta", base_cover_image) == base_cover_image
    )


def test_resolve_cover_banner_uses_version_based_beta_banner() -> None:
    assert resolve_cover_banner(None, None, "6.2 beta") == (
        "BETA VERSION",
        "#d94a2b",
    )


def test_resolve_cover_banner_defaults_to_release_cover_banner() -> None:
    assert resolve_cover_banner(None, None, "6.2") == (
        "RELEASE VERSION",
        "#33519e",
    )


def test_resolve_cover_banner_supports_current_and_nightly_editions() -> None:
    assert resolve_cover_banner(None, None, "6.2", "current") == (
        "CURRENT EDITION",
        "#19733c",
    )
    assert resolve_cover_banner(None, None, "6.2", "nightly") == (
        "NIGHTLY EDITION",
        "#8e3fa9",
    )


def test_resolve_cover_banner_uses_default_for_blank_override() -> None:
    assert resolve_cover_banner("  ", None, "6.2") == (
        "RELEASE VERSION",
        "#33519e",
    )


def test_cover_template_path_supports_current_and_nightly_editions() -> None:
    assert cover_template_path("6.2", None, "current") == (
        COVER_CURRENT_TEMPLATE_PATH
    )
    assert cover_template_path("6.2", None, "nightly") == (
        COVER_NIGHTLY_TEMPLATE_PATH
    )


def test_cover_template_path_uses_selected_variant_override(
    tmp_path: Path,
) -> None:
    release_cover = tmp_path / "release.png"
    beta_cover = tmp_path / "beta.png"
    current_cover = tmp_path / "current.png"
    nightly_cover = tmp_path / "nightly.png"
    cover_template_paths = {
        "release": release_cover,
        "beta": beta_cover,
        "current": current_cover,
        "nightly": nightly_cover,
    }

    assert cover_template_path("6.2", None, None, cover_template_paths) == (
        release_cover
    )
    assert (
        cover_template_path("6.2 beta", None, None, cover_template_paths)
        == beta_cover
    )
    assert (
        cover_template_path("6.2 beta", None, "current", cover_template_paths)
        == current_cover
    )
    assert (
        cover_template_path("6.2", None, "nightly", cover_template_paths)
        == nightly_cover
    )


def test_cover_png_version_fill_supports_current_and_nightly_editions() -> (
    None
):
    assert cover_png_version_fill("6.2", "current") == "#19733c"
    assert cover_png_version_fill("6.2", "nightly") == "#8e3fa9"


def test_cover_png_version_text_omits_edition_suffix() -> None:
    assert cover_png_version_text("6.2") == "6.2"
    assert cover_png_version_text("Swift 6.2 Edition") == "6.2"
    assert cover_png_version_text("6.2 beta") == "6.2"


def test_cover_png_version_text_keeps_lowercase_beta_for_nightly() -> None:
    assert cover_png_version_text("6.2 beta", "nightly") == "6.2 beta"
    assert cover_png_version_text("6.2 Beta", "nightly") == "6.2 beta"
    assert cover_png_version_text("6.2", "nightly") == "6.2"


def test_cover_png_version_fill_uses_beta_color() -> None:
    assert cover_png_version_fill("6.2") == "#33519e"
    assert cover_png_version_fill("6.2 beta") == "#d94a2b"


def test_resolve_cover_variant_name_rejects_unknown_variant() -> None:
    try:
        resolve_cover_variant_name("6.2", "preview")
    except ValueError as error:
        assert "Unknown cover variant 'preview'" in str(error)
    else:
        raise AssertionError("Expected ValueError for unknown cover variant")


def test_resolve_cover_banner_keeps_version_based_beta_banner() -> None:
    assert resolve_cover_banner(None, None, "6.2 beta") == (
        "BETA VERSION",
        "#d94a2b",
    )


def test_build_publication_identifier_prefers_explicit_seed_override() -> None:
    expected = "urn:uuid:b984fd30-8362-53d6-9879-e2f1803a9020"
    assert (
        build_publication_identifier(
            "6.2.4",
            "2306b38fdd2235b9d7a070e342098c2e08dda90d",
            "version:6.2.3",
        )
        == expected
    )
