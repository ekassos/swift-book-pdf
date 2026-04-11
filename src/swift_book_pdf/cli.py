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
from typing import TypeVar

import click

from swift_book_pdf.config import Config, PDFConfig
from swift_book_pdf.files import validate_output_path
from swift_book_pdf.log import configure_logging
from swift_book_pdf.schema import OutputFormat

ConfigT = TypeVar("ConfigT", bound=Config)
LEGAL_NOTICES_WARNING = (
    "Generated legal notices were omitted from this build because "
    "--dangerously-skip-legal-notices was enabled. Omitting these notices "
    "may result in missing attribution, licensing, trademark, and "
    "non-affiliation disclosures that could be required for lawful "
    "redistribution. Do not distribute or publish this output unless you "
    "have independently verified that all applicable legal obligations "
    "remain satisfied. Proceed at your own risk."
)


def output_path_argument(
    func: Callable[..., object],
) -> Callable[..., object]:
    return click.argument(
        "output_path",
        type=click.Path(resolve_path=True),
        default=".",
        required=False,
    )(func)


def common_options(func: Callable[..., object]) -> Callable[..., object]:
    decorators = (
        click.option(
            "--input-path",
            "-i",
            help=(
                "Path to the root of a local copy of the swift-book repo. "
                "If not provided, the repository will be cloned from GitHub."
            ),
            type=click.Path(resolve_path=True),
            required=False,
        ),
        click.option(
            "--source-ref",
            type=str,
            default=None,
            help="Git tag, branch, or ref from the swift-book repository to build from",
        ),
        click.option(
            "--source-sha",
            type=str,
            default=None,
            help="Git commit SHA from the swift-book repository to build from",
        ),
        click.option(
            "--verbose", is_flag=True, help="Enable verbose logging."
        ),
    )

    for decorator in reversed(decorators):
        func = decorator(func)
    return func


def version_option(
    prog_name: str,
) -> Callable[[Callable[..., object]], Callable[..., object]]:
    return click.version_option(
        prog_name=prog_name,
        message="\033[1m%(prog)s\033[0m (version \033[36m%(version)s\033[0m)",
    )


def run_build(
    *,
    verbose: bool,
    output_path: str,
    output_format: OutputFormat,
    config_builder: Callable[[str, str], ConfigT],
    builder: Callable[[ConfigT], None],
) -> None:
    configure_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        validated_output_path = validate_output_path(
            output_path, output_format
        )
    except ValueError as e:
        logger.error(str(e))
        return

    with TemporaryDirectory() as temp:
        config: ConfigT | None = None
        try:
            config = config_builder(temp, validated_output_path)
            if config.dangerously_skip_legal_notices:
                logger.warning(LEGAL_NOTICES_WARNING)
            builder(config)
        except ValueError as e:
            logger.error(str(e))
        except Exception as e:
            details = _format_build_details(config)
            logger.error(
                f"Couldn't build The Swift Programming Language book: {e}{details}",
            )


def _format_build_details(config: Config | None) -> str:
    if isinstance(config, PDFConfig):
        return f"\n{config.font_config}"
    return ""
