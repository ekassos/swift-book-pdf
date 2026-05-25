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

"""Shared Click option decorators."""

from collections.abc import Callable

import click

OptionTarget = Callable[..., object]

LEGAL_NOTICES_OPTION_HELP = (
    "Omit the generated legal notices chapter. This may remove attribution, "
    "licensing, trademark, and non-affiliation disclaimers that can be "
    "required for redistribution."
)


def output_path_argument(func: OptionTarget) -> OptionTarget:
    """Add the optional output path argument shared by PDF and EPUB commands.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    return click.argument(
        "output_path",
        type=click.Path(resolve_path=True),
        default=".",
        required=False,
    )(func)


def source_options(func: OptionTarget) -> OptionTarget:
    """Add shared Swift Book source-selection options.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
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
    return apply_options(func, decorators)


def override_version_option(func: OptionTarget) -> OptionTarget:
    """Add the shared version override option.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    return click.option(
        "--override-version",
        type=str,
        default=None,
        help='Override the version number. Include "beta" for beta versions.',
    )(func)


def legal_notices_option(func: OptionTarget) -> OptionTarget:
    """Add the generated legal notices opt-out option.

    Args:
        func: Click command callback to decorate.

    Returns:
        Decorated command callback.
    """
    return click.option(
        "--dangerously-skip-legal-notices",
        is_flag=True,
        help=LEGAL_NOTICES_OPTION_HELP,
    )(func)


def version_option(
    prog_name: str,
) -> Callable[[OptionTarget], OptionTarget]:
    """Build the package version option for one command.

    Args:
        prog_name: Program name to display in the version message.

    Returns:
        Click version option decorator.
    """
    return click.version_option(
        prog_name=prog_name,
        message="\033[1m%(prog)s\033[0m (version \033[36m%(version)s\033[0m)",
    )


def apply_options(
    func: OptionTarget,
    decorators: tuple[Callable[[OptionTarget], OptionTarget], ...],
) -> OptionTarget:
    """Apply Click option decorators in declaration order.

    Args:
        func: Click command callback to decorate.
        decorators: Decorators to apply.

    Returns:
        Decorated command callback.
    """
    for decorator in reversed(decorators):
        func = decorator(func)
    return func
