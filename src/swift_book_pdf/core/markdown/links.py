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

"""Reference-link normalization for Markdown source lines."""

import re


def convert_reference_links_in_line(
    line: str, references: dict[str, str]
) -> str:
    """Convert reference-style links in one line to inline Markdown links.

    Args:
        line: Markdown line to rewrite.
        references: Mapping from reference label to URL collected from
            reference definition lines.

    Returns:
        The rewritten line. Unknown references are left unchanged.
    """
    pattern = re.compile(r"\[(.*?)\](?:\[(.*?)\])?")

    def repl(match: re.Match[str]) -> str:
        """Replace one reference-style Markdown link match.

        Args:
            match: Regex match for a possible reference-style link.
        Returns:
            The rewritten inline link, or the original text when no
            reference definition exists.
        """
        ref_1 = match.group(1)
        ref_2 = match.group(2)
        if ref_1 and ref_1 in references:
            return f"[{ref_1}]({references[ref_1]})"
        if ref_2 and ref_2 in references:
            if ref_1:
                return f"[{ref_1}]({references[ref_2]})"
            return f"[{ref_2}]({references[ref_2]})"
        return match.group(0)

    return pattern.sub(repl, line)


def convert_markdown_links(lines: list[str]) -> list[str]:
    """Convert reference-style Markdown links to inline Markdown links.

    Reference-style links are written with a link label in the content and a
    definition elsewhere in the document. For example:

    ```markdown
        This is an [example][].

        [example]: https://example.com
    ```

    This function rewrites the content line to:

    ```markdown
        This is an [example](https://example.com).
    ```

    Reference definition lines are removed from the returned content.

    Args:
        lines: Markdown lines that may include reference-style links and
            `[label]: URL` definitions.

    Returns:
        Content lines with known reference-style links rewritten to inline
        Markdown links. Reference definition lines are omitted.
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
    return [
        convert_reference_links_in_line(line, references)
        for line in content_lines
    ]
