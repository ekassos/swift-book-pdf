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

"""Block quote and aside parsing for Swift Book notes."""

import re
from collections.abc import Callable

from swift_book_pdf.core.blocks.model import Block, NoteBlock, ParagraphBlock
from swift_book_pdf.core.blocks.patterns import (
    NOTE_LABEL_PATTERN,
    NOTE_PARAGRAPH_BOUNDARY_PATTERN,
)
from swift_book_pdf.core.blocks.state import BlockParserState


class NoteBlockParser:
    """Consume `>` blocks as notes or ordinary quoted paragraphs."""

    def __init__(
        self,
        state: BlockParserState,
        parse_nested: Callable[[list[str]], list[Block]],
    ) -> None:
        """Create a parser component for quoted note content.

        Args:
            state: Mutable parser cursor and output block list.
            parse_nested: Callback used to parse nested note lines.
        """
        self.state = state
        self.parse_nested = parse_nested

    def consume_note(self, line: str) -> bool:
        """Consume a quoted note or quoted paragraph.

        Args:
            line: Current input line with its trailing newline already removed.

        Returns:
            True when the current line begins with `>`.
        """
        if not line.lstrip().startswith(">"):
            return False

        content_line = line.lstrip()[1:]
        match = NOTE_LABEL_PATTERN.match(content_line)
        if match:
            self.state.blocks.append(self._build_note_block(match))
            return True

        self.state.blocks.append(self._build_note_paragraph(content_line))
        return True

    def _build_note_block(self, match: re.Match[str]) -> NoteBlock:
        """Build a labeled aside from consecutive quoted lines.

        Args:
            match: Label/content match from the first quoted line.

        Returns:
            A note block whose content has been parsed recursively.
        """
        label = match.group(1).strip()
        aside_content = (
            [match.group(2).strip()] if match.group(2).strip() else []
        )
        self.state.idx += 1
        while self.state.idx < self.state.n and self.state.lines[
            self.state.idx
        ].lstrip().startswith(">"):
            aside_line = self.state.lines[self.state.idx].lstrip()[1:]
            aside_content.append(aside_line.rstrip("\n"))
            self.state.idx += 1
        return NoteBlock(label=label, blocks=self.parse_nested(aside_content))

    def _build_note_paragraph(self, content_line: str) -> ParagraphBlock:
        """Build a plain paragraph for quoted text without an aside label.

        Args:
            content_line: Text following the initial `>` marker.

        Returns:
            A paragraph block containing the quoted text.
        """
        note_para_lines = [content_line.strip()]
        self.state.idx += 1
        while (
            self.state.idx < self.state.n
            and self._is_note_paragraph_continuation(
                self.state.lines[self.state.idx]
            )
        ):
            note_para_lines.append(self.state.lines[self.state.idx].strip())
            self.state.idx += 1
        return ParagraphBlock(lines=note_para_lines)

    def _is_note_paragraph_continuation(self, line: str) -> bool:
        """Return whether a source line continues a quoted paragraph.

        Args:
            line: Candidate source line.

        Returns:
            True when the line is non-empty and does not begin another block.
        """
        return bool(
            line.strip() and not NOTE_PARAGRAPH_BOUNDARY_PATTERN.match(line)
        )
