# Copyright 2025-2026 Evangelos Kassos
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

from swift_book_pdf.core.generated.notices import (
    NOTICES_DOC_TAG,
    build_notices_chapter_metadata,
)
from swift_book_pdf.core.generated.summary.metadata import (
    generate_missing_generated_chapter_metadata,
)
from swift_book_pdf.core.navigation.chapters import generate_chapter_metadata
from swift_book_pdf.core.navigation.doc_tags import extract_doc_tags


class TableOfContents:
    """Loaded Swift Book table of contents plus derived chapter metadata.

    The instance keeps source document tags separate from generated entries so
    builders can decide whether to include generated notices and generated
    chapters.
    """

    def __init__(
        self,
        root_dir: str,
        tspl_file_path: str,
        temp_dir: str,
        include_notices: bool = True,
    ) -> None:
        """Load TOC content and prepare metadata needed by output builders.

        Args:
            root_dir: Path to `TSPL.docc`.
            tspl_file_path: Path to the source table of contents Markdown file.
            temp_dir: Temporary output directory used for generated chapters.
            include_notices: Whether to append generated notices metadata.

        Raises:
            FileNotFoundError: If `tspl_file_path` or a required chapter
                directory is missing.
        """
        self.tspl_file_path = tspl_file_path
        self.target_directories = [
            "GuidedTour",
            "LanguageGuide",
            "ReferenceManual",
            "RevisionHistory",
        ]

        with Path(tspl_file_path).open("r", encoding="utf-8") as file:
            self.file_content = file.readlines()

        self.source_doc_tags = extract_doc_tags(self.file_content)
        self.include_notices = include_notices
        self.doc_tags = (
            [*self.source_doc_tags, NOTICES_DOC_TAG]
            if include_notices
            else [*self.source_doc_tags]
        )
        self.chapter_metadata = generate_chapter_metadata(
            root_dir,
            self.target_directories,
        )
        self.chapter_metadata.update(
            generate_missing_generated_chapter_metadata(
                root_dir,
                temp_dir,
                self.source_doc_tags,
                self.chapter_metadata,
            ),
        )
        if include_notices:
            self.chapter_metadata[NOTICES_DOC_TAG.lower()] = (
                build_notices_chapter_metadata()
            )
