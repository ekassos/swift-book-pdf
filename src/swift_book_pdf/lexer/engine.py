# Copyright 2026 Evangelos Kassos
#
# Portions derived from highlight.js:
#   Copyright (c) 2006, Ivan Sagalaev.
#   Licensed under the BSD 3-Clause License.
#   See THIRD-PARTY-NOTICES.txt for details.
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

# This module preserves several upstream highlight.js identifiers and the
# camelCase mode-attribute names (beginKeywords, endsParent, beginScope,
# classNameAliases, ...) so the Swift mode tree can be ported 1:1. The mode
# objects are inherently dynamic mappings, so `Any` annotations and a
# little structural complexity are unavoidable in this faithful port.
# ruff: noqa: N802, ANN401, C901, PLR0912

"""Compile and run highlight.js-style language modes."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any, Literal, overload

from swift_book_pdf.lexer import regex as rx

Mode = dict[str, Any]

# Symbol used by the core loop to signal "no end match happened".
NO_MATCH = object()
MAX_KEYWORD_HITS = 7
# Last-ditch infinite-loop guard, mirroring highlight.js core.
_MAX_ITERATIONS = 100000

# highlight.js uses `/\B|\b/` as the implicit begin/end for modes that
# omit one. In JavaScript that pattern also matches at the boundaries of an
# empty (zero-length) remainder, which is essential to terminate a
# `match`-only mode at end-of-input. Python's `re` does NOT match `\B`
# against an empty string, so we append `$` to recover the JS semantics
# (`\b`/`\B` already cover every position of a non-empty string, so the
# only behavioural change is at end-of-string/line, which is exactly the
# divergence we are correcting).
_DEFAULT_BOUNDARY = r"\b|\B|$"

# Keywords that should have no default relevance value.
COMMON_KEYWORDS = [
    "of",
    "and",
    "for",
    "in",
    "not",
    "or",
    "if",
    "then",
    "parent",
    "list",
    "value",
]
DEFAULT_KEYWORD_SCOPE = "keyword"


# --------------------------------------------------------------------------
# Regex source helpers
# --------------------------------------------------------------------------


def _source(value: Any) -> str:
    """Return the regex source string for a value.

    Args:
        value: Pattern-like value to unwrap. Strings are returned unchanged;
            objects with `source` or `pattern` attributes expose those values.

    Returns:
        Regex source text.
    """
    if value is None:
        return None  # type: ignore[return-value]
    if isinstance(value, str):
        return value
    src = getattr(value, "source", None)
    if src is not None:
        return src
    pat = getattr(value, "pattern", None)
    if pat is not None:
        return pat
    return str(value)


def _count_match_groups(re_src: str) -> int:
    """Count the capturing groups in a regex source.

    Args:
        re_src: Regex source text.

    Returns:
        Number of capturing groups in the compiled expression.
    """
    return re.compile(re_src + "|").groups


# JS -> Python regex translation. The Swift grammar relies almost entirely
# on constructs shared by both engines. The notable differences handled
# here keep the patterns valid for Python's `re`.
def _js_regex_to_python(src: str) -> str:
    """Translate a JavaScript regex source to Python `re` syntax.

    Args:
        src: JavaScript regex source text.

    Returns:
        Python regex source text.

    Notes:
        The Swift grammar's patterns are currently compatible with Python
        `re`, so this is intentionally an identity transform.
    """
    return src


def _compile_re(value: Any) -> re.Pattern[str]:
    """Compile a regex-like value with multiline semantics.

    Args:
        value: Regex-like value accepted by `_source`.

    Returns:
        Compiled Python regex pattern.

    Notes:
        highlight.js compiles language regexes with the `m` flag. The
        JavaScript `global` flag has no Python equivalent because scan
        position is tracked explicitly by callers.
    """
    src = _js_regex_to_python(_source(value))
    return re.compile(src, re.MULTILINE)


def _rewrite_backreferences(regexps: list[Any], *, join_with: str) -> str:
    """Join regexes, wrapping each in a group and renumbering backrefs.

    Args:
        regexps: Regex-like values to join.
        join_with: Separator inserted between wrapped regex sources.

    Returns:
        Combined regex source with numeric backreferences adjusted for the
        inserted wrapper groups.
    """
    backref_re = re.compile(
        r"\[(?:[^\\\]]|\\.)*\]|\(\?\?|\(\?|\\([1-9][0-9]*)|\\."
    )
    num_captures = 0
    out_parts: list[str] = []
    for regexp in regexps:
        num_captures += 1
        offset = num_captures
        re_src = _source(regexp)
        out = ""
        while len(re_src) > 0:
            match = backref_re.search(re_src)
            if not match:
                out += re_src
                break
            out += re_src[: match.start()]
            matched = match.group(0)
            re_src = re_src[match.start() + len(matched) :]
            if matched[0] == "\\" and match.group(1):
                out += "\\" + str(int(match.group(1)) + offset)
            else:
                out += matched
                if matched == "(":
                    num_captures += 1
        out_parts.append(out)
    return join_with.join(f"({p})" for p in out_parts)


# --------------------------------------------------------------------------
# Keyword compilation (compile_keywords.js)
# --------------------------------------------------------------------------


def _common_keyword(keyword: str) -> bool:
    """Return whether a keyword should carry no default relevance.

    Args:
        keyword: Keyword text to check.

    Returns:
        `True` when `keyword` is in the common-keyword list.
    """
    return keyword.lower() in COMMON_KEYWORDS


def _score_for_keyword(keyword: str, provided: str | None) -> int:
    """Resolve the relevance score for a compiled keyword.

    Args:
        keyword: Keyword text without any explicit score suffix.
        provided: Optional explicit relevance score from a `|N` suffix.

    Returns:
        Integer relevance score.
    """
    if provided:
        return int(provided)
    return 0 if _common_keyword(keyword) else 1


def compile_keywords(
    raw: Any,
    case_insensitive: bool,
    scope_name: str = DEFAULT_KEYWORD_SCOPE,
) -> dict[str, tuple[str, int]]:
    """Compile raw keyword definitions into a lookup map.

    Args:
        raw: Space-separated keyword string, keyword list, or mapping from
            scope names to either form.
        case_insensitive: Whether compiled keyword keys should be lowercase.
        scope_name: Scope assigned to keywords when `raw` is not a mapping.

    Returns:
        Mapping from keyword text to `(scope, relevance)` tuples.
    """
    compiled: dict[str, tuple[str, int]] = {}

    def compile_list(scope: str, keyword_list: list[str]) -> None:
        """Add a list of keywords to the enclosing compiled map.

        Args:
            scope: Scope name assigned to every keyword in `keyword_list`.
            keyword_list: Keyword strings, each optionally suffixed with a
                `|N` relevance override.
        """
        words = keyword_list
        if case_insensitive:
            words = [w.lower() for w in words]
        for keyword in words:
            pair = keyword.split("|")
            score = _score_for_keyword(
                pair[0], pair[1] if len(pair) > 1 else None
            )
            compiled[pair[0]] = (scope, score)

    if isinstance(raw, str):
        compile_list(scope_name, raw.split(" "))
    elif isinstance(raw, list):
        # Lists may contain Regex markers (e.g. Swift.availabilityKeywords
        # are plain strings, but other buckets pass through here too). Only
        # plain strings are valid keyword entries.
        compile_list(scope_name, [_source(x) for x in raw])
    else:
        for key in raw:
            compiled.update(compile_keywords(raw[key], case_insensitive, key))
    return compiled


# --------------------------------------------------------------------------
# Common modes (modes.js)
# --------------------------------------------------------------------------

BACKSLASH_ESCAPE: Mode = {"begin": "\\\\[\\s\\S]", "relevance": 0}


def COMMENT(begin: Any, end: Any, mode_options: Mode | None = None) -> Mode:
    """Create a comment mode.

    Args:
        begin: Pattern that starts the comment.
        end: Pattern that ends the comment.
        mode_options: Optional mode fields to merge into the comment mode.

    Returns:
        Mode dictionary for highlight.js-style comment matching.

    Notes:
        The doctag and English-word sub-modes are preserved because they
        affect both relevance and emitted markup inside comments.
    """
    mode: Mode = {
        "scope": "comment",
        "begin": begin,
        "end": end,
        "contains": [],
    }
    if mode_options:
        mode.update(mode_options)
        if "contains" not in mode_options:
            mode["contains"] = []
        else:
            mode["contains"] = list(mode_options["contains"])

    mode["contains"].append(
        {
            "scope": "doctag",
            "begin": "[ ]*(?=(TODO|FIXME|NOTE|BUG|OPTIMIZE|HACK|XXX):)",
            "end": "(TODO|FIXME|NOTE|BUG|OPTIMIZE|HACK|XXX):",
            "excludeBegin": True,
            "relevance": 0,
        }
    )
    english_word = rx.either(
        "I",
        "a",
        "is",
        "so",
        "us",
        "to",
        "at",
        "if",
        "in",
        "it",
        "on",
        r"[A-Za-z]+['](d|ve|re|ll|t|s|n)",
        r"[A-Za-z]+[-][a-z]+",
        r"[A-Za-z][a-z]{2,}",
    )
    mode["contains"].append(
        {
            "begin": rx.concat(
                r"[ ]+",
                "(",
                english_word,
                r"[.]?[:]?([.][ ]|[ ])",
                "){3}",
            )
        }
    )
    return mode


C_LINE_COMMENT_MODE: Mode = COMMENT("//", "$")


# --------------------------------------------------------------------------
# Compiler extensions (compiler_extensions.js + ext/multi_class.js)
# --------------------------------------------------------------------------


def _skip_if_has_preceding_dot(match: MatchObj, response: Response) -> None:
    """Ignore a keyword match when the previous character is a dot.

    Args:
        match: Candidate match object.
        response: Callback response used to mark ignored matches.
    """
    before = match.input[match.index - 1] if match.index > 0 else None
    if before == ".":
        response.ignore_match()


def _ext_scope_class_name(mode: Mode, _parent: Mode | None) -> None:
    """Normalize `className` mode fields to `scope`.

    Args:
        mode: Mode dictionary to mutate.
        _parent: Parent mode, unused by this extension.
    """
    if "className" in mode:
        mode["scope"] = mode["className"]
        del mode["className"]


def _ext_compile_match(mode: Mode, _parent: Mode | None) -> None:
    """Normalize `match` mode fields to `begin`.

    Args:
        mode: Mode dictionary to mutate.
        _parent: Parent mode, unused by this extension.

    Raises:
        ValueError: If a mode mixes `match` with `begin` or `end`.
    """
    if "match" not in mode:
        return
    if mode.get("begin") or mode.get("end"):
        raise ValueError("begin & end are not supported with match")
    mode["begin"] = mode["match"]
    del mode["match"]


def _ext_begin_keywords(mode: Mode, parent: Mode | None) -> None:
    """Expand `beginKeywords` mode sugar into concrete regex fields.

    Args:
        mode: Mode dictionary to mutate.
        parent: Parent mode, required for nested keyword starts.
    """
    if not parent:
        return
    if not mode.get("beginKeywords"):
        return
    mode["begin"] = (
        "\\b("
        + "|".join(mode["beginKeywords"].split(" "))
        + ")(?!\\.)(?=\\b|\\s)"
    )
    mode["__beforeBegin"] = _skip_if_has_preceding_dot
    mode["keywords"] = mode.get("keywords") or mode["beginKeywords"]
    del mode["beginKeywords"]
    if "relevance" not in mode:
        mode["relevance"] = 0


def _ext_compile_illegal(mode: Mode, _parent: Mode | None) -> None:
    """Compile list-valued `illegal` fields into one alternation.

    Args:
        mode: Mode dictionary to mutate.
        _parent: Parent mode, unused by this extension.
    """
    illegal = mode.get("illegal")
    if not isinstance(illegal, list):
        return
    mode["illegal"] = rx.either(*[_source(x) for x in illegal])


def _ext_compile_relevance(mode: Mode, _parent: Mode | None) -> None:
    """Apply highlight.js' default relevance when a mode omits it.

    Args:
        mode: Mode dictionary to mutate.
        _parent: Parent mode, unused by this extension.
    """
    if "relevance" not in mode:
        mode["relevance"] = 1


# --- multi_class.js -------------------------------------------------------


def _remap_scope_names(mode: Mode, regexes: list[Any], key: str) -> None:
    """Map per-regex scope positions onto combined capture positions.

    Args:
        mode: Mode dictionary to mutate.
        regexes: Regex-like parts being combined.
        key: Scope field to remap, such as `beginScope` or `endScope`.
    """
    offset = 0
    scope_names = mode[key]
    emit: dict[int, bool] = {}
    positions: dict[int, str] = {}
    for i in range(1, len(regexes) + 1):
        positions[i + offset] = scope_names.get(i)
        emit[i + offset] = True
        offset += _count_match_groups(_source(regexes[i - 1]))
    mode[key] = positions
    mode[key + "__emit"] = emit
    mode[key + "__multi"] = True


def _scope_sugar(mode: Mode) -> None:
    """Expand dict-valued `scope` sugar into `beginScope`.

    Args:
        mode: Mode dictionary to mutate.
    """
    scope = mode.get("scope")
    if isinstance(scope, dict):
        mode["beginScope"] = scope
        del mode["scope"]


def _ext_multi_class(mode: Mode, _parent: Mode | None) -> None:
    """Compile multi-class begin/end scope definitions.

    Args:
        mode: Mode dictionary to mutate.
        _parent: Parent mode, unused by this extension.
    """
    _scope_sugar(mode)

    if isinstance(mode.get("beginScope"), str):
        mode["beginScope__wrap"] = mode["beginScope"]
        mode["beginScope"] = None
    if isinstance(mode.get("endScope"), str):
        mode["endScope__wrap"] = mode["endScope"]
        mode["endScope"] = None

    begin = mode.get("begin")
    if isinstance(begin, list):
        _remap_scope_names(mode, begin, "beginScope")
        mode["begin"] = _rewrite_backreferences(begin, join_with="")
    end = mode.get("end")
    if isinstance(end, list):
        _remap_scope_names(mode, end, "endScope")
        mode["end"] = _rewrite_backreferences(end, join_with="")


# --------------------------------------------------------------------------
# Response object (lib/response.js)
# --------------------------------------------------------------------------


class Response:
    """Callback response state for mode hooks."""

    def __init__(self, mode: Mode) -> None:
        """Initialize response state for a mode callback.

        Args:
            mode: Mode dictionary that owns callback data.
        """
        self._mode = mode
        self.is_match_ignored = False
        self.data = mode.setdefault("data", {})

    def ignore_match(self) -> None:
        """Mark the current callback match as ignored."""
        self.is_match_ignored = True


class MatchObj:
    """A lightweight match wrapper exposing the fields the engine needs."""

    __slots__ = (
        "groups",
        "index",
        "input",
        "position",
        "rule",
        "type",
    )

    def __init__(
        self,
        groups: list[str | None],
        index: int,
        input_str: str,
    ) -> None:
        """Initialize a match wrapper.

        Args:
            groups: Match groups with the whole matched lexeme at index `0`.
            index: Start offset of the match in `input_str`.
            input_str: Full input being highlighted.
        """
        self.groups = groups
        self.index = index
        self.input = input_str
        self.rule: Mode | None = None
        self.type: str | None = None
        self.position: int = 0

    @overload
    def __getitem__(self, i: Literal[0]) -> str:
        """Return the whole matched lexeme."""

    @overload
    def __getitem__(self, i: int) -> str | None:
        """Return an optional capture group."""

    def __getitem__(self, i: int) -> str | None:
        """Return the match group at an index.

        Args:
            i: Group index.

        Returns:
            Matched group text, or `None` when the group did not match.
        """
        return self.groups[i]

    def __len__(self) -> int:
        """Return the number of stored match groups.

        Returns:
            Number of match groups, including group `0`.
        """
        return len(self.groups)


# --------------------------------------------------------------------------
# Combined-regex matchers, from mode_compiler.js
# --------------------------------------------------------------------------


class MultiRegex:
    """Combines many regexes into one, tracking which rule matched."""

    def __init__(self) -> None:
        """Initialize an empty combined-regex matcher."""
        self.match_indexes: dict[int, Mode] = {}
        self.regexes: list[tuple[Mode, Any]] = []
        self.match_at = 1
        self.position = 0
        self.matcher_re: re.Pattern[str] | None = None
        self.last_index = 0

    def add_rule(self, re_val: Any, opts: Mode) -> None:
        """Add one regex rule to the combined matcher.

        Args:
            re_val: Regex-like value to add.
            opts: Match metadata returned when the rule matches.
        """
        opts["position"] = self.position
        self.position += 1
        self.match_indexes[self.match_at] = opts
        self.regexes.append((opts, re_val))
        self.match_at += _count_match_groups(_source(re_val)) + 1

    def compile(self) -> None:
        """Compile added rules into one regex pattern."""
        if len(self.regexes) == 0:
            self.matcher_re = None
            return
        terminators = [el[1] for el in self.regexes]
        joined = _rewrite_backreferences(terminators, join_with="|")
        self.matcher_re = _compile_re(joined)
        self.last_index = 0

    def exec(self, s: str) -> MatchObj | None:
        """Search the input for the next rule match.

        Args:
            s: Input text to scan.

        Returns:
            Wrapped match object, or `None` when no rule matches.
        """
        if self.matcher_re is None:
            return None
        m = self.matcher_re.search(s, self.last_index)
        if not m:
            return None
        groups = list(m.groups())
        # group(0) is the whole match; prepend so indexing matches JS.
        full = [m.group(0), *groups]
        # Find first non-None group with index > 0.
        i = next(
            (idx for idx, el in enumerate(full) if idx > 0 and el is not None),
            None,
        )
        if i is None:
            return None
        match_data = self.match_indexes[i]
        # Trim off earlier non-relevant match groups.
        trimmed = full[i:]
        match = MatchObj(trimmed, m.start(), s)
        match.rule = match_data.get("rule")
        match.type = match_data.get("type")
        match.position = match_data.get("position", 0)
        return match


class ResumableMultiRegex:
    """Dynamically build multi-regex matchers per scan position."""

    def __init__(self) -> None:
        """Initialize an empty resumable matcher."""
        self.rules: list[tuple[Any, Mode]] = []
        self.multi_regexes: dict[int, MultiRegex] = {}
        self.count = 0
        self.last_index = 0
        self.regex_index = 0

    def get_matcher(self, index: int) -> MultiRegex:
        """Return a matcher that starts considering rules at an index.

        Args:
            index: Rule index to start from.

        Returns:
            Cached or newly built matcher.
        """
        if index in self.multi_regexes:
            return self.multi_regexes[index]
        matcher = MultiRegex()
        for re_val, opts in self.rules[index:]:
            matcher.add_rule(re_val, opts)
        matcher.compile()
        self.multi_regexes[index] = matcher
        return matcher

    def resuming_scan_at_same_position(self) -> bool:
        """Return whether scanning resumed after an ignored same-offset rule.

        Returns:
            `True` when rule scanning should continue from a later rule.
        """
        return self.regex_index != 0

    def consider_all(self) -> None:
        """Reset scanning so every rule is considered."""
        self.regex_index = 0

    def add_rule(self, re_val: Any, opts: Mode) -> None:
        """Add a resumable regex rule.

        Args:
            re_val: Regex-like value to add.
            opts: Match metadata returned when the rule matches.
        """
        self.rules.append((re_val, opts))
        if opts.get("type") == "begin":
            self.count += 1

    def exec(self, s: str) -> MatchObj | None:
        """Search the input using the current resumable rule position.

        Args:
            s: Input text to scan.

        Returns:
            Wrapped match object, or `None` when no rule matches.
        """
        m = self.get_matcher(self.regex_index)
        m.last_index = self.last_index
        result = m.exec(s)

        if self.resuming_scan_at_same_position():
            if result and result.index == self.last_index:
                pass
            else:
                m2 = self.get_matcher(0)
                m2.last_index = self.last_index + 1
                result = m2.exec(s)

        if result:
            self.regex_index += result.position + 1
            if self.regex_index == self.count:
                self.consider_all()

        return result


# --------------------------------------------------------------------------
# Mode compiler (mode_compiler.js)
# --------------------------------------------------------------------------


CompilerExt = Callable[[Mode, "Mode | None"], None]


def _dependency_on_parent(mode: Mode | None) -> bool:
    """Return whether a mode depends on its parent terminator.

    Args:
        mode: Mode dictionary to inspect.

    Returns:
        `True` when `mode` or one of its `starts` modes ends with its parent.
    """
    if not mode:
        return False
    return bool(mode.get("endsWithParent")) or _dependency_on_parent(
        mode.get("starts")
    )


def _inherit(original: Mode, *objects: Mode) -> Mode:
    """Create a shallow mode copy with override fields.

    Args:
        original: Base mode dictionary.
        *objects: Additional dictionaries applied in order.

    Returns:
        Merged mode dictionary.
    """
    result: Mode = {}
    result.update(original)
    for obj in objects:
        for key, val in obj.items():
            result[key] = val
    return result


def _expand_or_clone_mode(mode: Mode) -> Mode | list[Mode]:
    """Expand variants or clone parent-dependent mode definitions.

    Args:
        mode: Mode dictionary to expand.

    Returns:
        Original mode, cloned mode, or expanded variant modes.
    """
    if mode.get("variants") and not mode.get("cachedVariants"):
        mode["cachedVariants"] = [
            _inherit(mode, {"variants": None}, variant)
            for variant in mode["variants"]
        ]
    if mode.get("cachedVariants"):
        return mode["cachedVariants"]
    if _dependency_on_parent(mode):
        return _inherit(
            mode,
            {
                "starts": _inherit(mode["starts"])
                if mode.get("starts")
                else None
            },
        )
    return mode


class Compiler:
    """Compile a language definition for the runtime highlighter."""

    def __init__(self, language: Mode) -> None:
        """Initialize a compiler for one language definition.

        Args:
            language: Root language mode dictionary.
        """
        self.language = language
        self.case_insensitive = bool(language.get("case_insensitive"))

    def build_mode_regex(self, mode: Mode) -> ResumableMultiRegex:
        """Build the matcher for a compiled mode.

        Args:
            mode: Compiled mode dictionary.

        Returns:
            Resumable matcher containing begin, end, and illegal rules.
        """
        mm = ResumableMultiRegex()
        for term in mode["contains"]:
            mm.add_rule(term["begin"], {"rule": term, "type": "begin"})
        if mode.get("terminatorEnd"):
            mm.add_rule(mode["terminatorEnd"], {"type": "end"})
        if mode.get("illegal"):
            mm.add_rule(mode["illegal"], {"type": "illegal"})
        return mm

    def compile_mode(self, mode: Mode, parent: Mode | None = None) -> Mode:
        """Compile one mode and its nested modes.

        Args:
            mode: Mode dictionary to compile.
            parent: Optional parent mode.

        Returns:
            Compiled mode dictionary.

        Raises:
            ValueError: If mode fields contain unsupported combinations.
        """
        if mode.get("isCompiled"):
            return mode

        exts: list[CompilerExt] = [
            _ext_scope_class_name,
            _ext_compile_match,
            _ext_multi_class,
        ]
        for ext in exts:
            ext(mode, parent)

        # __beforeBegin is private API; default to None unless an extension
        # (beginKeywords) set it. Mirror the JS ordering: it is reset, then
        # beginKeywords may set it.
        if "__beforeBegin" not in mode:
            mode["__beforeBegin"] = None

        late_exts: list[CompilerExt] = [
            _ext_begin_keywords,
            _ext_compile_illegal,
            _ext_compile_relevance,
        ]
        for ext in late_exts:
            ext(mode, parent)

        mode["isCompiled"] = True

        keyword_pattern = None
        kw = mode.get("keywords")
        if isinstance(kw, dict) and kw.get("$pattern"):
            kw = dict(kw)
            keyword_pattern = kw["$pattern"]
            del kw["$pattern"]
            mode["keywords"] = kw
        keyword_pattern = keyword_pattern or r"\w+"

        if mode.get("keywords"):
            mode["keywords"] = compile_keywords(
                mode["keywords"], self.case_insensitive
            )

        mode["keywordPatternRe"] = _compile_re(keyword_pattern)

        if parent:
            if not mode.get("begin"):
                mode["begin"] = _DEFAULT_BOUNDARY
            mode["beginRe"] = _compile_re(mode["begin"])
            if not mode.get("end") and not mode.get("endsWithParent"):
                mode["end"] = _DEFAULT_BOUNDARY
            if mode.get("end"):
                mode["endRe"] = _compile_re(mode["end"])
            mode["terminatorEnd"] = _source(mode.get("end")) or ""
            if mode.get("endsWithParent") and parent.get("terminatorEnd"):
                mode["terminatorEnd"] += (
                    "|" if mode.get("end") else ""
                ) + parent["terminatorEnd"]

        if mode.get("illegal"):
            mode["illegalRe"] = _compile_re(mode["illegal"])
        if "contains" not in mode:
            mode["contains"] = []

        expanded: list[Mode] = []
        for c in mode["contains"]:
            target = mode if c == "self" else c
            result = _expand_or_clone_mode(target)
            if isinstance(result, list):
                expanded.extend(result)
            else:
                expanded.append(result)
        mode["contains"] = expanded
        for c in mode["contains"]:
            self.compile_mode(c, mode)

        if mode.get("starts"):
            self.compile_mode(mode["starts"], parent)

        mode["matcher"] = self.build_mode_regex(mode)
        return mode

    def compile(self) -> Mode:
        """Compile the root language mode.

        Returns:
            Compiled root language mode.

        Raises:
            ValueError: If the top-level mode contains `self`.
        """
        if "compilerExtensions" not in self.language:
            self.language["compilerExtensions"] = []
        if "self" in (self.language.get("contains") or []):
            raise ValueError(
                "contains `self` is not supported at the top-level."
            )
        self.language["classNameAliases"] = dict(
            self.language.get("classNameAliases") or {}
        )
        return self.compile_mode(self.language)


def compile_language(language: Mode) -> Mode:
    """Compile a language definition for highlighting.

    Args:
        language: Root language mode dictionary.

    Returns:
        Compiled root language mode.
    """
    return Compiler(language).compile()


# --------------------------------------------------------------------------
# Token-tree emitter, from token_tree.js
# --------------------------------------------------------------------------


class Node:
    """A token-tree node with an optional highlighting scope."""

    __slots__ = ("children", "scope")

    def __init__(self, scope: str | None = None) -> None:
        """Initialize a token-tree node.

        Args:
            scope: Optional highlight.js scope represented by this node.
        """
        self.scope = scope
        self.children: list[Node | str] = []


class TokenTreeEmitter:
    """Build a nested token tree while the highlighter scans input."""

    def __init__(self) -> None:
        """Initialize an empty token tree."""
        self.root_node = Node()
        self.stack: list[Node] = [self.root_node]

    @property
    def top(self) -> Node:
        """Return the currently open token-tree node.

        Returns:
            Top node on the open-node stack.
        """
        return self.stack[-1]

    @property
    def root(self) -> Node:
        """Return the root token-tree node.

        Returns:
            Root node for the emitted token tree.
        """
        return self.root_node

    def add(self, node: Node | str) -> None:
        """Append a child to the current token-tree node.

        Args:
            node: Child node or text leaf to append.
        """
        self.top.children.append(node)

    def open_node(self, scope: str) -> None:
        """Open a scoped child node.

        Args:
            scope: Highlight.js scope for the child node.
        """
        node = Node(scope)
        self.add(node)
        self.stack.append(node)

    def close_node(self) -> Node | None:
        """Close the current scoped node.

        Returns:
            Closed node, or `None` when the stack is already at the root.
        """
        if len(self.stack) > 1:
            return self.stack.pop()
        return None

    def close_all_nodes(self) -> None:
        """Close every open scoped node."""
        while self.close_node():
            pass

    def walk(self, builder: Any) -> Any:
        """Walk the token tree with a renderer object.

        Args:
            builder: Object with `add_text`, `open_node`, and `close_node`
                methods.

        Returns:
            The same builder after traversal.
        """
        return self._walk(builder, self.root_node)

    @classmethod
    def _walk(cls, builder: Any, node: Node | str) -> Any:
        """Recursively visit a token-tree node.

        Args:
            builder: Object with renderer callbacks.
            node: Node or text leaf to visit.

        Returns:
            The same builder after traversal.
        """
        if isinstance(node, str):
            builder.add_text(node)
        else:
            builder.open_node(node)
            for child in node.children:
                cls._walk(builder, child)
            builder.close_node(node)
        return builder

    def add_text(self, text: str) -> None:
        """Append text to the current token-tree node.

        Args:
            text: Text to append. Empty strings are ignored.
        """
        if text == "":
            return
        self.add(text)

    def start_scope(self, scope: str) -> None:
        """Open a token-tree scope.

        Args:
            scope: Highlight.js scope to open.
        """
        self.open_node(scope)

    def end_scope(self) -> None:
        """Close the current token-tree scope."""
        self.close_node()

    def finalize(self) -> None:
        """Close any remaining token-tree scopes."""
        self.close_all_nodes()


# --------------------------------------------------------------------------
# Core highlight loop (highlight.js)
# --------------------------------------------------------------------------


class Highlighter:
    """Runs the compiled mode tree over input, building a token tree."""

    def __init__(
        self,
        language: Mode,
        code: str,
        ignore_illegals: bool = True,
    ) -> None:
        """Initialize a highlighter run.

        Args:
            language: Compiled language mode dictionary.
            code: Source code to highlight.
            ignore_illegals: Whether illegal matches should be ignored.
        """
        self.language = language
        self.code = code
        self.ignore_illegals = ignore_illegals
        self.keyword_hits: dict[str, int] = {}
        self.emitter = TokenTreeEmitter()
        self.relevance = 0
        self.mode_buffer = ""
        self.index = 0
        self.iterations = 0
        self.resume_at_same_position = False
        self.top: Mode = language
        self.last_match: dict[str, Any] = {}

    # --- keyword / scope emission -----------------------------------------

    def _keyword_data(
        self, mode: Mode, match_text: str
    ) -> tuple[str, int] | None:
        """Return compiled keyword data for matched text.

        Args:
            mode: Current mode dictionary.
            match_text: Candidate keyword text.

        Returns:
            `(scope, relevance)` tuple, or `None` when the text is not a
            keyword.
        """
        return mode["keywords"].get(match_text)

    def _emit_keyword(self, keyword: str, scope: str) -> None:
        """Emit text inside a scoped token node.

        Args:
            keyword: Text to emit.
            scope: Highlight.js scope to apply.
        """
        if keyword == "":
            return
        self.emitter.start_scope(scope)
        self.emitter.add_text(keyword)
        self.emitter.end_scope()

    def _process_keywords(self) -> None:
        """Emit the mode buffer, applying keyword scopes where configured."""
        if not self.top.get("keywords"):
            self.emitter.add_text(self.mode_buffer)
            return
        last_index = 0
        pattern_re: re.Pattern[str] = self.top["keywordPatternRe"]
        buf = ""
        for match in pattern_re.finditer(self.mode_buffer):
            buf += self.mode_buffer[last_index : match.start()]
            word = (
                match.group(0).lower()
                if self.language.get("case_insensitive")
                else match.group(0)
            )
            data = self._keyword_data(self.top, word)
            if data:
                kind, keyword_relevance = data
                self.emitter.add_text(buf)
                buf = ""
                self.keyword_hits[word] = self.keyword_hits.get(word, 0) + 1
                if self.keyword_hits[word] <= MAX_KEYWORD_HITS:
                    self.relevance += keyword_relevance
                if kind.startswith("_"):
                    buf += match.group(0)
                else:
                    css = self.language["classNameAliases"].get(kind) or kind
                    self._emit_keyword(match.group(0), css)
            else:
                buf += match.group(0)
            last_index = match.end()
        buf += self.mode_buffer[last_index:]
        self.emitter.add_text(buf)

    def _process_buffer(self) -> None:
        """Flush buffered text through keyword processing."""
        # Swift uses no sub-languages, so only keyword processing applies.
        self._process_keywords()
        self.mode_buffer = ""

    def _emit_multi_class(
        self, scope: dict[int, str], emit: dict[int, bool], match: MatchObj
    ) -> None:
        """Emit scopes assigned to capture groups in a multi-class match.

        Args:
            scope: Capture-group index to scope-name mapping.
            emit: Capture-group index to emission flag mapping.
            match: Match object containing captured text.
        """
        i = 1
        max_i = len(match) - 1
        while i <= max_i:
            if not emit.get(i):
                i += 1
                continue
            klass = self.language["classNameAliases"].get(
                scope.get(i)
            ) or scope.get(i)
            text = match[i] or ""
            if klass:
                self._emit_keyword(text, klass)
            else:
                self.mode_buffer = text or ""
                self._process_keywords()
                self.mode_buffer = ""
            i += 1

    # --- mode entry / exit ------------------------------------------------

    def _start_new_mode(self, mode: Mode, match: MatchObj) -> Mode:
        """Enter a child mode and emit any begin scopes.

        Args:
            mode: Mode dictionary being entered.
            match: Begin match that triggered the mode.

        Returns:
            Runtime child mode with its parent link attached.
        """
        scope = mode.get("scope")
        if scope and isinstance(scope, str):
            self.emitter.open_node(
                self.language["classNameAliases"].get(scope) or scope
            )
        if mode.get("beginScope") is not None or mode.get("beginScope__wrap"):
            if mode.get("beginScope__wrap"):
                self._emit_keyword(
                    self.mode_buffer,
                    self.language["classNameAliases"].get(
                        mode["beginScope__wrap"]
                    )
                    or mode["beginScope__wrap"],
                )
                self.mode_buffer = ""
            elif mode.get("beginScope__multi"):
                self._emit_multi_class(
                    mode["beginScope"],
                    mode["beginScope__emit"],
                    match,
                )
                self.mode_buffer = ""
        # Push child mode with a parent link.
        child = dict(mode)
        child["parent"] = self.top
        self.top = child
        return self.top

    def _end_of_mode(
        self, mode: Mode, match: MatchObj, rest: str
    ) -> Mode | None:
        """Find the mode ended by the current end match.

        Args:
            mode: Mode dictionary to test.
            match: End match being processed.
            rest: Input slice beginning at the match.

        Returns:
            Ended mode, or `None` when the match does not close a mode.
        """
        end_re: re.Pattern[str] | None = mode.get("endRe")
        matched = False
        if end_re is not None:
            m = end_re.match(rest)
            matched = m is not None
        if matched:
            on_end = mode.get("on:end")
            if on_end:
                resp = Response(mode)
                on_end(match, resp)
                if resp.is_match_ignored:
                    matched = False
            if matched:
                while mode.get("endsParent") and mode.get("parent"):
                    mode = mode["parent"]
                return mode
        if mode.get("endsWithParent"):
            return self._end_of_mode(mode["parent"], match, rest)
        return None

    # --- match handlers ---------------------------------------------------

    def _do_ignore(self, lexeme: str) -> int:
        """Handle a callback-ignored match.

        Args:
            lexeme: Ignored lexeme text.

        Returns:
            Number of input characters consumed.
        """
        if self.top["matcher"].regex_index == 0:
            self.mode_buffer += lexeme[0]
            return 1
        self.resume_at_same_position = True
        return 0

    def _do_begin_match(self, match: MatchObj) -> int:
        """Handle a begin-rule match.

        Args:
            match: Begin match to process.

        Returns:
            Number of input characters consumed.
        """
        lexeme = match[0]
        new_mode = match.rule
        if new_mode is None:
            raise RuntimeError("begin match is missing its mode rule")
        resp = Response(new_mode)
        before_callbacks = [
            new_mode.get("__beforeBegin"),
            new_mode.get("on:begin"),
        ]
        for cb in before_callbacks:
            if not cb:
                continue
            cb(match, resp)
            if resp.is_match_ignored:
                return self._do_ignore(lexeme)

        if new_mode.get("skip"):
            self.mode_buffer += lexeme
        else:
            if new_mode.get("excludeBegin"):
                self.mode_buffer += lexeme
            self._process_buffer()
            if not new_mode.get("returnBegin") and not new_mode.get(
                "excludeBegin"
            ):
                self.mode_buffer = lexeme
        self._start_new_mode(new_mode, match)
        return 0 if new_mode.get("returnBegin") else len(lexeme)

    def _do_end_match(self, match: MatchObj) -> Any:
        """Handle an end-rule match.

        Args:
            match: End match to process.

        Returns:
            Number of input characters consumed, or `NO_MATCH` when the
            match does not close the current mode.
        """
        lexeme = match[0]
        rest = self.code[match.index :]
        end_mode = self._end_of_mode(self.top, match, rest)
        if not end_mode:
            return NO_MATCH

        origin = self.top
        if origin.get("endScope") and origin.get("endScope__wrap"):
            self._process_buffer()
            self._emit_keyword(lexeme, origin["endScope__wrap"])
        elif origin.get("endScope") and origin.get("endScope__multi"):
            self._process_buffer()
            self._emit_multi_class(
                origin["endScope"], origin["endScope__emit"], match
            )
        elif origin.get("skip"):
            self.mode_buffer += lexeme
        else:
            if not (origin.get("returnEnd") or origin.get("excludeEnd")):
                self.mode_buffer += lexeme
            self._process_buffer()
            if origin.get("excludeEnd"):
                self.mode_buffer = lexeme

        # Pop modes until we reach end_mode's parent.
        while True:
            if self.top.get("scope"):
                self.emitter.close_node()
            if not self.top.get("skip") and not self.top.get("subLanguage"):
                self.relevance += self.top.get("relevance", 0)
            self.top = self.top["parent"]
            if self.top is end_mode.get("parent"):
                break

        if end_mode.get("starts"):
            self._start_new_mode(end_mode["starts"], match)
        return 0 if origin.get("returnEnd") else len(lexeme)

    def _process_continuations(self) -> None:
        """Restore open token scopes from the current mode stack."""
        items: list[str] = []
        current = self.top
        while current is not self.language:
            if current.get("scope"):
                items.insert(0, current["scope"])
            current = current["parent"]
        for item in items:
            self.emitter.open_node(item)

    def _process_lexeme(
        self, text_before: str, match: MatchObj | None = None
    ) -> int:
        """Process plain text followed by an optional regex match.

        Args:
            text_before: Text between the previous match and this match.
            match: Optional match to handle after `text_before`.

        Returns:
            Number of characters consumed from the matched lexeme.

        Raises:
            RuntimeError: If the scan appears to be stuck in an infinite loop.
            _IllegalError: If an illegal match is found and illegals are not
                ignored.
        """
        self.mode_buffer += text_before

        if match is None:
            self._process_buffer()
            return 0

        lexeme = match[0]
        if (
            self.last_match.get("type") == "begin"
            and match.type == "end"
            and self.last_match.get("index") == match.index
            and lexeme == ""
        ):
            self.mode_buffer += self.code[match.index : match.index + 1]
            return 1

        self.last_match = {
            "type": match.type,
            "index": match.index,
            "rule": match.rule,
        }

        if match.type == "begin":
            return self._do_begin_match(match)
        if match.type == "illegal" and not self.ignore_illegals:
            scope = self.top.get("scope") or "<unnamed>"
            raise _IllegalError(
                f'Illegal lexeme "{lexeme}" for mode "{scope}"'
            )
        if match.type == "end":
            processed = self._do_end_match(match)
            if processed is not NO_MATCH:
                return processed

        if match.type == "illegal" and lexeme == "":
            if match.index != len(self.code):
                self.mode_buffer += "\n"
            return 1

        if (
            self.iterations > _MAX_ITERATIONS
            and self.iterations > match.index * 3
        ):
            raise RuntimeError("potential infinite loop")

        self.mode_buffer += lexeme
        return len(lexeme)

    def run(self) -> TokenTreeEmitter:
        """Walk the input and return the populated emitter.

        Returns:
            Token-tree emitter containing highlighted output.

        Raises:
            _IllegalError: If an illegal match is found and illegals are not
                ignored.
        """
        self._process_continuations()
        matcher: ResumableMultiRegex = self.top["matcher"]
        matcher.consider_all()
        try:
            while True:
                self.iterations += 1
                if self.resume_at_same_position:
                    self.resume_at_same_position = False
                else:
                    self.top["matcher"].consider_all()
                self.top["matcher"].last_index = self.index
                match = self.top["matcher"].exec(self.code)
                if not match:
                    break
                before = self.code[self.index : match.index]
                processed = self._process_lexeme(before, match)
                self.index = match.index + processed
            self._process_lexeme(self.code[self.index :])
            self.emitter.finalize()
            return self.emitter
        except _IllegalError:
            # Bail like SAFE_MODE: re-run is not needed; the renderer treats
            # the (partial) tree, but to match hljs ignoreIllegals=True path
            # we never reach here. Propagate for non-ignore callers.
            raise


class _IllegalError(Exception):
    """Raised when an illegal lexeme is hit and illegals are not ignored."""


def highlight(language: Mode, code: str) -> TokenTreeEmitter:
    """Highlight source code with a compiled-or-raw language definition.

    Args:
        language: Language mode dictionary. It is compiled in place when
            needed.
        code: Source code to highlight.

    Returns:
        Token-tree emitter containing highlighted output.
    """
    if not language.get("isCompiled"):
        compile_language(language)
    return Highlighter(language, code, ignore_illegals=True).run()
