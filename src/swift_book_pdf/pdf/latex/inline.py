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

from swift_book_pdf.pdf.options import RenderingMode

UNDERSCORE_EMPHASIS_PATTERN = re.compile(
    r"(?<!\\)(?<!\w)_(?![\s_])(.+?)(?<![\s_])_(?!\w)"
)
MARKDOWN_LINK_PATTERN = re.compile(
    r"\[([^\]]+)\]\((https?:\/\/[^\s()]+(?:\([^()]*\)[^\s()]*)*)\)"
)


def escape_texttt(text: str) -> str:
    """
    Escape characters in text that cause issues inside `\texttt`.
    """
    # Order matters: escape backslash first
    text = text.replace("\\", r"\textbackslash ")

    # Escape curly braces and underscore that conflict with LaTeX grouping
    text = text.replace("{", r"\{")
    text = text.replace("}", r"\}")
    text = text.replace("_", r"\_")

    # Escape hash symbol (if not already escaped)
    text = re.sub(r"(?<!\\)#", r"\#", text)

    # Escape other special characters
    text = text.replace("$", r"\$")
    text = text.replace("&", r"\&")
    text = text.replace("%", r"\%")
    text = text.replace("^", r"\textasciicircum ")
    text = text.replace("`", r"\textasciigrave ")
    text = text.replace("~", r"\textasciitilde ")
    text = text.replace("[", r"{[}")
    text = text.replace("]", r"{]}")
    text = text.replace("(", r"{(}")
    text = text.replace(")", r"{)}")
    text = text.replace(".", r"{.}")
    text = text.replace(",", r"{,}")
    text = text.replace(":", r"{:}")
    text = text.replace(";", r"{;}")
    text = text.replace("=", r"{=}")
    text = text.replace("@", r"{@}")
    text = text.replace("?", r"{?}")
    text = text.replace("!", r"{!}")

    # The arrow token "->" is two characters long.
    # Replace it before any chance of interfering with its hyphen.
    text = text.replace("->", r"{->}")

    return override_characters(text)


def override_characters(text: str, in_code_block: bool = False) -> str:
    """
    Override characters in text that may have special formatting in LaTeX.
    """
    override_set = {"é⃝": "\\textcircled{é}"}

    if in_code_block:
        override_set = {k: f"|{v}|" for k, v in override_set.items()}

    for char, replacement in override_set.items():
        text = text.replace(char, replacement)
    return text


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

    markdown_links: dict[str, tuple[str, str]] = {}

    def replace_markdown_link(match: re.Match[str]) -> str:
        token = f"%%MARKDOWN-LINK-{len(markdown_links)}%%"
        markdown_links[token] = (match.group(1), match.group(2))
        return token

    text = re.sub(r"(\{\\CodeStyle\s+\\texttt\{.*?\}\})", replace_inline, text)
    text = MARKDOWN_LINK_PATTERN.sub(replace_markdown_link, text)

    # Escape literal currency/math markers from source text before we inject
    # formatter-owned LaTeX snippets that intentionally use math mode.
    text = text.replace("$", r"\$")

    # Apply formatting to the rest of the text.
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
        lambda m: (
            (
                "\\fallbackrefbook{"
                if mode == RenderingMode.PRINT
                else "\\fallbackrefdigital{"
            )
            + m.group(1).lower()
            + "_"
            + m.group(2).lower()
            + "}"
        ),
        text,
    )
    text = re.sub(
        r"<doc:([^>#]+)>",
        lambda m: (
            (
                "\\fallbackrefbook{"
                if mode == RenderingMode.PRINT
                else "\\fallbackrefdigital{"
            )
            + m.group(1).lower()
            + "}"
        ),
        text,
    )
    text = re.sub(r"(?<!\\)#", r"\#", text)

    for token, (label, url) in markdown_links.items():
        formatted_label = _apply_non_link_formatting(label, mode)
        replacement = (
            f"\\href{{{url}}}{{{formatted_label}}}\\footnote{{\\url{{{url}}}}}"
            if mode == RenderingMode.PRINT
            else f"\\href{{{url}}}{{{formatted_label}}}"
        )
        text = text.replace(token, replacement)

    # Restore the inline code segments.
    for token, segment in inline_segments.items():
        text = text.replace(token, segment)

    return override_characters(text)


def _apply_non_link_formatting(text: str, mode: RenderingMode) -> str:
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
        lambda m: (
            (
                "\\fallbackrefbook{"
                if mode == RenderingMode.PRINT
                else "\\fallbackrefdigital{"
            )
            + m.group(1).lower()
            + "_"
            + m.group(2).lower()
            + "}"
        ),
        text,
    )
    text = re.sub(
        r"<doc:([^>#]+)>",
        lambda m: (
            (
                "\\fallbackrefbook{"
                if mode == RenderingMode.PRINT
                else "\\fallbackrefdigital{"
            )
            + m.group(1).lower()
            + "}"
        ),
        text,
    )
    return re.sub(r"(?<!\\)#", r"\#", text)


def convert_inline_code(text: str) -> str:
    """
    Replace inline code delimited by unescaped backticks with
    `{\\CodeStyle \texttt{...}}`.

    This converter supports two kinds of delimiters:
      • Double backticks (``...``): These blocks are processed first
        and “protected” so that any inner single backticks (as in “`x`”)
        are not processed a second time.
      • Single backticks (`...`): Handled afterward.

    Escaped backticks (preceded by a backslash) are not processed.
    """
    # Protect double-backtick replacements with placeholders.
    double_placeholder: dict[str, str] = {}

    def repl_double(match: re.Match[str]) -> str:
        inner = match.group(1)  # Everything between the double backticks.
        processed = (
            r"{\CodeStyle \texttt{" + escape_texttt(inner).strip() + "}}"
        )
        # Create a unique token unlikely to appear in the text.
        token = f"@@DOUBLE{len(double_placeholder)}@@"
        double_placeholder[token] = processed
        return token

    # Process double-backtick code first.
    # This regex matches two unescaped backticks on each side.
    text = re.sub(r"(?<!\\)``(.*?)``", repl_double, text)

    # Now process single-backtick code.
    def repl_single(match: re.Match[str]) -> str:
        inner = match.group(1)
        return r"{\CodeStyle \texttt{" + escape_texttt(inner).strip() + "}}"

    text = re.sub(r"(?<!\\)`(.*?)`", repl_single, text)

    # Finally, restore the double-backtick replacements.
    for token, replacement in double_placeholder.items():
        text = text.replace(token, replacement)

    return text
