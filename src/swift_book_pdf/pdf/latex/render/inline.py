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

"""Inline Markdown formatting for LaTeX output."""

import re
from collections.abc import Mapping
from dataclasses import dataclass

from swift_book_pdf.core.source import ChapterMetadata
from swift_book_pdf.pdf.config import RenderingMode
from swift_book_pdf.pdf.latex.render.escaping import override_characters
from swift_book_pdf.pdf.latex.render.links import (
    extract_markdown_links,
    restore_markdown_links,
)

UNDERSCORE_EMPHASIS_PATTERN = re.compile(
    r"(?<!\\)(?<!\w)_(?![\s_])(.+?)(?<![\s_])_(?!\w)"
)


@dataclass(frozen=True)
class DocReferenceResolver:
    """Resolve document references that cannot exist in subset builds.

    Attributes:
        chapter_metadata: Chapter metadata keyed by normalized document key.
        live_reference_prefixes: Label prefixes emitted by the current subset.
    """

    chapter_metadata: Mapping[str, ChapterMetadata]
    """Chapter metadata keyed by normalized document key."""

    live_reference_prefixes: frozenset[str]
    """Label prefixes emitted by the current subset."""

    def static_text_for_missing_reference(self, key: str) -> str | None:
        """Return static text when a target label is outside the subset.

        Args:
            key: Normalized LaTeX reference label.

        Returns:
            Static chapter title for missing cross-chapter references, or
            `None` when the reference should remain live.
        """
        if self._can_resolve_live(key):
            return None

        chapter_key = key.split("_", maxsplit=1)[0]
        metadata = self.chapter_metadata.get(chapter_key)
        if metadata is None:
            return None
        return metadata.header_line

    def _can_resolve_live(self, key: str) -> bool:
        """Return whether the current subset should emit `key`.

        Args:
            key: Normalized LaTeX reference label.

        Returns:
            Whether the label is expected in the rendered subset.
        """
        return any(
            key == prefix or key.startswith(f"{prefix}_")
            for prefix in self.live_reference_prefixes
        )


def apply_formatting(
    text: str,
    mode: RenderingMode,
    doc_references: DocReferenceResolver | None = None,
) -> str:
    """Apply Markdown inline formatting and source glyph overrides.

    Notes:
        Inline code and Markdown links are protected before formatting so
        emphasis and escaping rules do not rewrite LaTeX that was already
        produced by more specific renderers.

    Args:
        text: Markdown text after inline code conversion.
        mode: PDF rendering mode.
        doc_references: Optional resolver for subset-build document refs.

    Returns:
        LaTeX-safe formatted text.
    """
    # Temporarily extract inline code segments produced by convert_inline_code
    inline_segments: dict[str, str] = {}

    def replace_inline(match: re.Match[str]) -> str:
        """Replace rendered inline code with a temporary placeholder.

        Args:
            match: Regex match for already-rendered inline code.

        Returns:
            Placeholder token for the protected inline code.
        """
        token = f"%%INLINE-CODE-{len(inline_segments)}%%"
        inline_segments[token] = match.group(0)
        return token

    text = re.sub(r"(\{\\CodeStyle\s+\\texttt\{.*?\}\})", replace_inline, text)
    text, markdown_links = extract_markdown_links(text)

    # Escape literal currency/math markers from source text before we inject
    # formatter-owned LaTeX snippets that intentionally use math mode.
    text = text.replace("$", r"\$")
    text = _apply_text_formatting(text, mode, doc_references)

    text = restore_markdown_links(
        text,
        markdown_links,
        mode,
        lambda label: _apply_text_formatting(label, mode, doc_references),
    )

    # Restore the inline code segments.
    for token, segment in inline_segments.items():
        text = text.replace(token, segment)

    return override_characters(text)


def _apply_text_formatting(
    text: str,
    mode: RenderingMode,
    doc_references: DocReferenceResolver | None,
) -> str:
    """Apply inline Markdown transforms that operate on plain text.

    Args:
        text: Markdown text with protected inline segments removed.
        mode: PDF rendering mode.
        doc_references: Optional resolver for subset-build document refs.

    Returns:
        Text with inline Markdown converted to LaTeX snippets.
    """
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
            doc_references,
        ),
        text,
    )
    text = re.sub(
        r"<doc:([^>#]+)>",
        lambda m: _format_doc_reference(
            mode,
            m.group(1).lower(),
            doc_references,
        ),
        text,
    )
    return re.sub(r"(?<!\\)#", r"\#", text)


def _format_doc_reference(
    mode: RenderingMode,
    key: str,
    doc_references: DocReferenceResolver | None,
) -> str:
    """Format a Swift Book doc reference for the active rendering mode.

    Args:
        mode: PDF rendering mode.
        key: Normalized document reference key.
        doc_references: Optional resolver for subset-build document refs.

    Returns:
        LaTeX fallback reference command.
    """
    if doc_references is not None:
        static_text = doc_references.static_text_for_missing_reference(key)
        if static_text is not None:
            return static_text

    command = (
        "\\fallbackrefbook"
        if mode == RenderingMode.PRINT
        else "\\fallbackrefdigital"
    )
    return f"{command}{{{key}}}"
