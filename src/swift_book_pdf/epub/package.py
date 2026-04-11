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

from __future__ import annotations

import html
import logging
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from swift_book_pdf.schema import (
    DocumentEntry,
    ImageAsset,
    ManifestItem,
    PartEntry,
)

from .constants import (
    COVER_FOOTER_TEXT_FILL,
    COVER_FOOTER_TEXT_SIZE,
    COVER_FOOTER_TEXT_Y,
    COVER_TEXT_FILL,
    COVER_TEXT_SIZE,
    COVER_TEXT_TRACKING,
    COVER_TEXT_VERTICAL_SCALE,
    COVER_TEXT_WIDTH,
    COVER_TEXT_X,
    COVER_TEXT_Y,
    DEFAULT_BOOK_TITLE,
    EPUB_COVER_LOGO_DARK_FILE_NAME,
    EPUB_COVER_LOGO_FILE_NAME,
    EPUB_IDENTIFIER_ID,
    NAV_DOC_FILE_NAME,
    NCX_FILE_NAME,
    REFERENCE_STATIC_DIR,
    SWIFT_LOGO_PNG_PATH,
    SWIFT_LOGO_WHITE_PNG_PATH,
)
from .helpers import (
    cover_edition_text,
    cover_template_path,
    oebps_workspace_path,
    relative_href,
)

if TYPE_CHECKING:
    from swift_book_pdf.config import EPUBConfig

logger = logging.getLogger(__name__)


