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

# The bindings below intentionally preserve the original highlight.js
# names (camelCase functions and module-level constants) so that this
# port is a faithful, drop-in mirror of `kws_swift.js` and callers can
# import the same identifiers. Disable pep8-naming for this file.
# ruff: noqa: N802, N816

"""Define Swift keyword tables for the highlight.js-style lexer."""

from __future__ import annotations

from swift_book_pdf.lexer.regex import concat, either


class Regex:
    """A marker for a regex-typed token.

    Notes:
        The `source` attribute mirrors JavaScript's `RegExp.prototype.source`:
        pattern text without delimiters or flags. This keeps the upstream
        distinction between plain keyword strings and regex keyword entries.
    """

    __slots__ = ("source",)

    def __init__(self, source: str) -> None:
        """Initialize a regex marker.

        Args:
            source: Regex source text without delimiters or flags.
        """
        self.source = source

    def __repr__(self) -> str:
        """Return a debugging representation.

        Returns:
            Representation containing the regex source.
        """
        return f"Regex({self.source!r})"

    def __eq__(self, other: object) -> bool:
        """Compare regex markers by source text.

        Args:
            other: Object to compare.

        Returns:
            `True` when `other` is a `Regex` with the same source, or
            `NotImplemented` for unsupported object types.
        """
        if isinstance(other, Regex):
            return self.source == other.source
        return NotImplemented

    def __hash__(self) -> int:
        """Return a stable hash for the regex marker.

        Returns:
            Hash derived from the marker type and source text.
        """
        return hash(("Regex", self.source))


def _src(value: str | Regex) -> str:
    """Return the regex source for a string or marker.

    Args:
        value: Plain keyword string or regex marker.

    Returns:
        Raw regex source text.
    """
    if isinstance(value, Regex):
        return value.source
    return value


def keywordWrapper(keyword: str) -> Regex:
    r"""Wrap a keyword with word boundaries.

    Args:
        keyword: Regex source for the keyword body.

    Returns:
        Regex marker for the keyword with leading and trailing word-boundary
        handling.
    """
    last = keyword[-1:] if keyword else ""
    trailing = r"\b" if (last.isalnum() or last == "_") else r"\B"
    return Regex(concat(r"\b", _src(keyword), trailing))


# Keywords that require a leading dot.
dotKeywords: list[Regex] = [
    keywordWrapper(kw)
    for kw in [
        "Protocol",  # contextual
        "Type",  # contextual
    ]
]

# Keywords that may have a leading dot.
optionalDotKeywords: list[Regex] = [
    keywordWrapper(kw)
    for kw in [
        "init",
        "self",
    ]
]

# should register as keyword, not type
keywordTypes: list[str] = [
    "Any",
    "Self",
]

