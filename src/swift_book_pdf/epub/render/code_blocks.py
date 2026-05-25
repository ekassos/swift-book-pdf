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

"""Swift code-block rendering for EPUB XHTML."""

from __future__ import annotations

import html

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import SwiftLexer

from swift_book_pdf.epub.patterns import CODE_PLACEHOLDER_PATTERN

WRAPPING_PLACEHOLDER_MIN_LENGTH = 28


def render_code_block(code_lines: list[str]) -> str:
    """Render Swift code lines with syntax highlighting or outline markup.

    Args:
        code_lines: Swift code lines without surrounding Markdown fences.

    Returns:
        XHTML code block. Placeholder-bearing outline code is rendered line by
        line so `<#...#>` regions can receive custom span classes.
    """
    has_placeholders = any(
        CODE_PLACEHOLDER_PATTERN.search(line) for line in code_lines
    )
    if has_placeholders:
        highlighted_lines = [
            _render_outline_code_line(line) for line in code_lines
        ]
    else:
        highlighted_lines = highlight(
            "\n".join(code_lines),
            SwiftLexer(),
            HtmlFormatter(nowrap=True),
        ).splitlines()
    if not highlighted_lines:
        highlighted_lines = [""]
    items = "".join(f"<li>{line or ' '}</li>" for line in highlighted_lines)
    block_class = "code-block code-block--outline"
    if not has_placeholders:
        block_class = "code-block"
    return (
        f'<div class="{block_class}">'
        '<div class="code-block__shell"><div class="code-block__frame highlight">'
        f'<ol class="code-block__lines">{items}</ol>'
        "</div></div></div>"
    )


def _render_outline_code_line(line: str) -> str:
    """Render one placeholder-bearing outline code line.

    Args:
        line: Swift code line that may contain outline placeholders.

    Returns:
        Highlighted XHTML for the line with placeholder spans preserved.
    """
    parts: list[str] = []
    last_index = 0

    for match in CODE_PLACEHOLDER_PATTERN.finditer(line):
        prefix = line[last_index : match.start()]
        if prefix:
            parts.append(_highlight_swift_fragment(prefix))
        parts.append(_render_outline_placeholder(match.group(1)))
        last_index = match.end()

    suffix = line[last_index:]
    if suffix:
        parts.append(_highlight_swift_fragment(suffix))

    return "".join(parts)


def _render_outline_placeholder(text: str) -> str:
    """Render an outline placeholder span.

    Args:
        text: Placeholder text without `<#` and `#>` markers.

    Returns:
        XHTML span using the wrapping class for long human-readable
        placeholders.
    """
    class_name = "gi"
    if _needs_wrapping_placeholder(text):
        class_name = "gi gi-wrap"
    return f'<span class="{class_name}">{html.escape(text)}</span>'


def _needs_wrapping_placeholder(text: str) -> bool:
    """Return whether a placeholder should allow wrapping.

    Args:
        text: Placeholder text.

    Returns:
        True for long multi-word placeholders that would otherwise stretch code
        blocks on narrow screens.
    """
    normalized = text.strip()
    return (
        len(normalized) > WRAPPING_PLACEHOLDER_MIN_LENGTH and " " in normalized
    )


def _highlight_swift_fragment(fragment: str) -> str:
    """Syntax-highlight a Swift code fragment without wrapper markup.

    Args:
        fragment: Swift source fragment outside an outline placeholder.

    Returns:
        Pygments-generated inline XHTML with trailing newlines removed.
    """
    return highlight(
        fragment, SwiftLexer(), HtmlFormatter(nowrap=True)
    ).rstrip("\n")
