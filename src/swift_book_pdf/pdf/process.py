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

"""PDF subprocess logging helpers."""

import logging
import sys
import textwrap
from collections.abc import Callable
from subprocess import Popen


def run_process_with_logs(
    process: Popen[str],
    max_lines_default: int = 10,
    max_line_length: int = 80,
    log_check_func: Callable[[str], None] | None = None,
) -> None:
    """Stream a subprocess log while keeping non-debug output compact.

    Args:
        process: Running process whose `stdout` is read line by line.
        max_lines_default: Number of recent wrapped lines to display outside
            debug logging.
        max_line_length: Maximum line width before wrapping display output.
        log_check_func: Optional callback invoked for each raw output line.

    Raises:
        Exception: Any exception raised while reading or processing output. The
            process is killed before the exception is re-raised.
    """
    last_lines: list[str] = []
    printed_lines = 0
    gray = "\033[37m"
    reset = "\033[0m"

    is_debug = logging.getLogger().isEnabledFor(logging.DEBUG)
    max_lines = None if is_debug else max_lines_default

    try:
        while True:
            if process.stdout is None:
                break
            line = process.stdout.readline()
            if not line:
                break

            if log_check_func is not None:
                log_check_func(line)

            _append_wrapped_line(last_lines, line, max_line_length)
            last_lines = _trim_output_buffer(last_lines, max_lines)

            if not is_debug:
                _clear_printed_lines(printed_lines)

            out = "\n".join(last_lines)
            sys.stdout.write(gray + out + reset + "\n")
            sys.stdout.flush()
            printed_lines = len(last_lines)

        process.wait()

        if not is_debug:
            _clear_printed_lines(printed_lines)
            sys.stdout.write("\033[F")

        sys.stdout.flush()
    except Exception:
        process.kill()
        process.wait()
        raise


def _append_wrapped_line(
    last_lines: list[str], line: str, max_line_length: int
) -> None:
    """Append one display line, wrapping it when it exceeds the width limit.

    Args:
        last_lines: Mutable recent-output buffer.
        line: Raw subprocess output line.
        max_line_length: Maximum display width before wrapping.
    """
    stripped_line = line.rstrip("\n")
    if len(stripped_line) > max_line_length:
        last_lines.extend(textwrap.wrap(stripped_line, width=max_line_length))
        return

    last_lines.append(stripped_line)


def _trim_output_buffer(
    last_lines: list[str], max_lines: int | None
) -> list[str]:
    """Trim the display buffer to the requested number of recent lines.

    Args:
        last_lines: Recent-output buffer.
        max_lines: Maximum lines to retain, or `None` to keep all lines.

    Returns:
        The original or trimmed buffer.
    """
    if max_lines is None or len(last_lines) <= max_lines:
        return last_lines
    return last_lines[-max_lines:]


def _clear_printed_lines(printed_lines: int) -> None:
    """Clear previously printed terminal lines.

    Args:
        printed_lines: Number of terminal lines to erase.
    """
    for _ in range(printed_lines):
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[2K")
