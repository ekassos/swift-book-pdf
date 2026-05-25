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
from swift_book_pdf.pdf.layout import PDFDocumentConfig
from swift_book_pdf.pdf.options import EngineKind


@dataclass(frozen=True, kw_only=True)
class PDFConfig(BaseBuildConfig):
    """Resolved configuration for PDF builds.

    Attributes:
        doc_config: PDF document layout configuration.
        engine_kind: PDF engine implementation.
        override_version: Optional Swift version override.
    """

    doc_config: PDFDocumentConfig
    engine_kind: EngineKind
    override_version: str | None = None

    output_format: ClassVar[OutputFormat] = OutputFormat.PDF

    def diagnostic_details(self) -> str:
        """Format resolved PDF build details for debug diagnostics."""
        return str(self.doc_config)

    def build_error_details(self) -> str:
        """Format backend-specific details for unexpected build errors."""
        return ""
