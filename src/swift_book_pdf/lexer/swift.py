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

# The mode tree below preserves the upstream highlight.js identifier and
# attribute names (camelCase like beginKeywords, endsParent, beginScope,
# rawDelimiter) so this is a faithful 1:1 port of src/languages/swift.js.
# build_language is a single long function by design (it mirrors the one
# big factory in swift.js). Disable the style checks that fight that.
# ruff: noqa: N802, N806, N803, N812, ANN401, PLR0915

"""Build the Swift language definition and Pygments lexer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from pygments.lexer import Lexer
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    String,
    Token,
    _TokenType,
)

from swift_book_pdf.lexer import keywords as Swift
from swift_book_pdf.lexer.engine import (
    BACKSLASH_ESCAPE,
    C_LINE_COMMENT_MODE,
    COMMENT,
    Node,
    highlight,
)
from swift_book_pdf.lexer.regex import concat, either, lookahead

if TYPE_CHECKING:
    from collections.abc import Iterator

Mode = dict[str, Any]


def _src(value: Any) -> str:
    """Return regex source text from a string or marker.

    Args:
        value: Plain regex source or object with a `source` attribute.

    Returns:
        Regex source text.
    """
    src = getattr(value, "source", None)
    if src is not None:
        return src
    return value


def build_language() -> Mode:
    """Build a fresh Swift language definition.

    Returns:
        Root mode dictionary for the Swift grammar.

    Notes:
        The mode tree preserves upstream highlight.js naming and structure so
        it can be compared directly with `src/languages/swift.js`.
    """
    WHITESPACE: Mode = {"match": r"\s+", "relevance": 0}

    BLOCK_COMMENT = COMMENT(r"/\*", r"\*/", {"contains": ["self"]})
    COMMENTS = [C_LINE_COMMENT_MODE, BLOCK_COMMENT]

    DOT_KEYWORD: Mode = {
        "match": [
            r"\.",
            either(
                *[_src(k) for k in Swift.dotKeywords],
                *[_src(k) for k in Swift.optionalDotKeywords],
            ),
        ],
        "className": {2: "keyword"},
    }
    KEYWORD_GUARD: Mode = {
        "match": concat(r"\.", either(*[_src(k) for k in Swift.keywords])),
        "relevance": 0,
    }
    PLAIN_KEYWORDS = [kw for kw in Swift.keywords if isinstance(kw, str)] + [
        "_|0"
    ]
    REGEX_KEYWORDS = [
        Swift.keywordWrapper(_src(kw))
        for kw in Swift.keywords
        if not isinstance(kw, str)
    ] + [Swift.keywordWrapper(kw) for kw in Swift.keywordTypes]
    KEYWORD: Mode = {
        "variants": [
            {
                "className": "keyword",
                "match": either(
                    *[_src(k) for k in REGEX_KEYWORDS],
                    *[_src(k) for k in Swift.optionalDotKeywords],
                ),
            }
        ]
    }
    KEYWORDS: Mode = {
        "$pattern": either(r"\b\w+", r"#\w+"),
        "keyword": PLAIN_KEYWORDS + Swift.numberSignKeywords,
        "literal": Swift.literals,
    }
    KEYWORD_MODES = [DOT_KEYWORD, KEYWORD_GUARD, KEYWORD]

    BUILT_IN_GUARD: Mode = {
        "match": concat(r"\.", either(*Swift.builtIns)),
        "relevance": 0,
    }
    BUILT_IN: Mode = {
        "className": "built_in",
        "match": concat(r"\b", either(*Swift.builtIns), r"(?=\()"),
    }
    BUILT_INS = [BUILT_IN_GUARD, BUILT_IN]

    OPERATOR_GUARD: Mode = {"match": r"->", "relevance": 0}
    OPERATOR: Mode = {
        "className": "operator",
        "relevance": 0,
        "variants": [
            {"match": _src(Swift.operator)},
            {"match": "\\.(\\.|" + _src(Swift.operatorCharacter) + ")+"},
        ],
    }
    OPERATORS = [OPERATOR_GUARD, OPERATOR]

    decimalDigits = "([0-9]_*)+"
    hexDigits = "([0-9a-fA-F]_*)+"
    NUMBER: Mode = {
        "className": "number",
        "relevance": 0,
        "variants": [
            {
                "match": "\\b("
                + decimalDigits
                + ")(\\.("
                + decimalDigits
                + "))?"
                + "([eE][+-]?("
                + decimalDigits
                + "))?\\b"
            },
            {
                "match": "\\b0x("
                + hexDigits
                + ")(\\.("
                + hexDigits
                + "))?"
                + "([pP][+-]?("
                + decimalDigits
                + "))?\\b"
            },
            {"match": r"\b0o([0-7]_*)+\b"},
            {"match": r"\b0b([01]_*)+\b"},
        ],
    }

    def ESCAPED_CHARACTER(rawDelimiter: str = "") -> Mode:
        """Build a string-escape mode.

        Args:
            rawDelimiter: Optional raw-string delimiter prefix.

        Returns:
            Mode dictionary for escaped characters.
        """
        return {
            "className": "subst",
            "variants": [
                {"match": concat(r"\\", rawDelimiter, r"[0\\tnr\"']")},
                {
                    "match": concat(
                        r"\\", rawDelimiter, r"u\{[0-9a-fA-F]{1,8}\}"
                    )
                },
            ],
        }

    def ESCAPED_NEWLINE(rawDelimiter: str = "") -> Mode:
        """Build an escaped-newline mode.

        Args:
            rawDelimiter: Optional raw-string delimiter prefix.

        Returns:
            Mode dictionary for escaped newlines.
        """
        return {
            "className": "subst",
            "match": concat(r"\\", rawDelimiter, r"[\t ]*(?:[\r\n]|\r\n)"),
        }

    def INTERPOLATION(rawDelimiter: str = "") -> Mode:
        """Build a string-interpolation mode.

        Args:
            rawDelimiter: Optional raw-string delimiter prefix.

        Returns:
            Mode dictionary for interpolated expressions.
        """
        return {
            "className": "subst",
            "label": "interpol",
            "begin": concat(r"\\", rawDelimiter, r"\("),
            "end": r"\)",
        }

    def MULTILINE_STRING(rawDelimiter: str = "") -> Mode:
        """Build a multiline-string mode.

        Args:
            rawDelimiter: Optional raw-string delimiter prefix.

        Returns:
            Mode dictionary for triple-quoted strings.
        """
        return {
            "begin": concat(rawDelimiter, r'"""'),
            "end": concat(r'"""', rawDelimiter),
            "contains": [
                ESCAPED_CHARACTER(rawDelimiter),
                ESCAPED_NEWLINE(rawDelimiter),
                INTERPOLATION(rawDelimiter),
            ],
        }

    def SINGLE_LINE_STRING(rawDelimiter: str = "") -> Mode:
        """Build a single-line-string mode.

        Args:
            rawDelimiter: Optional raw-string delimiter prefix.

        Returns:
            Mode dictionary for double-quoted strings.
        """
        return {
            "begin": concat(rawDelimiter, r'"'),
            "end": concat(r'"', rawDelimiter),
            "contains": [
                ESCAPED_CHARACTER(rawDelimiter),
                INTERPOLATION(rawDelimiter),
            ],
        }

    STRING: Mode = {
        "className": "string",
        "variants": [
            MULTILINE_STRING(),
            MULTILINE_STRING("#"),
            MULTILINE_STRING("##"),
            MULTILINE_STRING("###"),
            SINGLE_LINE_STRING(),
            SINGLE_LINE_STRING("#"),
            SINGLE_LINE_STRING("##"),
            SINGLE_LINE_STRING("###"),
        ],
    }

    REGEXP_CONTENTS = [
        BACKSLASH_ESCAPE,
        {
            "begin": r"\[",
            "end": r"\]",
            "relevance": 0,
            "contains": [BACKSLASH_ESCAPE],
        },
    ]

    BARE_REGEXP_LITERAL: Mode = {
        "begin": r"\/[^\s](?=[^/\n]*\/)",
        "end": r"\/",
        "contains": REGEXP_CONTENTS,
    }

    def EXTENDED_REGEXP_LITERAL(rawDelimiter: str) -> Mode:
        """Build an extended-regex-literal mode.

        Args:
            rawDelimiter: Raw-regex delimiter prefix.

        Returns:
            Mode dictionary for slash-delimited regex literals.
        """
        begin = concat(rawDelimiter, r"\/")
        end = concat(r"\/", rawDelimiter)
        return {
            "begin": begin,
            "end": end,
            "contains": [
                *REGEXP_CONTENTS,
                {
                    "scope": "comment",
                    "begin": "#(?!.*" + end + ")",
                    "end": r"$",
                },
            ],
        }

    REGEXP: Mode = {
        "scope": "regexp",
        "variants": [
            EXTENDED_REGEXP_LITERAL("###"),
            EXTENDED_REGEXP_LITERAL("##"),
            EXTENDED_REGEXP_LITERAL("#"),
            BARE_REGEXP_LITERAL,
        ],
    }

    QUOTED_IDENTIFIER: Mode = {
        "match": concat(r"`", _src(Swift.identifier), r"`")
    }
    IMPLICIT_PARAMETER: Mode = {
        "className": "variable",
        "match": r"\$\d+",
    }
    PROPERTY_WRAPPER_PROJECTION: Mode = {
        "className": "variable",
        "match": "\\$" + _src(Swift.identifierCharacter) + "+",
    }
    IDENTIFIERS = [
        QUOTED_IDENTIFIER,
        IMPLICIT_PARAMETER,
        PROPERTY_WRAPPER_PROJECTION,
    ]

    AVAILABLE_ATTRIBUTE: Mode = {
        "match": r"(@|#(un)?)available",
        "scope": "keyword",
        "starts": {
            "contains": [
                {
                    "begin": r"\(",
                    "end": r"\)",
                    "keywords": Swift.availabilityKeywords,
                    "contains": [*OPERATORS, NUMBER, STRING],
                }
            ]
        },
    }

    KEYWORD_ATTRIBUTE: Mode = {
        "scope": "keyword",
        "match": concat(
            r"@",
            either(*[_src(k) for k in Swift.keywordAttributes]),
            lookahead(either(r"\(", r"\s+")),
        ),
    }

    USER_DEFINED_ATTRIBUTE: Mode = {
        "scope": "meta",
        "match": concat(r"@", _src(Swift.identifier)),
    }

    ATTRIBUTES = [
        AVAILABLE_ATTRIBUTE,
        KEYWORD_ATTRIBUTE,
        USER_DEFINED_ATTRIBUTE,
    ]

    TYPE: Mode = {
        "match": lookahead(r"\b[A-Z]"),
        "relevance": 0,
        "contains": [
            {
                "className": "type",
                "match": concat(
                    r"(AV|CA|CF|CG|CI|CL|CM|CN|CT|MK|MP|MTK|MTL|NS|"
                    r"SCN|SK|UI|WK|XC)",
                    _src(Swift.identifierCharacter),
                    "+",
                ),
            },
            {
                "className": "type",
                "match": _src(Swift.typeIdentifier),
                "relevance": 0,
            },
            {"match": r"[?!]+", "relevance": 0},
            {"match": r"\.\.\.", "relevance": 0},
            {
                "match": concat(
                    r"\s+&\s+", lookahead(_src(Swift.typeIdentifier))
                ),
                "relevance": 0,
            },
        ],
    }
    GENERIC_ARGUMENTS: Mode = {
        "begin": r"<",
        "end": r">",
        "keywords": KEYWORDS,
        "contains": [
            *COMMENTS,
            *KEYWORD_MODES,
            *ATTRIBUTES,
            OPERATOR_GUARD,
            TYPE,
        ],
    }
    TYPE["contains"].append(GENERIC_ARGUMENTS)

    TUPLE_ELEMENT_NAME: Mode = {
        "match": concat(_src(Swift.identifier), r"\s*:"),
        "keywords": "_|0",
        "relevance": 0,
    }
    TUPLE: Mode = {
        "begin": r"\(",
        "end": r"\)",
        "relevance": 0,
        "keywords": KEYWORDS,
        "contains": [
            "self",
            TUPLE_ELEMENT_NAME,
            *COMMENTS,
            REGEXP,
            *KEYWORD_MODES,
            *BUILT_INS,
            *OPERATORS,
            NUMBER,
            STRING,
            *IDENTIFIERS,
            *ATTRIBUTES,
            TYPE,
        ],
    }

    GENERIC_PARAMETERS: Mode = {
        "begin": r"<",
        "end": r">",
        "keywords": "repeat each",
        "contains": [*COMMENTS, TYPE],
    }
    FUNCTION_PARAMETER_NAME: Mode = {
        "begin": either(
            lookahead(concat(_src(Swift.identifier), r"\s*:")),
            lookahead(
                concat(
                    _src(Swift.identifier),
                    r"\s+",
                    _src(Swift.identifier),
                    r"\s*:",
                )
            ),
        ),
        "end": r":",
        "relevance": 0,
        "contains": [
            {"className": "keyword", "match": r"\b_\b"},
            {"className": "params", "match": _src(Swift.identifier)},
        ],
    }
    FUNCTION_PARAMETERS: Mode = {
        "begin": r"\(",
        "end": r"\)",
        "keywords": KEYWORDS,
        "contains": [
            FUNCTION_PARAMETER_NAME,
            *COMMENTS,
            *KEYWORD_MODES,
            *OPERATORS,
            NUMBER,
            STRING,
            *ATTRIBUTES,
            TYPE,
            TUPLE,
        ],
        "endsParent": True,
        "illegal": r"[\"']",
    }
    FUNCTION_OR_MACRO: Mode = {
        "match": [
            r"(func|macro)",
            r"\s+",
            either(
                QUOTED_IDENTIFIER["match"],
                _src(Swift.identifier),
                _src(Swift.operator),
            ),
        ],
        "className": {1: "keyword", 3: "title.function"},
        "contains": [
            GENERIC_PARAMETERS,
            FUNCTION_PARAMETERS,
            WHITESPACE,
        ],
        "illegal": [r"\[", r"%"],
    }

    INIT_SUBSCRIPT: Mode = {
        "match": [
            r"\b(?:subscript|init[?!]?)",
            r"\s*(?=[<(])",
        ],
        "className": {1: "keyword"},
        "contains": [
            GENERIC_PARAMETERS,
            FUNCTION_PARAMETERS,
            WHITESPACE,
        ],
        "illegal": r"\[|%",
    }
    OPERATOR_DECLARATION: Mode = {
        "match": [r"operator", r"\s+", _src(Swift.operator)],
        "className": {1: "keyword", 3: "title"},
    }

    PRECEDENCEGROUP: Mode = {
        "begin": [
            r"precedencegroup",
            r"\s+",
            _src(Swift.typeIdentifier),
        ],
        "className": {1: "keyword", 3: "title"},
        "contains": [TYPE],
        "keywords": [
            *Swift.precedencegroupKeywords,
            *Swift.literals,
        ],
        "end": r"}",
    }

    CLASS_FUNC_DECLARATION: Mode = {
        "match": [
            r"class\b",
            r"\s+",
            r"func\b",
            r"\s+",
            r"\b[A-Za-z_][A-Za-z0-9_]*\b",
        ],
        "scope": {1: "keyword", 3: "keyword", 5: "title.function"},
    }

    CLASS_VAR_DECLARATION: Mode = {
        "match": [r"class\b", r"\s+", r"var\b"],
        "scope": {1: "keyword", 3: "keyword"},
    }

    TYPE_DECLARATION: Mode = {
        "begin": [
            r"(struct|protocol|class|extension|enum|actor)",
            r"\s+",
            _src(Swift.identifier),
            r"\s*",
        ],
        "beginScope": {1: "keyword", 3: "title.class"},
        "keywords": KEYWORDS,
        "contains": [
            GENERIC_PARAMETERS,
            *KEYWORD_MODES,
            {
                "begin": r":",
                "end": r"\{",
                "keywords": KEYWORDS,
                "contains": [
                    {
                        "scope": "title.class.inherited",
                        "match": _src(Swift.typeIdentifier),
                    },
                    *KEYWORD_MODES,
                ],
                "relevance": 0,
            },
        ],
    }

    # Add supported submodes to string interpolation.
    for variant in STRING["variants"]:
        interpolation = next(
            m for m in variant["contains"] if m.get("label") == "interpol"
        )
        interpolation["keywords"] = KEYWORDS
        submodes = [
            *KEYWORD_MODES,
            *BUILT_INS,
            *OPERATORS,
            NUMBER,
            STRING,
            *IDENTIFIERS,
        ]
        interpolation["contains"] = [
            *submodes,
            {
                "begin": r"\(",
                "end": r"\)",
                "contains": ["self", *submodes],
            },
        ]

    return {
        "name": "Swift",
        "keywords": KEYWORDS,
        "contains": [
            *COMMENTS,
            FUNCTION_OR_MACRO,
            INIT_SUBSCRIPT,
            CLASS_FUNC_DECLARATION,
            CLASS_VAR_DECLARATION,
            TYPE_DECLARATION,
            OPERATOR_DECLARATION,
            PRECEDENCEGROUP,
            {
                "beginKeywords": "import",
                "end": r"$",
                "contains": [*COMMENTS],
                "relevance": 0,
            },
            REGEXP,
            *KEYWORD_MODES,
            *BUILT_INS,
            *OPERATORS,
            NUMBER,
            STRING,
            *IDENTIFIERS,
            *ATTRIBUTES,
            TYPE,
            TUPLE,
        ],
    }


