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
    """
    Parse the provided lines into blocks.

    :param lines: The lines to parse into blocks
    :return: A list of blocks
    """
    blocks: list[Block] = []
    idx = 0
    n = len(lines)

    while idx < n:
        line = lines[idx].rstrip("\n")
        if not line.strip():
            idx += 1
            continue

        # TABLE BLOCK
        if line.strip().startswith("|") and idx + 1 < n:
            next_line = lines[idx + 1].rstrip("\n")

            # Sanity check: the next line should contain dashes and pipes
            if re.match(r"^\|\s*[-:]+(\s*\|\s*[-:]+)+\s*\|?$", next_line):
                table_rows = []
                # Process header row
                header_cells = [
                    cell.strip() for cell in line.strip().strip("|").split("|")
                ]
                table_rows.append(header_cells)
                idx += 2  # skip header and separator
                # Process subsequent rows
                while idx < n and lines[idx].strip().startswith("|"):
                    data_line = lines[idx].rstrip("\n")
                    cells = [
                        cell.strip() for cell in data_line.strip().strip("|").split("|")
                    ]
                    table_rows.append(cells)
                    idx += 1
                blocks.append(TableBlock(rows=table_rows))
                continue

        # IMAGE BLOCK
        if line.strip().startswith("![") and "](" in line:
            # Extract alt text and URL
            alt_text = line.split("![")[1].split("]")[0]
            url = line.split("](")[1].split(")")[0]
            blocks.append(ImageBlock(alt=alt_text, imgname=url))
            idx += 1
            continue

        # ORDERED LIST BLOCK
        ordered_match = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if ordered_match:
            ol_items: list[str] = []
            current_item = ordered_match.group(1).strip()
            idx += 1
            while idx < n and re.match(r"^\s{2,}\S", lines[idx]):
                current_item += " " + lines[idx].strip()
                idx += 1
            ol_items.append(current_item)
            while idx < n:
                if not lines[idx].strip():
                    idx += 1
                    continue
                m = re.match(r"^\s*\d+\.\s+(.*)$", lines[idx])
                if m:
                    current_item = m.group(1).strip()
                    idx += 1
                    while idx < n and re.match(r"^\s{2,}\S", lines[idx]):
                        current_item += " " + lines[idx].strip()
                        idx += 1
                    ol_items.append(current_item)
                else:
                    break
            blocks.append(OrderedListBlock(items=ol_items))
            continue

        # CODE BLOCK
        if line.strip() == "```swift":
            idx += 1
            code_lines = []
            while idx < n and lines[idx].strip() != "```":
                code_lines.append(lines[idx].rstrip("\n"))
                idx += 1
            idx += 1  # skip ending ```
            blocks.append(CodeBlock(lines=code_lines))
            continue

        # HEADER 2 BLOCK
        if line.lstrip().startswith("## "):
            header_text = line.lstrip()[3:].strip()
            blocks.append(Header2Block(content=header_text))
            idx += 1
            continue

        # HEADER 3 BLOCK
        if line.lstrip().startswith("### "):
            header_text = line.lstrip()[4:].strip()
            blocks.append(Header3Block(content=header_text))
            idx += 1
            continue

        # HEADER 4 BLOCK
        if line.lstrip().startswith("#### "):
            header_text = line.lstrip()[5:].strip()
            blocks.append(Header4Block(content=header_text))
            idx += 1
            continue

        # NOTE BLOCK
        if line.lstrip().startswith(">"):
            content_line = line.lstrip()[1:]  # remove the leading ">"
            m = re.match(r"^([^:]+):\s*(.*)$", content_line)
            if m:
                label = m.group(1).strip()
                aside_content = []
                if m.group(2).strip():
                    aside_content.append(m.group(2).strip())
                idx += 1
                while idx < n and lines[idx].lstrip().startswith(">"):
                    aside_line = lines[idx].lstrip()[1:]
                    aside_content.append(aside_line.rstrip("\n"))
                    idx += 1
                # Recursively parse aside content to allow nested code blocks.
                aside_blocks = parse_blocks(aside_content)
                blocks.append(NoteBlock(label=label, blocks=aside_blocks))
                continue
            else:
                # Fallback: treat as a normal paragraph.
                note_para_lines = [content_line.strip()]
                idx += 1
                while (
                    idx < n
                    and lines[idx].strip()
                    and not re.match(r"^\s*([#>-]|```swift|[-]\s+)", lines[idx])
                ):
                    note_para_lines.append(lines[idx].strip())
                    idx += 1
                blocks.append(ParagraphBlock(lines=note_para_lines))
                continue

        # UNORDERED LIST BLOCK
        bullet_match = re.match(r"^(\s*)-\s+(.*)$", line)
        if bullet_match:
            ul_items: list[list[Block]] = []
            while idx < n:
                current_line = lines[idx].rstrip("\n")
                if not current_line.strip():
                    idx += 1
                    continue
                m = re.match(r"^(\s*)-\s+(.*)$", current_line)
                if not m:
                    break
                base_indent = len(m.group(1))
                item_first_line = m.group(2)
                # Represent the list item as a list of nested blocks.
                sub_blocks: list[Block] = [
                    ParagraphBlock(lines=[item_first_line.strip()])
                ]
                idx += 1
                pending_new_paragraph = False  # flag indicating a blank line was seen
                # Process contiguous indented lines as part of the same list item.
                while idx < n:
                    # If the next line is blank, mark a pending start for a new paragraph.
                    if not lines[idx].strip():
                        pending_new_paragraph = True
                        idx += 1
                        continue
                    curr_line = lines[idx].rstrip("\n")
                    curr_indent = len(curr_line) - len(curr_line.lstrip())
                    # If a line is not indented more than the bullet's, then this item is finished.
                    if curr_indent <= base_indent:
                        break
                    # Remove the base indent.
                    content = curr_line[base_indent:]
                    # Handle a fenced code block inside the list item.
                    if content.lstrip().startswith("```"):
                        idx += 1
                        code_lines = []
                        while idx < n:
                            next_line = lines[idx].rstrip("\n")
                            if next_line[base_indent:].lstrip().startswith("```"):
                                idx += 1
                                break
                            code_lines.append(next_line[base_indent:])
                            idx += 1
                        sub_blocks.append(CodeBlock(lines=code_lines))
                        pending_new_paragraph = False  # reset new paragraph flag after a sub-block that isn't text
                    else:
                        # If we had a blank line or if there is no current paragraph block, start a new one.
                        if (
                            pending_new_paragraph
                            or not sub_blocks
                            or sub_blocks[-1].type != "paragraph"
                        ):
                            sub_blocks.append(ParagraphBlock(lines=[content.strip()]))
                        else:
                            sub_blocks[-1].lines.append(content.strip())
                        pending_new_paragraph = False
                        idx += 1
                ul_items.append(sub_blocks)

            # Check whether this list is a term list.
            is_term_list = True
            term_items = []
            for sub_blocks in ul_items:
                # Merge all paragraphs (ignoring code sub-blocks) into one string.
                merged_text = ""
                for sb in sub_blocks:
                    if sb.type == "paragraph":
                        # Only add nonempty paragraphs
                        if any(line.strip() for line in sb.lines):
                            merged_text += " " + " ".join(sb.lines)
                merged_text = merged_text.strip()
                # The list item must start with "term "
                if not merged_text or not merged_text.lower().startswith("term "):
                    is_term_list = False
                    break
                # Remove the "term " prefix.
                merged_text = merged_text[5:].strip()
                inside_code = False
                colon_idx = None
                for i, ch in enumerate(merged_text):
                    if ch == "`":
                        inside_code = not inside_code
                    elif ch == ":" and not inside_code:
                        colon_idx = i
                        break
                if colon_idx is None:
                    is_term_list = False
                    break
                label = merged_text[:colon_idx].strip()
                content = merged_text[colon_idx + 1 :].strip()
                term_items.append(TermListItem(label=label, content=content))

            if is_term_list and term_items:
                blocks.append(TermListBlock(items=term_items))
            else:
                blocks.append(UnorderedListBlock(items=ul_items))
            continue

        # FALLBACK: PARAGRAPH BLOCK
        # Paragraph block.
        para_lines = [line.strip()]
        idx += 1
        while (
            idx < n
            and lines[idx].strip()
            and not (
                lines[idx].lstrip().startswith("## ")
                or lines[idx].strip() == "```swift"
                or lines[idx].lstrip().startswith(">")
                or re.match(r"^\s*[-]\s+", lines[idx])
            )
        ):
            para_lines.append(lines[idx].strip())
            idx += 1
        blocks.append(ParagraphBlock(lines=para_lines))

    return blocks
