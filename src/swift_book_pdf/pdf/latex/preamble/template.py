# Copyright 2025-2026 Evangelos Kassos
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

"""LaTeX preamble template rendering."""

import logging

from swift_book_pdf.pdf.latex.config import LaTeXPDFConfig
from swift_book_pdf.pdf.latex.preamble.geometry import get_geometry_opts
from swift_book_pdf.pdf.latex.styling.colors import get_document_colors
from swift_book_pdf.pdf.latex.styling.typography import (
    compute_font_sizes,
    compute_spacing,
    compute_typography_variables,
    get_css_points,
)
from swift_book_pdf.pdf.latex.templating import load_latex_template

logger = logging.getLogger(__name__)


def generate_preamble(config: LaTeXPDFConfig) -> str:
    """Generate the LaTeX preamble for a resolved build configuration.

    Args:
        config: Resolved LaTeX-backed PDF build configuration.

    Returns:
        Rendered LaTeX preamble.
    """
    return PREAMBLE.substitute(**build_preamble_substitutions(config))


def build_preamble_substitutions(
    config: LaTeXPDFConfig,
) -> dict[str, str]:
    """Compute the LaTeX preamble template substitutions.

    Args:
        config: Resolved LaTeX-backed PDF build configuration.

    Returns:
        Template substitution values for the preamble.
    """
    font_config = config.latex_config.font_config
    unicode_fallback = "\n".join(
        [f'      "{font}:mode=node;",' for font in font_config.unicode_fonts],
    )
    colors = get_document_colors(
        config.doc_config.mode, config.doc_config.appearance
    )

    ### PREVIOUSLY:
    ### TODO(ekassos): Remove this once we've transitioned to the new typography variables.
    _font_sizes = compute_font_sizes(config.doc_config.font_size)
    _spacing = compute_spacing(config.doc_config.font_size)
    _template_vars = {**_font_sizes, **_spacing}
    for key, value in sorted(_font_sizes.items()):
        logger.debug(f"{key}: {value}pt")
    for key, value in sorted(_spacing.items()):
        logger.debug(f"{key}: {value}")

    ### NEW:
    template_vars = compute_typography_variables(config.doc_config.font_size)
    ### TODO(ekassos): Remove this once we've transitioned to the new typography variables.
    template_vars = {**template_vars, **_template_vars}
    code_block_font_size = get_css_points(
        "font_style_documentation_code_listing_font_size",
        config.doc_config.font_size,
    )
    template_vars["breakindent_minted"] = f"{3.8 * code_block_font_size:.2f}bp"

    for key, value in sorted(template_vars.items()):
        logger.debug(f"{key}: {value}")

    header_footer_hero = _render_header_footer_hero(
        font_config.header_footer_font,
        template_vars,
        config.doc_config.gutter,
    )
    return {
        "color_text_background": colors.color_text_background,
        "color_text": colors.color_text,
        "color_article_background": colors.color_article_background,
        "color_header_footer_background": (
            colors.color_header_footer_background
        ),
        "color_header_footer_text": colors.color_header_footer_text,
        "color_link": colors.color_link,
        "color_grid": colors.color_grid,
        "color_code_background": colors.color_code_background,
        "color_code_plain": colors.color_code_plain,
        "color_aside_note_background": colors.color_aside_note_background,
        "color_aside_note_border": colors.color_aside_note_border,
        "color_aside_note": colors.color_aside_note,
        "code_style": colors.code_style,
        "geometry_opts": get_geometry_opts(
            config.doc_config.paper_size,
            config.doc_config.gutter,
        ),
        "fancyhead_fancyfoot_hero": header_footer_hero,
        "main_font": font_config.main_font,
        "mono_font": font_config.mono_font,
        "emoji_font": font_config.emoji_font,
        "unicode_font": unicode_fallback,
        "header_footer_font": font_config.header_footer_font,
        **template_vars,
    }


def _render_header_footer_hero(
    header_footer_font: str,
    template_vars: dict[str, str],
    gutter: bool,
) -> str:
    """Render the header/footer hero template variant.

    Args:
        header_footer_font: Font family used in headers and footers.
        template_vars: Shared preamble typography substitutions.
        gutter: Whether the gutter-aware header/footer template should be used.

    Returns:
        Rendered header/footer hero LaTeX.
    """
    if gutter:
        return HEADER_FOOTER_HERO_WITH_GUTTER.substitute(
            header_footer_font=header_footer_font,
            **template_vars,
        )
    return HEADER_FOOTER_HERO_NO_GUTTER.substitute(
        header_footer_font=header_footer_font,
        **template_vars,
    )


HEADER_FOOTER_HERO_WITH_GUTTER = load_latex_template(
    "header_footer_hero_with_gutter.tex"
)
HEADER_FOOTER_HERO_NO_GUTTER = load_latex_template(
    "header_footer_hero_no_gutter.tex"
)
PREAMBLE = load_latex_template("preamble.tex")
