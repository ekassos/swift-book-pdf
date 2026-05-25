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

from __future__ import annotations

import re

from swift_book_pdf.core.blocks.models import NoteBlock, ParagraphBlock

MARKDOWN_WRAPPED_TERM_LENGTH = 2


def is_grammar_note_label(label: str) -> bool:
    return label.lower().startswith("grammar of ")


def clean_grammar_line(line: str) -> str:
    clean_line = line.strip()
    if clean_line.endswith("\\"):
        return clean_line[:-1].rstrip()
    return clean_line


def parse_grammar_rule(line: str) -> tuple[str, str] | None:
    clean_line = clean_grammar_line(line)
    if "→" not in clean_line:
        return None

    left, right = (part.strip() for part in clean_line.split("→", 1))
    if _is_wrapped_markdown_term(left):
        left = left[1:-1]
    return left, right


def extract_grammar_terms(block: NoteBlock) -> list[str]:
    terms: list[str] = []
    for sub_block in block.blocks:
        if not isinstance(sub_block, ParagraphBlock):
            continue
        for line in sub_block.lines:
            rule = parse_grammar_rule(line)
            if rule is not None:
                terms.append(rule[0])
    return terms


def grammar_anchor_fragment(term: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", term.strip()).strip("-")


def _is_wrapped_markdown_term(text: str) -> bool:
    return (
        text.startswith("*")
        and text.endswith("*")
        and len(text) > MARKDOWN_WRAPPED_TERM_LENGTH
    )
