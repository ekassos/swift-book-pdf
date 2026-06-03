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

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pytest

from swift_book_pdf.lexer import highlight_swift
from swift_book_pdf.lexer.swift import SwiftLexer
from swift_book_pdf.pdf.latex.preamble.styles import (
    CustomSwiftBookDarkStyle,
    CustomSwiftBookStyle,
)

if TYPE_CHECKING:
    from pygments.style import Style

pytestmark = pytest.mark.external_corpus

SWIFT_BOOK_REPO_URL = "https://github.com/swiftlang/swift-book.git"
SWIFT_DOCC_RENDER_REPO_URL = (
    "https://github.com/swiftlang/swift-docc-render.git"
)
RUN_ENV_VAR = "SWIFT_BOOK_CORPUS_TEST"
SWIFT_BOOK_SOURCE_ENV_VAR = "SWIFT_BOOK_SOURCE"
SWIFT_DOCC_RENDER_SOURCE_ENV_VAR = "SWIFT_DOCC_RENDER_SOURCE"

RGB_RE = re.compile(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)")
BASE_COLOR_RE = re.compile(
    r"(?P<name>[\w-]+):\s*\(\s*"
    r"light:\s*(?P<light>rgb\([^)]+\)),\s*"
    r"dark:\s*(?P<dark>rgb\([^)]+\))",
    re.MULTILINE,
)
SYNTAX_VAR_RE = re.compile(
    r"--color-syntax-(?P<name>[\w-]+):\s*(?P<value>[^;]+);"
)
BASE_VAR_RE = re.compile(
    r"--color-(?P<name>[\w-]+):\s*"
    r"#\{(?:light|dark|base)-color\((?P<color>[\w-]+)\)\};"
)
TOKEN_GROUP_RE = re.compile(
    r"(?P<name>[\w-]+):\s*\((?P<body>.*?)\)", re.DOTALL
)


@dataclass(frozen=True)
class CodeBlock:
    """One fenced Swift code block from the Swift Book source."""

    path: str
    line: int
    code: str


@dataclass(frozen=True)
class HighlightResult:
    """Rendered HTML from a highlight.js run."""

    version: str
    html: list[str]


@dataclass(frozen=True)
class CorpusEnvironment:
    """External repositories and latest highlight.js installation."""

    swift_book: Path
    swift_docc_render: Path
    node_package: Path
    node: str


@pytest.fixture(scope="module")
def corpus_environment(
    tmp_path_factory: pytest.TempPathFactory,
) -> CorpusEnvironment:
    """Prepare the opt-in external corpus test workspace."""
    if os.environ.get(RUN_ENV_VAR) != "1":
        pytest.skip(f"Set {RUN_ENV_VAR}=1 to run the external corpus test.")

    git = _required_executable("git")
    node = _required_executable("node")
    npm = _required_executable("npm")

    tmp_path = tmp_path_factory.mktemp("swift-book-corpus")
    swift_book = _resolve_or_clone_repo(
        env_var=SWIFT_BOOK_SOURCE_ENV_VAR,
        repo_url=SWIFT_BOOK_REPO_URL,
        destination=tmp_path / "swift-book",
        git=git,
    )
    swift_docc_render = _resolve_or_clone_repo(
        env_var=SWIFT_DOCC_RENDER_SOURCE_ENV_VAR,
        repo_url=SWIFT_DOCC_RENDER_REPO_URL,
        destination=tmp_path / "swift-docc-render",
        git=git,
    )
    node_package = _install_latest_highlight_js(tmp_path / "node", npm)
    return CorpusEnvironment(
        swift_book=swift_book,
        swift_docc_render=swift_docc_render,
        node_package=node_package,
        node=node,
    )


def test_swift_book_corpus_matches_latest_highlightjs_html(
    corpus_environment: CorpusEnvironment,
) -> None:
    """Verify the ported lexer emits the same HTML as latest highlight.js."""
    blocks = _extract_swift_code_blocks(corpus_environment.swift_book)
    highlightjs = _highlight_with_latest_highlightjs(
        corpus_environment,
        [block.code for block in blocks],
        class_prefix=None,
    )

    mismatches: list[dict[str, object]] = []
    for index, (block, expected) in enumerate(
        zip(blocks, highlightjs.html, strict=True)
    ):
        actual = highlight_swift(block.code)
        if actual != expected:
            mismatches.append(
                _html_mismatch(index, block, expected=expected, actual=actual)
            )

    assert mismatches == [], (
        f"Latest highlight.js {highlightjs.version} differed from the "
        f"ported lexer for {len(mismatches)} of {len(blocks)} Swift Book "
        f"blocks:\n{json.dumps(mismatches[:5], indent=2)}"
    )


