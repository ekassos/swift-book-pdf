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

"""Helpers that recognize Swift Book term-list bullets."""

from swift_book_pdf.core.blocks.model import Block, TermListItem


def extract_term_list_items(
    ul_items: list[list[Block]],
) -> list[TermListItem]:
    """Return term-list items when every bullet follows `Term ...:` syntax.

    Args:
        ul_items: Parsed blocks for each unordered-list bullet.

    Returns:
        Parsed term-list entries. If any bullet is not a valid term entry, an
        empty list is returned so the caller can keep the unordered-list shape.
    """
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
    """Join paragraph text from nested list item blocks.

    Args:
        sub_blocks: Parsed blocks that belong to one bullet.

    Returns:
        Paragraph text joined with spaces. Non-paragraph blocks are ignored.
    """
    merged_parts = [
        " ".join(sb.lines)
        for sb in sub_blocks
        if sb.type == "paragraph" and any(line.strip() for line in sb.lines)
    ]
    return " ".join(merged_parts).strip()


def _split_term_item(merged_text: str) -> tuple[str, str] | None:
    """Split a term-list bullet into label and content.

    Args:
        merged_text: Bullet text after the leading `Term ` marker.

    Returns:
        `(label, content)` split at the first colon outside inline code, or
        `None` when no valid separator exists.
    """
    inside_code = False
    for index, character in enumerate(merged_text):
        if character == "`":
            inside_code = not inside_code
        elif character == ":" and not inside_code:
            label = merged_text[:index].strip()
            content = merged_text[index + 1 :].strip()
            return label, content
    return None
