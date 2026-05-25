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

"""Leaf block parsing for images, fenced Swift code, and headings."""

from swift_book_pdf.core.blocks.model import (
    CodeBlock,
    Header2Block,
    Header3Block,
    Header4Block,
    ImageBlock,
)
from swift_book_pdf.core.blocks.state import BlockParserState


class LeafBlockParser:
    """Consume block types that do not contain nested block content."""

    def __init__(self, state: BlockParserState) -> None:
        """Create a parser component that appends leaf blocks to shared state.

        Args:
            state: Mutable parser cursor and output block list.
        """
        self.state = state

    def consume_image(self, line: str) -> bool:
        """Consume a single Markdown image line.

        Args:
            line: Current input line with its trailing newline already removed.

        Returns:
            True when the line was parsed as an image block.
        """
        if not (line.strip().startswith("![") and "](" in line):
            return False

        alt_text = line.split("![", maxsplit=1)[1].split("]", maxsplit=1)[0]
        url = line.split("](", maxsplit=1)[1].split(")", maxsplit=1)[0]
        self.state.blocks.append(ImageBlock(alt=alt_text, imgname=url))
        self.state.idx += 1
        return True

    def consume_code_block(self, line: str) -> bool:
        """Consume a fenced Swift code block.

        Args:
            line: Current input line with its trailing newline already removed.

        Returns:
            True when the current line opens a Swift code fence.
        """
        if line.strip() != "```swift":
            return False

        self.state.idx += 1
        code_lines = []
        while (
            self.state.idx < self.state.n
            and self.state.lines[self.state.idx].strip() != "```"
        ):
            code_lines.append(self.state.lines[self.state.idx].rstrip("\n"))
            self.state.idx += 1
        self.state.idx += 1
        self.state.blocks.append(CodeBlock(lines=code_lines))
        return True

    def consume_header(self, line: str) -> bool:
        """Consume level-two through level-four Markdown headings.

        Args:
            line: Current input line with its trailing newline already removed.

        Returns:
            True when a supported heading level was parsed.
        """
        stripped = line.lstrip()
        if stripped.startswith("#### "):
            self.state.blocks.append(
                Header4Block(content=stripped[5:].strip())
            )
            self.state.idx += 1
            return True
        if stripped.startswith("### "):
            self.state.blocks.append(
                Header3Block(content=stripped[4:].strip())
            )
            self.state.idx += 1
            return True
        if stripped.startswith("## "):
            self.state.blocks.append(
                Header2Block(content=stripped[3:].strip())
            )
            self.state.idx += 1
            return True
        return False
