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

"""Shared loading for bundled LaTeX templates."""

from importlib import resources
from string import Template

LATEX_TEMPLATE_PACKAGE = "swift_book_pdf.pdf.latex.templates"


def read_latex_template(template_name: str) -> str:
    """Read a bundled LaTeX template as text.

    Args:
        template_name: Name of the template under `pdf.latex.templates`.

    Returns:
        Template file contents.
    """
    template_file = resources.files(LATEX_TEMPLATE_PACKAGE).joinpath(
        template_name
    )
    return template_file.read_text(encoding="utf-8")


def load_latex_template(template_name: str) -> Template:
    """Load a bundled LaTeX template for `string.Template` substitution.

    Args:
        template_name: Name of the template under `pdf.latex.templates`.

    Returns:
        A `Template` initialized with the template file contents.
    """
    return Template(read_latex_template(template_name))
