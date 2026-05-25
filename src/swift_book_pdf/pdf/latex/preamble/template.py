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

import logging

from swift_book_pdf.pdf.config import PDFConfig
from swift_book_pdf.pdf.latex.preamble.geometry import get_geometry_opts
from swift_book_pdf.pdf.latex.templating import load_latex_template
from swift_book_pdf.pdf.styling.colors import get_document_colors
from swift_book_pdf.pdf.styling.typography import (
    compute_font_sizes,
    compute_spacing,
)

logger = logging.getLogger(__name__)


def generate_preamble(config: PDFConfig) -> str:
    unicode_fallback = "\n".join(
        [
            f'      "{font}:mode=node;",'
            for font in config.font_config.unicode_font_list
        ],
    )
    colors = get_document_colors(
        config.doc_config.mode, config.doc_config.appearance
    )
    font_sizes = compute_font_sizes(config.doc_config.font_size)
    spacing = compute_spacing(config.doc_config.font_size)
    template_vars = {**font_sizes, **spacing}
    template_vars["breakindent_minted"] = (
        f"{3.8 * float(template_vars['font_size_minted']):.2f}pt"
    )
    for key, value in sorted(font_sizes.items()):
        logger.debug(f"{key}: {value}pt")
    for key, value in sorted(spacing.items()):
        logger.debug(f"{key}: {value}")
    return PREAMBLE.substitute(
        background=colors.background,
        text=colors.text,
        header_background=colors.header_background,
        header_text=colors.header_text,
        hero_background=colors.hero_background,
        hero_text=colors.hero_text,
        link=colors.link,
        aside_background=colors.aside_background,
        aside_text=colors.aside_text,
        aside_border=colors.aside_border,
        table_border=colors.table_border,
        code_border=colors.code_border,
        code_background=colors.code_background,
        code_style=colors.code_style,
        geometry_opts=get_geometry_opts(
            config.doc_config.paper_size,
            config.doc_config.gutter,
        ),
        main_font=config.font_config.main_font,
        mono_font=config.font_config.mono_font,
        emoji_font=config.font_config.emoji_font,
        unicode_font=unicode_fallback,
        header_footer_font=config.font_config.header_footer_font,
        fancyhead_fancyfoot_hero=(
            HEADER_FOOTER_HERO_WITH_GUTTER.substitute(
                header_footer_font=config.font_config.header_footer_font,
                **template_vars,
            )
            if config.doc_config.gutter
            else HEADER_FOOTER_HERO_NO_GUTTER.substitute(
                header_footer_font=config.font_config.header_footer_font,
                **template_vars,
            )
        ),
        **template_vars,
    )


HEADER_FOOTER_HERO_WITH_GUTTER = load_latex_template(
    "header_footer_hero_with_gutter.tex"
)
HEADER_FOOTER_HERO_NO_GUTTER = load_latex_template(
    "header_footer_hero_no_gutter.tex"
)
PREAMBLE = load_latex_template("preamble.tex")
