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
    Keyword,
    Name,
    Operator,
    Comment,
    String,
    Number,
    Punctuation,
    Error,
)


class CustomSwiftBookStyle(Style):
    styles = {
        Text: "#000",
        Error: "#000",
        Keyword: "#ad3da4",  # --color-syntax-keywords
        Keyword.Constant: "#ad3da4",  # --color-syntax-keywords
        Keyword.Declaration: "#ad3da4",  # --color-syntax-keywords
        Keyword.Reserved: "#ad3da4",  # --color-syntax-keywords
        Name: "#000",
        Name.Builtin: "#703daa",  # --color-syntax-other-type-names
        Name.Builtin.Pseudo: "#000",
        Name.Class: "#703daa",  # --color-syntax-other-type-names
        Name.Function: "#703daa",  # --color-syntax-other-type-names
        Name.Variable: "#000",
        String: "#d12f1b",  # --color-syntax-strings
        String.Escape: "#d12f1b",  # --color-syntax-strings
        String.Interpol: "#000",
        Number: "#272ad8",  # --color-syntax-numbers
        Operator: "#000",
        Punctuation: "#000",
        Comment: "#707f8c",  # --color-syntax-comments
        Comment.Special: "#506375",  # --color-syntax-documentation-markup-keywords
    }


class CustomSwiftBookDarkStyle(Style):
    styles = {
        Text: "#fff",
        Error: "#fff",
        Keyword: "#ff7ab2",  # --color-syntax-keywords
        Keyword.Constant: "#ff7ab2",  # --color-syntax-keywords
        Keyword.Declaration: "#ff7ab2",  # --color-syntax-keywords
        Keyword.Reserved: "#ff7ab2",  # --color-syntax-keywords
        Name: "#fff",
        Name.Builtin: "#dabaff",  # --color-syntax-other-type-names
        Name.Builtin.Pseudo: "#fff",
        Name.Class: "#dabaff",  # --color-syntax-other-type-names
        Name.Function: "#dabaff",  # --color-syntax-other-type-names
        Name.Variable: "#fff",
        String: "#ff8170",  # --color-syntax-strings
        String.Escape: "#ff8170",  # --color-syntax-strings
        String.Interpol: "#fff",
        Number: "#d9c97c",  # --color-syntax-numbers
        Operator: "#fff",
        Punctuation: "#fff",
        Comment: "#7f8c98",  # --color-syntax-comments
        Comment.Special: "#a3b1bf",  # --color-syntax-documentation-markup-keywords
    }
