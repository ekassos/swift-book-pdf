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

from swift_book_pdf.epub.render.notices import render_notices_xhtml


def test_render_notices_xhtml_uses_detected_year_range() -> None:
    xhtml = render_notices_xhtml("Acknowledgments", (2014, 2026))

    assert (
        "Copyright &#169; 2014-2026 Apple Inc. and the Swift project authors"
        in xhtml
    )
    assert "swift-book-pdf" in xhtml
    assert "supporting assets derived from <em>swift-book-pdf</em>." in xhtml
    assert "This edition uses IBM Plex Sans and IBM Plex Serif" in xhtml
    assert "IBM Plex Font License" in xhtml
    assert "SIL OPEN FONT LICENSE Version 1.1" in xhtml
    assert "swift-docc-render project" not in xhtml
