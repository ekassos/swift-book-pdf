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

"""User-facing messages for Summary of the Grammar generation."""

AWK_UNAVAILABLE_FALLBACK = (
    "Falling back to built-in grammar extraction because "
    "swift-book/bin/extract_grammar.awk or `awk` is unavailable."
)
AWK_FAILED_FALLBACK = (
    "Falling back to built-in grammar extraction because "
    "swift-book/bin/extract_grammar.awk couldn't be used."
)
AWK_GENERATION_FAILED = (
    "Couldn't generate Summary of the Grammar using "
    "swift-book/bin/extract_grammar.awk: %s"
)
GENERATE_GRAMMAR_PARSE_FAILED = (
    "Couldn't parse Summary of the Grammar source chapters from "
    "swift-book/bin/generate-grammar; using fallback chapter list."
)
PUBLISH_BOOK_PARSE_FAILED = (
    "Couldn't parse Summary of the Grammar source chapters from "
    "swift-book/bin/publish-book; using fallback chapter list."
)
SUMMARY_SCRIPT_MISSING = (
    "swift-book/bin/generate-grammar and swift-book/bin/publish-book are "
    "missing; using fallback chapter list for Summary of the Grammar."
)
FALLBACK_CHAPTERS_MISSING = (
    "Couldn't generate Summary of the Grammar because fallback source "
    "chapters are missing: %s"
)
