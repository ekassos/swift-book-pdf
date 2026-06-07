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

"""Shared state for LaTeX block rendering."""

from dataclasses import dataclass

from swift_book_pdf.pdf.config import Appearance, RenderingMode
from swift_book_pdf.pdf.latex.render.inline import DocReferenceResolver


@dataclass(frozen=True)
class LaTeXRenderContext:
    """Backend state needed while rendering parsed blocks as LaTeX."""

    file_name: str
    """Current document key used in labels."""

    assets_dir: str
    """Directory containing Swift Book image assets."""

    mode: RenderingMode
    """PDF rendering mode."""

    appearance: Appearance
    """PDF color appearance."""

    main_font: str
    """Resolved main text font."""

    body_font_size: float
    """Base paragraph font size in points."""

    doc_references: DocReferenceResolver | None = None
    """Optional resolver for subset-build document references."""
