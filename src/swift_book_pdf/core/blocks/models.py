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

from typing import Literal

from pydantic import BaseModel


class TableBlock(BaseModel):
    """A Markdown table represented as plain cell text."""

    type: Literal["table"] = "table"
    """Discriminator used by renderers and tests."""

    rows: list[list[str]]
    """Table rows after trimming cell whitespace."""


class ImageBlock(BaseModel):
    """A Markdown image reference resolved later by each output backend."""

    type: Literal["image"] = "image"
    """Discriminator used by renderers and tests."""

    alt: str
    """Alternative text from the Markdown image."""

    imgname: str
    """Raw image path or name from the Markdown image target."""


class OrderedListBlock(BaseModel):
    """A flat ordered list whose items have already been line-joined."""

    type: Literal["orderedlist"] = "orderedlist"
    """Discriminator used by renderers and tests."""

    items: list[str]
    """Ordered list item text in source order."""


class CodeBlock(BaseModel):
    """A fenced Swift code block."""

    type: Literal["code"] = "code"
    """Discriminator used by renderers and tests."""

    lines: list[str]
    """Code lines without the opening and closing fences."""


class Header2Block(BaseModel):
    """A second-level Markdown heading."""

    type: Literal["header2"] = "header2"
    """Discriminator used by renderers and tests."""

    content: str
    """Heading text without the leading Markdown markers."""


class Header3Block(BaseModel):
    """A third-level Markdown heading."""

    type: Literal["header3"] = "header3"
    """Discriminator used by renderers and tests."""

    content: str
    """Heading text without the leading Markdown markers."""


class Header4Block(BaseModel):
    """A fourth-level Markdown heading."""

    type: Literal["header4"] = "header4"
    """Discriminator used by renderers and tests."""

    content: str
    """Heading text without the leading Markdown markers."""


class NoteBlock(BaseModel):
    """A labeled Swift Book aside containing nested blocks."""

    type: Literal["aside"] = "aside"
    """Discriminator used by renderers and tests."""

    label: str
    """Aside label before the colon, for example `Note`."""

    blocks: list["Block"]
    """Parsed content inside the aside."""


class ParagraphBlock(BaseModel):
    """A Markdown paragraph before backend-specific inline conversion."""

    type: Literal["paragraph"] = "paragraph"
    """Discriminator used by renderers and tests."""

    lines: list[str]
    """Paragraph lines with surrounding whitespace stripped."""


class TermListItem(BaseModel):
    """One parsed grammar term-list entry."""

    label: str
    """Grammar term being defined."""

    content: str
    """Definition text that follows the term separator."""


class TermListBlock(BaseModel):
    """A list of grammar terms detected from Swift Book bullet syntax."""

    type: Literal["termlist"] = "termlist"
    """Discriminator used by renderers and tests."""

    items: list[TermListItem]
    """Parsed term entries in source order."""


class UnorderedListBlock(BaseModel):
    """An unordered list whose items can contain nested blocks."""

    type: Literal["list"] = "list"
    """Discriminator used by renderers and tests."""

    items: list[list["Block"]]
    """Each source bullet represented as parsed nested blocks."""


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
