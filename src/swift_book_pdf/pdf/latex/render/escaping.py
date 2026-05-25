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

"""LaTeX escaping helpers."""

import re


def escape_texttt(text: str) -> str:
    """Escape characters that cause issues inside ``\\texttt``."""
    text = text.replace("\\", r"\textbackslash ")
    text = text.replace("{", r"\{")
    text = text.replace("}", r"\}")
    text = text.replace("_", r"\_")
    text = re.sub(r"(?<!\\)#", r"\#", text)
    text = text.replace("$", r"\$")
    text = text.replace("&", r"\&")
    text = text.replace("%", r"\%")
    text = text.replace("^", r"\textasciicircum ")
    text = text.replace("`", r"\textasciigrave ")
    text = text.replace("~", r"\textasciitilde ")
    text = text.replace("[", r"{[}")
    text = text.replace("]", r"{]}")
    text = text.replace("(", r"{(}")
    text = text.replace(")", r"{)}")
    text = text.replace(".", r"{.}")
    text = text.replace(",", r"{,}")
    text = text.replace(":", r"{:}")
    text = text.replace(";", r"{;}")
    text = text.replace("=", r"{=}")
    text = text.replace("@", r"{@}")
    text = text.replace("?", r"{?}")
    text = text.replace("!", r"{!}")
    text = text.replace("->", r"{->}")
    return override_characters(text)


def override_characters(text: str, in_code_block: bool = False) -> str:
    """Replace source glyphs that require custom LaTeX markup."""
    override_set = {"é⃝": "\\textcircled{é}"}

    if in_code_block:
        override_set = {k: f"|{v}|" for k, v in override_set.items()}

    for char, replacement in override_set.items():
        text = text.replace(char, replacement)
    return text