# --------------------------------------------------------------------------
# Pygments integration
# --------------------------------------------------------------------------

# Maps a highlight.js scope (its first segment) to a Pygments token type.
_SCOPE_TO_TOKEN: dict[str, _TokenType] = {
    "addition": Token.Generic.Inserted,
    "attr": Name.Class,
    "attribute": Token.Text,
    "bullet": Number,
    "builtin-name": Name.Builtin,
    "keyword": Keyword,
    "literal": Keyword.Constant,
    "selector-tag": Keyword,
    "built_in": Name.Builtin,
    "class": Name.Class,
    "type": Name.Class,
    "title": Name.Function,
    "section": Name.Class,
    "string": String,
    "subst": Token.Text,
    "number": Number,
    "symbol": Number,
    "tag": Number,
    "comment": Comment,
    "quote": Comment,
    "deletion": Token.Generic.Deleted,
    "doctag": Comment,
    "operator": Operator,
    "regexp": Token.Text,
    "variable": Token.Text,
    "meta": Keyword,
    "params": Name.Class,
    "property": Token.Text,
    "identifier": Token.Text,
}


def _scope_to_token(scope: str | None) -> _TokenType:
    """Map a highlight.js scope to a Pygments token type.

    Args:
        scope: Highlight.js scope name.

    Returns:
        Pygments token type for the scope.
    """
    if not scope:
        return Token.Text
    first = scope.split(".")[0]
    return _SCOPE_TO_TOKEN.get(first, Token.Text)


