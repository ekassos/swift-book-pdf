# Copyright 2025 Evangelos Kassos
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

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class RenderingMode(StrEnum):
    DIGITAL = "digital"
    PRINT = "print"


class OutputFormat(StrEnum):
    PDF = "pdf"
    EPUB = "epub"


class Appearance(StrEnum):
    LIGHT = "light"
    DARK = "dark"


class PaperSize(StrEnum):
    A4 = "a4"
    LETTER = "letter"
    LEGAL = "legal"


class SwiftBookRepoFilePaths(BaseModel):
    toc_file_path: str
    root_dir: str
    assets_dir: str


class RunOptions(BaseModel):
    mode: str
    paper: str
    typesets: int
    main: str | None
    mono: str | None
    unicode: tuple[str, ...]
    emoji: str | None
    header_footer: str | None
    font_size: float | None
    dark: bool
    gutter: bool | None
    output_cover_image: bool = False


class ImageAsset(BaseModel):
    source_path: Path
    href: str
    media_type: str


class DocumentEntry(BaseModel):
    key: str
    title: str
    subtitle: str | None
    href: str
    directory: str | None
    source_path: Path | None = None
    heading_map: dict[str, str] = Field(default_factory=dict)


class PartEntry(BaseModel):
    title: str
    href: str
    directory: str
    children: list[DocumentEntry]


class ManifestItem(BaseModel):
    item_id: str
    href: str
    media_type: str
    properties: str | None = None


class ChapterMetadata(BaseModel):
    file_path: str | None = None
    header_line: str | None = None
    subtitle_line: str | None = None


class GeneratedSummary(BaseModel):
    path: str
    title: str
    subtitle: str


class PublishBookSummaryConfig(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    source_paths: list[str] = Field(default_factory=list)


class TableBlock(BaseModel):
    type: Literal["table"] = "table"
    rows: list[list[str]]


class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    alt: str
    imgname: str


class OrderedListBlock(BaseModel):
    type: Literal["orderedlist"] = "orderedlist"
    items: list[str]


class CodeBlock(BaseModel):
    type: Literal["code"] = "code"
    lines: list[str]


class Header2Block(BaseModel):
    type: Literal["header2"] = "header2"
    content: str


class Header3Block(BaseModel):
    type: Literal["header3"] = "header3"
    content: str


class Header4Block(BaseModel):
    type: Literal["header4"] = "header4"
    content: str


class NoteBlock(BaseModel):
    type: Literal["aside"] = "aside"
    label: str
    blocks: list["Block"]


class ParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    lines: list[str]


class TermListItem(BaseModel):
    label: str
    content: str


class TermListBlock(BaseModel):
    type: Literal["termlist"] = "termlist"
    items: list[TermListItem]


class UnorderedListBlock(BaseModel):
    type: Literal["list"] = "list"
    items: list[list["Block"]]


Block = (
    TableBlock
    | ImageBlock
    | OrderedListBlock
    | CodeBlock
    | Header2Block
    | Header3Block
    | Header4Block
    | NoteBlock
    | ParagraphBlock
    | TermListBlock
    | UnorderedListBlock
)


class SourceDocument(BaseModel):
    entry: DocumentEntry
    lines: list[str]
    blocks: list[Block]


class DocumentColors(BaseModel):
    background: str
    text: str
    header_background: str
    header_text: str
    hero_background: str
    hero_text: str
    link: str
    aside_background: str
    aside_border: str
    aside_text: str
    table_border: str
    code_border: str
    code_background: str
    code_style: str
