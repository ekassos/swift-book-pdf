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

"""PDF build configuration."""

from dataclasses import dataclass
from typing import ClassVar

from swift_book_pdf.core.config.models import BaseBuildConfig
from swift_book_pdf.core.output import OutputFormat
from swift_book_pdf.pdf.latex.fonts import FontConfig
from swift_book_pdf.pdf.layout import DocConfig
from swift_book_pdf.pdf.options import EngineKind


@dataclass(frozen=True, kw_only=True)
class PDFConfig(BaseBuildConfig):
    """Resolved configuration for PDF builds.

    Attributes:
        font_config: PDF font configuration.
        doc_config: PDF document layout configuration.
        override_version: Optional Swift version override.
    """

    font_config: FontConfig
    doc_config: DocConfig
    engine_kind: EngineKind = EngineKind.LATEX
    override_version: str | None = None

    output_format: ClassVar[OutputFormat] = OutputFormat.PDF
