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
from typing import TYPE_CHECKING, cast

import pytest

from swift_book_pdf.pdf import engine

if TYPE_CHECKING:
    from swift_book_pdf.pdf.config import PDFConfig


def test_pdf_converter_uses_package_assets_dir(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        engine.shutil, "which", lambda name: f"/usr/bin/{name}"
    )
    monkeypatch.setattr(
        engine, "check_required_latex_packages_installed", lambda: None
    )
    monkeypatch.setattr(
        engine, "check_minted_runtime_compatibility", lambda: None
    )

    converter = engine.PDFConverter(cast("PDFConfig", SimpleNamespace()))

    asset_dirs = tuple(Path(path) for path in converter.local_asset_dirs)
    assert [path.name for path in asset_dirs] == [
        "swift-logo",
        "icons",
        "ibm-plex",
    ]
    assert (asset_dirs[0] / "Swift_logo_white.png").is_file()
    assert (asset_dirs[1] / "chapter-icon.png").is_file()
    assert (asset_dirs[2] / "IBMPlexSerif-Regular.ttf").is_file()
