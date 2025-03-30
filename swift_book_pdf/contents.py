# Copyright 2025 Evangelos Kassos
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

from typing import Optional

from swift_book_pdf.schema import Appearance, ChapterMetadata, RenderingMode


def remove_directives(file_content: list[str]) -> list[str]:
    """ "
    Remove DocC directives from the provided file content.

    :param file_content: The content of the file to remove directives from
    :return: A list of lines with directives removed
    """
    result: list[str] = []
    in_multiline_string = False

    for line in file_content:
        stripped_line = line.strip()

        # Check if the line is the start of a multi-line directive
        if stripped_line.startswith("@") and stripped_line.endswith("{"):
            in_multiline_string = True
        elif in_multiline_string and stripped_line == "}":
            # End of a multi-line directive
            in_multiline_string = False
        elif not in_multiline_string:
            # If not in a multi-line directive, add the line to the result
            result.append(line)

    return result


def replace_and_extract_version(
    file_content: list[str],
) -> tuple[list[str], Optional[str]]:
    """
    Replace the version format in the file content and extract the version number."
    """

    version_info = None
    updated_lines: list[str] = []

    for line in file_content:
        match = re.search(r"# The Swift Programming Language \((.*?)\)", line)

        if match:
            # Extract version information
            version_info = match.group(1)
            # Use a two-line format for the version information
            updated_lines.append("# The Swift Programming Language\n")
            updated_lines.append(f"Version {version_info}\n")
        else:
            # If no match, keep the line unchanged
            updated_lines.append(line)

    return updated_lines, version_info


def replace_chapter_href_with_toc_item(
    file_content: list[str],
    chapter_metadata: dict[str, ChapterMetadata],
    mode: RenderingMode,
    appearance: Appearance,
) -> list[str]:
    """
    Replace the chapter references with the corresponding Table of Contents item.

    :param file_content: The content of the file to replace the chapter references
    :param chapter_metadata: The metadata of the chapter to replace the references with
    :param mode: The rendering mode for the replacement
    :return: A list of lines with the chapter references replaced
    """
    updated_lines: list[str] = []

    match mode:
        case RenderingMode.DIGITAL:
            pattern = re.compile(
                r"\\item \\ParagraphStyle{\\fallbackrefdigital{(.*?)}}"
            )

            def replacement(match):
                key = match.group(1)
                subtitle = (
                    chapter_metadata.get(key, ChapterMetadata()).subtitle_line or ""
                )
                return rf"\needspace{{2\baselineskip}}\item[{{\includegraphics[width=0.1in]{{chapter-icon{'~dark' if appearance == Appearance.DARK else ''}.png}}}}] \nameref{{{key}}} \\ {subtitle}"

        case RenderingMode.PRINT:
            pattern = re.compile(r"\\item \\ParagraphStyle{\\fallbackrefbook{(.*?)}}")

            def replacement(match):
                key = match.group(1)
                subtitle = (
                    chapter_metadata.get(key, ChapterMetadata()).subtitle_line or ""
                )
                return rf"\needspace{{2\baselineskip}}\item[{{\includegraphics[width=0.1in]{{chapter-icon{'~dark' if appearance == Appearance.DARK else ''}.png}}}}] \nameref{{{key}}} {{\textcolor{{aside_border}}{{\hrulefill}}}} \pageref{{{key}}} \\ {subtitle}"

        case _:
            raise ValueError("Invalid rendering mode specified.")

    for line in file_content:
        updated_line = pattern.sub(replacement, line)
        updated_lines.append(updated_line)

    return updated_lines
