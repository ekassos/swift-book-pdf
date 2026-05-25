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

"""DocC directive removal for Markdown source lines."""


def remove_directives(file_content: list[str]) -> list[str]:
    """Remove DocC directive blocks from Markdown content.

    Args:
        file_content: Source lines from a Swift Book Markdown file.

    Returns:
        A new list of lines with multi-line DocC directives removed. Lines
        outside directives are preserved as-is, including their original
        trailing newlines.
    """
    result: list[str] = []
    in_multiline_string = False

    for line in file_content:
        stripped_line = line.strip()

        # Check if the line is the start of a multi-line directive
        if stripped_line.startswith("@") and stripped_line.endswith("{"):
            in_multiline_string = True
        elif in_multiline_string and stripped_line == "}":
            # End of a multi-line directive
            in_multiline_string = False
        elif not in_multiline_string:
            # If not in a multi-line directive, add the line to the result
            result.append(line)

    return result
