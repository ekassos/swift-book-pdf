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

"""Helpers for parsing Swift grammar rules in source Markdown."""

from __future__ import annotations

import re

from swift_book_pdf.core.blocks.models import NoteBlock, ParagraphBlock

MIN_WRAPPED_MARKDOWN_TERM_LENGTH = 3


def is_grammar_note_label(label: str) -> bool:
    """Return whether an aside label introduces a grammar block.

    Args:
        label: Parsed Swift Book aside label.

    Returns:
        True when the label starts with `Grammar of `, ignoring case.
    """
    return label.lower().startswith("grammar of ")


def clean_grammar_line(line: str) -> str:
    """Strip grammar line whitespace and trailing Markdown breaks.

    Generated grammar summaries use trailing backslashes to force Markdown line
    breaks. EPUB grammar rendering consumes those markers before applying its
    own XHTML structure.
    """
    clean_line = line.strip()
    if clean_line.endswith("\\"):
        return clean_line[:-1].rstrip()
    return clean_line


def parse_grammar_rule(line: str) -> tuple[str, str] | None:
    """Parse a grammar production into `(term, expression)`.

    Args:
        line: Raw grammar line from a parsed grammar aside.

    Returns:
        Left-hand grammar term and right-hand production expression, or `None`
        for prose lines inside grammar asides.
    """
    clean_line = clean_grammar_line(line)
    if "→" not in clean_line:
        return None

    left, right = (part.strip() for part in clean_line.split("→", 1))
    if _is_wrapped_markdown_term(left):
        left = left[1:-1]
    return left, right


def extract_grammar_terms(block: NoteBlock) -> list[str]:
    """Return grammar terms defined inside a parsed grammar aside.

    Args:
        block: Parsed `Grammar of ...` aside.

    Returns:
        Grammar terms in source order. Non-paragraph nested content and prose
        lines are ignored because they do not define linkable productions.
    """
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
    """Normalize a grammar term for use in an EPUB anchor fragment.

    Args:
        term: Grammar term text from the left side of a production.

    Returns:
        Fragment-safe term used below the `grammar_` anchor prefix.
    """
    return re.sub(r"[^A-Za-z0-9_-]+", "-", term.strip()).strip("-")


def _is_wrapped_markdown_term(text: str) -> bool:
    """Return whether text is an emphasized grammar term token.

    Args:
        text: Candidate left-hand production term.

    Returns:
        True when the term is wrapped in Markdown emphasis markers.
    """
    return (
        text.startswith("*")
        and text.endswith("*")
        and len(text) >= MIN_WRAPPED_MARKDOWN_TERM_LENGTH
    )
