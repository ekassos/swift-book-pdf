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

from typing import Optional
from swift_book_pdf.chapters import generate_chapter_metadata
from swift_book_pdf.contents import (
    remove_directives,
    replace_and_extract_version,
    replace_chapter_href_with_toc_item,
)
from swift_book_pdf.doc_tags import extract_doc_tags
from swift_book_pdf.files import get_file_name
from swift_book_pdf.latex import LaTeXConverter
from swift_book_pdf.schema import Appearance, RenderingMode


class TableOfContents:
    def __init__(self, root_dir: str, tspl_file_path: str):
        self.tspl_file_path = tspl_file_path
        self.target_directories = [
            "GuidedTour",
            "LanguageGuide",
            "ReferenceManual",
            "RevisionHistory",
        ]

        with open(tspl_file_path, "r", encoding="utf-8") as file:
            self.file_content = file.readlines()

        self.chapter_metadata = generate_chapter_metadata(
            root_dir, self.target_directories
        )
        self.doc_tags = extract_doc_tags(self.file_content)

    def generate_toc_latex(
        self, converter: LaTeXConverter
    ) -> tuple[str, Optional[str]]:
        processed_lines = remove_directives(self.file_content)
        processed_lines = replace_chapter_href_with_toc_item(
            processed_lines,
            self.chapter_metadata,
            converter.config.doc_config.mode,
            converter.config.doc_config.appearance,
        )
        processed_lines, version_info = replace_and_extract_version(processed_lines)
        file_name = get_file_name(self.tspl_file_path)
        toc_latex_lines = converter.convert_file_to_latex(processed_lines, file_name)
        toc_latex_lines = self.toc_latex_overrides(
            toc_latex_lines,
            converter.config.doc_config.mode,
            converter.config.doc_config.appearance,
        )
        toc_latex = "\n".join(toc_latex_lines)
        return toc_latex, version_info

    def toc_latex_overrides(
        self,
        latex_lines: list[str],
        mode: RenderingMode,
        appearance: Appearance,
    ) -> list[str]:
        latex_text = "\n".join(latex_lines)
        latex_text = latex_text.replace(r"\SectionHeader", r"\SectionHeaderTOC")
        latex_text = latex_text.replace(r"\SubsectionHeader", r"\SubsectionHeaderTOC")
        return replace_chapter_href_with_toc_item(
            latex_text.splitlines(), self.chapter_metadata, mode, appearance
        )
