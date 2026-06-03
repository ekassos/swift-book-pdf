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

from pathlib import Path

from swift_book_pdf.lexer import highlight_swift

_FIXTURES = Path(__file__).parent / "fixtures"


def test_tuples() -> None:
    source = (_FIXTURES / "tuples.txt").read_text()
    expected = (_FIXTURES / "tuples.expect.txt").read_text()
    # highlight.js's markup test harness compares trimmed output on
    # both sides; some .expect.txt fixtures were saved with an extra
    # or missing trailing newline, so normalize it before comparing.
    assert highlight_swift(source).rstrip("\n") == expected.rstrip("\n")
