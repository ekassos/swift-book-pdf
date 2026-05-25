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

"""LaTeX PDF engine orchestration."""

from pathlib import Path

from tqdm import trange

from swift_book_pdf.pdf.contracts import PDFBuildContext
from swift_book_pdf.pdf.latex.build.compiler import LuaLaTeXCompiler
from swift_book_pdf.pdf.latex.config import LaTeXPDFConfig
from swift_book_pdf.pdf.latex.document import write_latex_document
from swift_book_pdf.pdf.latex.renderer import LaTeXRenderer


class LaTeXEngine:
    """Render Swift Book Markdown to LaTeX and compile it to PDF."""

    def build(self, context: PDFBuildContext) -> Path:
        """Build the temporary PDF for a LaTeX-backed PDF build."""
        config = _require_latex_config(context.config)
        latex_file_path = Path(config.temp_dir) / "inner_content.tex"
        write_latex_document(
            config,
            context.toc,
            LaTeXRenderer(config),
            latex_file_path,
        )

        compiler = LuaLaTeXCompiler(config)
        for _ in trange(config.latex_config.typesets, leave=False):
            compiler.convert_to_pdf(str(latex_file_path))

        return Path(config.temp_dir) / "inner_content.pdf"


def _require_latex_config(config: object) -> LaTeXPDFConfig:
    if isinstance(config, LaTeXPDFConfig):
        return config
    raise TypeError("LaTeXEngine requires a LaTeXPDFConfig.")
