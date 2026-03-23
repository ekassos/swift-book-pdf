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
import re
import shutil
import subprocess
from pathlib import Path

from swift_book_pdf.schema import (
    ChapterMetadata,
    GeneratedSummary,
    PublishBookSummaryConfig,
)

logger = logging.getLogger(__name__)

SUMMARY_OF_THE_GRAMMAR_KEY = "summaryofthegrammar"
SUMMARY_OF_THE_GRAMMAR_FILE_NAME = "SummaryOfTheGrammar.md"
SUMMARY_DEFAULT_TITLE = "Summary of the Grammar"
SUMMARY_DEFAULT_SUBTITLE = "Read the whole formal grammar."
SUMMARY_HEADING_LINE_COUNT = 2
SUMMARY_ECHO_PATTERN = re.compile(r'echo\s+"([^"]*)"')
SUMMARY_SOURCE_PATH_PATTERN = re.compile(
    r"awk -f bin/extract_grammar\.awk "
    r"(TSPL\.docc/ReferenceManual/[A-Za-z0-9]+\.md)"
)
SUMMARY_FALLBACK_SOURCE_PATHS = (
    "TSPL.docc/ReferenceManual/LexicalStructure.md",
    "TSPL.docc/ReferenceManual/Types.md",
    "TSPL.docc/ReferenceManual/Expressions.md",
    "TSPL.docc/ReferenceManual/Statements.md",
    "TSPL.docc/ReferenceManual/Declarations.md",
    "TSPL.docc/ReferenceManual/Attributes.md",
    "TSPL.docc/ReferenceManual/Patterns.md",
    "TSPL.docc/ReferenceManual/GenericParametersAndArguments.md",
)


def generate_missing_chapter_metadata(
    root_dir: str,
    temp_dir: str,
    doc_tags: list[str],
    chapter_metadata: dict[str, ChapterMetadata],
) -> dict[str, ChapterMetadata]:
    if not _should_generate_summary(doc_tags, chapter_metadata):
        return {}

    generated_summary = _generate_summary_file(
        Path(root_dir).parent, Path(temp_dir)
    )
    if generated_summary is None:
        return {}

    return {
        SUMMARY_OF_THE_GRAMMAR_KEY: ChapterMetadata(
            file_path=generated_summary.path,
            header_line=generated_summary.title,
            subtitle_line=generated_summary.subtitle,
        )
    }


def _should_generate_summary(
    doc_tags: list[str],
    chapter_metadata: dict[str, ChapterMetadata],
) -> bool:
    return (
        SUMMARY_OF_THE_GRAMMAR_KEY in {tag.lower() for tag in doc_tags}
        and SUMMARY_OF_THE_GRAMMAR_KEY not in chapter_metadata
    )


def _generate_summary_file(
    repo_root: Path,
    temp_dir: Path,
) -> GeneratedSummary | None:
    publish_book_script = repo_root / "bin" / "publish-book"
    publish_book_config = _parse_publish_book(publish_book_script)
    source_paths = _resolve_summary_source_paths(
        repo_root,
        publish_book_script,
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
        _build_summary_text(
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


def _build_summary_text(
    title: str,
    subtitle: str,
    source_paths: list[Path],
    extract_grammar_script: Path,
    awk_executable: str | None,
) -> str:
    return (
        f"# {title}\n\n"
        f"{subtitle}\n\n"
        f"{_extract_summary_text(source_paths, extract_grammar_script, awk_executable)}"
    )


def _parse_publish_book(
    publish_book_script: Path,
) -> PublishBookSummaryConfig:
    if not publish_book_script.exists():
        return PublishBookSummaryConfig()

    saw_summary_chapter = False
    in_summary_block = False
    echo_values: list[str] = []
    source_paths: list[Path] = []

    with publish_book_script.open("r", encoding="utf-8") as script_file:
        for raw_line in script_file:
            line = raw_line.strip()
            if not saw_summary_chapter:
                saw_summary_chapter = line.startswith('summary_chapter="')
                continue

            if not in_summary_block and line == "{":
                in_summary_block = True

            if in_summary_block:
                match = SUMMARY_ECHO_PATTERN.fullmatch(line)
                if match and match.group(1):
                    echo_values.append(match.group(1))
                    if len(echo_values) > SUMMARY_HEADING_LINE_COUNT:
                        echo_values = echo_values[:SUMMARY_HEADING_LINE_COUNT]

            source_match = SUMMARY_SOURCE_PATH_PATTERN.search(line)
            if source_match:
                source_paths.append(
                    publish_book_script.parent.parent / source_match.group(1)
                )

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


def _resolve_summary_source_paths(
    repo_root: Path,
    publish_book_script: Path,
    publish_book_source_paths: list[Path],
) -> list[Path] | None:
    if publish_book_source_paths:
        return publish_book_source_paths

    if publish_book_script.exists():
        logger.warning(
            "Couldn't parse Summary of the Grammar source chapters from swift-book/bin/publish-book; using fallback chapter list.",
        )
    else:
        logger.warning(
            "swift-book/bin/publish-book is missing; using fallback chapter list for Summary of the Grammar.",
        )

    fallback_paths = [
        repo_root / path for path in SUMMARY_FALLBACK_SOURCE_PATHS
    ]
    missing_paths = [str(path) for path in fallback_paths if not path.exists()]
    if missing_paths:
        logger.warning(
            "Couldn't generate Summary of the Grammar because fallback source chapters are missing: %s",
            ", ".join(missing_paths),
        )
        return None
    return fallback_paths


def _extract_summary_text(
    source_paths: list[Path],
    extract_grammar_script: Path,
    awk_executable: str | None,
) -> str:
    awk_text = _extract_summary_text_with_awk(
        source_paths,
        extract_grammar_script,
        awk_executable,
    )
    if awk_text is not None:
        return awk_text

    if awk_executable is None or not extract_grammar_script.exists():
        logger.warning(
            "Falling back to built-in grammar extraction because swift-book/bin/extract_grammar.awk or `awk` is unavailable.",
        )
    else:
        logger.warning(
            "Falling back to built-in grammar extraction because swift-book/bin/extract_grammar.awk couldn't be used.",
        )
    return _extract_summary_text_in_python(source_paths)


def _extract_summary_text_in_python(source_paths: list[Path]) -> str:
    return "".join(
        _extract_grammar_from_markdown(path) for path in source_paths
    )


def _extract_summary_text_with_awk(
    source_paths: list[Path],
    extract_grammar_script: Path,
    awk_executable: str | None,
) -> str | None:
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
        logger.warning(
            "Couldn't generate Summary of the Grammar using swift-book/bin/extract_grammar.awk: %s",
            error,
        )
        return None
    return result.stdout


def _extract_grammar_from_markdown(chapter_path: Path) -> str:
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
