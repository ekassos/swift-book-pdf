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

from pydantic import BaseModel, Field

from swift_book_pdf.core.blocks.model import Block


class DocumentEntry(BaseModel):
    """Navigation metadata for one source document in a generated book."""

    key: str
    """Stable lowercase document key used for cross-document links."""

    title: str
    """Display title."""

    subtitle: str | None
    """Optional subtitle line."""

    href: str
    """Output-relative document href."""

    directory: str | None
    """Source section directory, or `None` for generated entries."""

    source_path: Path | None = None
    """Optional path to the source Markdown file."""

    heading_map: dict[str, str] = Field(default_factory=dict)
    """Mapping from source heading text to generated anchors."""


class PartEntry(BaseModel):
    """A top-level book part and the documents grouped under it."""

    title: str
    """Part display title."""

    href: str
    """Output-relative part page href."""

    directory: str
    """Source directory represented by this part."""

    children: list[DocumentEntry]
    """Documents grouped under this part."""


class SourceDocument(BaseModel):
    """A source document after Markdown preprocessing and block parsing."""

    entry: DocumentEntry
    """Navigation metadata for the source document."""

    lines: list[str]
    """Preprocessed Markdown lines."""

    blocks: list[Block]
    """Parsed backend-neutral block tree."""
