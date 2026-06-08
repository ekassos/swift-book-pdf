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

"""Markdown-to-LaTeX renderer for Swift Book source documents."""

from collections.abc import Mapping
from pathlib import Path

from swift_book_pdf.core.blocks.parser import parse_blocks
from swift_book_pdf.core.markdown import (
    convert_markdown_links,
    remove_multiline_comments,
)
from swift_book_pdf.core.source import ChapterMetadata
from swift_book_pdf.core.source.paths import get_file_name
from swift_book_pdf.pdf.latex.config import LaTeXPDFConfig
from swift_book_pdf.pdf.latex.render.blocks import convert_blocks_to_latex
from swift_book_pdf.pdf.latex.render.chapter import generate_chapter_title
from swift_book_pdf.pdf.latex.render.context import LaTeXRenderContext
from swift_book_pdf.pdf.latex.render.inline import DocReferenceResolver


class LaTeXRenderer:
    """Render Swift Book Markdown files into LaTeX body content."""

    def __init__(
        self,
        config: LaTeXPDFConfig,
        chapter_metadata: Mapping[str, ChapterMetadata] | None = None,
    ) -> None:
        """Initialize a renderer for one resolved PDF build.

        Args:
            config: Resolved LaTeX-backed PDF build configuration.
            chapter_metadata: Chapter metadata keyed by document key.
        """
        self.config = config
        self.chapter_metadata = chapter_metadata or {}

    def render_file(self, file_path: str) -> str:
        """Render a Markdown source file as LaTeX.

        Args:
            file_path: Path to the Markdown source file.

        Returns:
            Rendered LaTeX content.

        Raises:
            FileNotFoundError: If `file_path` does not exist.
        """
        file_name = get_file_name(file_path)
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Couldn't find the file {file_name} at {file_path}.",
            )

        with path.open("r", encoding="utf-8") as file:
            file_content = file.readlines()

        latex_lines = self.convert_file_to_latex(
            file_content, file_name.lower()
        )
        return "\n".join(latex_lines)

    def convert_file_to_latex(
        self,
        file_content: list[str],
        file_name: str,
    ) -> list[str]:
        """Convert Markdown file content to LaTeX lines.

        Args:
            file_content: Source Markdown lines.
            file_name: Lowercase document key used for labels.

        Returns:
            Rendered LaTeX lines.
        """
        file_content = remove_multiline_comments(file_content)
        file_content = convert_markdown_links(file_content)
        file_content = [line.strip("\n") for line in file_content]
        if not file_content:
            return []

        chapter_title_box, file_content = generate_chapter_title(
            file_content,
            file_name,
        )

        latex_lines = []
        latex_lines.extend(chapter_title_box.splitlines())
        latex_lines.append("")
        latex_lines.append("{\\DocCArticleBodyStyle\n")
        blocks = parse_blocks(file_content)
        body_latex = convert_blocks_to_latex(
            blocks,
            LaTeXRenderContext(
                file_name=file_name,
                assets_dir=self.config.assets_dir,
                mode=self.config.doc_config.mode,
                appearance=self.config.doc_config.appearance,
                main_font=self.config.latex_config.font_config.main_font,
                body_font_size=self.config.doc_config.font_size,
                doc_references=self._doc_reference_resolver(file_name),
            ),
        )
        latex_lines.extend(body_latex)
        latex_lines.append("}\n\\newpage")
        return latex_lines

    def _doc_reference_resolver(
        self,
        file_name: str,
    ) -> DocReferenceResolver | None:
        """Build a subset reference resolver for the current file.

        Args:
            file_name: Lowercase document key used for labels.

        Returns:
            Resolver for single-chapter builds, otherwise `None`.
        """
        selection = self.config.content_selection
        if selection.only_chapter is None:
            return None
        return DocReferenceResolver(
            chapter_metadata=self.chapter_metadata,
            live_reference_prefixes=frozenset({file_name}),
        )
