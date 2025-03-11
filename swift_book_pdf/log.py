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

from subprocess import Popen
import sys
import textwrap


def run_process_with_logs(
    process: Popen[str], MAX_LINES: int = 5, MAX_LINE_LENGTH: int = 80
) -> None:
    last_lines = []
    printed_lines = 0
    BLUE = "\033[34m"
    RESET = "\033[0m"

    while True:
        if process.stdout is None:
            break
        line = process.stdout.readline()
        if not line:
            break

        # Split long lines
        if len(line.rstrip("\n")) > MAX_LINE_LENGTH:
            wrapped_lines = textwrap.wrap(line.rstrip("\n"), width=MAX_LINE_LENGTH)
            for wrapped_line in wrapped_lines:
                last_lines.append(wrapped_line)
        else:
            last_lines.append(line.rstrip("\n"))

        # Keep only the last MAX_LINES lines
        if len(last_lines) > MAX_LINES:
            last_lines = last_lines[-MAX_LINES:]

        for _ in range(printed_lines):
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[2K")

        out = "\n".join(last_lines)
        sys.stdout.write(BLUE + out + RESET + "\n")
        sys.stdout.flush()
        printed_lines = len(last_lines)

    process.wait()

    for _ in range(printed_lines):
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[2K")
    sys.stdout.write("\033[F")

    sys.stdout.flush()
