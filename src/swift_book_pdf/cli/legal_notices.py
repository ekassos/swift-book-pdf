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

"""CLI legal-notice option text and runtime warnings."""

import logging
from collections.abc import Callable
from typing import Protocol

import click

OptionTarget = Callable[..., object]

LEGAL_NOTICES_OPTION_HELP = (
    "Omit the generated legal notices chapter. This may remove attribution, "
    "licensing, trademark, and non-affiliation disclaimers that can be "
    "required for redistribution."
)
LEGAL_NOTICES_WARNING = (
    "Generated legal notices were omitted from this build because "
    "--dangerously-skip-legal-notices was enabled. Omitting these notices "
    "may result in missing attribution, licensing, trademark, and "
    "non-affiliation disclosures that could be required for lawful "
    "redistribution. Do not distribute or publish this output unless you "
    "have independently verified that all applicable legal obligations "
    "remain satisfied. Proceed at your own risk."
)


class LegalNoticesConfig(Protocol):
    """Build configuration fields used by legal-notice CLI policy."""

    @property
    def dangerously_skip_legal_notices(self) -> bool:
        """Whether generated legal notices were intentionally omitted."""
        ...


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


def warn_if_legal_notices_skipped(
    config: LegalNoticesConfig, logger: logging.Logger
) -> None:
    """Log the CLI warning when generated legal notices are omitted."""
    if config.dangerously_skip_legal_notices:
        logger.warning(LEGAL_NOTICES_WARNING)
