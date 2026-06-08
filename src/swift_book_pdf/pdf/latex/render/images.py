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

"""LaTeX rendering for image blocks."""

import logging
import os
import struct
from pathlib import Path, PureWindowsPath

from swift_book_pdf.core.blocks.models import ImageBlock
from swift_book_pdf.pdf.config import Appearance

logger = logging.getLogger(__name__)
MAX_IMAGE_WIDTH_IN = 6.5


def convert_image_block(
    block: ImageBlock,
    assets_dir: str,
    appearance: Appearance,
) -> list[str]:
    """Render an image block as a LaTeX figure.

    Args:
        block: Parsed image block.
        assets_dir: Directory containing Swift Book image assets.
        appearance: PDF appearance used to choose light or dark assets.

    Returns:
        Rendered LaTeX figure lines, or an empty list when the image cannot be
        read.
    """
    img_path = Path(assets_dir) / (
        f"{block.imgname}{'~dark' if appearance == Appearance.DARK else ''}@2x.png"
    )
    latex_img_path = (
        PureWindowsPath(img_path).as_posix()
        if os.sep == "\\"
        else str(img_path)
    )
    width = read_image_width(img_path)
    if width is None:
        return []

    final_width = (
        f"{MAX_IMAGE_WIDTH_IN}in"
        if width > MAX_IMAGE_WIDTH_IN
        else f"{width}in"
    )
    return [
        "\\DocCContentNodeInlineImageBefore\n"
        f"\\begin{{figure}}[H]\n\\centering\\includegraphics[width={final_width}]{{{latex_img_path}}}\n\\end{{figure}}\n"
        "\\global\\precededbyboxfalse\n"
        "\\global\\precededbysectionfalse\n"
        "\\global\\precededbyparagraphfalse\n"
        "\\global\\precededbynotefalse\n"
        "\\global\\precededbyinlineimagetrue\n"
        "\\global\\precededbytablefalse\n"
        "\\global\\AtPageTopfalse\n",
    ]


def read_image_width(img_path: Path) -> float | None:
    """Read a PNG image width and convert it to inches.

    Args:
        img_path: Path to a PNG image.

    Returns:
        Image width in inches, or `None` when the file cannot be read as PNG.
    """
    try:
        with img_path.open("rb") as f:
            f.seek(16)
            width, _ = struct.unpack(">II", f.read(8))
        return width / 273.2
    except (OSError, struct.error) as exc:
        logger.debug(f"Failed to read image width for {img_path}: {exc}")
        return None
