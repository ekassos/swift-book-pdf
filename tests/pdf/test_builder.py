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

"""Tests for top-level PDF build artifact handling."""

from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

import pytest

from swift_book_pdf.pdf import builder
from swift_book_pdf.pdf.config import PDFConfig


def test_build_pdf_can_save_intermediates_without_changing_pdf_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "inner_content.aux").write_text("AUX", encoding="utf-8")
    temp_artifact_path = temp_dir / "inner_content.pdf"
    temp_artifact_path.write_text("PDF", encoding="utf-8")
    output_dir = tmp_path / "build-files"
    output_path = tmp_path / "swift_book.pdf"

    monkeypatch.setattr(builder, "TableOfContents", Mock())
    monkeypatch.setattr(
        builder,
        "select_engine",
        Mock(return_value=Mock(build=Mock(return_value=temp_artifact_path))),
    )

    builder.build_pdf(
        cast(
            PDFConfig,
            SimpleNamespace(
                root_dir=str(tmp_path / "book"),
                toc_file_path=str(tmp_path / "toc.md"),
                temp_dir=str(temp_dir),
                dangerously_skip_legal_notices=False,
                doc_config=SimpleNamespace(
                    mode=SimpleNamespace(value="digital"),
                    appearance="light",
                ),
                save_tex=False,
                output_path=str(output_path),
                intermediates_path=str(output_dir),
                diagnostic_details=lambda: "",
            ),
        )
    )

    assert (output_dir / "inner_content.aux").read_text(
        encoding="utf-8"
    ) == "AUX"
    assert (output_dir / "inner_content.pdf").read_text(
        encoding="utf-8"
    ) == "PDF"
    assert not (output_dir / "swift_book.pdf").exists()
    assert output_path.read_text(encoding="utf-8") == "PDF"


def test_build_pdf_rejects_existing_intermediates_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    temp_artifact_path = temp_dir / "inner_content.pdf"
    temp_artifact_path.write_text("PDF", encoding="utf-8")
    output_dir = tmp_path / "build-files"
    output_dir.mkdir()

    monkeypatch.setattr(builder, "TableOfContents", Mock())
    monkeypatch.setattr(
        builder,
        "select_engine",
        Mock(return_value=Mock(build=Mock(return_value=temp_artifact_path))),
    )

    with pytest.raises(RuntimeError, match="already exists"):
        builder.build_pdf(
            cast(
                PDFConfig,
                SimpleNamespace(
                    root_dir=str(tmp_path / "book"),
                    toc_file_path=str(tmp_path / "toc.md"),
                    temp_dir=str(temp_dir),
                    dangerously_skip_legal_notices=False,
                    doc_config=SimpleNamespace(
                        mode=SimpleNamespace(value="digital"),
                        appearance="light",
                    ),
                    save_tex=False,
                    output_path=str(tmp_path / "swift_book.pdf"),
                    intermediates_path=str(output_dir),
                    diagnostic_details=lambda: "",
                ),
            )
        )
