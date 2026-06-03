# Copyright 2026 Evangelos Kassos
#
# Portions derived from highlight.js:
#   Copyright (c) 2006, Ivan Sagalaev.
#   Licensed under the BSD 3-Clause License.
#   See THIRD-PARTY-NOTICES.txt for details.
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

"""Compose regex source strings for the Swift lexer."""

from typing import TypedDict

# A "regex-like" in highlight.js is either a string or a RegExp object
# exposing a `.source`. In this Python port we only ever pass pattern
# strings, so a regex source is simply `str`.
RegexSource = str


class RegexEitherOptions(TypedDict, total=False):
    """Options accepted as the trailing argument to `either`."""

    capture: bool


def source(re: RegexSource | None) -> str | None:
    """Return the pattern text for a regex-like value.

    Args:
        re: Regex source string or `None`.

    Returns:
        Pattern text, or `None` for falsy input.
    """
    if not re:
        return None
    return re


def lookahead(re: RegexSource) -> str:
    """Wrap a pattern in a non-consuming lookahead.

    Args:
        re: Regex source to wrap.

    Returns:
        Regex source in `(?=...)` form.
    """
    return concat("(?=", re, ")")


def any_number_of_times(re: RegexSource) -> str:
    """Match the pattern zero or more times.

    Args:
        re: Regex source to repeat.

    Returns:
        Regex source in `(?:...)*` form.
    """
    return concat("(?:", re, ")*")


def optional(re: RegexSource) -> str:
    """Match the pattern zero or one time.

    Args:
        re: Regex source to make optional.

    Returns:
        Regex source in `(?:...)?` form.
    """
    return concat("(?:", re, ")?")


def concat(*args: RegexSource) -> str:
    """Join regex sources into one pattern string.

    Args:
        *args: Regex source fragments.

    Returns:
        Concatenated regex source.
    """
    return "".join(source(x) or "" for x in args)


def either(
    *args: RegexSource | RegexEitherOptions,
) -> str:
    """Build an alternation from the given patterns.

    Args:
        *args: Regex source fragments, optionally followed by an options
            dictionary supporting `{"capture": True}`.

    Returns:
        Capturing or non-capturing alternation source.
    """
    arg_list = list(args)
    opts = _strip_options_from_args(arg_list)
    prefix = "" if opts.get("capture") else "?:"
    parts = [source(x) or "" for x in arg_list]  # type: ignore[arg-type]
    return "(" + prefix + "|".join(parts) + ")"


def _strip_options_from_args(
    args: list[RegexSource | RegexEitherOptions],
) -> RegexEitherOptions:
    """Pop a trailing options dictionary from an argument list.

    Args:
        args: Mutable list of regex fragments and possibly an options
            dictionary.

    Returns:
        Removed options dictionary, or an empty dictionary when no options
        were present.
    """
    if not args:
        return {}
    last = args[-1]
    if isinstance(last, dict):
        args.pop()
        return last
    return {}
