# Copyright 2026 Evangelos Kassos
#
# Portions derived from swift-docc-render:
#   Copyright (c) 2021-2025 Apple Inc. and the Swift project authors
#   Licensed under Apache License v2.0 with Runtime Library Exception
#
#   See https://swift.org/LICENSE.txt for details.
#   The Swift project authors are credited at https://swift.org/CONTRIBUTORS.txt.
#   See THIRD-PARTY-NOTICES.txt for details.
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

DOCC_WORD_BREAK = r"\allowbreak{}"


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
        processed = _render_code_voice(inner)
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
        return _render_code_voice(inner)

    text = re.sub(r"(?<!\\)`(.*?)`", repl_single, text)

    for token, replacement in double_placeholder.items():
        text = text.replace(token, replacement)

    return text


def _render_code_voice(text: str) -> str:
    """Render a Markdown code span as a DocC `codeVoice` LaTeX span.

    Args:
        text: Raw inline-code text.

    Returns:
        LaTeX for the inline-code span.
    """
    return (
        r"{\DocCCodeVoiceStyle \texttt{"
        + _escape_texttt_with_word_breaks(text.strip())
        + "}}"
    )


def _escape_texttt_with_word_breaks(text: str) -> str:
    """Escape inline code and preserve DocC Render word-break hints.

    DocC Render's `CodeVoice` component wraps inline code in `WordBreak`, whose
    default boundary pattern inserts break opportunities between lower/uppercase
    pairs, after colons, before dots, and before underscores.

    Args:
        text: Raw inline-code text.

    Returns:
        Escaped inline-code text with LaTeX break opportunities.
    """
    pieces: list[str] = []
    start = 0

    for boundary in _docc_word_break_boundaries(text):
        pieces.append(escape_texttt(text[start:boundary]))
        pieces.append(DOCC_WORD_BREAK)
        start = boundary

    pieces.append(escape_texttt(text[start:]))
    return "".join(pieces)


def _docc_word_break_boundaries(text: str) -> list[int]:
    """Return the raw-string indexes where DocC Render inserts `<wbr>`.

    Args:
        text: Raw inline-code text.

    Returns:
        Character indexes after which a break opportunity should be inserted.
    """
    return [
        match.start() + 1
        for match in re.finditer(
            r"([a-z](?=[A-Z])|(:)\w|\w(?=[._]\w))",
            text,
        )
    ]
