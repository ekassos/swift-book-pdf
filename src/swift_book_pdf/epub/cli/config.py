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

"""EPUB config assembly for CLI commands."""

from pathlib import Path

import click

from swift_book_pdf.config import EPUBConfig


def resolve_cover_variant(
    current_edition: bool, nightly_edition: bool
) -> str | None:
    """Resolve the hidden edition flag pair into a cover variant.

    Args:
        current_edition: Whether the current-edition cover was requested.
        nightly_edition: Whether the nightly-edition cover was requested.

    Returns:
        Selected cover variant name, or `None` for the default release/beta
        behavior.

    Raises:
        click.UsageError: If mutually exclusive hidden edition flags are both
            set.
    """
    if current_edition and nightly_edition:
        raise click.UsageError(
            "--current-edition and --nightly-edition cannot be used together."
        )
    if current_edition:
        return "current"
    if nightly_edition:
        return "nightly"
    return None


def build_cover_template_paths(
    *,
    release: Path | None,
    beta: Path | None,
    current: Path | None,
    nightly: Path | None,
) -> dict[str, Path]:
    """Build the cover-template override mapping.

    Args:
        release: Optional release cover template path.
        beta: Optional beta cover template path.
        current: Optional current-edition cover template path.
        nightly: Optional nightly-edition cover template path.

    Returns:
        Mapping of variant name to supplied template path.
    """
    return {
        name: path
        for name, path in {
            "release": release,
            "beta": beta,
            "current": current,
            "nightly": nightly,
        }.items()
        if path is not None
    }


def build_epub_config(  # noqa: PLR0913
    temp_dir: str,
    output_path: str,
    *,
    input_path: str | None,
    export_cover_image: bool,
    base_cover_image: Path | None,
    cover_template_paths: dict[str, Path],
    cover_footer_line: str | None,
    cover_banner_text: str | None,
    cover_banner_color: str | None,
    cover_variant: str | None,
    override_version: str | None,
    publication_identifier_seed: str | None,
    ibooks_version: str | None,
    publisher: str | None,
    contributor: str | None,
    source_ref: str | None,
    source_sha: str | None,
    dangerously_skip_legal_notices: bool,
) -> EPUBConfig:
    """Build the EPUB configuration from normalized CLI options.

    Args:
        temp_dir: Temporary build directory.
        output_path: Validated EPUB output path.
        input_path: Optional local Swift Book repository path.
        export_cover_image: Whether to export the cover as a standalone image.
        base_cover_image: Optional base cover image path.
        cover_template_paths: Cover template overrides keyed by variant.
        cover_footer_line: Optional cover footer text.
        cover_banner_text: Optional inner-cover banner text.
        cover_banner_color: Optional inner-cover banner color.
        cover_variant: Optional edition cover variant.
        override_version: Optional Swift version override.
        publication_identifier_seed: Optional EPUB identifier seed.
        ibooks_version: Optional Apple Books version metadata.
        publisher: Optional publisher metadata.
        contributor: Optional contributor metadata.
        source_ref: Optional Swift Book Git ref.
        source_sha: Optional Swift Book commit SHA.
        dangerously_skip_legal_notices: Whether notices should be omitted.

    Returns:
        EPUB builder configuration.
    """
    return EPUBConfig(
        temp_dir,
        output_path,
        input_path=input_path,
        export_cover_image=export_cover_image,
        base_cover_image=base_cover_image,
        cover_template_paths=cover_template_paths,
        cover_footer_line=cover_footer_line,
        cover_banner_text=cover_banner_text,
        cover_banner_color=cover_banner_color,
        cover_variant=cover_variant,
        override_version=override_version,
        publication_identifier_seed=publication_identifier_seed,
        ibooks_version=ibooks_version,
        publisher=publisher,
        contributor=contributor,
        source_ref=source_ref,
        source_sha=source_sha,
        dangerously_skip_legal_notices=dangerously_skip_legal_notices,
    )
