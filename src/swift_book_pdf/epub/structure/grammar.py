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

"""Collect grammar term targets for EPUB cross-links."""

from swift_book_pdf.core.blocks.models import NoteBlock
from swift_book_pdf.core.document import PartEntry, SourceDocument
from swift_book_pdf.epub.grammar_rules import (
    extract_grammar_terms,
    grammar_anchor_fragment,
    is_grammar_note_label,
)


def build_grammar_target_map(
    parts: list[PartEntry],
    source_documents: dict[str, SourceDocument],
) -> dict[str, str]:
    """Build a map from grammar term text to target href.

    Args:
        parts: Top-level book parts whose children define spine order.
        source_documents: Parsed source documents keyed by document key.

    Returns:
        First definition href for each grammar term. Later duplicates are left
        untouched so grammar links point to the earliest defining production.
    """
    grammar_targets: dict[str, str] = {}
    for part in parts:
        for document in part.children:
            source_document = source_documents[document.key]
            for block in source_document.blocks:
                if not isinstance(block, NoteBlock):
                    continue
                if not is_grammar_note_label(block.label):
                    continue
                for term in extract_grammar_terms(block):
                    grammar_targets.setdefault(
                        term,
                        f"{document.href}#grammar_{grammar_anchor_fragment(term)}",
                    )
    return grammar_targets
