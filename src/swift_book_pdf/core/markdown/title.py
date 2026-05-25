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

"""Title and version extraction for Swift Book Markdown."""

import re

VERSIONED_TITLE_PATTERN = re.compile(
    r"# The Swift Programming Language \((.*?)\)"
)


def normalize_versioned_title(file_content: list[str]) -> list[str]:
    """Normalize the TSPL title heading into title and version lines.

    Args:
        file_content: Markdown lines that may contain a title in the form
            `# The Swift Programming Language (...)`.

    Returns:
        Markdown lines with any versioned TSPL title split across two lines.
    """
    updated_lines: list[str] = []

    for line in file_content:
        match = VERSIONED_TITLE_PATTERN.search(line)
        if match:
            updated_lines.append("# The Swift Programming Language\n")
            updated_lines.append(f"Version {match.group(1)}\n")
        else:
            updated_lines.append(line)

    return updated_lines


def extract_version_info(file_content: list[str]) -> str | None:
    """Extract the Swift version from a TSPL title heading."""
    for line in file_content:
        match = VERSIONED_TITLE_PATTERN.search(line)
        if match:
            return match.group(1)
    return None


def resolve_version_info(
    file_content: list[str],
    override_version: str | None = None,
) -> str:
    """Resolve the version string used in generated book metadata.

    Args:
        file_content: Table-of-contents Markdown lines to inspect when no
            override is provided.
        override_version: Optional caller-provided version string. Whitespace
            is stripped before use.

    Returns:
        The normalized override version or the version parsed from the table of
        contents.
    Raises:
        ValueError: If neither an override nor a parseable TOC title provides
            the version.
    """
    if override_version is not None:
        normalized_override_version = override_version.strip()
        if normalized_override_version:
            return normalized_override_version

    version_info = extract_version_info(file_content)
    if version_info is not None:
        return version_info

    raise ValueError(
        "Couldn't determine the Swift version by parsing the table of "
        "contents. Please provide --override-version."
    )
