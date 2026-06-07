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

# Ports the Swift-applicable cases of swift-docc-render's
# tests/unit/utils/syntax-highlight.spec.js. The spec exercises two outputs:
# the raw `highlight()` HTML and the line-wrapped `highlightContent()` form.
# This package mirrors the first with `highlight_swift` (markup layer) and the
# second with `SwiftLexer`, whose per-line token stream feeds the LaTeX/minted
# renderer instead of HTML line wrapping.

from __future__ import annotations

from pygments.token import String

from swift_book_pdf.lexer import SwiftLexer, highlight_swift


def _tokens(code: str) -> list[tuple[object, str]]:
    """Tokenize Swift source through the DocC Render Pygments adapter.

    Args:
        code: Swift source text.

    Returns:
        List of (token type, value) pairs, in order.
    """
    return [
        (token, value)
        for _position, token, value in SwiftLexer().get_tokens_unprocessed(
            code
        )
    ]


def test_does_nothing_to_single_row_syntax() -> None:
    source = "\n".join(
        [
            'let name = "Rosa"',
            r'let personalizedGreeting = "Welcome, \(name)!"',
        ]
    )
    expected = "\n".join(
        [
            '<span class="hljs-keyword">let</span> name '
            '<span class="hljs-operator">=</span> '
            '<span class="hljs-string">&quot;Rosa&quot;</span>',
            '<span class="hljs-keyword">let</span> personalizedGreeting '
            '<span class="hljs-operator">=</span> '
            '<span class="hljs-string">&quot;Welcome, '
            r'<span class="hljs-subst">\(name)</span>!&quot;</span>',
        ]
    )
    assert highlight_swift(source) == expected


def test_tokenizes_swift_class_functions_correctly() -> None:
    source = "class func foo() async throws -> [Bar]"
    expected = (
        '<span class="hljs-keyword">class</span> '
        '<span class="hljs-keyword">func</span> '
        '<span class="hljs-title function_">foo</span>() '
        '<span class="hljs-keyword">async</span> '
        '<span class="hljs-keyword">throws</span> -&gt; '
        '[<span class="hljs-type">Bar</span>]'
    )
    assert highlight_swift(source) == expected


def test_does_not_tokenize_swift_keywords_inside_words() -> None:
    source = "\n".join(
        [
            "var protocolMock = true  // 'protocol' is not highlighted",
            "var myenum = true  // 'enum' is not highlighted",
            "if FooConfig.supportsReconstruction(.someClassification) {",
            "    configuration.fooReconstruction = .someprotocolextensionclass",
            "}",
        ]
    )
    expected = "\n".join(
        [
            '<span class="hljs-keyword">var</span> protocolMock '
            '<span class="hljs-operator">=</span> '
            '<span class="hljs-literal">true</span>  '
            '<span class="hljs-comment">// &#x27;protocol&#x27; is not '
            "highlighted</span>",
            '<span class="hljs-keyword">var</span> myenum '
            '<span class="hljs-operator">=</span> '
            '<span class="hljs-literal">true</span>  '
            '<span class="hljs-comment">// &#x27;enum&#x27; is not '
            "highlighted</span>",
            '<span class="hljs-keyword">if</span> '
            '<span class="hljs-type">FooConfig</span>'
            ".supportsReconstruction(.someClassification) {",
            "    configuration.fooReconstruction "
            '<span class="hljs-operator">=</span> '
            ".someprotocolextensionclass",
            "}",
        ]
    )
    assert highlight_swift(source) == expected


def test_wraps_multiline_string_blocks_in_string_scope() -> None:
    source = "\n".join(
        [
            'let banner = """',
            "          __,",
            "         (           o  /) _/_",
            "          `.  , , , ,  //  /",
            "        (___)(_(_/_(_ //_ (__",
            "                     /)",
            "                    (/",
            '        """',
        ]
    )
    literal_start = source.index('"""')
    offset = 0
    for token, value in _tokens(source):
        if offset >= literal_start:
            assert token in String, (token, value)
        offset += len(value)


def test_keeps_escaped_newline_tokens_on_the_same_line() -> None:
    source = "\n".join(
        [
            'let multiline = """',
            "a \\",
            "b",
            "",
            "c \\",
            "d",
            '"""',
        ]
    )
    tokens = _tokens(source)
    rendered = "".join(value for _token, value in tokens)
    assert rendered == source
    # The escaped-newline override emits the backslash as its own token and
    # leaves the newline with the surrounding string, so no single token spans
    # the line continuation.
    assert any(value == "\\" for _token, value in tokens)
    assert not any("\\" in value and "\n" in value for _token, value in tokens)
