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

from __future__ import annotations

import html

from swift_book_pdf.latex_helpers import (
    apply_formatting,
    convert_inline_code,
    generate_chapter_title,
)
from swift_book_pdf.schema import ChapterMetadata, RenderingMode

NOTICES_DOC_TAG = "CopyrightAndNotices"
NOTICES_DOC_KEY = NOTICES_DOC_TAG.lower()
NOTICES_DOC_TITLE = "Acknowledgments"
NOTICES_DOC_SUBTITLE = "Review notices about this edition."
NOTICES_SECTION_TITLE = "About This Edition"
NOTICES_DOC_FILE_NAME = "Trademarks.xhtml"
NOTICES_SECTION_ID = "copyright-and-notices"
COPYRIGHT_PLACEHOLDER = "[[COPYRIGHT]]"

SWIFT_LICENSE_URL = "https://swift.org/LICENSE.txt"
SWIFT_CONTRIBUTORS_URL = "https://swift.org/CONTRIBUTORS.txt"
SWIFT_BOOK_REPO_URL = "https://github.com/swiftlang/swift-book"
SWIFT_DOCC_RENDER_REPO_URL = "https://github.com/swiftlang/swift-docc-render"
SWIFT_BOOK_PDF_REPO_URL = "https://github.com/ekassos/swift-book-pdf"
APACHE_LICENSE_V2_URL = "https://www.apache.org/licenses/LICENSE-2.0"

APACHE_LICENSE_V2_TEXT = """                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

    TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

    1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

    2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

    3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

    4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

    5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

    6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

    7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

    8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

    9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

    END OF TERMS AND CONDITIONS

    APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

    Copyright [yyyy] [name of copyright owner]

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.



### Runtime Library Exception to the Apache 2.0 License: ###


    As an exception, if you use this Software to compile your source code and
    portions of this Software are embedded into the binary product as a result,
    you may redistribute such product without providing attribution as would
    otherwise be required by Sections 4(a), 4(b) and 4(d) of the License.
"""

SWIFT_DOCC_RENDER_NOTICE_TEXT = """                        The Swift-DocC-Render Project
                        =============================

Please visit the Swift-DocC-Render web site for more information:

  * https://github.com/swiftlang/swift-docc-render

Copyright (c) 2021 Apple Inc. and the Swift project authors

The Swift Project licenses this file to you under the Apache License, version
2.0 (the "License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

-------------------------------------------------------------------------------

This product depends on Vue.js.

  * LICENSE (MIT):
    * https://github.com/vuejs/vue/blob/dev/LICENSE
  * HOMEPAGE:
    * https://github.com/vuejs/vue

---

This product depends on vue-router.

  * LICENSE (MIT):
    * https://github.com/vuejs/vue-router/blob/dev/LICENSE
  * HOMEPAGE:
    * https://github.com/vuejs/vue-router

---

This product depends on core-js.

  * LICENSE (MIT):
    * https://github.com/zloirock/core-js/blob/master/LICENSE
  * HOMEPAGE:
    * https://github.com/zloirock/core-js

---

This product depends on Highlight.js.

  * LICENSE (BSD-3-Clause):
    * https://github.com/highlightjs/highlight.js/blob/main/LICENSE
  * HOMEPAGE:
    * https://github.com/highlightjs/highlight.js

---

This product depends on the IntersectionObserver polyfill.

  * LICENSE (W3C Software and Document):
    * https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document
  * HOMEPAGE:
    * https://github.com/w3c/IntersectionObserver/tree/main/polyfill

---

This product depends on PortalVue.

  * LICENSE (MIT):
    * https://github.com/LinusBorg/portal-vue/blob/develop/LICENCE
  * HOMEPAGE:
    * https://github.com/LinusBorg/portal-vue

---

This product depends on highlightjs-pkl.

  * LICENSE (Apache-2.0):
    * https://github.com/apple/highlightjs-pkl/blob/main/LICENSE.txt
  * HOMEPAGE:
    * https://github.com/apple/highlightjs-pkl
"""


