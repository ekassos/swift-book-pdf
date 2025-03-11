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

import re


def extract_doc_tags(file_content: list[str]) -> list[str]:
    """
    Use regex to find all document references in the format <doc:DocumentName>

    :param file_content: The content of the file to search for document references

    :return: A list of document references found in the file
    """
    return re.findall(r"<doc:(.*?)>", "".join(file_content))
