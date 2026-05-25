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

"""Shared cursor state for block parser components."""

from dataclasses import dataclass, field

from swift_book_pdf.core.blocks.models import Block


@dataclass
class BlockParserState:
    """Mutable cursor state shared by composed block parser components."""

    lines: list[str]
    """Markdown source lines to parse."""

    idx: int = 0
    """Current parser cursor position."""

    blocks: list[Block] = field(default_factory=list)
    """Parsed blocks accumulated in source order."""

    @property
    def n(self) -> int:
        """Return the number of source lines available to the parser.

        Returns:
            Total source line count.
        """
        return len(self.lines)
