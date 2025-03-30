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

import os
from swift_book_pdf.blocks import parse_blocks
from swift_book_pdf.config import Config
from swift_book_pdf.files import get_file_name
from swift_book_pdf.latex_helpers import (
    convert_blocks_to_latex,
    generate_chapter_title,
)
from swift_book_pdf.markdown_helpers import (
    convert_markdown_links,
    remove_multiline_comments,
)


class LaTeXConverter:
    def __init__(self, config: Config):
        self.config = config

    def generate_latex(self, file_path: str) -> str:
        file_name = get_file_name(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Couldn't find the file {file_name} at {file_path}."
            )

        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.readlines()

        latex_lines = self.convert_file_to_latex(file_content, file_name.lower())
        return "\n".join(latex_lines)

    def convert_file_to_latex(
        self, file_content: list[str], file_name: str
    ) -> list[str]:
        """
        Convert the markdown content to LaTeX.
        """
        file_content = remove_multiline_comments(file_content)
        file_content = convert_markdown_links(file_content)
        file_content = [line.strip("\n") for line in file_content]
        if not file_content:
            return []

        chapter_title_box, file_content = generate_chapter_title(
            file_content, file_name
        )

        latex_lines = []
        latex_lines.extend(chapter_title_box.splitlines())
        latex_lines.append("")
        latex_lines.append("{\\BodyStyle\n")
        blocks = parse_blocks(file_content)
        body_latex = convert_blocks_to_latex(
            blocks,
            file_name,
            self.config.assets_dir,
            self.config.doc_config.mode,
            self.config.doc_config.appearance,
            self.config.font_config.main_font,
        )
        latex_lines.extend(body_latex)
        latex_lines.append("}\n\\newpage\n")
        return latex_lines
