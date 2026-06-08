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

from swift_book_pdf.core.source import ChapterMetadata
from swift_book_pdf.pdf.config import Appearance, RenderingMode
from swift_book_pdf.pdf.latex.render.toc import (
    apply_toc_latex_overrides,
    replace_chapter_href_with_toc_item,
)


def test_toc_chapter_icon_uses_em_based_width_in_digital_mode() -> None:
    lines = [
        r"\item \DocCSuppressNextTopMargin",
        r"\begin{DocCContentListItemParagraph}",
        r"\fallbackrefdigital{guidedtour}",
        r"\end{DocCContentListItemParagraph}",
    ]
    metadata = {
        "guidedtour": ChapterMetadata(subtitle_line="A quick start."),
    }

    rendered = replace_chapter_href_with_toc_item(
        lines,
        metadata,
        RenderingMode.DIGITAL,
        Appearance.LIGHT,
    )

    assert r"\DocCTopicLinkBlock{chapter-icon.png}" in rendered[0]
    assert r"\fallbackrefdigital{guidedtour}" not in rendered[0]
    assert r"\fallbackrefbook{guidedtour}" not in rendered[0]
    assert r"\nameref{guidedtour}" in rendered[0]
    assert r"\pageref{guidedtour}" not in rendered[0]
    assert "0.1in" not in rendered[0]


def test_toc_chapter_icon_uses_dark_asset_in_print_mode() -> None:
    lines = [
        r"\item \DocCSuppressNextTopMargin",
        r"\begin{DocCContentListItemParagraph}",
        r"\fallbackrefbook{guidedtour}",
        r"\end{DocCContentListItemParagraph}",
    ]
    metadata = {
        "guidedtour": ChapterMetadata(subtitle_line="A quick start."),
    }

    rendered = replace_chapter_href_with_toc_item(
        lines,
        metadata,
        RenderingMode.PRINT,
        Appearance.DARK,
    )

    assert r"\DocCTopicLinkBlock{chapter-icon~dark.png}" in rendered[0]
    assert r"\fallbackrefdigital{guidedtour}" not in rendered[0]
    assert r"\fallbackrefbook{guidedtour}" not in rendered[0]
    assert r"\nameref{guidedtour}" in rendered[0]
    assert r"\pageref{guidedtour}" in rendered[0]


def test_toc_topic_links_remove_generic_list_spacing_wrappers() -> None:
    lines = [
        r"\DocCDocumentationTopicContentNodeListBefore",
        r"\begin{itemize}",
        r"\item \DocCSuppressNextTopMargin",
        r"\begin{DocCContentListItemParagraph}",
        r"\fallbackrefdigital{guidedtour}",
        r"\end{DocCContentListItemParagraph}",
        r"\DocCContentNodeListItemBefore",
        r"\item \DocCSuppressNextTopMargin",
        r"\begin{DocCContentListItemParagraph}",
        r"\fallbackrefdigital{thebasics}",
        r"\end{DocCContentListItemParagraph}",
        r"\end{itemize}",
        r"\DocCDocumentationTopicContentNodeListAfter",
    ]
    metadata = {
        "guidedtour": ChapterMetadata(subtitle_line="Explore Swift."),
        "thebasics": ChapterMetadata(subtitle_line="Write basic syntax."),
    }

    rendered = "\n".join(
        apply_toc_latex_overrides(
            lines,
            metadata,
            RenderingMode.DIGITAL,
            Appearance.LIGHT,
        )
    )

    assert r"\DocCDocumentationTopicContentNodeListBefore" not in rendered
    assert r"\DocCDocumentationTopicContentNodeListAfter" not in rendered
    assert r"\DocCContentNodeListItemBefore" not in rendered
    assert r"\DocCContentListItemParagraph" not in rendered
    assert r"\begin{DocCTopicLinkBlockList}" in rendered
    assert (
        r"\DocCTopicLinkBlock{chapter-icon.png}{\nameref{guidedtour}}"
        in rendered
    )
    assert (
        r"\DocCTopicLinkBlock{chapter-icon.png}{\nameref{thebasics}}"
        in rendered
    )


def test_toc_only_mode_uses_static_chapter_titles() -> None:
    lines = [
        "\\item \\begin{DocCContentListItemParagraph}\n"
        "\\fallbackrefdigital{guidedtour}\n"
        "\\end{DocCContentListItemParagraph}"
    ]
    metadata = {
        "guidedtour": ChapterMetadata(
            header_line="A Guided Tour",
            subtitle_line="A quick start.",
        ),
    }

    rendered = replace_chapter_href_with_toc_item(
        lines,
        metadata,
        RenderingMode.DIGITAL,
        Appearance.LIGHT,
        resolve_references=False,
    )

    assert rendered[0] == (
        r"\DocCTopicLinkBlock{chapter-icon.png}"
        r"{A Guided Tour}{A quick start.}"
    )
    assert r"\nameref{guidedtour}" not in rendered[0]
    assert "??" not in rendered[0]


def test_toc_overrides_convert_generated_topic_link_list_items() -> None:
    rendered = apply_toc_latex_overrides(
        [
            r"\begin{itemize}",
            "\\item \\begin{DocCContentListItemParagraph}\n"
            "\\fallbackrefdigital{guidedtour}\n"
            "\\end{DocCContentListItemParagraph}",
            r"\end{itemize}",
        ],
        {
            "guidedtour": ChapterMetadata(
                header_line="A Guided Tour",
                subtitle_line="A quick start.",
            )
        },
        RenderingMode.DIGITAL,
        Appearance.LIGHT,
        resolve_references=False,
    )

    assert rendered == [
        r"\begin{DocCTopicLinkBlockList}",
        (
            r"\DocCTopicLinkBlock{chapter-icon.png}"
            r"{A Guided Tour}{A quick start.}"
        ),
        r"\end{DocCTopicLinkBlockList}",
    ]
    assert r"\item" not in "\n".join(rendered)


def test_toc_heading_overrides_use_tex_control_word_names() -> None:
    rendered = apply_toc_latex_overrides(
        [
            r"\DocCContentNodeHeadingTwo{Topics}{topics}",
            r"\DocCContentNodeHeadingThree{Welcome}{welcome}",
            r"\DocCContentNodeHeadingFour{Details}{details}",
        ],
        {},
        RenderingMode.DIGITAL,
        Appearance.LIGHT,
    )

    assert rendered[0] == r"\DocCContentNodeHeadingTwoTOC{Topics}{topics}"
    assert rendered[1] == r"\DocCContentNodeHeadingThreeTOC{Welcome}{welcome}"
    assert rendered[2] == r"\DocCContentNodeHeadingFour{Details}{details}"
    assert "Heading2" not in "\n".join(rendered)
    assert "Heading3" not in "\n".join(rendered)
    assert "Heading4" not in "\n".join(rendered)
