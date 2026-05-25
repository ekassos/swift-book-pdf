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

"""Backend-neutral build configuration models and source resolution."""

from swift_book_pdf.core.config.models import (
    BaseBuildConfig,
    BuildSourceConfig,
    ResolvedBuildSource,
)
from swift_book_pdf.core.config.source import resolve_build_source

__all__ = [
    "BaseBuildConfig",
    "BuildSourceConfig",
    "ResolvedBuildSource",
    "resolve_build_source",
]
