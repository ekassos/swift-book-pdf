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

from dataclasses import dataclass
from pathlib import Path

from swift_book_pdf.core.generated.summary import PublishBookSummaryConfig
from swift_book_pdf.core.generated.summary.constants import (
    SUMMARY_HEADING_LINE_COUNT,
    SUMMARY_SCRIPT_END_PATTERN,
)
from swift_book_pdf.core.generated.summary.script import scan_summary_script


def parse_summary_config(
    publish_book_script: Path,
    generate_grammar_script: Path,
) -> PublishBookSummaryConfig:
    """Parse Summary of the Grammar generation config from upstream scripts.

    Args:
        publish_book_script: Path to the legacy `bin/publish-book` script.
        generate_grammar_script: Path to the current `bin/generate-grammar`
            script.

    Returns:
        Parsed title, subtitle, and grammar source paths. The current
        generate-grammar script is preferred when it provides source paths.
    """
    generate_grammar_config = parse_generate_grammar(generate_grammar_script)
    if generate_grammar_config.source_paths:
        return generate_grammar_config
    return parse_publish_book(publish_book_script)


def parse_generate_grammar(
    generate_grammar_script: Path,
) -> PublishBookSummaryConfig:
    """Parse the current upstream generate-grammar script layout.

    Args:
        generate_grammar_script: Path to `bin/generate-grammar`.

    Returns:
        Parsed summary config. Missing scripts return an empty config.
    """
    if not generate_grammar_script.exists():
        return PublishBookSummaryConfig()

    echo_values, source_paths = scan_summary_script(generate_grammar_script)
    return build_summary_config(echo_values, source_paths)


def parse_publish_book(
    publish_book_script: Path,
) -> PublishBookSummaryConfig:
    """Parse the legacy publish-book embedded summary block.

    Args:
        publish_book_script: Path to `bin/publish-book`.

    Returns:
        Parsed summary config. Only lines inside the `summary_chapter` block are
        considered. Missing scripts return an empty config.
    """
    if not publish_book_script.exists():
        return PublishBookSummaryConfig()

    echo_values, source_paths = scan_summary_script(
        publish_book_script,
        PublishBookSummaryBlockFilter(),
    )
    return build_summary_config(echo_values, source_paths)


@dataclass
class PublishBookSummaryBlockFilter:
    """Select lines inside the legacy `publish-book` summary block.

    The old shell script writes the Summary of the Grammar by assigning a
    `summary_chapter` path and then piping a brace-delimited block into that
    file. This callable keeps that scan state explicit so `parse_publish_book`
    does not need nested mutable variables.
    """

    saw_summary_chapter: bool = False
    """Whether the `summary_chapter` assignment has been seen."""

    in_summary_block: bool = False
    """Whether the current line is inside the brace-delimited write block."""

    def __call__(self, line: str) -> bool:
        """Return whether a publish-book line belongs to the summary block.

        Args:
            line: Stripped shell-script line.

        Returns:
            True while scanning lines inside the legacy summary block.
        """
        if not self.saw_summary_chapter:
            self.saw_summary_chapter = line.startswith('summary_chapter="')
            return False

        if not self.in_summary_block and line == "{":
            self.in_summary_block = True
            return False

        if self.in_summary_block and SUMMARY_SCRIPT_END_PATTERN.match(line):
            self.in_summary_block = False
            return False

        return self.in_summary_block


def build_summary_config(
    echo_values: list[str],
    source_paths: list[Path],
) -> PublishBookSummaryConfig:
    """Build a summary config from collected script output and source paths.

    Args:
        echo_values: Values captured from script `echo` commands.
        source_paths: Source chapter paths captured from awk invocations.

    Returns:
        A config with title/subtitle when the first two echo values match the
        expected heading shape. Source paths are preserved even when title
        metadata is unavailable.
    """
    if len(echo_values) < SUMMARY_HEADING_LINE_COUNT or not echo_values[
        0
    ].startswith("# "):
        return PublishBookSummaryConfig(
            source_paths=[str(path) for path in source_paths]
        )
    return PublishBookSummaryConfig(
        title=echo_values[0][2:],
        subtitle=echo_values[1],
        source_paths=[str(path) for path in source_paths],
    )
