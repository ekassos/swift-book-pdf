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

"""EPUB Click callback validators."""

import re

import click

_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


def validate_hex_color(
    _ctx: click.Context, _param: click.Parameter, value: str | None
) -> str | None:
    """Validate an optional `#RGB` or `#RRGGBB` color value.

    Args:
        _ctx: Active Click context.
        _param: Click parameter being validated.
        value: User-provided option value.

    Returns:
        The validated value, or `None` when the option was omitted.

    Raises:
        click.BadParameter: If `value` is not a supported hex color string.
    """
    if value is None:
        return None
    if not _HEX_COLOR_RE.match(value):
        raise click.BadParameter(
            f"{value!r} is not a valid hex color (expected #RGB or #RRGGBB)."
        )
    return value
