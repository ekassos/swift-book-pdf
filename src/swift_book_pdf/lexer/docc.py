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

"""Swift-DocC-Render-specific Swift lexer adjustments."""

from __future__ import annotations

from swift_book_pdf.lexer.swift import Mode, build_language


def build_docc_render_language() -> Mode:
    r"""Build Swift-DocC-Render's Swift grammar variant.

    Start from this package's port of highlight.js Swift and apply DocC
    Render's multiline-string escaped-newline override. DocC Render's older
    class-declaration override is already represented by the current grammar:
    ``class func`` and ``class var`` have dedicated modes, and type
    declarations require an identifier after the declaration keyword.

    Returns:
        Highlight.js mode tree for DocC-rendered Swift code blocks.
    """
    language = build_language()
    _override_multiline_string_escaped_newline(language)
    return language


def _override_multiline_string_escaped_newline(language: Mode) -> None:
    """Replace escaped-newline submodes in multiline string variants.

    Args:
        language: Swift highlight.js mode tree to mutate.
    """
    contains = language.get("contains")
    if not isinstance(contains, list):
        return
    string_mode = next(
        (
            mode
            for mode in contains
            if isinstance(mode, dict) and mode.get("className") == "string"
        ),
        None,
    )
    if not isinstance(string_mode, dict):
        return
    variants = string_mode.get("variants")
    if not isinstance(variants, list):
        return
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        submodes = variant.get("contains")
        if not isinstance(submodes, list):
            continue
        for index, mode in enumerate(submodes):
            if _is_escaped_newline_mode(mode):
                submodes[index] = {
                    "className": "subst",
                    "begin": r"\\#{0,3}",
                    "end": r"[\t ]*(?:[\r\n]|\r\n)",
                    "excludeEnd": True,
                }


def _is_escaped_newline_mode(mode: object) -> bool:
    """Return whether a submode matches Swift-DocC-Render's source check."""
    if not isinstance(mode, dict):
        return False
    if mode.get("className") != "subst":
        return False
    match = mode.get("match")
    if match is None:
        return False
    match_str = str(match)
    return match_str.startswith("\\") and match_str.endswith(
        r"[\t ]*(?:[\r\n]|\r\n)"
    )


__all__ = ["build_docc_render_language"]
