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

from pydantic import BaseModel


class SwiftBookRepoFilePaths(BaseModel):
    """Resolved paths needed to read the Swift Book source repository."""

    toc_file_path: str
    """Path to `The-Swift-Programming-Language.md`."""

    root_dir: str
    """Path to the `TSPL.docc` directory."""

    assets_dir: str
    """Path to the source image assets directory."""


class ChapterMetadata(BaseModel):
    """Title, subtitle, and path metadata for a Swift Book chapter."""

    file_path: str | None = None
    """Optional source Markdown path."""

    header_line: str | None = None
    """Optional top-level chapter title."""

    subtitle_line: str | None = None
    """Optional first non-empty line after the title."""
