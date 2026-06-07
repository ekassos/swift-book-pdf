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

from swift_book_pdf.lexer.engine import highlight
from swift_book_pdf.lexer.markup import render
from swift_book_pdf.lexer.swift import build_language


def highlight_base_swift(code: str) -> str:
    """Highlight Swift with the unmodified highlight.js Swift grammar."""
    return render(highlight(build_language(), code))