class EPUBPackageWriter:
    def __init__(self, config: EPUBConfig) -> None:
        self.config = config
        self.publication_identifier = ""

    def prepare_workspace(self) -> Path:
        workspace = Path(self.config.temp_dir) / "epub"
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace

    def write_text(
        self, workspace: Path, relative_path: str, content: str
    ) -> None:
        path = oebps_workspace_path(workspace, relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_container_file(self, workspace: Path) -> None:
        self._write_text_file(workspace / "mimetype", "application/epub+zip")
        self._write_text_file(
            workspace / "META-INF" / "container.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
""",
        )

    def write_static_files(self, workspace: Path) -> None:
        self._copy_reference_static_asset("epub.css", workspace)
        self._copy_reference_static_asset("pygments.css", workspace)
        if SWIFT_LOGO_PNG_PATH.exists():
            destination = oebps_workspace_path(
                workspace, EPUB_COVER_LOGO_FILE_NAME
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SWIFT_LOGO_PNG_PATH, destination)
        if SWIFT_LOGO_WHITE_PNG_PATH.exists():
            dark_destination = oebps_workspace_path(
                workspace, EPUB_COVER_LOGO_DARK_FILE_NAME
            )
            dark_destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SWIFT_LOGO_WHITE_PNG_PATH, dark_destination)

    def write_cover_asset(
        self, workspace: Path, version_info: str | None
    ) -> None:
        template_path = cover_template_path(version_info)
        if not template_path.exists():
            logger.warning(
                "Couldn't find cover template %s; skipping cover.",
                template_path,
            )
            return

        cover_destination = oebps_workspace_path(
            workspace, "_static/cover.png"
        )
        cover_destination.parent.mkdir(parents=True, exist_ok=True)
        edition_text = cover_edition_text(version_info)
        if edition_text is None and not self.config.cover_footer_line:
            shutil.copy2(template_path, cover_destination)
            return

        cover_image = Image.open(template_path).convert("RGBA")
        if edition_text is not None:
            font = _load_cover_font(COVER_TEXT_SIZE)
            _draw_cover_edition_text(cover_image, edition_text, font)
        if self.config.cover_footer_line:
            footer_line_font = _load_cover_font(COVER_FOOTER_TEXT_SIZE)
            _draw_cover_footer_line(
                cover_image,
                self.config.cover_footer_line,
                footer_line_font,
            )
        cover_image.convert("RGB").save(cover_destination, format="PNG")

    def export_cover_asset(self, workspace: Path) -> Path | None:
        source = oebps_workspace_path(workspace, "_static/cover.png")
        if not source.exists():
            return None

        output_path = Path(self.config.output_path)
        destination = output_path.with_name(f"{output_path.stem}_cover.png")
        shutil.copy2(source, destination)
        return destination

    def has_cover_asset(self, workspace: Path) -> bool:
        return oebps_workspace_path(workspace, "_static/cover.png").exists()

    def copy_image_assets(
        self, workspace: Path, image_assets: dict[str, ImageAsset]
    ) -> None:
        for asset in image_assets.values():
            destination = oebps_workspace_path(workspace, asset.href)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset.source_path, destination)

    def write_nav_file(
        self,
        workspace: Path,
        cover: DocumentEntry | None,
        parts: list[PartEntry],
        notices: DocumentEntry | None,
    ) -> None:
        reader_start_href = (
            parts[0].href
            if parts
            else notices.href
            if notices is not None
            else cover.href
            if cover is not None
            else NAV_DOC_FILE_NAME
        )
        reader_start_relative_href = relative_href(
            NAV_DOC_FILE_NAME, reader_start_href
        )
        cover_relative_href = (
            relative_href(NAV_DOC_FILE_NAME, cover.href)
            if cover is not None
            else None
        )
        items = []
        if cover is not None:
            items.append(
                "        <li>\n"
                f'          <a href="{html.escape(cover_relative_href or "")}">{html.escape(cover.title)}</a>\n'
                "        </li>"
            )
        for part in parts:
            chapter_items = "\n".join(
                (
                    "            <li>\n"
                    f'              <a href="{html.escape(relative_href(NAV_DOC_FILE_NAME, child.href))}">{html.escape(child.title)}</a>\n'
                    "            </li>"
                )
                for child in part.children
            )
            items.append(
                "        <li>\n"
                f'          <a href="{html.escape(relative_href(NAV_DOC_FILE_NAME, part.href))}">{html.escape(part.title)}</a>\n'
                "          <ol>\n"
                f"{chapter_items}\n"
                "          </ol>\n"
                "        </li>"
            )
        if notices is not None:
            items.append(
                "        <li>\n"
                f'          <a href="{html.escape(relative_href(NAV_DOC_FILE_NAME, notices.href))}">{html.escape(notices.title)}</a>\n'
                "        </li>"
            )
        self.write_text(
            workspace,
            NAV_DOC_FILE_NAME,
            """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      xmlns:ibooks="http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0"
      epub:prefix="ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"
      lang="en" xml:lang="en">
  <head>
    <title>Table of Contents</title>
    <link rel="stylesheet" href="_static/epub.css" type="text/css" />
  </head>
  <body>
    <section>
      <header>
        <h1>Table of Contents</h1>
      </header>
      <nav epub:type="toc" id="toc">
        <ol>
"""
            + "\n".join(items)
            + """
        </ol>
      </nav>
      <nav epub:type="landmarks">
        <h1>Guide</h1>
        <ol>
        <li>
          <a epub:type="ibooks:reader-start-page" href=\""""
            + html.escape(reader_start_relative_href)
            + """\">Start Reading</a>
        </li>
"""
            + (
                """        <li>
          <a epub:type="cover" href=\""""
                + html.escape(cover_relative_href)
                + """\">Cover</a>
        </li>
"""
                if cover_relative_href is not None
                else ""
            )
            + """        <li>
          <a epub:type="bodymatter" href=\""""
            + html.escape(reader_start_relative_href)
            + """\">"""
            + html.escape(parts[0].title if parts else DEFAULT_BOOK_TITLE)
            + """</a>
        </li>
"""
            + (
                """        <li>
          <a epub:type="acknowledgements" href=\""""
                + html.escape(relative_href(NAV_DOC_FILE_NAME, notices.href))
                + """\">Acknowledgments</a>
        </li>
"""
                if notices is not None
                else ""
            )
            + """
        </ol>
      </nav>
    </section>
  </body>
</html>
""",
        )

    def write_toc_ncx_file(
        self,
        workspace: Path,
        cover: DocumentEntry | None,
        parts: list[PartEntry],
        notices: DocumentEntry | None,
        book_title: str,
    ) -> None:
        part_navpoints: list[str] = []
        navpoint_index = 1
        if cover is not None:
            cover_navpoint, navpoint_index = _build_ncx_navpoint_tree(
                navpoint_index,
                cover.title,
                cover.href,
            )
            part_navpoints.append(cover_navpoint)
        for part in parts:
            part_navpoint, navpoint_index = _build_ncx_navpoint_tree(
                navpoint_index,
                part.title,
                part.href,
                [(child.title, child.href) for child in part.children],
            )
            part_navpoints.append(part_navpoint)
        if notices is not None:
            notices_navpoint, _ = _build_ncx_navpoint_tree(
                navpoint_index,
                notices.title,
                notices.href,
            )
            part_navpoints.append(notices_navpoint)
        self.write_text(
            workspace,
            NCX_FILE_NAME,
            """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content=\""""
            + html.escape(self.publication_identifier)
            + """\"/>
    <meta name="dtb:depth" content="2"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>"""
            + html.escape(book_title)
            + """</text>
  </docTitle>
  <navMap>
"""
            + "\n".join(part_navpoints)
            + """
  </navMap>
</ncx>
""",
        )

    def write_content_opf_file(
        self,
        workspace: Path,
        book_title: str,
        documents: list[DocumentEntry],
        image_assets: dict[str, ImageAsset],
        publication_identifier: str,
    ) -> None:
        manifest: list[ManifestItem] = [
            ManifestItem(
                item_id="ncx",
                href=NCX_FILE_NAME,
                media_type="application/x-dtbncx+xml",
            ),
            ManifestItem(
                item_id="nav",
                href=NAV_DOC_FILE_NAME,
                media_type="application/xhtml+xml",
                properties="nav",
            ),
        ]
        for index, document in enumerate(documents):
            manifest.append(
                ManifestItem(
                    item_id=f"epub-doc-{index}",
                    href=document.href,
                    media_type="application/xhtml+xml",
                )
            )

        for index, asset in enumerate(
            sorted(image_assets.values(), key=lambda item: item.href)
        ):
            manifest.append(
                ManifestItem(
                    item_id=f"epub-image-{index}",
                    href=asset.href,
                    media_type=asset.media_type,
                )
            )

        manifest.extend(
            [
                ManifestItem(
                    item_id="epub-style",
                    href="_static/epub.css",
                    media_type="text/css",
                ),
                ManifestItem(
                    item_id="epub-pygments",
                    href="_static/pygments.css",
                    media_type="text/css",
                ),
            ]
        )
        if oebps_workspace_path(workspace, EPUB_COVER_LOGO_FILE_NAME).exists():
            manifest.append(
                ManifestItem(
                    item_id="epub-cover-logo",
                    href=EPUB_COVER_LOGO_FILE_NAME,
                    media_type="image/png",
                )
            )
        if oebps_workspace_path(
            workspace, EPUB_COVER_LOGO_DARK_FILE_NAME
        ).exists():
            manifest.append(
                ManifestItem(
                    item_id="epub-cover-logo-dark",
                    href=EPUB_COVER_LOGO_DARK_FILE_NAME,
                    media_type="image/png",
                )
            )
        if self.has_cover_asset(workspace):
            manifest.append(
                ManifestItem(
                    item_id="epub-cover",
                    href="_static/cover.png",
                    media_type="image/png",
                    properties="cover-image",
                )
            )

        manifest_xml = "\n".join(
            _format_manifest_item(item) for item in manifest
        )
        spine_items = "\n".join(
            f'    <itemref idref="epub-doc-{index}" />'
            for index, _ in enumerate(documents)
        )
        modified = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        cover_meta = ""
        if self.has_cover_asset(workspace):
            cover_meta = '<meta name="cover" content="epub-cover"/>\n    '
        publisher_xml = ""
        if self.config.publisher is not None:
            publisher_xml = f"<dc:publisher>{html.escape(self.config.publisher)}</dc:publisher>\n    "
        contributor_xml = ""
        if self.config.contributor is not None:
            contributor_xml = f"<dc:contributor>{html.escape(self.config.contributor)}</dc:contributor>\n    "
        ibooks_version_xml = ""
        if self.config.ibooks_version is not None:
            ibooks_version_xml = (
                f'<meta property="ibooks:version">'
                f"{html.escape(self.config.ibooks_version)}</meta>\n    "
            )
        content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" xml:lang="en"
 prefix="ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"
 xmlns:epub="http://www.idpf.org/2007/ops"
 xmlns:ibooks="http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"
 unique-identifier="{EPUB_IDENTIFIER_ID}">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf"
        xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:language>en</dc:language>
    <dc:title>{html.escape(book_title)}</dc:title>
    <dc:creator>The Swift project authors</dc:creator>
    {publisher_xml}{contributor_xml}<dc:identifier id="{EPUB_IDENTIFIER_ID}">{html.escape(publication_identifier)}</dc:identifier>
    {ibooks_version_xml}<meta property="dcterms:modified">{modified}</meta>
    <meta property="ibooks:specified-fonts">true</meta>
    {cover_meta}</metadata>
  <manifest>
{manifest_xml}
  </manifest>
  <spine toc="ncx" page-progression-direction="ltr">
{spine_items}
  </spine>
</package>
"""
        self.write_text(workspace, "content.opf", content_opf)

    def package_epub(self, workspace: Path) -> None:
        output_path = Path(self.config.output_path)
        archive_path = Path(self.config.temp_dir) / output_path.name
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.write(
                workspace / "mimetype",
                "mimetype",
                compress_type=zipfile.ZIP_STORED,
            )
            for file_path in sorted(workspace.rglob("*")):
                if file_path.is_dir() or file_path.name == "mimetype":
                    continue
                archive.write(
                    file_path,
                    file_path.relative_to(workspace).as_posix(),
                    compress_type=zipfile.ZIP_DEFLATED,
                )

        shutil.move(str(archive_path), self.config.output_path)

    def _copy_reference_static_asset(self, name: str, workspace: Path) -> None:
        source = REFERENCE_STATIC_DIR / name
        destination = oebps_workspace_path(workspace, f"_static/{name}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    def _write_text_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _build_ncx_navpoint_tree(
    index: int,
    title: str,
    href: str,
    children: list[tuple[str, str]] | None = None,
) -> tuple[str, int]:
    current_index = index
    next_index = index + 1
    child_navpoints: list[str] = []
    for child_title, child_href in children or []:
        child_navpoint, next_index = _build_ncx_navpoint_tree(
            next_index,
            child_title,
            child_href,
        )
        child_navpoints.append(child_navpoint)

    child_lines = "".join(child_navpoints)
    navpoint = (
        f'    <navPoint id="navPoint{current_index}" playOrder="{current_index}">\n'
        "      <navLabel>\n"
        f"        <text>{html.escape(title)}</text>\n"
        "      </navLabel>\n"
        f'      <content src="{html.escape(href)}" />\n'
        f"{child_lines}"
        "    </navPoint>"
    )
    return navpoint, next_index


def _format_manifest_item(item: ManifestItem) -> str:
    properties = (
        f' properties="{html.escape(item.properties)}"'
        if item.properties is not None
        else ""
    )
    return (
        f'    <item id="{html.escape(item.item_id)}"'
        f' href="{html.escape(item.href)}"'
        f' media-type="{html.escape(item.media_type)}"{properties} />'
    )


def _load_cover_font(
    size: int,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidate_paths = [
        Path("/Library/Fonts/SF-Pro-Display-Regular.otf"),
        Path("/System/Library/Fonts/HelveticaNeue.ttc"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
        Path(ImageFont.__file__).resolve().parent / "fonts/DejaVuSans.ttf",
    ]
    candidate_names = [
        "SF-Pro-Display-Regular.otf",
        "HelveticaNeue.ttc",
        "Helvetica.ttc",
        "Arial.ttf",
        "DejaVuSans.ttf",
    ]

    for candidate in candidate_paths:
        if not candidate.exists():
            continue
        try:
            return ImageFont.truetype(str(candidate), size)
        except OSError:
            continue

    for candidate_name in candidate_names:
        font = _load_named_font(candidate_name, size)
        if font is not None:
            return font

    return ImageFont.load_default()


def _draw_cover_edition_text(
    image: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> None:
    text_width, text_height, bbox_left, bbox_top = _measure_tracked_text(
        text, font
    )
    padding = 12
    overlay_width = max(1, int(text_width + (padding * 2)))
    overlay_height = max(1, int(text_height + (padding * 2)))
    overlay = Image.new(
        "RGBA", (overlay_width, overlay_height), (255, 255, 255, 0)
    )
    overlay_draw = ImageDraw.Draw(overlay)
    _draw_tracked_text(
        overlay_draw,
        (padding - bbox_left, padding - bbox_top),
        text,
        font,
        COVER_TEXT_TRACKING,
    )
    if COVER_TEXT_VERTICAL_SCALE != 1:
        scaled_height = max(
            1, round(overlay.height * COVER_TEXT_VERTICAL_SCALE)
        )
        overlay = overlay.resize(
            (overlay.width, scaled_height), Image.Resampling.LANCZOS
        )

    x = round(COVER_TEXT_X + ((COVER_TEXT_WIDTH - overlay.width) / 2))
    y = round(COVER_TEXT_Y)
    image.alpha_composite(overlay, (x, y))


def _draw_cover_footer_line(
    image: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> None:
    _draw_cover_centered_text(
        image,
        text,
        font,
        COVER_FOOTER_TEXT_Y,
        COVER_FOOTER_TEXT_FILL,
    )


def _measure_tracked_text(
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    tracking: float = COVER_TEXT_TRACKING,
) -> tuple[float, int, int, int]:
    dummy = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
    draw = ImageDraw.Draw(dummy)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    width = float(right - left)
    if len(text) > 1:
        width += tracking * (len(text) - 1)
    return width, bottom - top, left, top


def _draw_tracked_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    tracking: float,
) -> None:
    cursor_x, y = position
    for index, character in enumerate(text):
        draw.text((cursor_x, y), character, fill=COVER_TEXT_FILL, font=font)
        cursor_x += draw.textlength(character, font=font)
        if index < len(text) - 1:
            cursor_x += tracking


def _draw_cover_centered_text(
    image: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    top_y: float,
    fill: str,
) -> None:
    text_width, text_height, bbox_left, bbox_top = _measure_tracked_text(
        text,
        font,
        tracking=0,
    )
    padding = 8
    overlay_width = max(1, int(text_width + (padding * 2)))
    overlay_height = max(1, int(text_height + (padding * 2)))
    overlay = Image.new(
        "RGBA", (overlay_width, overlay_height), (255, 255, 255, 0)
    )
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.text(
        (padding - bbox_left, padding - bbox_top),
        text,
        fill=fill,
        font=font,
    )

    x = round((image.width - overlay.width) / 2)
    y = round(top_y)
    image.alpha_composite(overlay, (x, y))


def _load_named_font(
    font_name: str, size: int
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont | None:
    try:
        return ImageFont.truetype(font_name, size)
    except OSError:
        return None
