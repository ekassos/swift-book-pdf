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

"""Paragraph parsing and paragraph-boundary checks."""

from swift_book_pdf.core.blocks.models import ParagraphBlock
from swift_book_pdf.core.blocks.patterns import BULLET_PATTERN
from swift_book_pdf.core.blocks.state import BlockParserState


class ParagraphBlockParser:
    """Consume runs of text that do not start another block type."""

    def __init__(self, state: BlockParserState) -> None:
        """Create a parser component that appends paragraphs to shared state.

        Args:
            state: Mutable parser cursor and output block list.
        """
        self.state = state

    def consume_paragraph(self, line: str) -> None:
        """Consume a paragraph starting at the current parser index.

        Args:
            line: Current input line with its trailing newline already removed.
        """
        para_lines = [line.strip()]
        self.state.idx += 1
        while (
            self.state.idx < self.state.n
            and self._is_paragraph_continuation(
                self.state.lines[self.state.idx]
            )
        ):
            para_lines.append(self.state.lines[self.state.idx].strip())
            self.state.idx += 1
        self.state.blocks.append(ParagraphBlock(lines=para_lines))

    def _is_paragraph_continuation(self, line: str) -> bool:
        """Return whether a source line continues the current paragraph.

        Args:
            line: Candidate source line.

        Returns:
            True when the line is non-empty and does not start a supported
            non-paragraph block.
        """
        return bool(
            line.strip()
            and not (
                line.lstrip().startswith("## ")
                or line.strip() == "```swift"
                or line.lstrip().startswith(">")
                or BULLET_PATTERN.match(line)
            )
        )
