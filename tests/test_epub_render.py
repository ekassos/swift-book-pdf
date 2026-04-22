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

from swift_book_pdf.epub.render import (
    LinkResolver,
    _normalize_prose_punctuation,
    _render_inline,
)


def test_normalize_prose_punctuation_converts_triple_hyphen_to_em_dash() -> (
    None
):
    assert _normalize_prose_punctuation("before --- after") == "before—after"


def test_normalize_prose_punctuation_converts_double_hyphen_to_en_dash() -> (
    None
):
    assert (
        _normalize_prose_punctuation("Swift 5.9--6.0") == "Swift 5.9\u20136.0"
    )


def test_render_inline_keeps_markdown_like_code_spans_literal() -> None:
    rendered = _render_inline(
        (
            "Alternatively, you can create an empty array of a certain type "
            "using explicit initializer syntax, by writing the element type "
            "in square brackets followed by parentheses---for example, "
            "`[Int]()` in the following:"
        ),
        "CollectionTypes.xhtml",
        LinkResolver([]),
    )

    assert "@@INLINE" not in rendered
    assert '<code class="inline-code">[Int]()</code>' in rendered


def test_render_inline_supports_code_inside_markdown_link_labels() -> None:
    rendered = _render_inline(
        "Read [`Array`](https://example.com) first.",
        "CollectionTypes.xhtml",
        LinkResolver([]),
    )

    assert (
        '<a href="https://example.com">'
        '<code class="inline-code">Array</code></a>' in rendered
    )
