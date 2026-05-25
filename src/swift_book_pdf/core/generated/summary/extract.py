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

import logging
import subprocess
from pathlib import Path

from swift_book_pdf.core.generated.summary.messages import (
    AWK_FAILED_FALLBACK,
    AWK_GENERATION_FAILED,
    AWK_UNAVAILABLE_FALLBACK,
)

logger = logging.getLogger(__name__)


def extract_summary_text(
    source_paths: list[Path],
    extract_grammar_script: Path,
    awk_executable: str | None,
) -> str:
    """Extract grammar text with upstream awk when possible, else Python.

    Args:
        source_paths: Markdown chapters to scan for grammar sections.
        extract_grammar_script: Path to upstream `extract_grammar.awk`.
        awk_executable: Resolved `awk` executable path, or `None`.

    Returns:
        Extracted Markdown grammar text.
    """
    awk_text = extract_summary_text_with_awk(
        source_paths,
        extract_grammar_script,
        awk_executable,
    )
    if awk_text is not None:
        return awk_text

    if awk_executable is None or not extract_grammar_script.exists():
        logger.warning(AWK_UNAVAILABLE_FALLBACK)
    else:
        logger.warning(AWK_FAILED_FALLBACK)
    return extract_summary_text_in_python(source_paths)


def extract_summary_text_in_python(source_paths: list[Path]) -> str:
    """Extract grammar sections with the built-in Markdown scanner.

    Args:
        source_paths: Markdown chapters to scan in order.

    Returns:
        Concatenated grammar sections.
    """
    return "".join(
        extract_grammar_from_markdown(path) for path in source_paths
    )


def extract_summary_text_with_awk(
    source_paths: list[Path],
    extract_grammar_script: Path,
    awk_executable: str | None,
) -> str | None:
    """Run upstream extract_grammar.awk and return its output if successful.

    Args:
        source_paths: Markdown chapters passed to awk.
        extract_grammar_script: Path to the awk script.
        awk_executable: Resolved `awk` executable path, or `None`.

    Returns:
        Awk output when awk is available and succeeds; otherwise `None`.
    """
    if awk_executable is None or not extract_grammar_script.exists():
        return None

    try:
        result = subprocess.run(  # noqa: S603
            [
                awk_executable,
                "-f",
                str(extract_grammar_script),
                *(str(path) for path in source_paths),
            ],
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        logger.warning(AWK_GENERATION_FAILED, error)
        return None
    return result.stdout


def extract_grammar_from_markdown(chapter_path: Path) -> str:
    """Extract blockquoted grammar sections from one Markdown chapter.

    Args:
        chapter_path: Markdown chapter to scan.

    Returns:
        Markdown containing level-two chapter headings and contiguous
        blockquoted grammar sections.
    """
    extracted_lines: list[str] = []
    in_grammar = False

    with chapter_path.open("r", encoding="utf-8") as chapter_file:
        for line in chapter_file:
            if line.startswith("# "):
                extracted_lines.extend((line.replace("#", "##", 1), "\n"))
                continue

            if line.startswith("> Grammar of "):
                in_grammar = True

            if in_grammar and line.startswith(">"):
                extracted_lines.append(line)
                continue

            if in_grammar and not line.strip():
                in_grammar = False
                extracted_lines.append("\n")

    return "".join(extracted_lines)
