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

import logging

from swift_book_pdf.schema import Appearance, PaperSize, RenderingMode

logger = logging.getLogger(__name__)


class DocConfig:
    def __init__(  # noqa: PLR0913
        self,
        mode: RenderingMode = RenderingMode.DIGITAL,
        paper_size: PaperSize = PaperSize.LETTER,
        typesets: int = 4,
        dark_mode: bool = False,
        gutter: bool | None = None,
        font_size: float | None = None,
    ) -> None:
        self.mode = mode
        self.paper_size = paper_size
        self.typesets = typesets
        self.appearance = Appearance.DARK if dark_mode else Appearance.LIGHT
        self.gutter = True if gutter is None else gutter
        self.font_size = font_size if font_size is not None else 9.0
        if self.font_size <= 0:
            raise ValueError("Font size must be a positive number.")
        logger.debug(f"Rendering mode: {self.mode}")
        logger.debug(f"Paper size: {self.paper_size}")
        logger.debug(f"Typesets: {self.typesets}")
        logger.debug(f"Appearance: {self.appearance}")
        logger.debug(f"Book Gutter: {self.gutter}")
        logger.debug(f"Font size: {self.font_size}pt")
