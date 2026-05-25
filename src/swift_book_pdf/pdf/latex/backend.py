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

"""LaTeX PDF backend configuration adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from swift_book_pdf.pdf.config import EngineKind, PDFConfig
from swift_book_pdf.pdf.latex.config import LaTeXConfig, LaTeXPDFConfig
from swift_book_pdf.pdf.latex.fonts.resolver import resolve_for_latex

if TYPE_CHECKING:
    from swift_book_pdf.pdf.backend import PDFBackendConfigInput


class LaTeXBackend:
    """LaTeX backend adapter for resolved PDF config construction."""

    kind = EngineKind.LATEX

    def build_config(self, config_input: PDFBackendConfigInput) -> PDFConfig:
        """Build a LaTeX-backed PDF configuration.

        Args:
            config_input: Shared PDF config inputs and LaTeX CLI options.

        Returns:
            Resolved LaTeX-backed PDF configuration.
        """
        backend_options = config_input.backend_options
        font_config = resolve_for_latex(backend_options)
        latex_config = LaTeXConfig(
            font_config=font_config,
            typesets=int(backend_options["typesets"]),
        )
        return LaTeXPDFConfig(
            source=config_input.source,
            output_path=config_input.output_path,
            dangerously_skip_legal_notices=(
                config_input.dangerously_skip_legal_notices
            ),
            doc_config=config_input.doc_config,
            latex_config=latex_config,
            override_version=config_input.override_version,
        )
