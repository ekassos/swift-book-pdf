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

"""Render Swift grammar asides and cross-linked grammar references."""

from __future__ import annotations

import html
import re

from swift_book_pdf.core.blocks.models import NoteBlock, ParagraphBlock
from swift_book_pdf.epub.grammar_rules import (
    clean_grammar_line,
    grammar_anchor_fragment,
    parse_grammar_rule,
)
from swift_book_pdf.epub.paths import relative_href
from swift_book_pdf.epub.render.inline import replace_inline_code_spans

EMPHASIS_PATTERN = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")


def render_grammar_block(
    block: NoteBlock,
    current_href: str,
    grammar_targets: dict[str, str],
    grammar_anchor_counts: dict[str, int],
) -> str:
    """Render a `Grammar of ...` aside as EPUB XHTML.

    Args:
        block: Parsed grammar aside.
        current_href: Href of the document containing the aside.
        grammar_targets: Global grammar term href map.
        grammar_anchor_counts: Mutable per-document anchor counters.

    Returns:
        XHTML aside with grouped grammar rule markup.
    """
    groups: list[str] = []
    for sub_block in block.blocks:
        if not isinstance(sub_block, ParagraphBlock):
            continue
        syntax_lines = [
            render_grammar_line(
                line, current_href, grammar_targets, grammar_anchor_counts
            )
            for line in sub_block.lines
            if line.strip()
        ]
        if syntax_lines:
            groups.append(
                '<div class="grammar-group">'
                + "".join(syntax_lines)
                + "</div>"
            )

    return (
        '<div class="aside grammar">'
        f'<p class="first aside-title">{html.escape(block.label)}</p>'
        + "".join(groups)
        + "</div>"
    )


def render_grammar_line(
    line: str,
    current_href: str,
    grammar_targets: dict[str, str],
    grammar_anchor_counts: dict[str, int],
) -> str:
    """Render one grammar rule or prose line.

    Args:
        line: Raw grammar line from a paragraph inside a grammar aside.
        current_href: Href of the document containing the line.
        grammar_targets: Global grammar term href map.
        grammar_anchor_counts: Mutable per-document anchor counters.

    Returns:
        XHTML paragraph for a production rule or grammar prose.
    """
    rule = parse_grammar_rule(line)
    if rule is None:
        return (
            "<p>"
            + _render_grammar_fragment(
                clean_grammar_line(line), current_href, grammar_targets
            )
            + "</p>"
        )

    left, right = rule
    anchor_id = _next_grammar_anchor_id(left, grammar_anchor_counts)
    return (
        '<p class="grammar-rule">'
        f'<span class="grammar-term"><a id="{html.escape(anchor_id)}"></a>{html.escape(left)}</span>'
        '<span class="arrow"> → </span>'
        f"{_render_grammar_fragment(right, current_href, grammar_targets)}</p>"
    )


def _render_grammar_fragment(
    text: str,
    current_href: str,
    grammar_targets: dict[str, str],
) -> str:
    """Render inline grammar tokens while preserving generated markup.

    The renderer protects code spans and grammar-category links with
    placeholders before escaping. This allows source grammar syntax like
    `*expression*` and `_?_` to become EPUB-specific markup without leaking raw
    HTML from source text.
    """
    placeholders: dict[str, str] = {}
    placeholder_index = 0

    def store(value: str) -> str:
        nonlocal placeholder_index
        token = f"@@GRAMMAR{placeholder_index}@@"
        placeholders[token] = value
        placeholder_index += 1
        return token

    text = re.sub(
        r"\*\*``\s*(.*?)\s*``\*\*",
        lambda match: store(f"<code>{html.escape(match.group(1))}</code>"),
        text,
    )
    text = re.sub(
        r"\*\*`([^`]+)`\*\*",
        lambda match: store(f"<code>{html.escape(match.group(1))}</code>"),
        text,
    )
    text = replace_inline_code_spans(
        text,
        lambda code: store(f"<code>{html.escape(code)}</code>"),
    )
    text = EMPHASIS_PATTERN.sub(
        lambda match: store(
            _render_grammar_category(
                match.group(1),
                current_href,
                grammar_targets,
            )
        ),
        text,
    )
    text = html.escape(text)
    text = text.replace(
        "_?_",
        '<span class="grammar-optional">?</span>',
    )

    for token, value in placeholders.items():
        text = text.replace(html.escape(token), value)

    return text


def _render_grammar_category(
    text: str,
    current_href: str,
    grammar_targets: dict[str, str],
) -> str:
    """Render a grammar category reference with a link when known.

    Args:
        text: Grammar category text from emphasized source markup.
        current_href: Href of the document containing the reference.
        grammar_targets: Global grammar term href map.

    Returns:
        XHTML span, linking to the first known target when available.
    """
    target_href = grammar_targets.get(text)
    if target_href is None:
        return '<span class="grammar-ref">' + html.escape(text) + "</span>"

    return (
        '<span class="grammar-ref">'
        f'<a href="{html.escape(relative_href(current_href, target_href))}">{html.escape(text)}</a>'
        "</span>"
    )


def _next_grammar_anchor_id(
    term: str, grammar_anchor_counts: dict[str, int]
) -> str:
    """Return the next unique grammar anchor ID for a term.

    Args:
        term: Grammar term being defined.
        grammar_anchor_counts: Mutable per-document count by normalized term.

    Returns:
        Stable anchor ID using `grammar_` for the first definition and a
        numeric suffix for later duplicate terms in the same document.
    """
    fragment = grammar_anchor_fragment(term)
    count = grammar_anchor_counts.get(fragment, 0) + 1
    grammar_anchor_counts[fragment] = count
    if count == 1:
        return f"grammar_{fragment}"
    return f"grammar_{fragment}_{count}"
