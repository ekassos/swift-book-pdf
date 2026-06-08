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


from swift_book_pdf.pdf.config import DEFAULT_BODY_FONT_SIZE
from swift_book_pdf.pdf.latex.styling.typography import (
    compute_typography_variables,
)


def test_default_body_font_size_matches_docc_root_font() -> None:
    assert compute_typography_variables(DEFAULT_BODY_FONT_SIZE)[
        "font_style_body_font_size"
    ] == ("9.5625bp")


def test_default_line_height_and_code_padding_match_docc_css() -> None:
    variables = compute_typography_variables(DEFAULT_BODY_FONT_SIZE)

    assert variables["font_style_body_line_height"] == "14.0625bp"
    assert variables["code_block_style_elements_padding_block"] == "4.5bp"
    assert variables["code_block_style_elements_padding_inline"] == "7.875bp"


def test_article_route_tokens_match_docc_css() -> None:
    variables = compute_typography_variables(DEFAULT_BODY_FONT_SIZE)

    assert variables["article_hero_headline_font_size"] == "22.5bp"
    assert variables["article_hero_headline_line_height"] == "24.75bp"
    assert variables["article_hero_intro_font_size"] == "11.8125bp"
    assert variables["article_hero_intro_line_height"] == "16.3125bp"
    assert variables["article_hero_padding_top"] == "16.875bp"
    assert variables["article_hero_padding_bottom"] == "16.875bp"
    assert variables["spacing_stacked_margin_large"] == "7.65bp"
    assert variables["documentation_topic_title_margin_bottom"] == "6.75bp"
    assert variables["content_node_heading_2_font_size"] == "18bp"
    assert variables["content_node_heading_2_line_height"] == "22.5bp"
    assert variables["font_style_documentation_h4_font_size"] == "13.5bp"
    assert variables["font_style_documentation_h4_line_height"] == "15.75bp"


def test_heading_spacing_tracks_selector_specific_css_margins() -> None:
    variables = compute_typography_variables(DEFAULT_BODY_FONT_SIZE)

    assert (
        variables["content_node_paragraph_to_heading_2_margin_top"] == "28.8bp"
    )
    assert (
        variables["content_node_paragraph_to_heading_4_margin_top"] == "21.6bp"
    )
    assert (
        variables["content_node_paragraph_to_heading_3_margin_top"] == "21.6bp"
    )


def test_table_and_aside_spacing_match_docc_css() -> None:
    variables = compute_typography_variables(DEFAULT_BODY_FONT_SIZE)

    assert variables["aside_padding"] == "9bp"
    assert variables["aside_border_width_left"] == "3.375bp"
    assert variables["content_node_table_cell_padding"] == "5.625bp"
    assert variables["content_node_table_border_width"] == "0.5625bp"
