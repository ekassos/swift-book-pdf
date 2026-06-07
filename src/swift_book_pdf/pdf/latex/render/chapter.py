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

"""LaTeX rendering for chapter title hero blocks."""


def generate_chapter_title(
    lines: list[str], file_name: str
) -> tuple[str, list[str]]:
    """Generate the chapter title LaTeX from source lines.

    Args:
        lines: Source lines for one chapter.
        file_name: Lowercase document key used for labels.

    Returns:
        Rendered title hero LaTeX and the remaining body lines.
    """
    header_line = None
    subtitle_line = None

    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("#"):
            header_line = lines[i].lstrip("#").strip()
            i += 1
            break
        i += 1
    while i < len(lines):
        if lines[i].strip():
            subtitle_line = lines[i].strip()
            i += 1
            break
        i += 1

    title_subtitle_snippet = rf"""
    \thispagestyle{{firstpagestyle}}
    \renewcommand{{\customheader}}{{{header_line}}}
    \vspace*{{\DocCArticleHeroChapterGap}}
    \DocCArticleHeroBox{{{header_line}}}{{{file_name}}}{{{subtitle_line}}}
    \vspace*{{\DocCArticleHeroChapterGap}}
    """

    return title_subtitle_snippet, lines[i:]