def test_swift_book_corpus_matches_swift_docc_render_colors(
    corpus_environment: CorpusEnvironment,
) -> None:
    """Verify the Pygments adapter keeps current DocC syntax colors."""
    blocks = _extract_swift_code_blocks(corpus_environment.swift_book)
    docc_theme = _load_docc_syntax_theme(corpus_environment.swift_docc_render)
    highlightjs = _highlight_with_latest_highlightjs(
        corpus_environment,
        [block.code for block in blocks],
        class_prefix="syntax-",
    )

    for appearance, style in (
        ("light", CustomSwiftBookStyle),
        ("dark", CustomSwiftBookDarkStyle),
    ):
        expected_colors = [
            _colors_from_highlight_html(
                html,
                fallback=docc_theme[appearance]["plain-text"],
                syntax_colors=docc_theme[appearance],
                token_colors=docc_theme["token_colors"],
            )
            for html in highlightjs.html
        ]
        actual_colors = [
            _colors_from_pygments(block.code, style) for block in blocks
        ]
        mismatches = _color_mismatches(
            blocks,
            expected_colors=expected_colors,
            actual_colors=actual_colors,
        )

        assert mismatches == [], (
            f"Latest highlight.js {highlightjs.version} plus current "
            f"swift-docc-render syntax colors differed from the {appearance} "
            f"Pygments adapter for {len(mismatches)} of {len(blocks)} Swift "
            f"Book blocks:\n{json.dumps(mismatches[:5], indent=2)}"
        )


def _required_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        pytest.skip(f"{name!r} is required for the external corpus test.")
        raise AssertionError("unreachable")
    return executable


