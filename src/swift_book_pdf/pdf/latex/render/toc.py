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

"""LaTeX rendering for the Swift Book table of contents."""

import re
from typing import TYPE_CHECKING

from swift_book_pdf.core.generated.notices.metadata import (
    build_notices_toc_lines,
)
from swift_book_pdf.core.markdown import (
    normalize_versioned_title,
    remove_directives,
)
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.core.source import ChapterMetadata
from swift_book_pdf.core.source.paths import get_file_name
from swift_book_pdf.pdf.config import Appearance, RenderingMode
from swift_book_pdf.pdf.latex.render.inline import apply_formatting

if TYPE_CHECKING:
    from swift_book_pdf.pdf.latex.renderer import LaTeXRenderer


def generate_toc_latex(
    toc: TableOfContents,
    converter: "LaTeXRenderer",
) -> str:
    """Render the source table of contents as LaTeX.

    Args:
        toc: Loaded Swift Book table of contents.
        converter: LaTeX renderer used for parsed Markdown content.

    Returns:
        Rendered table-of-contents LaTeX.
    """
    notices_lines = (
        build_notices_toc_lines(include_section_heading=True)
        if toc.include_notices
        else []
    )
    processed_lines = remove_directives(toc.file_content + notices_lines)
    processed_lines = normalize_versioned_title(processed_lines)
    file_name = get_file_name(toc.tspl_file_path)
    toc_latex_lines = converter.convert_file_to_latex(
        processed_lines, file_name
    )
    toc_latex_lines = apply_toc_latex_overrides(
        toc_latex_lines,
        toc.chapter_metadata,
        converter.config.doc_config.mode,
        converter.config.doc_config.appearance,
        resolve_references=not converter.config.content_selection.only_toc,
    )
    return "\n".join(toc_latex_lines)


def apply_toc_latex_overrides(
    latex_lines: list[str],
    chapter_metadata: dict[str, ChapterMetadata],
    mode: RenderingMode,
    appearance: Appearance,
    *,
    resolve_references: bool = True,
) -> list[str]:
    """Apply PDF-specific table-of-contents LaTeX overrides.

    Args:
        latex_lines: Initial LaTeX lines rendered from the Markdown TOC.
        chapter_metadata: Chapter metadata keyed by normalized document key.
        mode: PDF rendering mode.
        appearance: PDF color appearance.
        resolve_references: Whether TOC items should use LaTeX references.

    Returns:
        Adjusted LaTeX lines for the PDF table of contents.
    """
    latex_text = "\n".join(latex_lines)
    latex_text = latex_text.replace(
        r"\DocCContentNodeHeadingTwo", r"\DocCContentNodeHeadingTwoTOC"
    )
    latex_text = latex_text.replace(
        r"\DocCContentNodeHeadingThree", r"\DocCContentNodeHeadingThreeTOC"
    )
    latex_text = latex_text.replace(
        r"\begin{itemize}", r"\begin{DocCTopicLinkBlockList}"
    )
    latex_text = latex_text.replace(
        r"\end{itemize}", r"\end{DocCTopicLinkBlockList}"
    )
    return replace_chapter_href_with_toc_item(
        latex_text.splitlines(),
        chapter_metadata,
        mode,
        appearance,
        resolve_references=resolve_references,
    )


def replace_chapter_href_with_toc_item(
    file_content: list[str],
    chapter_metadata: dict[str, ChapterMetadata],
    mode: RenderingMode,
    appearance: Appearance,
    *,
    resolve_references: bool = True,
) -> list[str]:
    """Replace chapter references with LaTeX table-of-contents items.

    Args:
        file_content: LaTeX lines containing fallback chapter references.
        chapter_metadata: Chapter metadata keyed by normalized document key.
        mode: PDF rendering mode.
        appearance: PDF color appearance.
        resolve_references: Whether TOC items should use LaTeX references.

    Returns:
        Lines with chapter references replaced by table-of-contents items.

    Raises:
        ValueError: If `mode` is not a supported rendering mode.
    """
    updated_lines: list[str] = []
    icon_name = (
        f"chapter-icon{'~dark' if appearance == Appearance.DARK else ''}.png"
    )

    match mode:
        case RenderingMode.DIGITAL:
            pattern = re.compile(
                r"\\item\s+\\begin{DocCContentListItemParagraph}\s*"
                r"\\fallbackrefdigital{([^{}]+)}\s*"
                r"\\end{DocCContentListItemParagraph}"
            )

            def replacement(match: re.Match[str]) -> str:
                """Render a digital-mode table-of-contents item.

                Args:
                    match: Regex match for one fallback chapter reference.

                Returns:
                    Rendered LaTeX table-of-contents item.
                """
                key = match.group(1)
                subtitle = (
                    chapter_metadata.get(key, ChapterMetadata()).subtitle_line
                    or ""
                )
                title = _toc_item_title(
                    key,
                    chapter_metadata,
                    mode,
                    resolve_references=resolve_references,
                )
                return rf"\DocCTopicLinkBlock{{{icon_name}}}{{{title}}}{{{subtitle}}}"

        case RenderingMode.PRINT:
            pattern = re.compile(
                r"\\item\s+\\begin{DocCContentListItemParagraph}\s*"
                r"\\fallbackrefbook{([^{}]+)}\s*"
                r"\\end{DocCContentListItemParagraph}"
            )

            def replacement(match: re.Match[str]) -> str:
                """Render a print-mode table-of-contents item.

                Args:
                    match: Regex match for one fallback chapter reference.

                Returns:
                    Rendered LaTeX table-of-contents item.
                """
                key = match.group(1)
                subtitle = (
                    chapter_metadata.get(key, ChapterMetadata()).subtitle_line
                    or ""
                )
                title = _toc_item_title(
                    key,
                    chapter_metadata,
                    mode,
                    resolve_references=resolve_references,
                )
                page_ref = (
                    rf" {{\textcolor{{color_aside_note_border}}{{\hrulefill}}}} \pageref{{{key}}}"
                    if resolve_references
                    else ""
                )
                return rf"\DocCTopicLinkBlock{{{icon_name}}}{{{title}{page_ref}}}{{{subtitle}}}"

        case _:
            raise ValueError("Invalid rendering mode specified.")

    updated_text = pattern.sub(replacement, "\n".join(file_content))
    updated_lines.extend(updated_text.splitlines())
    return updated_lines


def _toc_item_title(
    key: str,
    chapter_metadata: dict[str, ChapterMetadata],
    mode: RenderingMode,
    *,
    resolve_references: bool,
) -> str:
    """Return a TOC item title for live or static rendering.

    Args:
        key: Normalized document key.
        chapter_metadata: Chapter metadata keyed by normalized document key.
        mode: PDF rendering mode.
        resolve_references: Whether TOC items should use LaTeX references.

    Returns:
        LaTeX for the TOC item title.
    """
    if resolve_references:
        return rf"\nameref{{{key}}}"
    title = chapter_metadata.get(key, ChapterMetadata()).header_line or key
    return apply_formatting(title, mode)
