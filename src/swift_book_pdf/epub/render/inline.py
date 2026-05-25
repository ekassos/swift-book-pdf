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

"""Inline Markdown-to-XHTML rendering for EPUB output."""

from __future__ import annotations

import html
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from swift_book_pdf.epub.render.links import LinkResolver

INLINE_CODE_PADDING_LENGTH = 2
DOC_LINK_PATTERN = re.compile(r"<doc:([^>]+)>")
STRONG_PATTERN = re.compile(r"\*\*(.+?)\*\*")
EMPHASIS_PATTERN = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")


def render_inline(
    text: str, current_href: str, link_resolver: LinkResolver
) -> str:
    """Render inline Markdown, code spans, and document links.

    Args:
        text: Inline Markdown text from a parsed block.
        current_href: Href of the document containing the text.
        link_resolver: Resolver for Swift Book `<doc:...>` links.

    Returns:
        XHTML inline markup. Links and code spans are protected with temporary
        placeholders before emphasis and escaping are applied.
    """
    placeholders: dict[str, str] = {}
    placeholder_index = 0

    def store(value: str) -> str:
        nonlocal placeholder_index
        token = f"@@INLINE{placeholder_index}@@"
        placeholders[token] = value
        placeholder_index += 1
        return token

    text = DOC_LINK_PATTERN.sub(
        lambda match: store(
            link_resolver.render_doc_link(current_href, match.group(1))
        ),
        text,
    )
    text = _replace_markdown_links(
        text,
        lambda label, href: store(
            '<a href="'
            + html.escape(href)
            + '">'
            + render_inline_styles(label)
            + "</a>"
        ),
    )
    text = replace_inline_code_spans(
        text,
        lambda code: store(
            '<code class="inline-code">' + html.escape(code) + "</code>"
        ),
    )
    return _render_inline_tail(text, placeholders)


def render_inline_styles(text: str) -> str:
    """Render inline emphasis, strong text, and code spans only.

    Args:
        text: Inline text that should not resolve document links.

    Returns:
        XHTML inline markup for emphasis, strong text, and code spans.
    """
    placeholders: dict[str, str] = {}
    placeholder_index = 0

    def store(value: str) -> str:
        nonlocal placeholder_index
        token = f"@@STYLE{placeholder_index}@@"
        placeholders[token] = value
        placeholder_index += 1
        return token

    text = replace_inline_code_spans(
        text,
        lambda code: store(
            '<code class="inline-code">' + html.escape(code) + "</code>"
        ),
    )
    return _render_inline_tail(text, placeholders)


def _render_inline_tail(text: str, placeholders: dict[str, str]) -> str:
    """Escape text, apply simple inline styles, and restore placeholders.

    Args:
        text: Inline text with placeholder tokens for pre-rendered markup.
        placeholders: Mapping from placeholder token to trusted rendered XHTML.

    Returns:
        Escaped XHTML with supported Markdown styles applied.
    """
    text = normalize_prose_punctuation(text)
    text = html.escape(text)
    text = STRONG_PATTERN.sub(r"<strong>\1</strong>", text)
    text = EMPHASIS_PATTERN.sub(r"<em>\1</em>", text)

    for token, value in placeholders.items():
        text = text.replace(html.escape(token), value)

    return text


def replace_inline_code_spans(text: str, render: Callable[[str], str]) -> str:
    """Replace Markdown inline code spans using the supplied renderer.

    Args:
        text: Inline Markdown text.
        render: Callback that receives unescaped code text.

    Returns:
        Text with matching backtick spans replaced by callback output. Unclosed
        spans and escaped backticks are preserved as literal text.
    """
    output: list[str] = []
    index = 0

    while index < len(text):
        if (
            text[index] == "\\"
            and index + 1 < len(text)
            and text[index + 1] == "`"
        ):
            output.append("`")
            index += 2
            continue

        if text[index] != "`":
            output.append(text[index])
            index += 1
            continue

        fence_end = index
        while fence_end < len(text) and text[fence_end] == "`":
            fence_end += 1

        fence = text[index:fence_end]
        closing_index = text.find(fence, fence_end)
        if closing_index == -1:
            output.append(fence)
            index = fence_end
            continue

        code = text[fence_end:closing_index]
        if (
            len(code) >= INLINE_CODE_PADDING_LENGTH
            and code[0] == " "
            and code[-1] == " "
            and any(character != " " for character in code)
        ):
            code = code[1:-1]

        output.append(render(code))
        index = closing_index + len(fence)

    return "".join(output)


def _replace_markdown_links(
    text: str, render: Callable[[str, str], str]
) -> str:
    """Replace Markdown links outside inline code spans.

    Args:
        text: Inline Markdown text.
        render: Callback that receives link label and href text.

    Returns:
        Text with Markdown links replaced, leaving links inside inline code
        spans untouched.
    """
    output: list[str] = []
    index = 0

    while index < len(text):
        fenced_segment = _consume_inline_code_fence(text, index)
        if fenced_segment is not None:
            output.append(fenced_segment[0])
            index = fenced_segment[1]
            continue

        if text[index] != "[":
            output.append(text[index])
            index += 1
            continue

        parsed_link = _parse_markdown_link(text, index)
        if parsed_link is None:
            output.append(text[index])
            index += 1
            continue

        label, href, next_index = parsed_link
        output.append(render(label, href))
        index = next_index

    return "".join(output)


def _consume_inline_code_fence(
    text: str, start_index: int
) -> tuple[str, int] | None:
    """Return the inline code fence segment starting at `start_index`.

    Args:
        text: Inline Markdown text.
        start_index: Candidate fence start.

    Returns:
        Literal fenced segment and next index, or `None` when the current
        character is not a backtick.
    """
    if text[start_index] != "`":
        return None

    fence_end = start_index
    while fence_end < len(text) and text[fence_end] == "`":
        fence_end += 1

    fence = text[start_index:fence_end]
    closing_index = text.find(fence, fence_end)
    if closing_index == -1:
        return text[start_index:], len(text)

    return text[start_index : closing_index + len(fence)], (
        closing_index + len(fence)
    )


def _parse_markdown_link(
    text: str, start_index: int
) -> tuple[str, str, int] | None:
    """Parse a Markdown link starting at `start_index`.

    Args:
        text: Inline Markdown text.
        start_index: Candidate `[` position.

    Returns:
        Link label, href, and next index, or `None` for non-link text.
    """
    label_end = text.find("]", start_index + 1)
    if label_end == -1 or label_end + 1 >= len(text):
        return None
    if text[label_end + 1] != "(":
        return None

    href_start = label_end + 2
    href_end = _find_balanced_href_end(text, href_start)
    if href_end is None:
        return None

    return (
        text[start_index + 1 : label_end],
        text[href_start:href_end],
        href_end + 1,
    )


def _find_balanced_href_end(text: str, start_index: int) -> int | None:
    """Return the closing parenthesis for a possibly nested link href.

    Args:
        text: Inline Markdown text.
        start_index: First character inside the href parentheses.

    Returns:
        Index of the matching closing parenthesis, or `None` if it is missing.
    """
    href_end = start_index
    depth = 1
    while href_end < len(text):
        character = text[href_end]
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return href_end
        href_end += 1
    return None


def normalize_prose_punctuation(text: str) -> str:
    """Normalize ASCII dash sequences to typographic dash characters.

    Args:
        text: Inline prose text before HTML escaping.

    Returns:
        Text with triple dashes converted to em dashes and double dashes to en
        dashes.
    """
    text = re.sub(r"\s*---\s*", "\u2014", text)
    return re.sub(r"--", "\u2013", text)