def build_notices_chapter_metadata() -> ChapterMetadata:
    return ChapterMetadata(
        file_path=None,
        header_line=NOTICES_DOC_TITLE,
        subtitle_line=NOTICES_DOC_SUBTITLE,
    )


def build_notices_toc_lines(
    *, include_section_heading: bool = False
) -> list[str]:
    lines = ["\n"]
    if include_section_heading:
        lines.extend([f"### {NOTICES_SECTION_TITLE}\n", "\n"])
    lines.append(f"- <doc:{NOTICES_DOC_TAG}>\n")
    return lines


def format_year_range(year_range: tuple[int, int] | None) -> str:
    if year_range is None:
        return ""
    start_year, end_year = year_range
    if start_year == end_year:
        return str(start_year)
    return f"{start_year}-{end_year}"


def build_original_work_copyright_sentence(
    year_range: tuple[int, int] | None,
) -> str:
    year_text = format_year_range(year_range)
    if year_text:
        return (
            f"The original work is Copyright {COPYRIGHT_PLACEHOLDER} "
            f"{year_text} Apple Inc. and the Swift project authors."
        )
    return (
        f"The original work is Copyright {COPYRIGHT_PLACEHOLDER} Apple Inc. "
        "and the Swift project authors."
    )


def _render_copyright_for_xhtml(text: str) -> str:
    return text.replace(COPYRIGHT_PLACEHOLDER, "&#169;")


def _render_copyright_for_latex(text: str) -> str:
    return text.replace(COPYRIGHT_PLACEHOLDER, r"\textcopyright{}")


def render_notices_xhtml(
    title: str,
    year_range: tuple[int, int] | None = None,
) -> str:
    return (
        f'  <div class="section" id="{html.escape(NOTICES_SECTION_ID)}">\n'
        f"<h1>{html.escape(title)}</h1>\n"
        "<p>This edition of <em>The Swift Programming Language</em> was generated using "
        f'<a href="{html.escape(SWIFT_BOOK_PDF_REPO_URL)}"><em>swift-book-pdf</em></a>. '
        "This publication includes styling and supporting assets derived from <em>swift-book-pdf</em>. "
        "These materials are Copyright &#169; 2026 Evangelos Kassos and are licensed under the Apache License, Version 2.0.</p>"
        "<p>This edition is derived from the <em>swift-book</em> source and is a modified version "
        "of the original work, converted and formatted for distribution.</p>\n"
        "<p>The <em>swift-book</em> "
        f'<a href="{html.escape(SWIFT_BOOK_REPO_URL)}">repository</a> '
        "is part of the Swift.org open source project. The <em>swift-book</em> source is licensed under the Apache License, Version 2.0 with Runtime Library Exception. "
        f'See <a href="{html.escape(SWIFT_LICENSE_URL)}">{html.escape(SWIFT_LICENSE_URL)}</a> for details. '
        f"{_render_copyright_for_xhtml(build_original_work_copyright_sentence(year_range))} The Swift project authors are credited at "
        f'<a href="{html.escape(SWIFT_CONTRIBUTORS_URL)}">{html.escape(SWIFT_CONTRIBUTORS_URL)}</a>.</p>\n'
        "<p>The Swift logo is a trademark of Apple Inc. "
        "This edition is not published by, endorsed by, or affiliated with Apple Inc. or the Swift.org open source project.</p>\n"
        "<h2>Apache License 2.0</h2>\n"
        f"<pre>{html.escape(APACHE_LICENSE_V2_TEXT)}</pre>\n"
        "</div>\n"
    )


def render_notices_latex(
    mode: RenderingMode,
    year_range: tuple[int, int] | None = None,
) -> str:
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
    original_work_copyright = _render_copyright_for_latex(
        build_original_work_copyright_sentence(year_range)
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
        "The Swift logo is a trademark of Apple Inc. This edition is not "
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


def _render_latex_preformatted_block(text: str) -> list[str]:
    lines = ["\\parskip=0pt\n" + r"\begin{flushleft}\begin{plainlistingbox}"]
    lines.extend(text.splitlines())
    lines.append(r"\end{plainlistingbox}" + "\n\\end{flushleft}\n")
    return lines
