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

"""LaTeX page geometry helpers."""

from swift_book_pdf.pdf.config import PaperSize
from swift_book_pdf.pdf.latex.styling.typography import get_css_dimension


def get_geometry_opts(
    paper_size: PaperSize,
    gutter: bool = True,
    body_font_size: float | None = None,
) -> str:
    """Return LaTeX geometry options for the requested page layout.

    Args:
        paper_size: Output paper size.
        gutter: Whether to reserve extra inner margin for book binding.
        body_font_size: Base paragraph font size in PDF points.

    Returns:
        Comma-separated geometry package options.
    """
    if gutter:
        layout_margins = {
            PaperSize.A4: "inner=1.67in,outer=0.75in",
            PaperSize.LETTER: "inner=1.9in,outer=0.75in",
            PaperSize.LEGAL: "inner=1.9in,outer=0.75in",
        }[paper_size]
    else:
        if body_font_size is None:
            raise ValueError(
                "body_font_size is required for no-gutter geometry"
            )
        no_gutter_hmargin = get_css_dimension(
            "documentation_layout_full_width_container_padding_inline",
            body_font_size,
        )
        layout_margins = f"hmargin={no_gutter_hmargin}"

    return {
        PaperSize.A4: f"a4paper,{layout_margins}",
        PaperSize.LETTER: f"letterpaper,{layout_margins}",
        PaperSize.LEGAL: f"legalpaper,{layout_margins}",
    }[paper_size]
