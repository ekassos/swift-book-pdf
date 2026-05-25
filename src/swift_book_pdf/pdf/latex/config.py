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

"""LaTeX-specific PDF build configuration."""

from dataclasses import dataclass

from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.fonts.config import FontConfig
from swift_book_pdf.pdf.latex.fonts.config import format_for_latex
from swift_book_pdf.pdf.options import EngineKind

DEFAULT_TYPESETS = 4


@dataclass(frozen=True, kw_only=True)
class LaTeXConfig:
    """Resolved LaTeX backend configuration."""

    font_config: FontConfig
    typesets: int = DEFAULT_TYPESETS

    def __post_init__(self) -> None:
        """Validate the resolved LaTeX configuration."""
        if self.typesets <= 0:
            raise ValueError("Typesets must be a positive integer.")

    def __str__(self) -> str:
        """Format the resolved LaTeX configuration for diagnostics."""
        font_config = (
            format_for_latex(self.font_config)
            if isinstance(self.font_config, FontConfig)
            else str(self.font_config)
        )
        return "\n".join(
            [
                f"Typesets: {self.typesets}",
                font_config.rstrip(),
            ]
        )


@dataclass(frozen=True, kw_only=True)
class LaTeXPDFConfig(PDFConfig):
    """Resolved configuration for LaTeX-backed PDF builds."""

    latex_config: LaTeXConfig
    engine_kind: EngineKind = EngineKind.LATEX

    def diagnostic_details(self) -> str:
        """Format resolved LaTeX PDF build details for debug diagnostics."""
        return "\n".join([str(self.doc_config), str(self.latex_config)])

    def build_error_details(self) -> str:
        """Format LaTeX-specific details for unexpected build errors."""
        return str(self.latex_config)
