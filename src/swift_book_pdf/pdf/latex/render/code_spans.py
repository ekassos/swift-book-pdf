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

"""Inline code span rendering."""

import re

from swift_book_pdf.pdf.latex.render.escaping import escape_texttt


def convert_inline_code(text: str) -> str:
    """Render Markdown inline code spans as `\\CodeStyle` text.

    Args:
        text: Markdown text that may contain inline code spans.

    Returns:
        Text with Markdown inline code converted to LaTeX.
    """
    double_placeholder: dict[str, str] = {}

    def repl_double(match: re.Match[str]) -> str:
        """Protect and render a double-backtick code span.

        Args:
            match: Regex match for the Markdown code span.

        Returns:
            Placeholder token for the rendered code span.
        """
        inner = match.group(1)
        processed = (
            r"{\CodeStyle \texttt{" + escape_texttt(inner).strip() + "}}"
        )
        token = f"@@DOUBLE{len(double_placeholder)}@@"
        double_placeholder[token] = processed
        return token

    text = re.sub(r"(?<!\\)``(.*?)``", repl_double, text)

    def repl_single(match: re.Match[str]) -> str:
        """Render a single-backtick code span.

        Args:
            match: Regex match for the Markdown code span.

        Returns:
            Rendered LaTeX inline code span.
        """
        inner = match.group(1)
        return r"{\CodeStyle \texttt{" + escape_texttt(inner).strip() + "}}"

    text = re.sub(r"(?<!\\)`(.*?)`", repl_single, text)

    for token, replacement in double_placeholder.items():
        text = text.replace(token, replacement)

    return text
