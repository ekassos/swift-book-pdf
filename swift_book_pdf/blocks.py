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

import re

from swift_book_pdf.schema import (
    Block,
    CodeBlock,
    Header2Block,
    Header3Block,
    Header4Block,
    ImageBlock,
    NoteBlock,
    OrderedListBlock,
    ParagraphBlock,
    TableBlock,
    TermListBlock,
    TermListItem,
    UnorderedListBlock,
)


def parse_blocks(lines: list[str]) -> list[Block]:
    return _BlockParser(lines).parse()


class _BlockParser:
    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.n = len(lines)
        self.idx = 0
        self.blocks: list[Block] = []

    def parse(self) -> list[Block]:
        """
        Parse the provided lines into blocks.

        :param lines: The lines to parse into blocks
        :return: A list of blocks
        """
        while self.idx < self.n:
            line = self.lines[self.idx].rstrip("\n")
            if not line.strip():
                self.idx += 1
                continue

            if self._consume_table(line):
                continue
            if self._consume_image(line):
                continue
            if self._consume_ordered_list(line):
                continue
            if self._consume_code_block(line):
                continue
            if self._consume_header(line):
                continue
            if self._consume_note(line):
                continue
            if self._consume_unordered_list(line):
                continue
            self._consume_paragraph(line)

        return self.blocks

    def _consume_table(self, line: str) -> bool:
        if not (line.strip().startswith("|") and self.idx + 1 < self.n):
            return False

        next_line = self.lines[self.idx + 1].rstrip("\n")
        if not re.match(r"^\|\s*[-:]+(\s*\|\s*[-:]+)+\s*\|?$", next_line):
            return False

        table_rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]]
        self.idx += 2
        while self.idx < self.n and self.lines[self.idx].strip().startswith("|"):
            data_line = self.lines[self.idx].rstrip("\n")
            table_rows.append(
                [cell.strip() for cell in data_line.strip().strip("|").split("|")],
            )
            self.idx += 1
        self.blocks.append(TableBlock(rows=table_rows))
        return True

    def _consume_image(self, line: str) -> bool:
        if not (line.strip().startswith("![") and "](" in line):
            return False

        alt_text = line.split("![")[1].split("]")[0]
        url = line.split("](")[1].split(")")[0]
        self.blocks.append(ImageBlock(alt=alt_text, imgname=url))
        self.idx += 1
        return True

    def _consume_ordered_list(self, line: str) -> bool:
        ordered_match = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if not ordered_match:
            return False

        ol_items = [self._consume_ordered_list_item(ordered_match.group(1).strip())]
        while self.idx < self.n:
            if not self.lines[self.idx].strip():
                self.idx += 1
                continue
            match = re.match(r"^\s*\d+\.\s+(.*)$", self.lines[self.idx])
            if not match:
                break
            ol_items.append(self._consume_ordered_list_item(match.group(1).strip()))
        self.blocks.append(OrderedListBlock(items=ol_items))
        return True

    def _consume_ordered_list_item(self, item_text: str) -> str:
        current_item = item_text
        self.idx += 1
        while self.idx < self.n and re.match(r"^\s{2,}\S", self.lines[self.idx]):
            current_item += " " + self.lines[self.idx].strip()
            self.idx += 1
        return current_item

    def _consume_code_block(self, line: str) -> bool:
        if line.strip() != "```swift":
            return False

        self.idx += 1
        code_lines = []
        while self.idx < self.n and self.lines[self.idx].strip() != "```":
            code_lines.append(self.lines[self.idx].rstrip("\n"))
            self.idx += 1
        self.idx += 1
        self.blocks.append(CodeBlock(lines=code_lines))
        return True

    def _consume_header(self, line: str) -> bool:
        stripped = line.lstrip()
        if stripped.startswith("#### "):
            self.blocks.append(Header4Block(content=stripped[5:].strip()))
            self.idx += 1
            return True
        if stripped.startswith("### "):
            self.blocks.append(Header3Block(content=stripped[4:].strip()))
            self.idx += 1
            return True
        if stripped.startswith("## "):
            self.blocks.append(Header2Block(content=stripped[3:].strip()))
            self.idx += 1
            return True
        return False

    def _consume_note(self, line: str) -> bool:
        if not line.lstrip().startswith(">"):
            return False

        content_line = line.lstrip()[1:]
        match = re.match(r"^([^:]+):\s*(.*)$", content_line)
        if match:
            self.blocks.append(self._build_note_block(match))
            return True

        self.blocks.append(self._build_note_paragraph(content_line))
        return True

    def _build_note_block(self, match: re.Match[str]) -> NoteBlock:
        label = match.group(1).strip()
        aside_content = [match.group(2).strip()] if match.group(2).strip() else []
        self.idx += 1
        while self.idx < self.n and self.lines[self.idx].lstrip().startswith(">"):
            aside_line = self.lines[self.idx].lstrip()[1:]
            aside_content.append(aside_line.rstrip("\n"))
            self.idx += 1
        return NoteBlock(label=label, blocks=parse_blocks(aside_content))

    def _build_note_paragraph(self, content_line: str) -> ParagraphBlock:
        note_para_lines = [content_line.strip()]
        self.idx += 1
        while self.idx < self.n and self._is_note_paragraph_continuation(
            self.lines[self.idx]
        ):
            note_para_lines.append(self.lines[self.idx].strip())
            self.idx += 1
        return ParagraphBlock(lines=note_para_lines)

    def _is_note_paragraph_continuation(self, line: str) -> bool:
        return bool(
            line.strip() and not re.match(r"^\s*([#>-]|```swift|[-]\s+)", line),
        )

    def _consume_unordered_list(self, line: str) -> bool:
        bullet_match = re.match(r"^(\s*)-\s+(.*)$", line)
        if not bullet_match:
            return False

        ul_items: list[list[Block]] = []
        while self.idx < self.n:
            current_line = self.lines[self.idx].rstrip("\n")
            if not current_line.strip():
                self.idx += 1
                continue
            match = re.match(r"^(\s*)-\s+(.*)$", current_line)
            if not match:
                break
            ul_items.append(self._consume_unordered_list_item(match))

        term_items = _extract_term_list_items(ul_items)
        if term_items:
            self.blocks.append(TermListBlock(items=term_items))
        else:
            self.blocks.append(UnorderedListBlock(items=ul_items))
        return True

    def _consume_unordered_list_item(self, match: re.Match[str]) -> list[Block]:
        base_indent = len(match.group(1))
        item_first_line = match.group(2)
        sub_blocks: list[Block] = [ParagraphBlock(lines=[item_first_line.strip()])]
        self.idx += 1
        pending_new_paragraph = False

        while self.idx < self.n:
            if not self.lines[self.idx].strip():
                pending_new_paragraph = True
                self.idx += 1
                continue

            curr_line = self.lines[self.idx].rstrip("\n")
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
            self.idx += 1

        return sub_blocks

    def _append_code_sub_block(self, sub_blocks: list[Block], base_indent: int) -> None:
        self.idx += 1
        code_lines = []
        while self.idx < self.n:
            next_line = self.lines[self.idx].rstrip("\n")
            if next_line[base_indent:].lstrip().startswith("```"):
                self.idx += 1
                break
            code_lines.append(next_line[base_indent:])
            self.idx += 1
        sub_blocks.append(CodeBlock(lines=code_lines))

    def _consume_paragraph(self, line: str) -> None:
        para_lines = [line.strip()]
        self.idx += 1
        while self.idx < self.n and self._is_paragraph_continuation(
            self.lines[self.idx]
        ):
            para_lines.append(self.lines[self.idx].strip())
            self.idx += 1
        self.blocks.append(ParagraphBlock(lines=para_lines))

    def _is_paragraph_continuation(self, line: str) -> bool:
        return bool(
            line.strip()
            and not (
                line.lstrip().startswith("## ")
                or line.strip() == "```swift"
                or line.lstrip().startswith(">")
                or re.match(r"^\s*[-]\s+", line)
            )
        )


def _extract_term_list_items(ul_items: list[list[Block]]) -> list[TermListItem]:
    term_items: list[TermListItem] = []
    for sub_blocks in ul_items:
        merged_text = _merge_paragraph_text(sub_blocks)
        if not merged_text or not merged_text.lower().startswith("term "):
            return []

        label_content = merged_text[5:].strip()
        parts = _split_term_item(label_content)
        if parts is None:
            return []
        label, content = parts
        term_items.append(TermListItem(label=label, content=content))
    return term_items


def _merge_paragraph_text(sub_blocks: list[Block]) -> str:
    merged_parts = [
        " ".join(sb.lines)
        for sb in sub_blocks
        if sb.type == "paragraph" and any(line.strip() for line in sb.lines)
    ]
    return " ".join(merged_parts).strip()


def _split_term_item(merged_text: str) -> tuple[str, str] | None:
    inside_code = False
    for index, character in enumerate(merged_text):
        if character == "`":
            inside_code = not inside_code
        elif character == ":" and not inside_code:
            label = merged_text[:index].strip()
            content = merged_text[index + 1 :].strip()
            return label, content
    return None
