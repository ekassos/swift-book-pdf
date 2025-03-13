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

from swift_book_pdf.schema import PaperSize, RenderingMode


class DocConfig:
    def __init__(
        self,
        mode: RenderingMode = RenderingMode.DIGITAL,
        paper_size: PaperSize = PaperSize.LETTER,
        typesets: int = 4,
    ):
        self.mode = mode
        self.paper_size = paper_size
        self.typesets = typesets
