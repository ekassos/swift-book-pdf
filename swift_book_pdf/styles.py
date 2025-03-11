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

from pygments.style import Style
from pygments.token import (
    Text,
    Whitespace,
    Escape,
    Error,
    Other,
    Keyword,
    Name,
    Literal,
    String,
    Number,
    Punctuation,
    Operator,
    Comment,
    Generic,
)


class CustomSwiftBookStyle(Style):
    styles = {
        # Special tokens
        Text: "#000000",  # --color-syntax-plain-text: #000
        Whitespace: "#000000",
        Escape: "#000000",
        Error: "#FF0000",
        Other: "#000000",
        # Common tokens for source code
        Keyword: "#ad3da4",  # --color-syntax-keywords: #ad3da4
        Name: "#000000",
        Literal: "#000000",
        String: "#d12f1b",  # --color-syntax-strings: #d12f1b
        Number: "#272ad8",  # --color-syntax-numbers: #272ad8
        Punctuation: "#272ad8",  # --color-syntax-characters: #272ad8
        Operator: "#000000",  # --color-syntax-operators: #000000
        Comment: "#707f8c",  # --color-syntax-comments: #707f8c
        Generic: "#000000",
        # Additional refinement for Swift declarations and names
        Name.Class: "#703daa",  # --color-syntax-other-class-names: #703daa
        Name.Constant: "#4b21b0",  # --color-syntax-other-constants: #4b21b0
        Name.Decorator: "#047cb0",  # --color-syntax-other-declarations: #047cb0
        Name.Function: "#4b21b0",  # --color-syntax-other-function-and-method-names: #4b21b0
        Name.Namespace: "#703daa",  # --color-syntax-other-instance-variables-and-globals: #703daa
        Name.Preproc: "#78492a",  # --color-syntax-other-preprocessor-macros: #78492a
        Name.Builtin: "#703daa",  # --color-syntax-other-instance-variables-and-globals: #703daa
        Name.Builtin.Pseudo: "#703daa",  # --color-syntax-other-instance-variables-and-globals: #703daa
        # Generic insertions and deletions
        Generic.Deleted: "#FF0000",  # --color-syntax-deletion: red
        Generic.Inserted: "#008000",  # --color-syntax-addition: green
        Generic.Heading: "#ba2da2",  # --color-syntax-heading: #ba2da2
        Generic.Subheading: "#506375",  # --color-syntax-documentation-markup-keywords: #506375
    }
