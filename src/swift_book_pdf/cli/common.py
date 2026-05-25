# Copyright 2025-2026 Evangelos Kassos
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
from collections.abc import Callable
from tempfile import TemporaryDirectory
from typing import Protocol, TypeVar

import click

from swift_book_pdf.cli.legal_notices import warn_if_legal_notices_skipped
from swift_book_pdf.cli.logging_config import configure_logging
from swift_book_pdf.cli.output import validate_output_path
from swift_book_pdf.core.output import OutputFormat


class BuildConfig(Protocol):
    """Build configuration fields used by shared CLI orchestration."""

    @property
    def dangerously_skip_legal_notices(self) -> bool:
        """Whether generated legal notices were intentionally omitted."""
        ...


ConfigT = TypeVar("ConfigT", bound=BuildConfig)


def run_build(  # noqa: PLR0913
    *,
    verbose: bool,
    output_path: str,
    output_format: OutputFormat,
    config_builder: Callable[[str, str], ConfigT],
    builder: Callable[[ConfigT], None],
    error_details: Callable[[ConfigT | None], str] | None = None,
) -> None:
    """Validate common CLI state and run one book builder.

    Args:
        verbose: Whether debug logging should be enabled.
        output_path: User-provided output path.
        output_format: Artifact format being built.
        config_builder: Callback that builds a concrete config from the
            temporary directory and validated output path.
        builder: Backend build function.
        error_details: Optional callback that appends backend-specific details
            to unexpected build errors.
    """
    configure_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        validated_output_path = validate_output_path(
            output_path, output_format
        )
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    with TemporaryDirectory() as temp:
        config: ConfigT | None = None
        try:
            config = config_builder(temp, validated_output_path)
            warn_if_legal_notices_skipped(config, logger)
            builder(config)
        except ValueError as e:
            raise click.ClickException(str(e)) from e
        except Exception as e:
            details = error_details(config) if error_details else ""
            raise click.ClickException(
                f"Couldn't build The Swift Programming Language book: {e}{details}"
            ) from e
