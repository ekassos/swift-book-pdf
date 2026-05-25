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
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import click
import pytest
from click.testing import CliRunner, Result

from swift_book_pdf.cli.legal_notices import LEGAL_NOTICES_WARNING
from swift_book_pdf.cli.logging_config import configure_logging
from swift_book_pdf.cli.output import validate_output_path
from swift_book_pdf.core.config import BuildSourceConfig, ResolvedBuildSource
from swift_book_pdf.core.output import OutputFormat
from swift_book_pdf.epub.cli import command as epub_cli
from swift_book_pdf.epub.cli import config as epub_cli_config
from swift_book_pdf.epub.cli.validators import validate_hex_color
from swift_book_pdf.pdf.cli import command as pdf_cli
from swift_book_pdf.pdf.cli import config as pdf_cli_config

PDF_TYPESSETS = 2
PDF_FONT_SIZE = 10.5
RESOLVED_SOURCE = ResolvedBuildSource(
    temp_dir="swift-book-build",
    root_dir="swift-book/TSPL.docc",
    toc_file_path="swift-book/TSPL.docc/The-Swift-Programming-Language.md",
    assets_dir="swift-book/TSPL.docc/Assets",
    original_work_copyright_year_range=(2014, 2026),
)


@dataclass(frozen=True)
class DirectoryOutputScenario:
    module: ModuleType
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
        pdf_cli_config,
        "build_font_config",
        Mock(return_value=font_config),
    )
    return font_config


