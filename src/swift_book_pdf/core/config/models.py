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

"""Backend-neutral configuration data shared by PDF and EPUB builders."""

from dataclasses import dataclass
from typing import ClassVar

from swift_book_pdf.core.output import OutputFormat


@dataclass(frozen=True)
class BuildSourceConfig:
    """User-selected Swift Book source inputs.

    Attributes:
        temp_dir: Temporary build directory.
        input_path: Optional local Swift Book repository path.
        source_ref: Optional Swift Book Git ref.
        source_sha: Optional Swift Book commit SHA.
    """

    temp_dir: str
    input_path: str | None = None
    source_ref: str | None = None
    source_sha: str | None = None


@dataclass(frozen=True)
class ResolvedBuildSource:
    """Resolved Swift Book source paths and derived metadata.

    Attributes:
        temp_dir: Temporary build directory.
        root_dir: Path to the resolved `TSPL.docc` root.
        toc_file_path: Path to the Swift Book table-of-contents document.
        assets_dir: Path to the upstream Swift Book image assets.
        original_work_copyright_year_range: Optional inclusive copyright year
            range detected from the upstream Swift Book source.
    """

    temp_dir: str
    root_dir: str
    toc_file_path: str
    assets_dir: str
    original_work_copyright_year_range: tuple[int, int] | None


@dataclass(frozen=True, kw_only=True)
class BaseBuildConfig:
    """Common resolved build configuration for all output backends.

    Attributes:
        source: Resolved Swift Book source paths and derived metadata.
        output_path: Destination output path.
        dangerously_skip_legal_notices: Whether generated legal notices are
            intentionally omitted.
    """

    source: ResolvedBuildSource
    output_path: str
    dangerously_skip_legal_notices: bool = False

    output_format: ClassVar[OutputFormat]

    @property
    def temp_dir(self) -> str:
        """Temporary build directory."""
        return self.source.temp_dir

    @property
    def root_dir(self) -> str:
        """Path to the resolved `TSPL.docc` root."""
        return self.source.root_dir

    @property
    def toc_file_path(self) -> str:
        """Path to the Swift Book table-of-contents document."""
        return self.source.toc_file_path

    @property
    def assets_dir(self) -> str:
        """Path to the upstream Swift Book image assets."""
        return self.source.assets_dir

    @property
    def original_work_copyright_year_range(
        self,
    ) -> tuple[int, int] | None:
        """Inclusive copyright years detected from upstream Swift sources."""
        return self.source.original_work_copyright_year_range
