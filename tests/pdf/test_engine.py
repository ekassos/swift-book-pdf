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

from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

import pytest

from swift_book_pdf.core.config import ResolvedBuildSource
from swift_book_pdf.pdf.backend import PDFBuildContext
from swift_book_pdf.pdf.config import PDFDocumentConfig
from swift_book_pdf.pdf.latex.build import compiler
from swift_book_pdf.pdf.latex.config import LaTeXConfig, LaTeXPDFConfig
from swift_book_pdf.pdf.latex.engine import LaTeXEngine
from swift_book_pdf.pdf.latex.fonts.resolver import LaTeXFontConfig


def test_pdf_converter_uses_package_assets_dir(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        compiler.shutil, "which", lambda name: f"/usr/bin/{name}"
    )
    monkeypatch.setattr(
        compiler, "check_required_latex_packages_installed", lambda: None
    )
    monkeypatch.setattr(
        compiler, "check_minted_runtime_compatibility", lambda: None
    )

    converter = compiler.LuaLaTeXCompiler(
        cast(LaTeXPDFConfig, SimpleNamespace())
    )

    asset_dirs = tuple(Path(path) for path in converter.local_asset_dirs)
    assert [path.name for path in asset_dirs] == [
        "icons",
        "ibm-plex",
    ]
    assert (asset_dirs[0] / "chapter-icon.png").is_file()
    assert (asset_dirs[1] / "IBMPlexSerif-Regular.ttf").is_file()


def test_latex_engine_can_stop_after_writing_tex(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    docc_root = tmp_path / "swift-book" / "TSPL.docc"
    config = LaTeXPDFConfig(
        source=ResolvedBuildSource(
            temp_dir=str(tmp_path),
            root_dir=str(docc_root),
            toc_file_path=str(docc_root / "The-Swift-Programming-Language.md"),
            assets_dir=str(docc_root / "Assets"),
            original_work_copyright_year_range=(2014, 2026),
        ),
        output_path=str(tmp_path / "book.tex"),
        doc_config=PDFDocumentConfig(),
        latex_config=LaTeXConfig(
            font_config=LaTeXFontConfig(
                main_font="New York",
                mono_font="Berkeley Mono",
                emoji_font="Apple Color Emoji",
                unicode_fonts=("Noto Sans Symbols 2",),
                header_footer_font="SF Pro",
            ),
            typesets=1,
        ),
        save_tex=True,
    )
    context = PDFBuildContext(config=config, toc=Mock(chapter_metadata={}))

    monkeypatch.setattr(
        "swift_book_pdf.pdf.latex.engine.write_latex_document",
        lambda _config, _toc, _renderer, output_path: output_path.write_text(
            "TEX",
            encoding="utf-8",
        ),
    )
    compiler_mock = Mock()
    monkeypatch.setattr(
        "swift_book_pdf.pdf.latex.engine.LuaLaTeXCompiler",
        compiler_mock,
    )

    artifact_path = LaTeXEngine().build(context)

    assert artifact_path == tmp_path / "inner_content.tex"
    assert artifact_path.read_text(encoding="utf-8") == "TEX"
    compiler_mock.assert_not_called()
