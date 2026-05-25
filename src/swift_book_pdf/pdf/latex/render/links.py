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

"""Markdown-link protection and LaTeX rendering."""

import re
from collections.abc import Callable

from swift_book_pdf.pdf.config import RenderingMode

MARKDOWN_LINK_PATTERN = re.compile(
    r"\[([^\]]+)\]\((https?:\/\/[^\s()]+(?:\([^()]*\)[^\s()]*)*)\)"
)


def extract_markdown_links(
    text: str,
) -> tuple[str, dict[str, tuple[str, str]]]:
    """Replace Markdown links with placeholders and return link metadata."""
    markdown_links: dict[str, tuple[str, str]] = {}

    def replace_markdown_link(match: re.Match[str]) -> str:
        token = f"%%MARKDOWN-LINK-{len(markdown_links)}%%"
        markdown_links[token] = (match.group(1), match.group(2))
        return token

    return MARKDOWN_LINK_PATTERN.sub(
        replace_markdown_link, text
    ), markdown_links


def restore_markdown_links(
    text: str,
    markdown_links: dict[str, tuple[str, str]],
    mode: RenderingMode,
    format_label: Callable[[str], str],
) -> str:
    """Render previously extracted Markdown links as LaTeX."""
    for token, (label, url) in markdown_links.items():
        formatted_label = format_label(label)
        replacement = (
            f"\\href{{{url}}}{{{formatted_label}}}\\footnote{{\\url{{{url}}}}}"
            if mode == RenderingMode.PRINT
            else f"\\href{{{url}}}{{{formatted_label}}}"
        )
        text = text.replace(token, replacement)
    return text
