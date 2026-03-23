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

DEFAULT_BODY_FONT_SIZE = 9.0

# Default font sizes in points (at body font size = 9pt).
#
# | Element          | Default  | Ratio  |
# |------------------|----------|--------|
# | Footnote         | 8pt      | 0.889x |
# | Title            | 22pt     | 2.444x |
# | Subtitle         | 11.07pt  | 1.230x |
# | Body             | 9pt      | 1.000x |
# | Section (h1)     | 22pt     | 2.444x |
# | Subsection (h2)  | 16.88pt  | 1.876x |
# | Subsubsection    | 14.77pt  | 1.641x |
# | Paragraph (h4)   | 12.66pt  | 1.407x |
# | Code             | 9pt      | 1.000x |
# | Minted code      | 7.9pt    | 0.878x |
# | Minted leading   | 13.2pt   | 1.467x |
#
DEFAULT_FONT_SIZES = {
    "footnote": 8.0,
    "title": 22.0,
    "subtitle": 11.07,
    "body": 9.0,
    "section": 22.0,
    "subsection": 16.88,
    "subsubsection": 14.77,
    "paragraph": 12.66,
    "code": 9.0,
    "minted": 7.9,
    "minted_leading": 13.2,
}

# Default spacing values (at body font size = 9pt).
# All values scale proportionally with the body font size.
#
# | Element                     | Default  |
# |-----------------------------|----------|
# | Footnote separator          | 9pt      |
# | Paragraph skip              | 0.09in   |
# | Code paragraph skip         | 7pt      |
# | Paragraph after box/note    | 0.12in   |
# | Section adjust (negative)   | 0.09in   |
# | Section before              | 0.4in    |
# | Section after               | 0.1in    |
# | Subsection before           | 0.41in   |
# | Subsection before (para)    | 0.44in   |
# | Heading after               | 0.16in   |
# | TOC section after           | 0.20in   |
# | Subsubsection before        | 0.35in   |
# | Subsubsection before (para) | 0.37in   |
# | TOC adjust (negative)       | 0.15in   |
# | Paragraph before            | 0.32in   |
# | Paragraph before (para)     | 0.34in   |
# | Code box top/bottom         | 0.05in   |
# | Code box left/right         | 0.10in   |
# | Box before (preceded)       | 0.19in   |
# | Box before                  | 0.21in   |
# | Aside left padding          | 8.8pt    |
# | Aside padding (r/t/b)       | 8pt      |
# | List item spacing           | 0.02in   |
# | Hero top                    | 0.4in    |
# | Hero bottom                 | 0.28in   |
# | Baselineskip (title)        | 14.4pt   |
# | Baselineskip (subtitle)     | 14.4pt   |
# | Baselineskip (body)         | 13.8pt   |
# | Baselineskip (section)      | 18.0pt   |
# | Baselineskip (subsection)   | 20.7pt   |
# | Baselineskip (subsubsection)| 20.7pt   |
# | Baselineskip (paragraph)    | 20.7pt   |
# | Baselineskip (code)         | 15.18pt  |
# | Baselineskip (table)        | 15.87pt  |
#
DEFAULT_SPACING: dict[str, tuple[float, str]] = {
    "footnotesep": (9.0, "pt"),
    "parskip": (0.09, "in"),
    "code_parskip": (7.0, "pt"),
    "para_after_box": (0.12, "in"),
    "section_adjust": (0.09, "in"),
    "section_before": (0.4, "in"),
    "section_after": (0.1, "in"),
    "subsection_before": (0.41, "in"),
    "subsection_before_para": (0.44, "in"),
    "heading_after": (0.16, "in"),
    "toc_section_after": (0.20, "in"),
    "subsubsection_before": (0.35, "in"),
    "subsubsection_before_para": (0.37, "in"),
    "toc_adjust": (0.15, "in"),
    "paragraph_before": (0.32, "in"),
    "paragraph_before_para": (0.34, "in"),
    "code_box_tb": (0.05, "in"),
    "code_box_lr": (0.10, "in"),
    "box_before_preceded": (0.19, "in"),
    "box_before": (0.21, "in"),
    "aside_left": (8.8, "pt"),
    "aside_pad": (8.0, "pt"),
    "list_itemsep": (0.02, "in"),
    "hero_top": (0.4, "in"),
    "hero_bottom": (0.28, "in"),
    "baselineskip_title": (14.4, "pt"),
    "baselineskip_subtitle": (14.4, "pt"),
    "baselineskip_body": (13.8, "pt"),
    "baselineskip_section": (18.0, "pt"),
    "baselineskip_subsection": (20.7, "pt"),
    "baselineskip_subsubsection": (20.7, "pt"),
    "baselineskip_paragraph": (20.7, "pt"),
    "baselineskip_code": (15.18, "pt"),
    "baselineskip_table": (15.87, "pt"),
}


def _scale_factor(body_font_size: float) -> float:
    return body_font_size / DEFAULT_BODY_FONT_SIZE


def format_pt(value: float) -> str:
    """Format a font size value for LaTeX, removing unnecessary trailing zeros."""
    rounded = round(value, 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.2f}".rstrip("0")


def format_dimension(value: float, unit: str) -> str:
    """Format a dimension value with its unit for LaTeX."""
    rounded = round(value, 4)
    if rounded == int(rounded):
        return f"{int(rounded)}{unit}"
    formatted = f"{rounded:.4f}".rstrip("0").rstrip(".")
    return f"{formatted}{unit}"


def get_font_size(name: str, body_font_size: float) -> str:
    return format_pt(DEFAULT_FONT_SIZES[name] * _scale_factor(body_font_size))


def get_spacing(name: str, body_font_size: float) -> str:
    value, unit = DEFAULT_SPACING[name]
    return format_dimension(value * _scale_factor(body_font_size), unit)


def compute_font_sizes(body_font_size: float) -> dict[str, str]:
    """Compute all font sizes scaled proportionally from the body font size."""
    return {
        f"font_size_{key}": get_font_size(key, body_font_size)
        for key in DEFAULT_FONT_SIZES
    }


def compute_spacing(body_font_size: float) -> dict[str, str]:
    """Compute all spacing values scaled proportionally from the body font size."""
    return {
        f"spacing_{key}": get_spacing(key, body_font_size)
        for key in DEFAULT_SPACING
    }
