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

import re


def remove_multiline_comments(lines: list[str]) -> list[str]:
    """
    Remove comments that may span multiple lines.
    All lines between <!-- and --> (inclusive) are discarded.
    """
    output: list[str] = []
    in_comment = False
    for line in lines:
        if not in_comment:
            if "<!--" in line:
                if "-->" in line:
                    # Remove comment content on same line
                    line = re.sub(r"<!--.*?-->", "", line)
                    if line.strip():
                        output.append(line)
                else:
                    in_comment = True
                    before = line.split("<!--")[0]
                    if before.strip():
                        output.append(before)
            else:
                output.append(line)
        else:
            if "-->" in line:
                in_comment = False
                after = line.split("-->", 1)[1]
                if after.strip():
                    output.append(after)
    return output


def convert_reference_links_in_line(line: str, references: dict[str, str]) -> str:
    """
    Substitute Markdown links in the provided line to the normal Markdown format.

    :param line: The line to substitute reference links in
    :param references: The references to substitute
    :return: The line with the reference links substituted
    """
    pattern = re.compile(r"\[(.*?)\](?:\[(.*?)\])?")

    def repl(match):
        ref_1 = match.group(1)
        ref_2 = match.group(2)
        if ref_1 and ref_1 in references:
            return f"[{ref_1}]({references[ref_1]})"
        elif ref_2 and ref_2 in references:
            if ref_1:
                return f"[{ref_1}]({references[ref_2]})"
            else:
                return f"[{ref_2}]({references[ref_2]})"
        else:
            return match.group(0)

    return pattern.sub(repl, line)


def convert_markdown_links(lines: list[str]) -> list[str]:
    """
    Convert Markdown links in the provided lines to the normal Markdown format.

    For reference, the format is:
    ```
    This is an [example][].

    [example]: https://example.com
    ```

    The reference link will be converted to:
    ```
    This is an [example](https://example.com).
    ```

    :param lines: The lines to convert reference links in
    :return: The lines with the reference links converted
    """
    references: dict[str, str] = {}
    content_lines: list[str] = []
    ref_pattern = re.compile(r"^\s*\[([^\]]+)\]:\s*(\S+)")
    for line in lines:
        m = ref_pattern.match(line)
        if m:
            references[m.group(1)] = m.group(2)
        else:
            content_lines.append(line)
    return [convert_reference_links_in_line(line, references) for line in content_lines]
