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

"""EPUB build configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from swift_book_pdf.core.config.models import BaseBuildConfig
from swift_book_pdf.core.output import OutputFormat


@dataclass(frozen=True, kw_only=True)
class EPUBConfig(BaseBuildConfig):
    """Resolved configuration for EPUB builds.

    Attributes:
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
    """

    export_cover_image: bool = False
    base_cover_image: Path | None = None
    cover_template_paths: dict[str, Path] = field(default_factory=dict)
    cover_footer_line: str | None = None
    cover_banner_text: str | None = None
    cover_banner_color: str | None = None
    cover_variant: str | None = None
    override_version: str | None = None
    publication_identifier_seed: str | None = None
    ibooks_version: str | None = None
    publisher: str | None = None
    contributor: str | None = None

    output_format: ClassVar[OutputFormat] = OutputFormat.EPUB
