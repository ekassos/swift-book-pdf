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

import re

DOC_LINK_PATTERN = re.compile(r"<doc:([^>]+)>")
STRONG_PATTERN = re.compile(r"\*\*(.+?)\*\*")
EMPHASIS_PATTERN = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
HEADING_PATTERN = re.compile(r"^(#{1,4})\s+(.*)$")
DOC_TAG_LINE_PATTERN = re.compile(r"^-\s+<doc:(.*?)>\s*$")
PART_HEADING_PATTERN = re.compile(r"^###\s+(.*)$")
CODE_PLACEHOLDER_PATTERN = re.compile(r"<#(.*?)#>")
