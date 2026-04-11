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

from swift_book_pdf.latex_helpers import apply_formatting, convert_inline_code
from swift_book_pdf.schema import RenderingMode


def test_apply_formatting_converts_underscore_emphasis() -> None:
    rendered = apply_formatting(
        "> postfix-expression opt _?_", RenderingMode.PRINT
    )

    assert rendered == r"> postfix-expression opt \emph{?}"


def test_apply_formatting_leaves_identifier_underscores_literal() -> None:
    rendered = apply_formatting("Use snake_case here.", RenderingMode.PRINT)

    assert rendered == r"Use snake\_case here."


def test_apply_formatting_preserves_underscores_inside_link_urls() -> None:
    source = (
        "[`warning(_:_:)`]"
        "(https://developer.apple.com/documentation/swift/warning(_:_:))"
    )

    rendered = apply_formatting(
        convert_inline_code(source), RenderingMode.PRINT
    )

    assert (
        rendered
        == r"\href{https://developer.apple.com/documentation/swift/warning(_:_:)}"
        r"{{\CodeStyle \texttt{warning{(}\_{:}\_{:}{)}}}}"
        r"\footnote{\url{https://developer.apple.com/documentation/swift/warning(_:_:)}}"
    )
