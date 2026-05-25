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

"""Shared regular expressions for the Markdown block parser."""

import re

TABLE_DIVIDER_PATTERN = re.compile(r"^\|\s*[-:]+(\s*\|\s*[-:]+)+\s*\|?$")
ORDERED_LIST_PATTERN = re.compile(r"^\s*\d+\.\s+(.*)$")
INDENTED_CONTINUATION_PATTERN = re.compile(r"^\s{2,}\S")
NOTE_LABEL_PATTERN = re.compile(r"^([^:]+):\s*(.*)$")
NOTE_PARAGRAPH_BOUNDARY_PATTERN = re.compile(r"^\s*([#>-]|```swift|[-]\s+)")
BULLET_PATTERN = re.compile(r"^(\s*)-\s+(.*)$")
