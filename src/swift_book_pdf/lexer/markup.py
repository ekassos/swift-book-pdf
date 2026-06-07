# Copyright 2026 Evangelos Kassos
#
# Portions derived from highlight.js:
#   Copyright (c) 2006, Ivan Sagalaev.
#   Licensed under the BSD 3-Clause License.
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

"""Render highlighted Swift token trees to HTML markup."""

from __future__ import annotations

from swift_book_pdf.lexer.docc import build_docc_render_language
from swift_book_pdf.lexer.engine import Node, TokenTreeEmitter, highlight

CLASS_PREFIX = "hljs-"
SPAN_CLOSE = "</span>"


def escape_html(value: str) -> str:
    """Escape text using highlight.js-compatible HTML entities.

    Args:
        value: Raw text to escape.

    Returns:
        Escaped text with newlines preserved.
    """
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def emits_wrapping_tags(node: Node) -> bool:
    """Return whether a token-tree node emits a wrapping `span`.

    Args:
        node: Token-tree node to inspect.

    Returns:
        `True` when the node has a scope.
    """
    return bool(node.scope)


def scope_to_css_class(name: str, prefix: str = CLASS_PREFIX) -> str:
    """Convert a scope name to its highlight.js CSS class string.

    Args:
        name: Highlight.js scope name.
        prefix: CSS class prefix for ordinary scopes.

    Returns:
        CSS class string for the scope.
    """
    if name.startswith("language:"):
        return name.replace("language:", "language-")
    if "." in name:
        pieces = name.split(".")
        first = pieces[0]
        rest = pieces[1:]
        parts = [f"{prefix}{first}"]
        parts.extend(f"{seg}{'_' * (i + 1)}" for i, seg in enumerate(rest))
        return " ".join(parts)
    return f"{prefix}{name}"


class HTMLRenderer:
    """Walks a token tree and accumulates highlight.js HTML markup."""

    def __init__(
        self, emitter: TokenTreeEmitter, prefix: str = CLASS_PREFIX
    ) -> None:
        """Initialize the renderer and walk an emitter.

        Args:
            emitter: Token-tree emitter to render.
            prefix: CSS class prefix for ordinary scopes.
        """
        self.buffer = ""
        self.prefix = prefix
        emitter.walk(self)

    def add_text(self, text: str) -> None:
        """Append escaped text to the output buffer.

        Args:
            text: Raw text from the token tree.
        """
        self.buffer += escape_html(text)

    def open_node(self, node: Node) -> None:
        """Append the opening tag for a scoped node.

        Args:
            node: Token-tree node being opened.
        """
        if node.scope is None:
            return
        css = scope_to_css_class(node.scope, self.prefix)
        self.buffer += f'<span class="{css}">'

    def close_node(self, node: Node) -> None:
        """Append the closing tag for a scoped node.

        Args:
            node: Token-tree node being closed.
        """
        if not emits_wrapping_tags(node):
            return
        self.buffer += SPAN_CLOSE

    def value(self) -> str:
        """Return the rendered HTML.

        Returns:
            Accumulated inner HTML.
        """
        return self.buffer


def render(emitter: TokenTreeEmitter) -> str:
    """Render a token-tree emitter to highlight.js inner HTML.

    Args:
        emitter: Token-tree emitter to render.

    Returns:
        Highlight.js-compatible inner HTML.
    """
    return HTMLRenderer(emitter).value()


def highlight_swift(code: str) -> str:
    """Highlight Swift code and return highlight.js inner HTML.

    Args:
        code: Swift source text.

    Returns:
        Inner HTML only, without wrapping `pre` or `code` elements.
    """
    language = build_docc_render_language()
    emitter = highlight(language, code)
    return render(emitter)
