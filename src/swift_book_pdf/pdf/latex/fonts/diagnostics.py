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

"""Font-related LaTeX log diagnostics."""

import re

FONT_TROUBLESHOOTING_URL = (
    "https://github.com/ekassos/swift-book-pdf/wiki/Troubleshooting"
)


def check_for_missing_font_logs(log_line: str) -> None:
    """Raise a user-facing error when LuaTeX reports a missing glyph.

    Args:
        log_line: Raw line emitted by LuaLaTeX.

    Raises:
        ValueError: If the line reports an unsupported character for the
            configured font.
    """
    pattern = re.compile(
        r"Missing character: There is no (?P<char>\S+) "
        r"\((?P<code>U\+\w+)\) in font name:",
    )

    match = pattern.search(log_line)
    if match:
        missing_char = match.group("char")
        unicode_code = match.group("code")
        raise ValueError(
            f"The fonts you specified do not support character {missing_char} ({unicode_code}).\nIf you are using a custom font, please ensure that it supports the character set you are trying to use.\nOtherwise, see {FONT_TROUBLESHOOTING_URL} for more information.",
        )
