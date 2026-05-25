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

"""HTML comment removal for Markdown source lines."""


def remove_multiline_comments(lines: list[str]) -> list[str]:
    """Remove HTML comments from Markdown lines.

    Args:
        lines: Markdown source lines that may contain `<!-- ... -->` comments.

    Returns:
        A new list with comment-only ranges removed. Text before or after a
        same-line comment is preserved when it is non-empty.
    """
    output: list[str] = []
    in_comment = False
    for line in lines:
        if not in_comment:
            if "<!--" in line:
                if "-->" in line:
                    # Remove same-line comment content without regex-based HTML parsing.
                    comment_start = line.find("<!--")
                    comment_end = line.find("-->", comment_start)
                    if comment_end != -1:
                        comment_end += len("-->")
                    line_without_comment = line[:comment_start] + (
                        line[comment_end:] if comment_end != -1 else ""
                    )
                    if line_without_comment.strip():
                        output.append(line_without_comment)
                else:
                    in_comment = True
                    before = line.split("<!--")[0]
                    if before.strip():
                        output.append(before)
            else:
                output.append(line)
        elif "-->" in line:
            in_comment = False
            after = line.split("-->", 1)[1]
            if after.strip():
                output.append(after)
    return output
