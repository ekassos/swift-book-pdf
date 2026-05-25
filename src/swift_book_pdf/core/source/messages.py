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

"""User-facing messages for Swift Book source repository handling."""

INPUT_PATH_REVISION_CONFLICT = (
    "--source-ref and --source-sha can't be used with --input-path. "
    "Check out the desired revision in a separate local clone and pass that "
    "path with --input-path."
)
MISSING_GIT = "Git is not installed or not in PATH."
MISSING_REPOSITORY = (
    "The specified input path {input_path} does not contain the Swift book "
    "repository."
)
MISSING_TOC = (
    "Couldn't find the Table of Contents file "
    "(The-Swift-Programming-Language.md) in {root_dir}."
)
MISSING_ASSETS = "Couldn't find the Assets directory ({assets_dir})."
SOURCE_REF_IGNORED = (
    "Both source SHA and source ref are provided. Ignoring source ref %s and "
    "checking out source SHA %s."
)
