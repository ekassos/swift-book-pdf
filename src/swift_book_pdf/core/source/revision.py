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

"""Git revision lookup for Swift Book source paths."""

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def get_swift_book_repository_revision(root_dir: str | Path) -> str | None:
    """Return the current git commit for the Swift Book checkout if known.

    Args:
        root_dir: Path to `TSPL.docc`. The git repository is expected to be the
            parent directory.

    Returns:
        The current commit SHA, or `None` when git is unavailable or the path is
        not inside a usable git checkout.
    """
    repo_dir = Path(root_dir).parent
    git_executable = shutil.which("git")
    if git_executable is None:
        return None

    result = subprocess.run(  # noqa: S603
        [git_executable, "rev-parse", "HEAD"],
        cwd=repo_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.debug(
            "Couldn't determine swift-book git revision from %s: %s",
            repo_dir,
            result.stderr.strip(),
        )
        return None

    revision = result.stdout.strip()
    return revision or None
