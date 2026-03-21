# Copyright 2025 Evangelos Kassos
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
import sys
import textwrap
from subprocess import Popen
from typing import Callable, Optional


def configure_logging(verbose: bool) -> None:
    """Configures logging globally based on verbosity."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(levelname)s]: %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.propagate = False


def run_process_with_logs(
    process: Popen[str],
    MAX_LINES: int = 10,
    MAX_LINE_LENGTH: int = 80,
    log_check_func: Optional[Callable] = None,
) -> None:
    last_lines: list[str] = []
    printed_lines = 0
    GRAY = "\033[37m"
    RESET = "\033[0m"

    is_debug = logging.getLogger().isEnabledFor(logging.DEBUG)
    max_lines = None if is_debug else MAX_LINES

    try:
        while True:
            if process.stdout is None:
                break
            line = process.stdout.readline()
            if not line:
                break

            # Check if the line contains a specific log message
            if log_check_func is not None:
                log_check_func(line)

            _append_wrapped_line(last_lines, line, MAX_LINE_LENGTH)
            last_lines = _trim_output_buffer(last_lines, max_lines)

            if not is_debug:
                _clear_printed_lines(printed_lines)

            out = "\n".join(last_lines)
            sys.stdout.write(GRAY + out + RESET + "\n")
            sys.stdout.flush()
            printed_lines = len(last_lines)

        process.wait()

        if not is_debug:
            _clear_printed_lines(printed_lines)
            sys.stdout.write("\033[F")

        sys.stdout.flush()
    except:
        process.kill()
        process.wait()
        raise


def _append_wrapped_line(
    last_lines: list[str], line: str, max_line_length: int
) -> None:
    stripped_line = line.rstrip("\n")
    if len(stripped_line) > max_line_length:
        last_lines.extend(textwrap.wrap(stripped_line, width=max_line_length))
        return

    last_lines.append(stripped_line)


def _trim_output_buffer(last_lines: list[str], max_lines: int | None) -> list[str]:
    if max_lines is None or len(last_lines) <= max_lines:
        return last_lines
    return last_lines[-max_lines:]


def _clear_printed_lines(printed_lines: int) -> None:
    for _ in range(printed_lines):
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[2K")
