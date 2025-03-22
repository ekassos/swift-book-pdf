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


def configure_logging(verbose: bool):
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
    last_lines = []
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

            # Split long lines
            if len(line.rstrip("\n")) > MAX_LINE_LENGTH:
                wrapped_lines = textwrap.wrap(line.rstrip("\n"), width=MAX_LINE_LENGTH)
                for wrapped_line in wrapped_lines:
                    last_lines.append(wrapped_line)
            else:
                last_lines.append(line.rstrip("\n"))

            # Keep only the last max_lines lines
            if max_lines is not None and len(last_lines) > max_lines:
                last_lines = last_lines[-max_lines:]

            if not is_debug:
                for _ in range(printed_lines):
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[2K")

            out = "\n".join(last_lines)
            sys.stdout.write(GRAY + out + RESET + "\n")
            sys.stdout.flush()
            printed_lines = len(last_lines)

        process.wait()

        if not is_debug:
            for _ in range(printed_lines):
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[2K")
            sys.stdout.write("\033[F")

        sys.stdout.flush()
    except:
        process.kill()
        process.wait()
        raise
