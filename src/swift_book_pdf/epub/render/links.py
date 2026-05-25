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

"""Resolve Swift Book document links for EPUB XHTML."""

from __future__ import annotations

import html
from typing import TYPE_CHECKING

from swift_book_pdf.epub.paths import relative_href

if TYPE_CHECKING:
    from swift_book_pdf.core.document import DocumentEntry


class LinkResolver:
    """Resolve `<doc:...>` targets against generated document entries."""

    def __init__(self, documents: list[DocumentEntry]) -> None:
        """Index generated documents by lowercase document key."""
        self.documents = {document.key: document for document in documents}

    def render_doc_link(self, current_href: str, target: str) -> str:
        """Render one resolved document link or escaped unresolved target."""
        chapter_key, _, fragment = target.partition("#")
        document = self.documents.get(chapter_key.lower())
        if document is None:
            return html.escape(target)

        if fragment:
            link_text = document.heading_map.get(
                fragment, fragment.replace("-", " ")
            )
            href = f"{document.href}#{fragment}"
        else:
            link_text = document.title
            href = document.href

        return (
            f'<a href="{html.escape(relative_href(current_href, href))}">'
            f"{html.escape(link_text)}</a>"
        )
