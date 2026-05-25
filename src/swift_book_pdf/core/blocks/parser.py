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

"""Parse the Swift Book Markdown subset into backend-neutral blocks."""

from swift_book_pdf.core.blocks.leaf import LeafBlockParser
from swift_book_pdf.core.blocks.lists import ListBlockParser
from swift_book_pdf.core.blocks.models import Block
from swift_book_pdf.core.blocks.notes import NoteBlockParser
from swift_book_pdf.core.blocks.paragraphs import ParagraphBlockParser
from swift_book_pdf.core.blocks.state import BlockParserState
from swift_book_pdf.core.blocks.tables import TableBlockParser


def parse_blocks(lines: list[str]) -> list[Block]:
    """Parse Markdown source lines into backend-neutral block objects.

    Args:
        lines: Markdown lines from a Swift Book source document or nested
            block quote.

    Returns:
        Parsed blocks in source order. Inline markup is intentionally left in
        Markdown form for output backends to convert later.
    """
    return _BlockParser(lines).parse()


class _BlockParser:
    """Cursor-based parser for the Markdown subset used by Swift Book.

    The parser owns line traversal and delegates construct-specific parsing to
    composed parser components. Each `consume_*` method returns whether it
    recognized the current line and advances the shared cursor when it consumes
    input.
    """

    def __init__(self, lines: list[str]) -> None:
        """Initialize parser state for one list of Markdown lines.

        Args:
            lines: Markdown source lines to parse.
        """
        self.state = BlockParserState(lines=lines)
        self.tables = TableBlockParser(self.state)
        self.leaves = LeafBlockParser(self.state)
        self.lists = ListBlockParser(self.state)
        self.notes = NoteBlockParser(self.state, self._parse_nested)
        self.paragraphs = ParagraphBlockParser(self.state)

    def parse(self) -> list[Block]:
        """Consume all input lines and return parsed blocks.

        Returns:
            Parsed block objects accumulated while walking the input cursor.
        """
        while self.state.idx < self.state.n:
            line = self.state.lines[self.state.idx].rstrip("\n")
            if not line.strip():
                self.state.idx += 1
                continue

            if self.tables.consume_table(line):
                continue
            if self.leaves.consume_image(line):
                continue
            if self.lists.consume_ordered_list(line):
                continue
            if self.leaves.consume_code_block(line):
                continue
            if self.leaves.consume_header(line):
                continue
            if self.notes.consume_note(line):
                continue
            if self.lists.consume_unordered_list(line):
                continue
            self.paragraphs.consume_paragraph(line)

        return self.state.blocks

    def _parse_nested(self, lines: list[str]) -> list[Block]:
        """Parse nested Markdown content using a fresh parser instance.

        Args:
            lines: Nested Markdown lines extracted from a parent block.

        Returns:
            Parsed nested blocks.
        """
        return parse_blocks(lines)