def stub_resolve_build_source(
    module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> Mock:
    resolver = Mock(return_value=RESOLVED_SOURCE)
    monkeypatch.setattr(module, "resolve_build_source", resolver)
    return resolver


@pytest.mark.parametrize(
    ("command", "present_options", "absent_options"),
    [
        pytest.param(
            pdf_cli.pdf,
            (
                "--mode",
                "--paper",
                "--typesets",
                "--override-version",
                "--main",
                "--dangerously-skip-legal-notices",
            ),
            ("--export-cover-image", "--cover-footer-line"),
            id="pdf-help",
        ),
        pytest.param(
            epub_cli.epub,
            (
                "--export-cover-image",
                "--base-cover-image",
                "--cover-footer-line",
                "--cover-banner-text",
                "--cover-banner-color",
                "--override-version",
                "--publication-identifier-seed",
                "--ibooks-version",
                "--publisher",
                "--dangerously-skip-legal-notices",
            ),
            (
                "--mode",
                "--paper",
                "--typesets",
                "--current-edition",
                "--nightly-edition",
                "--release-cover-image",
                "--beta-cover-image",
                "--current-cover-image",
                "--nightly-cover-image",
            ),
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
    fake_config = SimpleNamespace(dangerously_skip_legal_notices=True)
    font_config = stub_pdf_font_config(monkeypatch)
    resolve_source = stub_resolve_build_source(pdf_cli_config, monkeypatch)
    pdf_config = Mock(return_value=fake_config)
    build_pdf = Mock()
    monkeypatch.setattr(pdf_cli_config, "PDFConfig", pdf_config)
    monkeypatch.setattr(pdf_cli, "build_pdf", build_pdf)

    output_dir = tmp_path / "dist"
    output_dir.mkdir()
    result = runner.invoke(
        pdf_cli.pdf,
        [
            str(output_dir),
            "--mode",
            "print",
            "--paper",
            "a4",
            "--typesets",
            str(PDF_TYPESSETS),
            "--override-version",
            "6.2 beta",
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
            "--dangerously-skip-legal-notices",
            "-G",
            "--input-path",
            "./swift-book",
            "--source-ref",
            "swift-6.2-branch",
            "--source-sha",
            "abc123",
        ],
    )

    assert_success(result)
    source_config = resolve_source.call_args.args[0]
    assert isinstance(source_config, BuildSourceConfig)
    assert source_config.temp_dir
    assert source_config.input_path == str(tmp_path / "swift-book")
    assert source_config.source_ref == "swift-6.2-branch"
    assert source_config.source_sha == "abc123"
    kwargs = pdf_config.call_args.kwargs
    assert kwargs["source"] is RESOLVED_SOURCE
    assert kwargs["output_path"] == str(output_dir / "swift_book.pdf")
    assert kwargs["font_config"] is font_config
    assert kwargs["doc_config"].mode.value == "print"
    assert kwargs["doc_config"].paper_size.value == "a4"
    assert kwargs["doc_config"].typesets == PDF_TYPESSETS
    assert kwargs["doc_config"].appearance.value == "dark"
    assert kwargs["doc_config"].gutter is False
    assert kwargs["doc_config"].font_size == PDF_FONT_SIZE
    assert kwargs["override_version"] == "6.2 beta"
    assert kwargs["dangerously_skip_legal_notices"] is True
    assert LEGAL_NOTICES_WARNING in result.output
    build_pdf.assert_called_once_with(fake_config)


def test_epub_command_builds_epub_config_and_calls_epub_builder(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fake_config = SimpleNamespace(dangerously_skip_legal_notices=True)
    resolve_source = stub_resolve_build_source(epub_cli_config, monkeypatch)
    epub_config = Mock(return_value=fake_config)
    build_epub = Mock()
    monkeypatch.setattr(epub_cli_config, "EPUBConfig", epub_config)
    monkeypatch.setattr(epub_cli, "build_epub", build_epub)

    output_dir = tmp_path / "dist"
    output_dir.mkdir()
    cover_path = tmp_path / "custom-cover.png"
    cover_path.write_bytes(b"png")
    release_cover_path = tmp_path / "release-cover.png"
    beta_cover_path = tmp_path / "beta-cover.png"
    current_cover_path = tmp_path / "current-cover.png"
    nightly_cover_path = tmp_path / "nightly-cover.png"
    for path in (
        release_cover_path,
        beta_cover_path,
        current_cover_path,
        nightly_cover_path,
    ):
        path.write_bytes(b"png")
    result = runner.invoke(
        epub_cli.epub,
        [
            str(output_dir),
            "--export-cover-image",
            "--base-cover-image",
            str(cover_path),
            "--release-cover-image",
            str(release_cover_path),
            "--beta-cover-image",
            str(beta_cover_path),
            "--current-cover-image",
            str(current_cover_path),
            "--nightly-cover-image",
            str(nightly_cover_path),
            "--cover-footer-line",
            "Beta",
            "--current-edition",
            "--override-version",
            "6.2 beta",
            "--publication-identifier-seed",
            "version:6.2.3",
            "--ibooks-version",
            "1.1",
            "--publisher",
            "Swift.org",
            "--contributor",
            "Open Source Contributors",
            "--dangerously-skip-legal-notices",
            "--input-path",
            "./swift-book",
            "--source-ref",
            "swift-6.2-branch",
            "--source-sha",
            "abc123",
        ],
    )

    assert_success(result)
    source_config = resolve_source.call_args.args[0]
    assert isinstance(source_config, BuildSourceConfig)
    assert source_config.temp_dir
    assert source_config.input_path == str(tmp_path / "swift-book")
    assert source_config.source_ref == "swift-6.2-branch"
    assert source_config.source_sha == "abc123"
    kwargs = epub_config.call_args.kwargs
    assert kwargs["source"] is RESOLVED_SOURCE
    assert kwargs["output_path"] == str(output_dir / "swift_book.epub")
    assert kwargs["export_cover_image"] is True
    assert kwargs["base_cover_image"] == cover_path
    assert kwargs["cover_template_paths"] == {
        "release": release_cover_path,
        "beta": beta_cover_path,
        "current": current_cover_path,
        "nightly": nightly_cover_path,
    }
    assert kwargs["cover_footer_line"] == "Beta"
    assert kwargs["cover_variant"] == "current"
    assert kwargs["override_version"] == "6.2 beta"
    assert kwargs["publication_identifier_seed"] == "version:6.2.3"
    assert kwargs["ibooks_version"] == "1.1"
    assert kwargs["publisher"] == "Swift.org"
    assert kwargs["contributor"] == "Open Source Contributors"
    assert kwargs["dangerously_skip_legal_notices"] is True
    assert LEGAL_NOTICES_WARNING in result.output
    build_epub.assert_called_once_with(fake_config)


@pytest.mark.parametrize(
    "scenario",
    [
        pytest.param(
            DirectoryOutputScenario(
                module=pdf_cli,
                command=pdf_cli.pdf,
                config_name="PDFConfig",
                builder_name="build_pdf",
                output_dir_name="books",
                expected_file="swift_book.pdf",
            ),
            id="pdf-default-output",
        ),
        pytest.param(
            DirectoryOutputScenario(
                module=epub_cli,
                command=epub_cli.epub,
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
    fake_config = SimpleNamespace(dangerously_skip_legal_notices=False)
    config_mock = Mock(return_value=fake_config)
    if scenario.module is pdf_cli:
        stub_pdf_font_config(monkeypatch)
    config_module = (
        pdf_cli_config if scenario.module is pdf_cli else epub_cli_config
    )
    stub_resolve_build_source(config_module, monkeypatch)
    monkeypatch.setattr(config_module, scenario.config_name, config_mock)
    monkeypatch.setattr(scenario.module, scenario.builder_name, Mock())

    output_dir = tmp_path / scenario.output_dir_name
    output_dir.mkdir()
    result = runner.invoke(scenario.command, [str(output_dir)])

    assert_success(result)
    assert config_mock.call_args.kwargs["output_path"] == str(
        output_dir / scenario.expected_file
    )


@pytest.mark.parametrize(
    "scenario",
    [
        pytest.param(
            InputPathValidationScenario(
                command=pdf_cli.pdf,
                output_name="book.pdf",
                revision_option="--source-ref",
                revision_value="main",
                requires_pdf_font_stub=True,
            ),
            id="pdf-source-ref-with-input-path",
        ),
        pytest.param(
            InputPathValidationScenario(
                command=epub_cli.epub,
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


def test_validate_output_path_handles_format_suffixes(tmp_path: Path) -> None:
    assert validate_output_path(str(tmp_path), OutputFormat.EPUB) == str(
        tmp_path / "swift_book.epub"
    )

    with pytest.raises(ValueError, match="not a PDF file"):
        validate_output_path(str(tmp_path / "book.epub"), OutputFormat.PDF)


def test_configure_logging_is_idempotent(
    capsys: pytest.CaptureFixture[str],
) -> None:
    root_logger = logging.getLogger()
    try:
        configure_logging(verbose=False)
        configure_logging(verbose=False)
        logging.getLogger("swift_book_pdf.tests.cli").info("hello")

        assert capsys.readouterr().out.count("[INFO]: hello") == 1
        assert len(root_logger.handlers) == 1
    finally:
        root_logger.handlers.clear()
        root_logger.setLevel(logging.NOTSET)


def test_epub_cli_validates_cover_option_values() -> None:
    assert validate_hex_color(Mock(), Mock(), "#123") == "#123"
    assert validate_hex_color(Mock(), Mock(), "#112233") == "#112233"
    assert validate_hex_color(Mock(), Mock(), None) is None

    with pytest.raises(click.BadParameter, match="not a valid hex color"):
        validate_hex_color(Mock(), Mock(), "33519e")
    with pytest.raises(
        click.UsageError,
        match="--current-edition and --nightly-edition",
    ):
        epub_cli_config.resolve_cli_cover_variant(
            current_edition=True,
            nightly_edition=True,
        )


def test_epub_cli_cover_variant_resolves_hidden_flags() -> None:
    assert epub_cli_config.resolve_cli_cover_variant(True, False) == "current"
    assert epub_cli_config.resolve_cli_cover_variant(False, True) == "nightly"
    assert epub_cli_config.resolve_cli_cover_variant(False, False) is None
