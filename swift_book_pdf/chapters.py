# Copyright 2025 Evangelos Kassos
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

import os

from swift_book_pdf.schema import ChapterMetadata


def generate_chapter_metadata(
    root_dir: str, target_directories: list[str]
) -> dict[str, ChapterMetadata]:
    """
    Generate metadata for all chapters in the specified `target_directories`.

    Args:
        root_dir: The root directory of the project.
        target_directories: A list of directories to search for chapters.

    Returns:
        A dictionary mapping the lowercase chapter key to the ChapterMetadata object.
    """
    chapter_metadata: dict[str, ChapterMetadata] = {}
    for directory in target_directories:
        dir_path = os.path.join(root_dir, directory)
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        for file_name in os.listdir(dir_path):
            if file_name.endswith(".md"):
                file_key = file_name.replace(".md", "")
                file_path = os.path.join(dir_path, file_name)
                header_line = None
                subtitle_line = None
                with open(file_path, "r", encoding="utf-8") as f:
                    line = f.readline()
                    while line:
                        if line.startswith("# "):
                            header_line = line.lstrip("#").strip()
                            line = f.readline()
                            continue
                        if line.strip():
                            subtitle_line = line.strip()
                            break
                        line = f.readline()
                chapter_metadata[file_key.lower()] = ChapterMetadata(
                    file_path=file_path,
                    header_line=header_line,
                    subtitle_line=subtitle_line,
                )
    return chapter_metadata
