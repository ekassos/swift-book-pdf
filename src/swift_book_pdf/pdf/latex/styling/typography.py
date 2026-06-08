# Copyright 2026 Evangelos Kassos
#
# Portions derived from swift-docc-render:
#   Copyright (c) 2021-2025 Apple Inc. and the Swift project authors
#   Licensed under Apache License v2.0 with Runtime Library Exception
#
#   See https://swift.org/LICENSE.txt for details.
#   The Swift project authors are credited at https://swift.org/CONTRIBUTORS.txt.
#   See THIRD-PARTY-NOTICES.txt for details.
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

"""DocC Render lengths converted to LaTeX PDF dimensions."""

from swift_book_pdf.pdf.config import DEFAULT_BODY_FONT_SIZE

CSS_ROOT_FONT_SIZE_PX = 17.0
CSS_POINT_PER_PX = 0.75
DOCC_PDF_SCALE = 0.75
LATEX_PDF_POINT_UNIT = "bp"

DOCC_RENDER_LENGTHS = {
    "font_style_body_font_size": "1rem",
    "font_style_body_line_height": "25px",
    "pdf_footnote_font_size": "14px",
    "pdf_footnote_line_height": "14px",
    "article_hero_headline_font_size": "40px",
    "article_hero_headline_line_height": "44px",
    "article_hero_intro_font_size": "21px",
    "article_hero_intro_line_height": "29px",
    "article_hero_padding_top": "30px",
    "article_hero_padding_bottom": "30px",
    "documentation_layout_full_width_container_padding_inline": "80px",
    "documentation_topic_title_margin_bottom": "12px",
    "documentation_topic_content_table_title_font_size": "32px",
    "documentation_topic_content_table_title_line_height": "36px",
    "documentation_topic_content_table_section_padding_top": "2.353rem",
    "documentation_topic_content_table_section_title_font_size": "24px",
    "documentation_topic_content_table_section_title_line_height": "28px",
    "documentation_topic_topics_link_block_margin_top": "15px",
    "documentation_topic_topics_link_block_has_adjacent_elements_padding_top": "5px",
    "documentation_topic_topics_link_block_has_adjacent_elements_padding_bottom": "5px",
    "documentation_topic_topic_link_icon_width": "1.294rem",
    "documentation_topic_topic_link_icon_spacing": "1rem",
    "documentation_topic_topic_icon_wrapper_height": "25px",
    "documentation_topic_topic_link_icon_height": "15px",
    "content_node_heading_2_font_size": "32px",
    "content_node_heading_2_line_height": "40px",
    "font_style_documentation_h3_font_size": "28px",
    "font_style_documentation_h3_line_height": "32px",
    "font_style_documentation_h4_font_size": "24px",
    "font_style_documentation_h4_line_height": "28px",
    "content_node_code_voice_font_size": "1rem",
    "content_node_code_voice_line_height": "25px",
    "font_style_documentation_code_listing_font_size": "15px",
    "font_style_documentation_code_listing_line_height": "25px",
    "spacing_stacked_margin_small": "0.4em",
    "spacing_stacked_margin_large": "0.8em",
    "spacing_stacked_margin_xlarge": "1.6em",
    "article_stacked_margin_small": "20px",
    "article_stacked_margin_large": "40px",
    "content_node_paragraph_margin": "0px",
    "content_node_paragraph_to_content_margin_top": "0.8em",
    "content_node_heading_to_content_margin_top": "0.8em",
    "content_node_paragraph_to_heading_2_margin_top": "51.2px",
    "content_node_paragraph_to_heading_3_margin_top": "38.4px",
    "content_node_paragraph_to_heading_4_margin_top": "38.4px",
    "content_node_code_listing_to_documentation_h2_margin_top": "51.2px",
    "content_node_aside_to_documentation_h2_margin_top": "51.2px",
    "content_node_code_listing_to_documentation_h3_margin_top": "44.8px",
    "content_node_aside_to_documentation_h3_margin_top": "44.8px",
    "content_node_code_listing_to_documentation_h4_margin_top": "38.4px",
    "content_node_aside_to_documentation_h4_margin_top": "38.4px",
    "documentation_topic_content_node_code_listing_margin_top": "1.6em",
    "documentation_topic_content_node_inline_image_container_margin_top": "1.6em",
    "documentation_topic_content_node_aside_margin_top": "1.6em",
    "documentation_topic_content_node_aside_code_listing_margin_top": "1.6em",
    "documentation_topic_content_node_term_list_margin_top": "0.8em",
    "documentation_topic_content_node_term_list_term_margin_top": "0.8em",
    "documentation_topic_content_node_term_list_definition_margin_left": "2em",
    "content_node_heading_overlap_adjust": "0px",
    "code_block_style_elements_padding_block": "8px",
    "code_block_style_elements_padding_inline": "14px",
    "content_node_code_listing_border_width": "1px",
    "aside_border_width_left": "6px",
    "aside_padding": "16px",
    "border_radius": "4px",
    "documentation_topic_content_node_list_margin_top": "0.8em",
    "documentation_topic_content_node_list_margin_inline_start": "20px",
    "documentation_topic_content_node_list_item_margin_top": "0.8em",
    "documentation_topic_content_node_ordered_list_margin_top": "0.8em",
    "documentation_topic_content_node_ordered_list_margin_inline_start": "20px",
    "documentation_topic_content_node_ordered_list_item_margin_top": "0.8em",
    "content_node_table_wrapper_margin_top": "1.6em",
    "content_node_table_cell_padding": "10px",
    "content_node_table_border_width": "1px",
}


