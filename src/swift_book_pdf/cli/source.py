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

"""Shared CLI source-resolution helpers."""

from swift_book_pdf.core.config import (
    BuildSourceConfig,
    ResolvedBuildSource,
    resolve_build_source,
)


def resolve_cli_build_source(
    *,
    temp_dir: str,
    input_path: str | None,
    source_ref: str | None,
    source_sha: str | None,
) -> ResolvedBuildSource:
    """Resolve Swift Book source options parsed by a CLI command.

    Args:
        temp_dir: Temporary build directory.
        input_path: Optional local Swift Book repository path.
        source_ref: Optional Swift Book Git ref.
        source_sha: Optional Swift Book commit SHA.

    Returns:
        Resolved source paths and derived copyright metadata.
    """
    return resolve_build_source(
        BuildSourceConfig(
            temp_dir=temp_dir,
            input_path=input_path,
            source_ref=source_ref,
            source_sha=source_sha,
        )
    )
