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

from pydantic import BaseModel, Field


class GeneratedSummary(BaseModel):
    """Generated Summary of the Grammar chapter metadata."""

    path: str
    """Path to the generated Markdown file."""

    title: str
    """Chapter title written into the generated file."""

    subtitle: str
    """Chapter subtitle written into the generated file."""


class PublishBookSummaryConfig(BaseModel):
    """Summary generation metadata parsed from upstream shell scripts."""

    title: str | None = None
    """Optional summary chapter title discovered from `echo` lines."""

    subtitle: str | None = None
    """Optional summary subtitle discovered from `echo` lines."""

    source_paths: list[str] = Field(default_factory=list)
    """Markdown chapter paths used to extract grammar blocks."""
