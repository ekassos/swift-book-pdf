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


def normalize_grammar_summary_text(summary_text: str) -> str:
    """Normalize generated grammar blocks for stable downstream rendering.

    Args:
        summary_text: Markdown produced by upstream awk extraction or the
            built-in Python extractor.

    Returns:
        Markdown with legacy separated grammar rule paragraphs converted to the
        current explicit line-break format. Input that already uses explicit
        grammar breaks is preserved.
    """
    lines = summary_text.splitlines()
    normalized_lines: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line.startswith("> Grammar of "):
            normalized_lines.append(line)
            index += 1
            continue

        block_lines = [line]
        index += 1
        while index < len(lines) and (
            lines[index].startswith(">") or not lines[index].strip()
        ):
            block_lines.append(lines[index])
            index += 1
        normalized_lines.extend(normalize_grammar_block(block_lines))

    return "\n".join(normalized_lines) + (
        "\n" if summary_text.endswith("\n") else ""
    )


def normalize_grammar_block(block_lines: list[str]) -> list[str]:
    """Normalize one contiguous `> Grammar of ...` block.

    Args:
        block_lines: Lines belonging to a single grammar block, including the
            opening `> Grammar of ...` line.

    Returns:
        Normalized block lines. Blocks that are empty or already have explicit
        line breaks are returned unchanged.
    """
    if len(block_lines) <= 1:
        return block_lines
    if any(line_uses_explicit_grammar_break(line) for line in block_lines):
        return block_lines

    normalized_lines = [block_lines[0]]
    current_group: list[str] = []
    separator_count = 0
    started_rules = False

    for line in block_lines[1:]:
        if line.strip() == ">":
            separator_count += 1
            continue

        if not line.strip():
            continue

        if not started_rules and separator_count > 0:
            normalized_lines.append(">")
        elif separator_count > 1 and current_group:
            normalized_lines.extend(
                normalize_grammar_rule_paragraph(current_group)
            )
            normalized_lines.append(">")
            current_group = []

        current_group.append(line)
        started_rules = True
        separator_count = 0

    if current_group:
        normalized_lines.extend(
            normalize_grammar_rule_paragraph(current_group)
        )

    return normalized_lines


def normalize_grammar_rule_paragraph(
    paragraph_rules: list[str],
) -> list[str]:
    """Add explicit Markdown line breaks between adjacent grammar rules.

    Args:
        paragraph_rules: Consecutive blockquoted grammar rule lines.

    Returns:
        Rule lines with trailing backslashes added to every line except the
        last one, unless explicit breaks were already present.
    """
    if any(line_uses_explicit_grammar_break(line) for line in paragraph_rules):
        return paragraph_rules

    normalized_rules: list[str] = []
    for index, line in enumerate(paragraph_rules):
        if index < len(paragraph_rules) - 1:
            normalized_rules.append(line.rstrip() + " \\")
        else:
            normalized_rules.append(line)
    return normalized_rules


def line_uses_explicit_grammar_break(line: str) -> bool:
    """Return whether a grammar line already ends with a Markdown break.

    Args:
        line: Grammar rule line to inspect.

    Returns:
        True when the stripped line ends with `\\`.
    """
    return line.rstrip().endswith("\\")
