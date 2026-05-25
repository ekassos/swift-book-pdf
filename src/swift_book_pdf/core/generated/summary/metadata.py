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

from pathlib import Path

from swift_book_pdf.core.generated.summary.constants import (
    SUMMARY_OF_THE_GRAMMAR_KEY,
)
from swift_book_pdf.core.generated.summary.generation import (
    generate_summary_file,
)
from swift_book_pdf.core.source import ChapterMetadata


def generate_missing_generated_chapter_metadata(
    root_dir: str,
    temp_dir: str,
    doc_tags: list[str],
    chapter_metadata: dict[str, ChapterMetadata],
) -> dict[str, ChapterMetadata]:
    """Generate metadata for generated chapters requested by the TOC.

    Args:
        root_dir: Path to `TSPL.docc`.
        temp_dir: Temporary output directory where generated files are written.
        doc_tags: Document tags requested by the source TOC.
        chapter_metadata: Metadata already discovered from source chapters.

    Returns:
        Metadata for generated chapters that were requested and successfully
        written. Returns an empty mapping when no generation is needed.
    """
    if not should_generate_summary(doc_tags, chapter_metadata):
        return {}

    generated_summary = generate_summary_file(
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


def should_generate_summary(
    doc_tags: list[str],
    chapter_metadata: dict[str, ChapterMetadata],
) -> bool:
    """Return whether the TOC asks for a missing generated summary chapter.

    Args:
        doc_tags: Document tags requested by the source TOC.
        chapter_metadata: Metadata already available from source chapters.

    Returns:
        True when the Summary of the Grammar tag is present in the TOC but its
        source file was not found.
    """
    return (
        SUMMARY_OF_THE_GRAMMAR_KEY in {tag.lower() for tag in doc_tags}
        and SUMMARY_OF_THE_GRAMMAR_KEY not in chapter_metadata
    )


__all__ = [
    "generate_missing_generated_chapter_metadata",
    "generate_summary_file",
    "should_generate_summary",
]
