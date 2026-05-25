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

import re
from pathlib import Path

SWIFT_BOOK_COPYRIGHT_PATTERN = re.compile(
    r"Copyright\s+(?:\(c\)|©)\s*(\d{4})"
    r"(?:\s*[-\u2013]\s*(\d{4}))?"
    r"\s+Apple Inc\. and the Swift project authors",
)


def find_swift_book_copyright_year_range(
    root_dir: str | Path,
) -> tuple[int, int] | None:
    """Find the copyright year range declared by Swift Book source files.

    Args:
        root_dir: Path to the `TSPL.docc` directory. The function scans the
            containing repository and skips `.git`.

    Returns:
        A `(start_year, end_year)` tuple spanning all matched copyright lines,
        or `None` when no matching copyright line is found.
    """
    repo_dir = Path(root_dir).parent
    start_year: int | None = None
    end_year: int | None = None

    for path in repo_dir.rglob("*"):
        if path.is_dir() or ".git" in path.parts:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for match in SWIFT_BOOK_COPYRIGHT_PATTERN.finditer(content):
            match_start_year = int(match.group(1))
            match_end_year = int(match.group(2) or match.group(1))
            if start_year is None or match_start_year < start_year:
                start_year = match_start_year
            if end_year is None or match_end_year > end_year:
                end_year = match_end_year

    if start_year is None or end_year is None:
        return None

    return start_year, end_year
