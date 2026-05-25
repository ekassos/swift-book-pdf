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

"""Shared Jinja rendering for EPUB package templates."""

from __future__ import annotations

from typing import TYPE_CHECKING

from jinja2 import Environment, PackageLoader, StrictUndefined

if TYPE_CHECKING:
    from collections.abc import Mapping

EPUB_TEMPLATE_ENV = Environment(
    loader=PackageLoader("swift_book_pdf.epub", "templates"),
    autoescape=True,
    undefined=StrictUndefined,
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_epub_template(
    template_name: str,
    context: Mapping[str, object],
) -> str:
    """Render a bundled EPUB template with XML/XHTML autoescaping.

    Args:
        template_name: Name of the template under `swift_book_pdf.epub`.
        context: Template variables to render.

    Returns:
        Rendered template text.
    """
    return EPUB_TEMPLATE_ENV.get_template(template_name).render(**context)
