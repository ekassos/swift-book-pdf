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

from swift_book_pdf.epub.helpers import (
    build_publication_identifier,
    cover_template_path,
    resolve_cover_banner,
)


def test_cover_template_path_prefers_explicit_base_cover_image(
    tmp_path: Path,
) -> None:
    base_cover_image = tmp_path / "cover-custom.png"
    assert (
        cover_template_path("6.2 beta", base_cover_image) == base_cover_image
    )


def test_resolve_cover_banner_uses_explicit_beta_base_cover_image() -> None:
    assert resolve_cover_banner(None, None, "6.2 beta", None) == (
        "Beta",
        "#a5aeb0",
    )


def test_resolve_cover_banner_keeps_version_based_beta_banner_for_explicit_cover_path(
    tmp_path: Path,
) -> None:
    assert resolve_cover_banner(
        None,
        None,
        "6.2 beta",
        tmp_path / "cover-custom.png",
    ) == (
        "Beta",
        "#a5aeb0",
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
