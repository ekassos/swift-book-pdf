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

"""Write generated Summary of the Grammar Markdown files."""

import logging
import shutil
from pathlib import Path

from swift_book_pdf.core.generated.summary import GeneratedSummary
from swift_book_pdf.core.generated.summary.config import parse_summary_config
from swift_book_pdf.core.generated.summary.constants import (
    SUMMARY_DEFAULT_SUBTITLE,
    SUMMARY_DEFAULT_TITLE,
    SUMMARY_OF_THE_GRAMMAR_FILE_NAME,
)
from swift_book_pdf.core.generated.summary.extract import extract_summary_text
from swift_book_pdf.core.generated.summary.normalize import (
    normalize_grammar_summary_text,
)
from swift_book_pdf.core.generated.summary.sources import (
    resolve_summary_source_paths,
)

logger = logging.getLogger(__name__)


def generate_summary_file(
    repo_root: Path,
    temp_dir: Path,
) -> GeneratedSummary | None:
    """Generate `SummaryOfTheGrammar.md` into the temporary output tree.

    Args:
        repo_root: Path to the `swift-book` repository root.
        temp_dir: Temporary output directory.

    Returns:
        Metadata for the generated file, or `None` when source paths cannot be
        resolved.
    """
    publish_book_script = repo_root / "bin" / "publish-book"
    generate_grammar_script = repo_root / "bin" / "generate-grammar"
    publish_book_config = parse_summary_config(
        publish_book_script,
        generate_grammar_script,
    )
    source_paths = resolve_summary_source_paths(
        repo_root,
        publish_book_script,
        generate_grammar_script,
        [Path(path) for path in publish_book_config.source_paths],
    )
    if source_paths is None:
        return None
    title = publish_book_config.title or SUMMARY_DEFAULT_TITLE
    subtitle = publish_book_config.subtitle or SUMMARY_DEFAULT_SUBTITLE

    output_dir = temp_dir / "generated" / "ReferenceManual"
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / SUMMARY_OF_THE_GRAMMAR_FILE_NAME

    logger.info("Generating Summary of the Grammar...")

    summary_path.write_text(
        build_summary_text(
            title,
            subtitle,
            source_paths,
            repo_root / "bin" / "extract_grammar.awk",
            shutil.which("awk"),
        ),
        encoding="utf-8",
    )
    return GeneratedSummary(
        path=str(summary_path),
        title=title,
        subtitle=subtitle,
    )


def build_summary_text(
    title: str,
    subtitle: str,
    source_paths: list[Path],
    extract_grammar_script: Path,
    awk_executable: str | None,
) -> str:
    """Build the full generated summary chapter Markdown text.

    Args:
        title: Chapter title to write as the first heading.
        subtitle: Subtitle paragraph below the heading.
        source_paths: Source chapters used for grammar extraction.
        extract_grammar_script: Path to upstream `extract_grammar.awk`.
        awk_executable: Resolved `awk` executable path, or `None`.

    Returns:
        Complete Markdown text for the generated chapter.
    """
    summary_text = extract_summary_text(
        source_paths, extract_grammar_script, awk_executable
    )
    return (
        f"# {title}\n\n"
        f"{subtitle}\n\n"
        f"{normalize_grammar_summary_text(summary_text)}"
    )
