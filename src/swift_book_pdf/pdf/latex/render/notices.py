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

"""Render the generated notices chapter as LaTeX."""

from swift_book_pdf.core.generated.notices.content import (
    APACHE_LICENSE_V2_TEXT,
    SWIFT_BOOK_PDF_REPO_URL,
    SWIFT_BOOK_REPO_URL,
    SWIFT_CONTRIBUTORS_URL,
    SWIFT_DOCC_RENDER_NOTICE_TEXT,
    SWIFT_DOCC_RENDER_REPO_URL,
    SWIFT_LICENSE_URL,
    format_copyright_year_range,
)
from swift_book_pdf.core.generated.notices.metadata import (
    NOTICES_DOC_KEY,
    NOTICES_DOC_SUBTITLE,
    NOTICES_DOC_TITLE,
)
from swift_book_pdf.pdf.latex.render.chapter import generate_chapter_title
from swift_book_pdf.pdf.latex.render.code_spans import convert_inline_code
from swift_book_pdf.pdf.latex.render.inline import apply_formatting
from swift_book_pdf.pdf.options import RenderingMode


def render_notices_latex(
    mode: RenderingMode,
    year_range: tuple[int, int] | None = None,
) -> str:
    """Render the generated notices chapter for the PDF backend.

    Args:
        mode: PDF rendering mode, used to decide whether named URLs should
            become hyperlinks.
        year_range: Optional inclusive copyright years detected from the
            upstream Swift Book source.

    Returns:
        LaTeX for the full generated notices chapter.
    """
    title_box, _ = generate_chapter_title(
        [f"# {NOTICES_DOC_TITLE}", "", NOTICES_DOC_SUBTITLE],
        NOTICES_DOC_KEY,
    )
    license_reference = (
        f"[{SWIFT_LICENSE_URL}]({SWIFT_LICENSE_URL})"
        if mode == RenderingMode.DIGITAL
        else SWIFT_LICENSE_URL
    )
    contributors_reference = (
        f"[{SWIFT_CONTRIBUTORS_URL}]({SWIFT_CONTRIBUTORS_URL})"
        if mode == RenderingMode.DIGITAL
        else SWIFT_CONTRIBUTORS_URL
    )
    original_work_copyright = _build_original_work_copyright_sentence(
        year_range
    )
    paragraphs = [
        "This edition of *The Swift Programming Language* was generated "
        f"using [*swift-book-pdf*]({SWIFT_BOOK_PDF_REPO_URL}). The PDF layout, typography, and "
        "rendering pipeline for this edition are provided by "
        "*swift-book-pdf*. *swift-book-pdf* is Copyright \\textcopyright{} 2025-2026 "
        "Evangelos Kassos and is licensed under the Apache License, "
        "Version 2.0.",
        "This edition is derived from the *swift-book* source and is a "
        "modified version of the original work, converted and formatted "
        "for distribution. `chapter-icon.png` and `chapter-icon~dark.png` are "
        "derived from Swift's *swift-docc-render* project.",
        f"The [*swift-book*]({SWIFT_BOOK_REPO_URL}) and [*swift-docc-render*]({SWIFT_DOCC_RENDER_REPO_URL}) "
        "repositories are part of the Swift.org open source project, which "
        "is licensed under the Apache License, Version 2.0 with Runtime "
        "Library Exception. "
        f"See {license_reference} for details. "
        f"{original_work_copyright} "
        "The Swift project authors are credited at "
        f"{contributors_reference}.",
        "Swift and the Swift logo are trademarks of Apple Inc. This edition is not "
        "published by, endorsed by, or affiliated with Apple Inc. or the "
        "Swift.org open source project.",
    ]

    latex_lines = [title_box, "", "{\\BodyStyle\n"]
    latex_lines.extend(
        "\\ParagraphStyle{"
        + apply_formatting(convert_inline_code(paragraph), mode)
        + "}\n"
        for paragraph in paragraphs
    )
    latex_lines.append(
        "\\SectionHeader{Apache License 2.0 and Related Notices}"
        f"{{{NOTICES_DOC_KEY}_apache-license-20_and_related_notices}}\n"
    )
    latex_lines.extend(
        _render_latex_preformatted_block(
            APACHE_LICENSE_V2_TEXT + "\n\n\n" + SWIFT_DOCC_RENDER_NOTICE_TEXT
        )
    )
    latex_lines.append("}\n\\newpage\n")
    return "\n".join(latex_lines)


def _build_original_work_copyright_sentence(
    year_range: tuple[int, int] | None,
) -> str:
    """Build the LaTeX-ready copyright sentence for upstream Swift sources."""
    year_text = format_copyright_year_range(year_range)
    if year_text:
        return (
            r"*swift-book* is Copyright \textcopyright{} "
            f"{year_text} Apple Inc. and the Swift project authors "
            r"and *swift-docc-render* is Copyright \textcopyright{} "
            "2021-2025 Apple Inc. and the Swift project authors."
        )
    return (
        r"*swift-book* is Copyright \textcopyright{} Apple Inc. "
        "and the Swift project authors and *swift-docc-render* is "
        r"Copyright \textcopyright{} 2021-2025 Apple Inc. "
        "and the Swift project authors."
    )


def _render_latex_preformatted_block(text: str) -> list[str]:
    """Render preformatted notice text in the PDF plain-listing box."""
    lines = ["\\parskip=0pt\n" + r"\begin{flushleft}\begin{plainlistingbox}"]
    lines.extend(text.splitlines())
    lines.append(r"\end{plainlistingbox}" + "\n\\end{flushleft}\n")
    return lines
