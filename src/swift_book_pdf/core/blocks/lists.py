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

"""Ordered, unordered, and term-list parsing."""

import re

from swift_book_pdf.core.blocks.models import (
    Block,
    CodeBlock,
    OrderedListBlock,
    ParagraphBlock,
    TermListBlock,
    UnorderedListBlock,
)
from swift_book_pdf.core.blocks.patterns import (
    BULLET_PATTERN,
    INDENTED_CONTINUATION_PATTERN,
    ORDERED_LIST_PATTERN,
)
from swift_book_pdf.core.blocks.state import BlockParserState
from swift_book_pdf.core.blocks.terms import extract_term_list_items


class ListBlockParser:
    """Consume Markdown lists and detect Swift Book term-list conventions."""

    def __init__(self, state: BlockParserState) -> None:
        """Create a parser component that appends list blocks to shared state.

        Args:
            state: Mutable parser cursor and output block list.
        """
        self.state = state

    def consume_ordered_list(self, line: str) -> bool:
        """Consume a flat ordered list.

        Args:
            line: Current input line with its trailing newline already removed.

        Returns:
            True when the current line starts an ordered list.
        """
        ordered_match = ORDERED_LIST_PATTERN.match(line)
        if not ordered_match:
            return False

        ol_items = [
            self._consume_ordered_list_item(ordered_match.group(1).strip())
        ]
        while self.state.idx < self.state.n:
            if not self.state.lines[self.state.idx].strip():
                self.state.idx += 1
                continue
            match = ORDERED_LIST_PATTERN.match(
                self.state.lines[self.state.idx]
            )
            if not match:
                break
            ol_items.append(
                self._consume_ordered_list_item(match.group(1).strip())
            )
        self.state.blocks.append(OrderedListBlock(items=ol_items))
        return True

    def _consume_ordered_list_item(self, item_text: str) -> str:
        """Consume one ordered-list item and its indented continuation lines.

        Args:
            item_text: Text captured from the numbered marker line.

        Returns:
            The item text with continuation lines joined by spaces.
        """
        current_item = item_text
        self.state.idx += 1
        while (
            self.state.idx < self.state.n
            and INDENTED_CONTINUATION_PATTERN.match(
                self.state.lines[self.state.idx]
            )
        ):
            current_item += " " + self.state.lines[self.state.idx].strip()
            self.state.idx += 1
        return current_item

    def consume_unordered_list(self, line: str) -> bool:
        """Consume an unordered list or term list.

        Args:
            line: Current input line with its trailing newline already removed.

        Returns:
            True when the current line starts an unordered list.
        """
        bullet_match = BULLET_PATTERN.match(line)
        if not bullet_match:
            return False

        ul_items: list[list[Block]] = []
        while self.state.idx < self.state.n:
            current_line = self.state.lines[self.state.idx].rstrip("\n")
            if not current_line.strip():
                self.state.idx += 1
                continue
            match = BULLET_PATTERN.match(current_line)
            if not match:
                break
            ul_items.append(self._consume_unordered_list_item(match))

        term_items = extract_term_list_items(ul_items)
        if term_items:
            self.state.blocks.append(TermListBlock(items=term_items))
        else:
            self.state.blocks.append(UnorderedListBlock(items=ul_items))
        return True

    def _consume_unordered_list_item(
        self, match: re.Match[str]
    ) -> list[Block]:
        """Consume one bullet and its indented nested content.

        Args:
            match: Bullet-pattern match for the current line.

        Returns:
            Parsed blocks belonging to the bullet item.
        """
        base_indent = len(match.group(1))
        item_first_line = match.group(2)
        sub_blocks: list[Block] = [
            ParagraphBlock(lines=[item_first_line.strip()])
        ]
        self.state.idx += 1
        pending_new_paragraph = False

        while self.state.idx < self.state.n:
            if not self.state.lines[self.state.idx].strip():
                pending_new_paragraph = True
                self.state.idx += 1
                continue

            curr_line = self.state.lines[self.state.idx].rstrip("\n")
            curr_indent = len(curr_line) - len(curr_line.lstrip())
            if curr_indent <= base_indent:
                break

            content = curr_line[base_indent:]
            if content.lstrip().startswith("```"):
                self._append_code_sub_block(sub_blocks, base_indent)
                pending_new_paragraph = False
                continue

            if pending_new_paragraph or sub_blocks[-1].type != "paragraph":
                sub_blocks.append(ParagraphBlock(lines=[content.strip()]))
            else:
                sub_blocks[-1].lines.append(content.strip())
            pending_new_paragraph = False
            self.state.idx += 1

        return sub_blocks

    def _append_code_sub_block(
        self, sub_blocks: list[Block], base_indent: int
    ) -> None:
        """Append a fenced code block nested under a list item.

        Args:
            sub_blocks: Mutable nested block list for the current bullet.
            base_indent: Indentation of the bullet marker.
        """
        self.state.idx += 1
        code_lines = []
        while self.state.idx < self.state.n:
            next_line = self.state.lines[self.state.idx].rstrip("\n")
            if next_line[base_indent:].lstrip().startswith("```"):
                self.state.idx += 1
                break
            code_lines.append(next_line[base_indent:])
            self.state.idx += 1
        sub_blocks.append(CodeBlock(lines=code_lines))
