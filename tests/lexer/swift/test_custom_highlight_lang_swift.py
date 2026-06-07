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

# Ports swift-docc-render's tests/unit/utils/custom-highlight-lang/swift.spec.js
# against this package's equivalent of `swift(hljs)`,
# `build_docc_render_language`.

from __future__ import annotations

import re

from swift_book_pdf.lexer.docc import build_docc_render_language

# The class/type declaration mode's leading `begin` regex in the current
# highlight.js Swift grammar (highlight.js 11.10 replaced the old
# `beginKeywords` class mode with this `TYPE_DECLARATION`).
_TYPE_DECLARATION_BEGIN = "(struct|protocol|class|extension|enum|actor)"


def _class_mode() -> dict:
    """Return the class declaration mode the way swift.spec.js locates it.

    Returns:
        The mode whose array `begin` matches a class declaration.
    """
    language = build_docc_render_language()
    contains = language["contains"]
    for mode in contains:
        if not isinstance(mode, dict):
            continue
        begin = mode.get("begin")
        if (
            isinstance(begin, list)
            and begin
            and re.search(begin[0], "class Foobar {")
        ):
            return mode
    raise AssertionError("no class declaration mode found")


def test_recognizes_the_distributed_keyword() -> None:
    language = build_docc_render_language()
    assert "distributed" in language["keywords"]["keyword"]


def test_class_mode_does_not_have_a_begin_keywords_attribute() -> None:
    assert "beginKeywords" not in _class_mode()


def test_class_mode_does_have_a_begin_attribute() -> None:
    mode = _class_mode()
    assert isinstance(mode["begin"], list)
    assert mode["begin"][0] == _TYPE_DECLARATION_BEGIN
