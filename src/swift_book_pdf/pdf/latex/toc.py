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

from swift_book_pdf.core.generated.notices import build_notices_toc_lines
from swift_book_pdf.core.markdown import (
    remove_directives,
    replace_and_extract_version,
)
from swift_book_pdf.core.navigation.toc import TableOfContents
from swift_book_pdf.core.source import ChapterMetadata
from swift_book_pdf.core.source.paths import get_file_name
from swift_book_pdf.pdf.latex import LaTeXConverter
from swift_book_pdf.pdf.options import Appearance, RenderingMode

CHAPTER_ICON_WIDTH_EM = 0.8


def generate_toc_latex(
    toc: TableOfContents,
    converter: LaTeXConverter,
) -> tuple[str, str | None]:
    notices_lines = (
        build_notices_toc_lines(include_section_heading=True)
        if toc.include_notices
        else []
    )
    processed_lines = remove_directives(toc.file_content + notices_lines)
    processed_lines = replace_chapter_href_with_toc_item(
        processed_lines,
        toc.chapter_metadata,
        converter.config.doc_config.mode,
        converter.config.doc_config.appearance,
    )
    processed_lines, version_info = replace_and_extract_version(
        processed_lines
    )
    file_name = get_file_name(toc.tspl_file_path)
    toc_latex_lines = converter.convert_file_to_latex(
        processed_lines, file_name
    )
    toc_latex_lines = apply_toc_latex_overrides(
        toc_latex_lines,
        toc.chapter_metadata,
        converter.config.doc_config.mode,
        converter.config.doc_config.appearance,
    )
    toc_latex = "\n".join(toc_latex_lines)
    return toc_latex, version_info


def apply_toc_latex_overrides(
    latex_lines: list[str],
    chapter_metadata: dict[str, ChapterMetadata],
    mode: RenderingMode,
    appearance: Appearance,
) -> list[str]:
    latex_text = "\n".join(latex_lines)
    latex_text = latex_text.replace(r"\SectionHeader", r"\SectionHeaderTOC")
    latex_text = latex_text.replace(
        r"\SubsectionHeader", r"\SubsectionHeaderTOC"
    )
    return replace_chapter_href_with_toc_item(
        latex_text.splitlines(),
        chapter_metadata,
        mode,
        appearance,
    )


def replace_chapter_href_with_toc_item(
    file_content: list[str],
    chapter_metadata: dict[str, ChapterMetadata],
    mode: RenderingMode,
    appearance: Appearance,
) -> list[str]:
    """
    Replace chapter references with LaTeX table-of-contents items.

    :param file_content: The content of the file to replace the chapter references
    :param chapter_metadata: The metadata of the chapter to replace the references with
    :param mode: The rendering mode for the replacement
    :return: A list of lines with the chapter references replaced
    """
    updated_lines: list[str] = []
    icon_name = (
        f"chapter-icon{'~dark' if appearance == Appearance.DARK else ''}.png"
    )
    icon_markup = (
        rf"\includegraphics[width={CHAPTER_ICON_WIDTH_EM}em]{{{icon_name}}}"
    )

    match mode:
        case RenderingMode.DIGITAL:
            pattern = re.compile(
                r"\\item \\ParagraphStyle{\\fallbackrefdigital{(.*?)}}",
            )

            def replacement(match: re.Match[str]) -> str:
                key = match.group(1)
                subtitle = (
                    chapter_metadata.get(key, ChapterMetadata()).subtitle_line
                    or ""
                )
                return rf"\needspace{{2\baselineskip}}\item[{{{icon_markup}}}] \nameref{{{key}}} \\ {subtitle}"

        case RenderingMode.PRINT:
            pattern = re.compile(
                r"\\item \\ParagraphStyle{\\fallbackrefbook{(.*?)}}"
            )

            def replacement(match: re.Match[str]) -> str:
                key = match.group(1)
                subtitle = (
                    chapter_metadata.get(key, ChapterMetadata()).subtitle_line
                    or ""
                )
                return rf"\needspace{{2\baselineskip}}\item[{{{icon_markup}}}] \nameref{{{key}}} {{\textcolor{{aside_border}}{{\hrulefill}}}} \pageref{{{key}}} \\ {subtitle}"

        case _:
            raise ValueError("Invalid rendering mode specified.")

    for line in file_content:
        updated_line = pattern.sub(replacement, line)
        updated_lines.append(updated_line)

    return updated_lines