# Regular keywords and literals.
#
# Strings below will be fed into the regular `keywords` engine while
# regex entries (`Regex` markers) will result in additional modes being
# created to scan for those keywords to avoid conflicts with other rules.
# The order is preserved exactly from the upstream source.
keywords: list[str | Regex] = [
    "actor",
    "any",  # contextual
    "associatedtype",
    "async",
    "await",
    Regex(r"as\?"),  # operator
    Regex(r"as!"),  # operator
    "as",  # operator
    "borrowing",  # contextual
    "break",
    "case",
    "catch",
    "class",
    "consume",  # contextual
    "consuming",  # contextual
    "continue",
    "convenience",  # contextual
    "copy",  # contextual
    "default",
    "defer",
    "deinit",
    "didSet",  # contextual
    "distributed",
    "do",
    "dynamic",  # contextual
    "each",
    "else",
    "enum",
    "extension",
    "fallthrough",
    Regex(r"fileprivate\(set\)"),
    "fileprivate",
    "final",  # contextual
    "for",
    "func",
    "get",  # contextual
    "guard",
    "if",
    "import",
    "indirect",  # contextual
    "infix",  # contextual
    Regex(r"init\?"),
    Regex(r"init!"),
    "inout",
    Regex(r"internal\(set\)"),
    "internal",
    "in",
    "is",  # operator
    "isolated",  # contextual
    "nonisolated",  # contextual
    "lazy",  # contextual
    "let",
    "macro",
    "mutating",  # contextual
    "nonmutating",  # contextual
    Regex(r"open\(set\)"),  # contextual
    "open",  # contextual
    "operator",
    "optional",  # contextual
    "override",  # contextual
    "package",
    "postfix",  # contextual
    "precedencegroup",
    "prefix",  # contextual
    Regex(r"private\(set\)"),
    "private",
    "protocol",
    Regex(r"public\(set\)"),
    "public",
    "repeat",
    "required",  # contextual
    "rethrows",
    "return",
    "set",  # contextual
    "some",  # contextual
    "static",
    "struct",
    "subscript",
    "super",
    "switch",
    "throws",
    "throw",
    Regex(r"try\?"),  # operator
    Regex(r"try!"),  # operator
    "try",  # operator
    "typealias",
    Regex(r"unowned\(safe\)"),  # contextual
    Regex(r"unowned\(unsafe\)"),  # contextual
    "unowned",  # contextual
    "var",
    "weak",  # contextual
    "where",
    "while",
    "willSet",  # contextual
]

# NOTE: Contextual keywords are reserved only in specific contexts.
# Ideally, these should be matched using modes to avoid false positives.

# Literals.
literals: list[str] = [
    "false",
    "nil",
    "true",
]

# Keywords used in precedence groups.
precedencegroupKeywords: list[str] = [
    "assignment",
    "associativity",
    "higherThan",
    "left",
    "lowerThan",
    "none",
    "right",
]

# Keywords that start with a number sign (#).
# #(un)available is handled separately.
numberSignKeywords: list[str] = [
    "#colorLiteral",
    "#column",
    "#dsohandle",
    "#else",
    "#elseif",
    "#endif",
    "#error",
    "#file",
    "#fileID",
    "#fileLiteral",
    "#filePath",
    "#function",
    "#if",
    "#imageLiteral",
    "#keyPath",
    "#line",
    "#selector",
    "#sourceLocation",
    "#warning",
]

# Global functions in the Standard Library.
builtIns: list[str] = [
    "abs",
    "all",
    "any",
    "assert",
    "assertionFailure",
    "debugPrint",
    "dump",
    "fatalError",
    "getVaList",
    "isKnownUniquelyReferenced",
    "max",
    "min",
    "numericCast",
    "pointwiseMax",
    "pointwiseMin",
    "precondition",
    "preconditionFailure",
    "print",
    "readLine",
    "repeatElement",
    "sequence",
    "stride",
    "swap",
    "swift_unboxFromSwiftValueWithType",
    "transcode",
    "type",
    "unsafeBitCast",
    "unsafeDowncast",
    "withExtendedLifetime",
    "withUnsafeMutablePointer",
    "withUnsafePointer",
    "withVaList",
    "withoutActuallyEscaping",
    "zip",
]

# Valid first characters for operators.
operatorHead: Regex = Regex(
    either(
        r"[/=\-+!*%<>&|^~?]",
        r"[\u00A1-\u00A7]",
        r"[\u00A9\u00AB]",
        r"[\u00AC\u00AE]",
        r"[\u00B0\u00B1]",
        r"[\u00B6\u00BB\u00BF\u00D7\u00F7]",
        r"[\u2016-\u2017]",
        r"[\u2020-\u2027]",
        r"[\u2030-\u203E]",
        r"[\u2041-\u2053]",
        r"[\u2055-\u205E]",
        r"[\u2190-\u23FF]",
        r"[\u2500-\u2775]",
        r"[\u2794-\u2BFF]",
        r"[\u2E00-\u2E7F]",
        r"[\u3001-\u3003]",
        r"[\u3008-\u3020]",
        r"[\u3030]",
    )
)

