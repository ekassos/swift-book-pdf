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

"""Table parsing for the Swift Book Markdown subset."""

from swift_book_pdf.core.blocks.model import TableBlock
from swift_book_pdf.core.blocks.patterns import TABLE_DIVIDER_PATTERN
from swift_book_pdf.core.blocks.state import BlockParserState


class TableBlockParser:
    """Consume GitHub-style Markdown tables."""

    def __init__(self, state: BlockParserState) -> None:
        """Create a parser component that appends table blocks to shared state.

        Args:
            state: Mutable parser cursor and output block list.
        """
        self.state = state

    def consume_table(self, line: str) -> bool:
        """Consume a pipe table starting at the current parser index.

        Args:
            line: Current input line with its trailing newline already removed.

        Returns:
            True when a table was recognized and appended to `state.blocks`;
            otherwise false without changing parser state.
        """
        if not (
            line.strip().startswith("|") and self.state.idx + 1 < self.state.n
        ):
            return False

        next_line = self.state.lines[self.state.idx + 1].rstrip("\n")
        if not TABLE_DIVIDER_PATTERN.match(next_line):
            return False

        table_rows = [
            [cell.strip() for cell in line.strip().strip("|").split("|")]
        ]
        self.state.idx += 2
        while self.state.idx < self.state.n and self.state.lines[
            self.state.idx
        ].strip().startswith("|"):
            data_line = self.state.lines[self.state.idx].rstrip("\n")
            table_rows.append(
                [
                    cell.strip()
                    for cell in data_line.strip().strip("|").split("|")
                ],
            )
            self.state.idx += 1
        self.state.blocks.append(TableBlock(rows=table_rows))
        return True
