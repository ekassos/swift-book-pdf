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

from swift_book_pdf.pdf.config import EngineKind, PDFConfig
from swift_book_pdf.pdf.latex.fonts.resolver import LaTeXFontConfig

DEFAULT_TYPESETS = 4


@dataclass(frozen=True, kw_only=True)
class LaTeXConfig:
    """Resolved LaTeX backend configuration."""

    font_config: LaTeXFontConfig
    """Resolved font names used by LuaLaTeX."""

    typesets: int = DEFAULT_TYPESETS
    """Number of LuaLaTeX typeset passes to run."""

    def __post_init__(self) -> None:
        """Validate the resolved LaTeX configuration.

        Raises:
            ValueError: If `typesets` is not positive.
        """
        if self.typesets <= 0:
            raise ValueError("Typesets must be a positive integer.")

    def diagnostic_details(self) -> str:
        """Format resolved LaTeX backend details for diagnostics.

        Returns:
            Human-readable LaTeX backend details.
        """
        return "\n".join(
            [
                f"Typesets: {self.typesets}",
                self.font_config.diagnostic_details().rstrip(),
            ]
        )


@dataclass(frozen=True, kw_only=True)
class LaTeXPDFConfig(PDFConfig):
    """Resolved configuration for LaTeX-backed PDF builds."""

    latex_config: LaTeXConfig
    """Resolved LaTeX backend configuration."""

    engine_kind: EngineKind = EngineKind.LATEX
    """PDF engine implementation."""

    def diagnostic_details(self) -> str:
        """Format resolved LaTeX PDF build details for debug diagnostics.

        Returns:
            Human-readable PDF and LaTeX details.
        """
        return "\n".join(
            [
                super().diagnostic_details(),
                self.latex_config.diagnostic_details(),
            ]
        )

    def build_error_details(self) -> str:
        """Format LaTeX-specific details for unexpected build errors.

        Returns:
            Human-readable LaTeX backend details.
        """
        return self.latex_config.diagnostic_details()
