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

"""EPUB Click command entrypoint."""

from functools import partial
from pathlib import Path

import click

import swift_book_pdf.epub.cli.config as epub_config
from swift_book_pdf.book import build_epub
from swift_book_pdf.cli.common import run_build
from swift_book_pdf.cli.legal_notices import legal_notices_option
from swift_book_pdf.cli.options import (
    output_path_argument,
    override_version_option,
    source_options,
    version_option,
)
from swift_book_pdf.core.output import OutputFormat
from swift_book_pdf.epub.cli.options import (
    epub_cover_options,
    epub_metadata_options,
)


@click.command(name="swift-book-epub")
@output_path_argument
@epub_cover_options
@override_version_option
@epub_metadata_options
@legal_notices_option
@source_options
@version_option("Swift-Book-EPUB")
def epub(  # noqa: PLR0913
    output_path: str,
    export_cover_image: bool,
    base_cover_image: Path | None,
    release_cover_image: Path | None,
    beta_cover_image: Path | None,
    current_cover_image: Path | None,
    nightly_cover_image: Path | None,
    cover_footer_line: str | None,
    cover_banner_text: str | None,
    cover_banner_color: str | None,
    current_edition: bool,
    nightly_edition: bool,
    override_version: str | None,
    publication_identifier_seed: str | None,
    ibooks_version: str | None,
    publisher: str | None,
    contributor: str | None,
    dangerously_skip_legal_notices: bool,
    input_path: str | None,
    source_ref: str | None,
    source_sha: str | None,
    verbose: bool,
) -> None:
    """Build the EPUB command from parsed Click options.

    Args:
        output_path: User-provided output path.
        export_cover_image: Whether to export the cover as a standalone image.
        base_cover_image: Optional base cover image path.
        release_cover_image: Optional release cover template path.
        beta_cover_image: Optional beta cover template path.
        current_cover_image: Optional current-edition cover template path.
        nightly_cover_image: Optional nightly-edition cover template path.
        cover_footer_line: Optional cover footer text.
        cover_banner_text: Optional inner-cover banner text.
        cover_banner_color: Optional inner-cover banner color.
        current_edition: Whether the current-edition cover was requested.
        nightly_edition: Whether the nightly-edition cover was requested.
        override_version: Optional Swift version override.
        publication_identifier_seed: Optional EPUB identifier seed.
        ibooks_version: Optional Apple Books version metadata.
        publisher: Optional publisher metadata.
        contributor: Optional contributor metadata.
        dangerously_skip_legal_notices: Whether generated notices are omitted.
        input_path: Optional local Swift Book repository path.
        source_ref: Optional Swift Book Git ref.
        source_sha: Optional Swift Book commit SHA.
        verbose: Whether debug logging should be enabled.
    """
    cover_variant = epub_config.resolve_cli_cover_variant(
        current_edition, nightly_edition
    )
    cover_template_paths = epub_config.build_cover_template_paths(
        release=release_cover_image,
        beta=beta_cover_image,
        current=current_cover_image,
        nightly=nightly_cover_image,
    )

    run_build(
        verbose=verbose,
        output_path=output_path,
        output_format=OutputFormat.EPUB,
        config_builder=partial(
            epub_config.build_epub_config,
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
        ),
        builder=build_epub,
    )


if __name__ == "__main__":
    epub()
