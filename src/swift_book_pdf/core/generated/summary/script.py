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

"""Shell-script scanning helpers for summary generation metadata."""

from collections.abc import Callable, Iterable
from pathlib import Path

from swift_book_pdf.core.generated.summary.constants import (
    SUMMARY_ECHO_PATTERN,
    SUMMARY_HEADING_LINE_COUNT,
    SUMMARY_SOURCE_PATH_PATTERN,
)

LineFilter = Callable[[str], bool]


def scan_summary_script(
    script_path: Path,
    include_line: LineFilter | None = None,
) -> tuple[list[str], list[Path]]:
    """Collect summary heading echoes and grammar source paths from a script.

    Args:
        script_path: Shell script to scan.
        include_line: Optional filter for limiting the scan to relevant script
            regions, such as the legacy publish-book summary block.

    Returns:
        A tuple containing heading echo values and grammar source paths. Missing
        scripts return two empty lists.
    """
    echo_values: list[str] = []
    source_paths: list[Path] = []
    if not script_path.exists():
        return echo_values, source_paths

    for line in _iter_relevant_script_lines(script_path, include_line):
        match = SUMMARY_ECHO_PATTERN.fullmatch(line)
        if match and match.group(1):
            echo_values.append(match.group(1))
            echo_values = echo_values[:SUMMARY_HEADING_LINE_COUNT]

        source_match = SUMMARY_SOURCE_PATH_PATTERN.fullmatch(line)
        if source_match:
            source_paths.append(
                script_path.parent.parent / source_match.group("path")
            )

    return echo_values, source_paths


def _iter_relevant_script_lines(
    script_path: Path,
    include_line: LineFilter | None,
) -> Iterable[str]:
    """Yield stripped script lines accepted by the optional line filter."""
    with script_path.open("r", encoding="utf-8") as script_file:
        for raw_line in script_file:
            line = raw_line.strip()
            if include_line is None or include_line(line):
                yield line
