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

"""Markdown preprocessing transforms used before backend rendering."""

from swift_book_pdf.core.markdown.comments import remove_multiline_comments
from swift_book_pdf.core.markdown.directives import remove_directives
from swift_book_pdf.core.markdown.links import (
    convert_markdown_links,
    convert_reference_links_in_line,
)
from swift_book_pdf.core.markdown.title import (
    replace_and_extract_version,
    resolve_version_info,
)

__all__ = [
    "convert_markdown_links",
    "convert_reference_links_in_line",
    "remove_directives",
    "remove_multiline_comments",
    "replace_and_extract_version",
    "resolve_version_info",
]