# Valid characters for operators.
operatorCharacter: Regex = Regex(
    either(
        _src(operatorHead),
        r"[\u0300-\u036F]",
        r"[\u1DC0-\u1DFF]",
        r"[\u20D0-\u20FF]",
        r"[\uFE00-\uFE0F]",
        r"[\uFE20-\uFE2F]",
        # TODO: The following characters are also allowed, but the regex
        # isn't supported yet.
        # /[\u{E0100}-\u{E01EF}]/u
    )
)

# Valid operator.
operator: Regex = Regex(
    concat(_src(operatorHead), _src(operatorCharacter), "*")
)

# Valid first characters for identifiers.
identifierHead: Regex = Regex(
    either(
        r"[a-zA-Z_]",
        r"[\u00A8\u00AA\u00AD\u00AF\u00B2-\u00B5\u00B7-\u00BA]",
        r"[\u00BC-\u00BE\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF]",
        r"[\u0100-\u02FF\u0370-\u167F\u1681-\u180D\u180F-\u1DBF]",
        r"[\u1E00-\u1FFF]",
        r"[\u200B-\u200D\u202A-\u202E\u203F-\u2040\u2054\u2060-\u206F]",
        r"[\u2070-\u20CF\u2100-\u218F\u2460-\u24FF\u2776-\u2793]",
        r"[\u2C00-\u2DFF\u2E80-\u2FFF]",
        r"[\u3004-\u3007\u3021-\u302F\u3031-\u303F\u3040-\uD7FF]",
        r"[\uF900-\uFD3D\uFD40-\uFDCF\uFDF0-\uFE1F\uFE30-\uFE44]",
        r"[\uFE47-\uFEFE\uFF00-\uFFFD]",
        # The remaining astral-plane ranges in the JS source are commented
        # out there too, as the regexes aren't supported yet.
    )
)

# Valid characters for identifiers.
identifierCharacter: Regex = Regex(
    either(
        _src(identifierHead),
        r"\d",
        r"[\u0300-\u036F\u1DC0-\u1DFF\u20D0-\u20FF\uFE20-\uFE2F]",
    )
)

# Valid identifier.
identifier: Regex = Regex(
    concat(_src(identifierHead), _src(identifierCharacter), "*")
)

# Valid type identifier.
typeIdentifier: Regex = Regex(concat(r"[A-Z]", _src(identifierCharacter), "*"))

# Built-in attributes, which are highlighted as keywords.
# @available is handled separately.
# https://docs.swift.org/swift-book/documentation/the-swift-programming-language/attributes
keywordAttributes: list[str | Regex] = [
    "attached",
    "autoclosure",
    Regex(concat(r"convention\(", either("swift", "block", "c"), r"\)")),
    "discardableResult",
    "dynamicCallable",
    "dynamicMemberLookup",
    "escaping",
    "freestanding",
    "frozen",
    "GKInspectable",
    "IBAction",
    "IBDesignable",
    "IBInspectable",
    "IBOutlet",
    "IBSegueAction",
    "inlinable",
    "main",
    "nonobjc",
    "NSApplicationMain",
    "NSCopying",
    "NSManaged",
    Regex(concat(r"objc\(", _src(identifier), r"\)")),
    "objc",
    "objcMembers",
    "propertyWrapper",
    "requires_stored_property_inits",
    "resultBuilder",
    "Sendable",
    "testable",
    "UIApplicationMain",
    "unchecked",
    "unknown",
    "usableFromInline",
    "warn_unqualified_access",
]

# Contextual keywords used in @available and #(un)available.
availabilityKeywords: list[str] = [
    "iOS",
    "iOSApplicationExtension",
    "macOS",
    "macOSApplicationExtension",
    "macCatalyst",
    "macCatalystApplicationExtension",
    "watchOS",
    "watchOSApplicationExtension",
    "tvOS",
    "tvOSApplicationExtension",
    "swift",
]
