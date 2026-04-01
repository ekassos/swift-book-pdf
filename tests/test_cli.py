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

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import click
import pytest
from click.testing import CliRunner, Result

from swift_book_pdf import cli_epub, cli_pdf

PDF_TYPESSETS = 2
PDF_FONT_SIZE = 10.5


@dataclass(frozen=True)
class DirectoryOutputScenario:
    module: Any
    command: click.Command
    config_name: str
    builder_name: str
    output_dir_name: str
    expected_file: str


@dataclass(frozen=True)
class InputPathValidationScenario:
    command: click.Command
    output_name: str
    revision_option: str
    revision_value: str
    requires_pdf_font_stub: bool = False


@pytest.fixture
def runner(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[CliRunner]:
    logging.getLogger().handlers.clear()
    logging.getLogger().setLevel(logging.NOTSET)
    monkeypatch.chdir(tmp_path)
    yield CliRunner()
    logging.getLogger().handlers.clear()
    logging.getLogger().setLevel(logging.NOTSET)


def assert_success(result: Result) -> None:
    assert result.exit_code == 0, result.output


def stub_pdf_font_config(monkeypatch: pytest.MonkeyPatch) -> Mock:
    font_config = Mock()
    monkeypatch.setattr(
        cli_pdf,
        "_build_font_config",
        Mock(return_value=font_config),
    )
    return font_config


@pytest.mark.parametrize(
    ("command", "present_options", "absent_options"),
    [
        pytest.param(
            cli_pdf.pdf,
            ("--mode", "--paper", "--typesets", "--main"),
            ("--export-cover-image", "--cover-footer-line"),
            id="pdf-help",
        ),
        pytest.param(
            cli_epub.epub,
            (
                "--export-cover-image",
                "--cover-footer-line",
                "--override-version",
                "--ibooks-version",
                "--publisher",
            ),
            ("--mode", "--paper", "--typesets"),
            id="epub-help",
        ),
    ],
)
def test_command_help_exposes_only_relevant_options(
    runner: CliRunner,
    command: click.Command,
    present_options: tuple[str, ...],
    absent_options: tuple[str, ...],
) -> None:
    result = runner.invoke(command, ["--help"])

    assert_success(result)
    for option in present_options:
        assert option in result.output
    for option in absent_options:
        assert option not in result.output
    assert "--input-path" in result.output
    assert "--source-ref" in result.output
    assert "--source-sha" in result.output


def test_pdf_command_builds_pdf_config_and_calls_pdf_builder(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fake_config = object()
    font_config = stub_pdf_font_config(monkeypatch)
    pdf_config = Mock(return_value=fake_config)
    build_pdf = Mock()
    monkeypatch.setattr(cli_pdf, "PDFConfig", pdf_config)
    monkeypatch.setattr(cli_pdf, "build_pdf", build_pdf)

    output_dir = tmp_path / "dist"
    output_dir.mkdir()
    result = runner.invoke(
        cli_pdf.pdf,
        [
            str(output_dir),
            "--mode",
            "print",
            "--paper",
            "a4",
            "--typesets",
            str(PDF_TYPESSETS),
            "--main",
            "New York",
            "--mono",
            "Berkeley Mono",
            "--unicode",
            "Noto Sans Symbols 2",
            "--emoji",
            "Apple Color Emoji",
            "--header-footer",
            "SF Pro",
            "--font-size",
            str(PDF_FONT_SIZE),
            "--dark",
            "--no-gutter",
            "--input-path",
            "./swift-book",
            "--source-ref",
            "swift-6.2-branch",
            "--source-sha",
            "abc123",
        ],
    )

    assert_success(result)
    args = pdf_config.call_args.args
    kwargs = pdf_config.call_args.kwargs
    assert args[1] == str(output_dir / "swift_book.pdf")
    assert args[2] is font_config
    assert args[3].mode.value == "print"
    assert args[3].paper_size.value == "a4"
    assert args[3].typesets == PDF_TYPESSETS
    assert args[3].appearance.value == "dark"
    assert args[3].gutter is False
    assert args[3].font_size == PDF_FONT_SIZE
    assert kwargs["input_path"] == str(tmp_path / "swift-book")
    assert kwargs["source_ref"] == "swift-6.2-branch"
    assert kwargs["source_sha"] == "abc123"
    build_pdf.assert_called_once_with(fake_config)


def test_epub_command_builds_epub_config_and_calls_epub_builder(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fake_config = object()
    epub_config = Mock(return_value=fake_config)
    build_epub = Mock()
    monkeypatch.setattr(cli_epub, "EPUBConfig", epub_config)
    monkeypatch.setattr(cli_epub, "build_epub", build_epub)

    output_dir = tmp_path / "dist"
    output_dir.mkdir()
    result = runner.invoke(
        cli_epub.epub,
        [
            str(output_dir),
            "--export-cover-image",
            "--cover-footer-line",
            "Beta",
            "--override-version",
            "6.2 beta",
            "--ibooks-version",
            "1.1",
            "--publisher",
            "Swift.org",
            "--contributor",
            "Open Source Contributors",
            "--input-path",
            "./swift-book",
            "--source-ref",
            "swift-6.2-branch",
            "--source-sha",
            "abc123",
        ],
    )

    assert_success(result)
    args = epub_config.call_args.args
    kwargs = epub_config.call_args.kwargs
    assert args[1] == str(output_dir / "swift_book.epub")
    assert kwargs["input_path"] == str(tmp_path / "swift-book")
    assert kwargs["export_cover_image"] is True
    assert kwargs["cover_footer_line"] == "Beta"
    assert kwargs["override_version"] == "6.2 beta"
    assert kwargs["ibooks_version"] == "1.1"
    assert kwargs["publisher"] == "Swift.org"
    assert kwargs["contributor"] == "Open Source Contributors"
    assert kwargs["source_ref"] == "swift-6.2-branch"
    assert kwargs["source_sha"] == "abc123"
    build_epub.assert_called_once_with(fake_config)


@pytest.mark.parametrize(
    "scenario",
    [
        pytest.param(
            DirectoryOutputScenario(
                module=cli_pdf,
                command=cli_pdf.pdf,
                config_name="PDFConfig",
                builder_name="build_pdf",
                output_dir_name="books",
                expected_file="swift_book.pdf",
            ),
            id="pdf-default-output",
        ),
        pytest.param(
            DirectoryOutputScenario(
                module=cli_epub,
                command=cli_epub.epub,
                config_name="EPUBConfig",
                builder_name="build_epub",
                output_dir_name="books",
                expected_file="swift_book.epub",
            ),
            id="epub-default-output",
        ),
    ],
)
def test_directory_output_defaults_to_format_extension(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    scenario: DirectoryOutputScenario,
) -> None:
    fake_config = object()
    config_mock = Mock(return_value=fake_config)
    if scenario.module is cli_pdf:
        stub_pdf_font_config(monkeypatch)
    monkeypatch.setattr(scenario.module, scenario.config_name, config_mock)
    monkeypatch.setattr(scenario.module, scenario.builder_name, Mock())

    output_dir = tmp_path / scenario.output_dir_name
    output_dir.mkdir()
    result = runner.invoke(scenario.command, [str(output_dir)])

    assert_success(result)
    assert config_mock.call_args.args[1] == str(
        output_dir / scenario.expected_file
    )


@pytest.mark.parametrize(
    "scenario",
    [
        pytest.param(
            InputPathValidationScenario(
                command=cli_pdf.pdf,
                output_name="book.pdf",
                revision_option="--source-ref",
                revision_value="main",
                requires_pdf_font_stub=True,
            ),
            id="pdf-source-ref-with-input-path",
        ),
        pytest.param(
            InputPathValidationScenario(
                command=cli_epub.epub,
                output_name="book.epub",
                revision_option="--source-sha",
                revision_value="abc123",
            ),
            id="epub-source-sha-with-input-path",
        ),
    ],
)
def test_input_path_rejects_revision_selection(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    scenario: InputPathValidationScenario,
) -> None:
    if scenario.requires_pdf_font_stub:
        stub_pdf_font_config(monkeypatch)
    result = runner.invoke(
        scenario.command,
        [
            scenario.output_name,
            "--input-path",
            "./swift-book",
            scenario.revision_option,
            scenario.revision_value,
        ],
    )

    assert_success(result)
    assert (
        "--source-ref and --source-sha can't be used with --input-path"
        in result.output
    )
