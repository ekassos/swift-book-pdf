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

from pathlib import Path

from swift_book_pdf.grammar_summary import (
    SUMMARY_FALLBACK_SOURCE_PATHS,
    _generate_summary_file,
    _parse_generate_grammar,
    _parse_publish_book,
)


def test_parse_generate_grammar_reads_current_upstream_layout(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "swift-book"
    script_path = repo_root / "bin" / "generate-grammar"
    script_path.parent.mkdir(parents=True)
    script_path.write_text(
        """#! /bin/bash
set -eux
{
\techo "# Summary of the Grammar"
\techo
\techo "Read the whole formal grammar."
\techo
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/LexicalStructure.md
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/Types.md
} > "$summary_chapter"
""",
        encoding="utf-8",
    )

    config = _parse_generate_grammar(script_path)

    assert config.title == "Summary of the Grammar"
    assert config.subtitle == "Read the whole formal grammar."
    assert config.source_paths == [
        str(repo_root / "TSPL.docc/ReferenceManual/LexicalStructure.md"),
        str(repo_root / "TSPL.docc/ReferenceManual/Types.md"),
    ]


def test_parse_publish_book_reads_legacy_embedded_summary_block(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "swift-book"
    script_path = repo_root / "bin" / "publish-book"
    script_path.parent.mkdir(parents=True)
    script_path.write_text(
        """#! /bin/bash
set -eux
summary_chapter="TSPL.docc/ReferenceManual/SummaryOfTheGrammar.md"
{
\techo "# Summary of the Grammar"
\techo
\techo "Read the whole formal grammar."
\techo
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/LexicalStructure.md
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/Types.md
} > "$summary_chapter"
echo "done"
""",
        encoding="utf-8",
    )

    config = _parse_publish_book(script_path)

    assert config.title == "Summary of the Grammar"
    assert config.subtitle == "Read the whole formal grammar."
    assert config.source_paths == [
        str(repo_root / "TSPL.docc/ReferenceManual/LexicalStructure.md"),
        str(repo_root / "TSPL.docc/ReferenceManual/Types.md"),
    ]


def test_generate_summary_file_uses_generate_grammar_source_list(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "swift-book"
    publish_book = repo_root / "bin" / "publish-book"
    generate_grammar = repo_root / "bin" / "generate-grammar"
    publish_book.parent.mkdir(parents=True)
    publish_book.write_text(
        """#! /bin/bash
summary_chapter="TSPL.docc/ReferenceManual/SummaryOfTheGrammar.md"
bin/generate-grammar
""",
        encoding="utf-8",
    )
    generate_grammar.write_text(
        """#! /bin/bash
{
\techo "# Summary of the Grammar"
\techo
\techo "Read the whole formal grammar."
\techo
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/LexicalStructure.md
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/Types.md
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/Expressions.md
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/Statements.md
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/Declarations.md
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/Attributes.md
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/Patterns.md
\tawk -f bin/extract_grammar.awk TSPL.docc/ReferenceManual/GenericParametersAndArguments.md
} > "$summary_chapter"
""",
        encoding="utf-8",
    )

    for source_path in SUMMARY_FALLBACK_SOURCE_PATHS:
        chapter_path = repo_root / source_path
        chapter_path.parent.mkdir(parents=True, exist_ok=True)
        title = chapter_path.stem.replace("And", " And ")
        chapter_path.write_text(
            f"# {title}\n\n"
            f"> Grammar of {title}\n"
            f"> {title.lower()} -> token\n\n",
            encoding="utf-8",
        )

    generated_summary = _generate_summary_file(
        repo_root,
        tmp_path / "temp-output",
    )

    assert generated_summary is not None
    assert generated_summary.title == "Summary of the Grammar"
    assert generated_summary.subtitle == "Read the whole formal grammar."

    summary_text = Path(generated_summary.path).read_text(encoding="utf-8")
    assert summary_text.startswith("# Summary of the Grammar\n\n")
    assert "Read the whole formal grammar.\n\n" in summary_text
    assert "## LexicalStructure\n\n" in summary_text
    assert "> Grammar of LexicalStructure\n" in summary_text
