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


def replace_and_extract_version(
    file_content: list[str],
) -> tuple[list[str], str | None]:
    """Normalize the TSPL title heading and extract the Swift version.

    Args:
        file_content: Markdown lines that may contain a title in the form
            `# The Swift Programming Language (...)`.

    Returns:
        A tuple containing the updated lines and the extracted version string.
        When no versioned title is present, the original lines are returned
        with `None` for the version.
    """

    version_info = None
    updated_lines: list[str] = []

    for line in file_content:
        match = re.search(r"# The Swift Programming Language \((.*?)\)", line)

        if match:
            # Extract version information
            version_info = match.group(1)
            # Use a two-line format for the version information
            updated_lines.append("# The Swift Programming Language\n")
            updated_lines.append(f"Version {version_info}\n")
        else:
            # If no match, keep the line unchanged
            updated_lines.append(line)

    return updated_lines, version_info


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

    _, version_info = replace_and_extract_version(file_content)
    if version_info is not None:
        return version_info

    raise ValueError(
        "Couldn't determine the Swift version by parsing the table of "
        "contents. Please provide --override-version."
    )