def css_length_to_px(css_length: str) -> float:
    """Convert a CSS px/rem/em length into CSS pixels.

    Args:
        css_length: CSS length using the supported `px`, `rem`, or `em` unit.

    Returns:
        Length converted to CSS pixels.

    Raises:
        ValueError: If the CSS unit is unsupported.
    """
    if css_length.endswith("px"):
        return float(css_length.removesuffix("px"))
    if css_length.endswith("rem"):
        return float(css_length.removesuffix("rem")) * CSS_ROOT_FONT_SIZE_PX
    if css_length.endswith("em"):
        return float(css_length.removesuffix("em")) * CSS_ROOT_FONT_SIZE_PX
    raise ValueError(f"Unsupported CSS typography unit: {css_length}")


def css_px_to_pdf_points(css_px: float, body_font_size: float) -> float:
    """Convert DocC CSS pixels to scaled PDF points.

    Args:
        css_px: Source DocC CSS pixel value.
        body_font_size: Base paragraph font size in PDF points.

    Returns:
        Scaled PDF point value.
    """
    return (
        css_px
        * CSS_POINT_PER_PX
        * DOCC_PDF_SCALE
        * _scale_factor(body_font_size)
    )


def get_css_points(name: str, body_font_size: float) -> float:
    """Return a CSS typography length converted to PDF points.

    Args:
        name: CSS typography length key.
        body_font_size: Base paragraph font size in PDF points.

    Returns:
        Scaled PDF point value.
    """
    return css_px_to_pdf_points(
        css_length_to_px(DOCC_RENDER_LENGTHS[name]), body_font_size
    )


def get_css_dimension(name: str, body_font_size: float) -> str:
    """Return a CSS typography length as a LaTeX `bp` dimension.

    Args:
        name: CSS typography length key.
        body_font_size: Base paragraph font size in PDF points.

    Returns:
        Scaled PDF dimension formatted for LaTeX.
    """
    return format_dimension(
        get_css_points(name, body_font_size), LATEX_PDF_POINT_UNIT
    )


def _scale_factor(body_font_size: float) -> float:
    """Compute the proportional scale for a body font size.

    Args:
        body_font_size: Base paragraph font size in PDF points.

    Returns:
        Scale relative to the default body font size.
    """
    return body_font_size / DEFAULT_BODY_FONT_SIZE


def format_number(value: float) -> str:
    """Format a numeric LaTeX value.

    Args:
        value: Numeric value.

    Returns:
        Value without unnecessary trailing zeros.
    """
    rounded = round(value, 4)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.4f}".rstrip("0")


def format_dimension(value: float, unit: str) -> str:
    """Format a dimension value with its unit for LaTeX.

    Args:
        value: Numeric dimension value.
        unit: LaTeX dimension unit.

    Returns:
        Dimension string without unnecessary trailing zeros.
    """
    return f"{format_number(value)}{unit}"


def compute_typography_variables(body_font_size: float) -> dict[str, str]:
    """Compute DocC Render-shaped variables for LaTeX templates.

    Args:
        body_font_size: Base paragraph font size in PDF points.

    Returns:
        Template variables keyed by DocC Render role names in snake case.
    """
    return {
        key: get_css_dimension(key, body_font_size)
        for key in DOCC_RENDER_LENGTHS
    }
