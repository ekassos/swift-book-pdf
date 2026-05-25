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

"""LaTeX page geometry helpers."""

from swift_book_pdf.pdf.config import PaperSize


def get_geometry_opts(paper_size: PaperSize, gutter: bool = True) -> str:
    return {
        PaperSize.A4: f"a4paper,{'inner=1.67in,outer=0.9in' if gutter else 'hmargin=1.285in'}",
        PaperSize.LETTER: f"letterpaper,{'inner=1.9in,outer=0.9in' if gutter else 'hmargin=1.4in'}",
        PaperSize.LEGAL: f"legalpaper,{'inner=1.9in,outer=0.9in' if gutter else 'hmargin=1.4in'}",
    }[paper_size]