def _resolve_or_clone_repo(
    *,
    env_var: str,
    repo_url: str,
    destination: Path,
    git: str,
) -> Path:
    env_path = os.environ.get(env_var)
    if env_path:
        path = Path(env_path)
        if not path.exists():
            pytest.fail(f"{env_var} points to a missing path: {path}")
        return path

    subprocess.run(  # noqa: S603
        [git, "clone", "--depth", "1", repo_url, str(destination)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return destination


def _install_latest_highlight_js(destination: Path, npm: str) -> Path:
    destination.mkdir()
    subprocess.run(  # noqa: S603
        [npm, "init", "-y"],
        cwd=destination,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(  # noqa: S603
        [npm, "install", "highlight.js@latest", "--no-audit", "--no-fund"],
        cwd=destination,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return destination


def _extract_swift_code_blocks(swift_book: Path) -> list[CodeBlock]:
    root = swift_book / "TSPL.docc"
    blocks: list[CodeBlock] = []
    for path in sorted(root.rglob("*.md")):
        relative_path = path.relative_to(swift_book).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        in_fence = False
        fence_language = ""
        start_line = 0
        code_lines: list[str] = []
        for line_number, line in enumerate(lines, start=1):
            stripped = line.rstrip("\r\n")
            if stripped.startswith("```"):
                if not in_fence:
                    in_fence = True
                    fence_language = (
                        stripped[3:].strip().split()[0]
                        if stripped[3:].strip()
                        else ""
                    )
                    start_line = line_number + 1
                    code_lines = []
                else:
                    if fence_language == "swift":
                        blocks.append(
                            CodeBlock(
                                path=relative_path,
                                line=start_line,
                                code="".join(code_lines),
                            )
                        )
                    in_fence = False
                    fence_language = ""
                    code_lines = []
            elif in_fence:
                code_lines.append(line)

    if not blocks:
        pytest.fail(f"No Swift code blocks found under {root}")
    return blocks


def _highlight_with_latest_highlightjs(
    corpus_environment: CorpusEnvironment,
    code_blocks: list[str],
    class_prefix: str | None,
) -> HighlightResult:
    script = f"""
const hljs = require("highlight.js");
const classPrefix = {json.dumps(class_prefix)};
if (classPrefix !== null) {{
  hljs.configure({{ classPrefix }});
}}
let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", chunk => input += chunk);
process.stdin.on("end", () => {{
  const blocks = JSON.parse(input);
  const html = blocks.map(code =>
    hljs.highlight(code, {{ language: "swift", ignoreIllegals: true }}).value
  );
  process.stdout.write(JSON.stringify({{
    version: require("highlight.js/package.json").version,
    html
  }}));
}});
"""
    completed = subprocess.run(  # noqa: S603
        [corpus_environment.node, "-e", script],
        cwd=corpus_environment.node_package,
        input=json.dumps(code_blocks),
        text=True,
        check=True,
        stdout=subprocess.PIPE,
    )
    payload = json.loads(completed.stdout)
    return HighlightResult(
        version=payload["version"],
        html=list(payload["html"]),
    )


def _load_docc_syntax_theme(
    swift_docc_render: Path,
) -> dict[str, dict[str, str]]:
    token_colors = _parse_docc_syntax_token_colors(
        swift_docc_render / "src/styles/core/_syntax.scss"
    )
    # Swift-DocC-Render overrides Swift attribute `meta` tokens from the
    # default character color to the keyword color in base/_syntax.scss.
    token_colors["meta"] = "keywords"

    return {
        "token_colors": token_colors,
        "light": _parse_docc_color_values(swift_docc_render, "light"),
        "dark": _parse_docc_color_values(swift_docc_render, "dark"),
    }


def _parse_docc_syntax_token_colors(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    start = text.index("$syntax-tokens-for-color")
    end = text.index("$token-classname-prefix", start)
    syntax_map = text[start:end]
    token_colors: dict[str, str] = {}
    for match in TOKEN_GROUP_RE.finditer(syntax_map):
        color_name = match.group("name")
        tokens = re.findall(r"[\w-]+", match.group("body"))
        for token in tokens:
            token_colors[token] = color_name
    if not token_colors:
        pytest.fail(f"No DocC syntax token colors parsed from {path}")
    return token_colors


def _parse_docc_color_values(
    swift_docc_render: Path,
    appearance: Literal["light", "dark"],
) -> dict[str, str]:
    base_colors = _parse_base_colors(
        swift_docc_render / "src/styles/core/_colors.scss"
    )
    light_color_file = swift_docc_render / "src/styles/core/colors/_light.scss"
    color_file = (
        swift_docc_render / f"src/styles/core/colors/_{appearance}.scss"
    )
    required = {
        "syntax-addition",
        "syntax-comments",
        "syntax-deletion",
        "syntax-keywords",
        "syntax-strings",
        "syntax-characters",
        "syntax-other-type-names",
        "syntax-plain-text",
    }
    variables = _parse_css_variables(
        color_file,
        base_colors,
        appearance,
        required=required,
        fallback_path=light_color_file if appearance == "dark" else None,
    )
    syntax_colors = {
        name: color
        for name, color in variables.items()
        if name.startswith("syntax-")
    }
    missing = sorted(required - syntax_colors.keys())
    if missing:
        pytest.fail(f"Missing DocC syntax color variables: {missing}")
    return {
        key.removeprefix("syntax-"): value
        for key, value in syntax_colors.items()
    }


def _parse_base_colors(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    colors: dict[str, dict[str, str]] = {}
    for match in BASE_COLOR_RE.finditer(text):
        colors[match.group("name")] = {
            "light": _rgb_to_hex(match.group("light")),
            "dark": _rgb_to_hex(match.group("dark")),
        }
    if not colors:
        pytest.fail(f"No base colors parsed from {path}")
    return colors


def _parse_css_variables(
    path: Path,
    base_colors: dict[str, dict[str, str]],
    appearance: Literal["light", "dark"],
    required: set[str],
    fallback_path: Path | None,
) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    variables: dict[str, str] = {}
    raw_values: dict[str, str] = (
        _parse_raw_syntax_variables(fallback_path) if fallback_path else {}
    )
    raw_values.update(_parse_raw_syntax_variables(path))
    for match in BASE_VAR_RE.finditer(text):
        if match.group("color") not in base_colors:
            continue
        variables[match.group("name")] = base_colors[match.group("color")][
            appearance
        ]
    for name, value in raw_values.items():
        if name not in required:
            continue
        variables[name] = _resolve_scss_color_value(
            value,
            variables=variables,
            base_colors=base_colors,
            appearance=appearance,
        )
    return variables


def _parse_raw_syntax_variables(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return {
        f"syntax-{match.group('name')}": match.group("value").strip()
        for match in SYNTAX_VAR_RE.finditer(text)
    }


def _resolve_scss_color_value(
    value: str,
    *,
    variables: dict[str, str],
    base_colors: dict[str, dict[str, str]],
    appearance: Literal["light", "dark"],
) -> str:
    if value.startswith("rgb("):
        return _rgb_to_hex(value)
    var_match = re.fullmatch(r"var\(--color-([\w-]+)\)", value)
    if var_match:
        return variables[var_match.group(1)]
    color_match = re.fullmatch(r"#\{(?:light|dark)-color\(([\w-]+)\)\}", value)
    if color_match:
        return base_colors[color_match.group(1)][appearance]
    pytest.fail(f"Unsupported DocC color value: {value}")
    raise AssertionError("unreachable")


def _rgb_to_hex(value: str) -> str:
    match = RGB_RE.fullmatch(value.strip())
    if not match:
        pytest.fail(f"Unsupported RGB color: {value}")
        raise AssertionError("unreachable")
    return "".join(f"{int(component):02x}" for component in match.groups())


def _colors_from_highlight_html(
    highlight_html: str,
    *,
    fallback: str,
    syntax_colors: dict[str, str],
    token_colors: dict[str, str],
) -> list[str]:
    parser = _DocCHighlightParser(
        fallback=fallback,
        syntax_colors=syntax_colors,
        token_colors=token_colors,
    )
    parser.feed(highlight_html)
    parser.close()
    return parser.colors


class _DocCHighlightParser(HTMLParser):
    """Extract per-character colors from highlight.js HTML."""

    def __init__(
        self,
        *,
        fallback: str,
        syntax_colors: dict[str, str],
        token_colors: dict[str, str],
    ) -> None:
        super().__init__(convert_charrefs=True)
        self._syntax_colors = syntax_colors
        self._token_colors = token_colors
        self._color_stack = [fallback]
        self.text = ""
        self.colors: list[str] = []

    def handle_starttag(
        self, _tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        classes = (dict(attrs).get("class") or "").split()
        color = self._color_for_classes(classes) or self._color_stack[-1]
        self._color_stack.append(color)

    def handle_endtag(self, _tag: str) -> None:
        if len(self._color_stack) > 1:
            self._color_stack.pop()

    def handle_data(self, data: str) -> None:
        self.text += data
        self.colors.extend([self._color_stack[-1]] * len(data))

    def _color_for_classes(self, classes: list[str]) -> str | None:
        for class_name in classes:
            if not class_name.startswith("syntax-"):
                continue
            token = class_name.removeprefix("syntax-")
            color_name = self._token_colors.get(token)
            if color_name is not None:
                return self._syntax_colors[color_name]
        return None


def _colors_from_pygments(
    code: str,
    style: type[Style],
) -> list[str]:
    lexer = SwiftLexer()
    colors: list[str] = []
    rendered_text = ""
    for _position, token, value in lexer.get_tokens_unprocessed(code):
        rendered_text += value
        colors.extend([_style_color(style, token)] * len(value))
    if rendered_text != code:
        pytest.fail("Pygments adapter did not preserve source text.")
    return colors


def _style_color(style: type[Style], token: object) -> str:
    color = style.style_for_token(token).get("color")
    if not color:
        pytest.fail(f"Missing Pygments color for token {token}.")
    return color.lower().lstrip("#").zfill(6)


def _color_mismatches(
    blocks: list[CodeBlock],
    *,
    expected_colors: list[list[str]],
    actual_colors: list[list[str]],
) -> list[dict[str, object]]:
    mismatches: list[dict[str, object]] = []
    for index, (block, expected, actual) in enumerate(
        zip(blocks, expected_colors, actual_colors, strict=True)
    ):
        if expected == actual:
            continue
        mismatch_indexes = [
            char_index
            for char_index, (expected_color, actual_color) in enumerate(
                zip(expected, actual, strict=True)
            )
            if expected_color != actual_color
        ]
        if mismatch_indexes:
            first = mismatch_indexes[0]
            mismatches.append(
                {
                    "id": index,
                    "path": block.path,
                    "line": block.line,
                    "mismatch_chars": len(mismatch_indexes),
                    "first_index": first,
                    "expected": expected[first],
                    "actual": actual[first],
                    "excerpt": _excerpt(block.code, first),
                }
            )
    return mismatches


def _html_mismatch(
    index: int,
    block: CodeBlock,
    *,
    expected: str,
    actual: str,
) -> dict[str, object]:
    first = next(
        (
            char_index
            for char_index, (expected_char, actual_char) in enumerate(
                zip(expected, actual, strict=False)
            )
            if expected_char != actual_char
        ),
        min(len(expected), len(actual)),
    )
    return {
        "id": index,
        "path": block.path,
        "line": block.line,
        "first_html_index": first,
        "expected": expected[max(0, first - 80) : first + 160],
        "actual": actual[max(0, first - 80) : first + 160],
    }


def _excerpt(value: str, index: int) -> str:
    return value[max(0, index - 50) : index + 80].replace("\n", "\\n")
