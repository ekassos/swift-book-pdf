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

"""PDF Click command entrypoint."""

from functools import partial

import click

import swift_book_pdf.pdf.cli.config as pdf_config
from swift_book_pdf.cli.common import run_build
from swift_book_pdf.cli.legal_notices import legal_notices_option
from swift_book_pdf.cli.options import (
    OptionTarget,
    apply_options,
    output_path_argument,
    override_version_option,
    source_options,
    version_option,
)
from swift_book_pdf.core.output import OutputFormat
from swift_book_pdf.pdf.builder import build_pdf
from swift_book_pdf.pdf.cli.options import (
    pdf_appearance_options,
    pdf_document_options,
    pdf_gutter_option,
    pdf_typography_options,
)
from swift_book_pdf.pdf.contracts import PDFBackend
from swift_book_pdf.pdf.options import EngineKind
from swift_book_pdf.pdf.registry import select_backend

DEFAULT_ENGINE = EngineKind.LATEX
LATEX_BACKEND = select_backend(EngineKind.LATEX)
BACKENDS_BY_KIND = {LATEX_BACKEND.kind: LATEX_BACKEND}
BACKENDS = tuple(BACKENDS_BY_KIND.values())


def apply_backend_build_options(func: OptionTarget) -> OptionTarget:
    """Add build options for every registered PDF backend."""
    return apply_options(
        func,
        tuple(backend.build_options for backend in BACKENDS),
    )


def apply_backend_command_options(func: OptionTarget) -> OptionTarget:
    """Add command options for every registered PDF backend."""
    return apply_options(
        func,
        tuple(backend.command_options for backend in BACKENDS),
    )


@click.command(name="swift-book-pdf", help="")
@output_path_argument
@pdf_document_options
@apply_backend_build_options
@override_version_option
@apply_backend_command_options
@click.option(
    "--engine",
    type=click.Choice([backend.kind.value for backend in BACKENDS]),
    default=DEFAULT_ENGINE.value,
    hidden=True,
)
@pdf_typography_options
@pdf_appearance_options
@legal_notices_option
@pdf_gutter_option
@source_options
@version_option("Swift-Book-PDF")
def pdf(  # noqa: PLR0913
    output_path: str,
    mode: str,
    paper: str,
    engine: str,
    override_version: str | None,
    font_size: float | None,
    dark: bool,
    dangerously_skip_legal_notices: bool,
    gutter: bool | None,
    input_path: str | None,
    source_ref: str | None,
    source_sha: str | None,
    verbose: bool,
    **backend_options: object,
) -> None:
    """Build the PDF command from parsed Click options.

    Args:
        output_path: User-provided output path.
        mode: Rendering mode option value.
        paper: Paper size option value.
        engine: PDF rendering engine option value.
        override_version: Optional Swift version override.
        font_size: Optional base paragraph font size.
        dark: Whether dark mode should be rendered.
        dangerously_skip_legal_notices: Whether generated notices are omitted.
        gutter: Optional gutter override.
        input_path: Optional local Swift Book repository path.
        source_ref: Optional Swift Book Git ref.
        source_sha: Optional Swift Book commit SHA.
        verbose: Whether debug logging should be enabled.
        backend_options: Engine-specific option values.
    """
    backend = _select_backend_for_cli(EngineKind(engine))
    doc_config = pdf_config.build_doc_config(
        mode=mode,
        paper=paper,
        dark=dark,
        gutter=gutter,
        font_size=font_size,
    )

    run_build(
        verbose=verbose,
        output_path=output_path,
        output_format=OutputFormat.PDF,
        config_builder=partial(
            pdf_config.build_pdf_config,
            backend=backend,
            doc_config=doc_config,
            backend_options=backend_options,
            override_version=override_version,
            source_ref=source_ref,
            source_sha=source_sha,
            input_path=input_path,
            dangerously_skip_legal_notices=dangerously_skip_legal_notices,
        ),
        builder=build_pdf,
        error_details=pdf_config.format_pdf_build_details,
    )


def _select_backend_for_cli(engine: EngineKind) -> PDFBackend:
    try:
        return BACKENDS_BY_KIND[engine]
    except KeyError as exc:
        raise click.ClickException(
            f"Unsupported PDF engine: {engine.value}"
        ) from exc


if __name__ == "__main__":
    pdf()