class SwiftLexer(Lexer):
    """A Pygments lexer for Swift backed by the highlight.js engine.

    Notes:
        Tokenization runs the ported highlight.js mode engine and maps each
        emitted scope to a Pygments token type. For exact highlight.js HTML,
        call `swift_book_pdf.lexer.markup.highlight_swift` instead.
    """

    name = "Swift"
    aliases: ClassVar[list[str]] = ["swift-book-swift"]
    filenames: ClassVar[list[str]] = ["*.swift"]
    mimetypes: ClassVar[list[str]] = ["text/x-swift"]

    def get_tokens_unprocessed(
        self, text: str
    ) -> Iterator[tuple[int, _TokenType, str]]:
        """Yield Pygments tokens from highlighted Swift source.

        Args:
            text: Swift source text.

        Yields:
            Tuples containing character offset, Pygments token type, and token
            text.
        """
        from swift_book_pdf.lexer.docc import build_docc_render_language

        language = build_docc_render_language()
        emitter = highlight(language, text)
        pos = 0
        for token_type, value in _flatten(emitter.root, None):
            if value == "":
                continue
            yield pos, token_type, value
            pos += len(value)


def _flatten(
    node: Node | str, scope: str | None
) -> Iterator[tuple[_TokenType, str]]:
    """Yield Pygments token pairs from a token tree.

    Args:
        node: Token-tree node or text leaf.
        scope: Current inherited highlight.js scope.

    Yields:
        Tuples containing Pygments token type and token text.
    """
    if isinstance(node, str):
        yield _scope_to_token(scope), node
        return
    current = node.scope or scope
    for child in node.children:
        yield from _flatten(child, current)


__all__ = ["SwiftLexer", "build_language"]
