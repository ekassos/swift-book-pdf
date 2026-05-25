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

SUMMARY_OF_THE_GRAMMAR_KEY = "summaryofthegrammar"
SUMMARY_OF_THE_GRAMMAR_FILE_NAME = "SummaryOfTheGrammar.md"
SUMMARY_DEFAULT_TITLE = "Summary of the Grammar"
SUMMARY_DEFAULT_SUBTITLE = "Read the whole formal grammar."
SUMMARY_HEADING_LINE_COUNT = 2
SUMMARY_ECHO_PATTERN = re.compile(r'echo\s+"([^"]*)"')
SUMMARY_SCRIPT_END_PATTERN = re.compile(r"}\s*>")
SUMMARY_SOURCE_PATH_PATTERN = re.compile(
    r"awk -f bin/extract_grammar\.awk "
    r"(?P<path>TSPL\.docc/ReferenceManual/[A-Za-z0-9._-]+\.md)"
)
SUMMARY_FALLBACK_SOURCE_PATHS = (
    "TSPL.docc/ReferenceManual/LexicalStructure.md",
    "TSPL.docc/ReferenceManual/Types.md",
    "TSPL.docc/ReferenceManual/Expressions.md",
    "TSPL.docc/ReferenceManual/Statements.md",
    "TSPL.docc/ReferenceManual/Declarations.md",
    "TSPL.docc/ReferenceManual/Attributes.md",
    "TSPL.docc/ReferenceManual/Patterns.md",
    "TSPL.docc/ReferenceManual/GenericParametersAndArguments.md",
)
