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

import re

from swift_book_pdf.pdf.latex.render.escaping import override_characters
from swift_book_pdf.pdf.latex.render.links import (
    extract_markdown_links,
    restore_markdown_links,
)
from swift_book_pdf.pdf.options import RenderingMode

UNDERSCORE_EMPHASIS_PATTERN = re.compile(
    r"(?<!\\)(?<!\w)_(?![\s_])(.+?)(?<![\s_])_(?!\w)"
)


def apply_formatting(text: str, mode: RenderingMode) -> str:
    """
    Apply formatting to the given text.
    """
    # Temporarily extract inline code segments produced by convert_inline_code
    inline_segments: dict[str, str] = {}

    def replace_inline(match: re.Match[str]) -> str:
        token = f"%%INLINE-CODE-{len(inline_segments)}%%"
        inline_segments[token] = match.group(0)
        return token

    text = re.sub(r"(\{\\CodeStyle\s+\\texttt\{.*?\}\})", replace_inline, text)
    text, markdown_links = extract_markdown_links(text)

    # Escape literal currency/math markers from source text before we inject
    # formatter-owned LaTeX snippets that intentionally use math mode.
    text = text.replace("$", r"\$")
    text = _apply_text_formatting(text, mode)

    text = restore_markdown_links(
        text,
        markdown_links,
        mode,
        lambda label: _apply_text_formatting(label, mode),
    )

    # Restore the inline code segments.
    for token, segment in inline_segments.items():
        text = text.replace(token, segment)

    return override_characters(text)


def _apply_text_formatting(text: str, mode: RenderingMode) -> str:
    text = text.replace("→", r"\scalebox{1.2}{$\rightarrow$}")
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"\*(.+?)\*", r"\\emph{\1}", text)
    text = UNDERSCORE_EMPHASIS_PATTERN.sub(r"\\emph{\1}", text)
    text = re.sub(r"\s\\\s", r" \\\\ ", text)
    text = re.sub(r"(?<!\\)_", r"\_", text)
    text = re.sub(r"---", r"\\textemdash \\ ", text)
    text = re.sub(r"--", r"\\textendash", text)
    text = re.sub(r"\(\\\`\)", r"(\;\`\; )", text)
    text = re.sub(
        r"<doc:([^>#]+)#([^>]+)>",
        lambda m: _format_doc_reference(
            mode,
            f"{m.group(1).lower()}_{m.group(2).lower()}",
        ),
        text,
    )
    text = re.sub(
        r"<doc:([^>#]+)>",
        lambda m: _format_doc_reference(mode, m.group(1).lower()),
        text,
    )
    return re.sub(r"(?<!\\)#", r"\#", text)


def _format_doc_reference(mode: RenderingMode, key: str) -> str:
    command = (
        "\\fallbackrefbook"
        if mode == RenderingMode.PRINT
        else "\\fallbackrefdigital"
    )
    return f"{command}{{{key}}}"
