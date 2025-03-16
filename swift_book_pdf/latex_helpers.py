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

import os
import re
import struct
import unicodedata

import emoji
from swift_book_pdf.schema import (
    Block,
    CodeBlock,
    Header2Block,
    Header3Block,
    Header4Block,
    ImageBlock,
    NoteBlock,
    OrderedListBlock,
    ParagraphBlock,
    RenderingMode,
    TableBlock,
    TermListBlock,
    UnorderedListBlock,
)


def generate_chapter_title(lines: list[str], file_name: str) -> tuple[str, list[str]]:
    """
    Generate the chapter title LaTeX from the provided lines.

    :param lines: The lines to generate the title from
    :return: A tuple containing the title and the remaining lines
    """
    header_line = None
    subtitle_line = None

    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("#"):
            header_line = lines[i].lstrip("#").strip()
            i += 1
            break
        i += 1
    while i < len(lines):
        if lines[i].strip():
            subtitle_line = lines[i].strip()
            i += 1
            break
        i += 1

    title_subtitle_snippet = rf"""
    \thispagestyle{{firstpagestyle}}
    \renewcommand{{\customheader}}{{{header_line}}}
    \vspace*{{0.3in}}
    \HeroBox{{{header_line}}}{{{file_name}}}{{{subtitle_line}}}
    \vspace*{{0.3in}}
    """

    return title_subtitle_snippet, lines[i:]


def escape_texttt(text: str) -> str:
    """
    Escape characters in text that cause issues inside `\texttt`.
    """
    # Order matters: escape backslash first
    text = text.replace("\\", r"\textbackslash ")

    # Escape curly braces and underscore that conflict with LaTeX grouping
    text = text.replace("{", r"\{")
    text = text.replace("}", r"\}")
    text = text.replace("_", r"\_")

    # Escape hash symbol (if not already escaped)
    text = re.sub(r"(?<!\\)#", r"\#", text)

    # Escape other special characters
    text = text.replace("$", r"\$")
    text = text.replace("&", r"\&")
    text = text.replace("%", r"\%")
    text = text.replace("^", r"\textasciicircum ")
    text = text.replace("`", r"\textasciigrave ")
    text = text.replace("~", r"\textasciitilde ")
    text = text.replace("[", r"{[}")
    text = text.replace("]", r"{]}")
    text = text.replace("(", r"{(}")
    text = text.replace(")", r"{)}")
    text = text.replace(".", r"{.}")
    text = text.replace(",", r"{,}")
    text = text.replace(":", r"{:}")
    text = text.replace(";", r"{;}")
    text = text.replace("=", r"{=}")
    text = text.replace("@", r"{@}")
    text = text.replace("?", r"{?}")
    text = text.replace("!", r"{!}")

    # The arrow token "->" is two characters long.
    # Replace it before any chance of interfering with its hyphen.
    text = text.replace("->", r"{->}")

    return text


def apply_formatting(text: str, mode: RenderingMode) -> str:
    """
    Apply formatting to the given text.
    """
    # Temporarily extract inline code segments produced by convert_inline_code
    inline_segments: dict[str, str] = {}

    def replace_inline(match):
        token = f"%%INLINE-CODE-{len(inline_segments)}%%"
        inline_segments[token] = match.group(0)
        return token

    text = re.sub(r"(\{\\CodeStyle\s+\\texttt\{.*?\}\})", replace_inline, text)

    # Apply formatting to the rest of the text.
    text = text.replace("→", r"\scalebox{1.2}{$\rightarrow$}")
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"\*(.+?)\*", r"\\emph{\1}", text)
    text = re.sub(r"\s\\\s", r" \\\\ ", text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?:\/\/(?:[^()\s]+|\([^()]*\))+)\)",
        (
            r"\\href{\2}{\1}\\footnote{\\url{\2}}"
            if mode == RenderingMode.PRINT
            else r"\\href{\2}{\1}"
        ),
        text,
    )
    text = re.sub(r"(?<!\\)_", r"\_", text)
    text = re.sub(r"---", r"\\textemdash \\ ", text)
    text = re.sub(r"--", r"\\textendash", text)
    text = re.sub(r"\(\\\`\)", "(\;\`\; )", text)
    text = re.sub(
        r"<doc:([^>#]+)#([^>]+)>",
        lambda m: (
            "\\fallbackrefbook{"
            if mode == RenderingMode.PRINT
            else "\\fallbackrefdigital{"
        )
        + m.group(1).lower()
        + "_"
        + m.group(2).lower()
        + "}",
        text,
    )
    text = re.sub(
        r"<doc:([^>#]+)>",
        lambda m: (
            "\\fallbackrefbook{"
            if mode == RenderingMode.PRINT
            else "\\fallbackrefdigital{"
        )
        + m.group(1).lower()
        + "}",
        text,
    )
    text = re.sub(r"(?<!\\)#", r"\#", text)

    # Restore the inline code segments.
    for token, segment in inline_segments.items():
        text = text.replace(token, segment)

    matches = emoji.emoji_list(text)
    if matches:
        for match in matches:
            emoji_char = match["emoji"]
            text = text.replace(emoji_char, f"\\loweremoji{{\\emoji{emoji_char}}}")

    matches = detect_non_latin(text)
    if matches:
        for ch in matches:
            text = text.replace(ch, f"\\textNonLatin{{{ch}}}")
    return text


def wrap_emoji_string(line: str) -> str:
    """
    Wrap emoji in the given line to escape code font rendering.
    """

    matches = emoji.emoji_list(line)
    matches = [match["emoji"] for match in matches]

    # NOTE: The emoji incorrectly detects these as emoji
    # Remove these from the matches list
    overrides = ["♥", "♡", "♠", "♤", "♦", "♢", "♣", "♧"]
    matches = [m for m in matches if m not in overrides]
    if not matches:
        return line

    is_comment = "//" in line

    def find_innermost_string(text, char):
        pattern = (
            r'((?:"[^"]*?'
            + re.escape(char)
            + "[^\"]*?\")|(?:'[^']*?"
            + re.escape(char)
            + "[^']*?'))"
        )
        matches = re.findall(pattern, text)
        return matches

    for emoji_char in matches:
        if is_comment:
            line = line.replace(
                emoji_char, f"|\\PYG{{c+c1}}{{\\loweremoji{{\\emoji{emoji_char}}}}}|"
            )
        else:
            string_result = find_innermost_string(line, emoji_char)
            if string_result:
                _string_result = string_result[0]
                _string_result = _string_result.replace(
                    emoji_char, f"\\loweremoji{{\\emoji{emoji_char}}}"
                )
                _matches = emoji.emoji_list(_string_result)
                for _match in _matches:
                    if _match["emoji"] != emoji_char:
                        _string_result = _string_result.replace(
                            _match["emoji"], f"\\loweremoji{{\\emoji{_match['emoji']}}}"
                        )
                        if _match["emoji"] in matches:
                            matches.remove(_match["emoji"])
                _string_result = _string_result.replace('"', r"\PYGZdq{}")
                _string_result = _string_result.replace("'", r"\PYGZsq{}")
                _string_result = f"|\\PYG{{l+s}}{{{_string_result}}}|"
                line = line.replace(string_result[0], _string_result)
            else:
                line = line.replace(
                    emoji_char, f"|\\PYG{{l+s}}{{\\loweremoji{{\\emoji{emoji_char}}}}}|"
                )

    return line


def detect_non_latin(text: str) -> dict[str, str]:
    """
    Detect non-Latin letters or numbers.

    Allowed characters:
      - Letters whose Unicode name includes "LATIN" (covers accented Latin letters too)
      - Decimal digits (category 'Nd') that are considered allowed.

    Only if a character is a letter (category 'L*') or a digit (Nd) and does not meet
    the allowed conditions will it be reported.

    Characters such as punctuation, whitespace, symbols, and control characters (even though
    they are non-Latin) are ignored.
    """

    matches = {}

    override_set = {"é⃝": "\\textcircled{é}"}
    for char, replacement in override_set.items():
        if char in text:
            text = text.replace(char, "")
            matches[char] = replacement

    for ch in text:
        cat = unicodedata.category(ch)

        # Check letters.
        if cat.startswith("L"):
            try:
                name = unicodedata.name(ch)
            except ValueError:
                continue

            if (
                ("LATIN" not in name)
                and ("GREEK" not in name)
                and ("CYRILLIC" not in name)
                and name not in {"MODIFIER LETTER SMALL X"}
                and ch not in {"é"}
            ):
                matches[ch] = ch

        # Check digits.
        elif cat == "Nd":
            if ch not in "0123456789":
                matches[ch] = ch

        # For all other categories (punctuation, space, symbols, control characters, etc.)
        # we do not want to report anything.
        else:
            continue

    return matches


def wrap_non_latin(text: str) -> str:
    """
    Wrap non-Latin characters in the given line to escape code font rendering.

    Processing is done in three stages:
      1. Comments (assumed to start with '//' until end-of-line) are replaced. Offending characters inside comments are replaced by: `│\PYG{c+c1}{\\textNonLatin{<replacement>}}│` and the entire comment region is protected with a placeholder.

      2. String literals (matching either "…" or '…') are processed. Inside a literal the inner content is scanned; if any offending characters are found then each is replaced by: `│\PYG{l+s}{\\textNonLatin{<replacement>}}│`.

         In that case the literal's surrounding quotes are also replaced (using markup tokens); for example, if the literal was double-quoted, the opening and closing quotes become `│\PYG{l+s}{\PYGZdq{}}│`.

         If no offending characters are found the literal is left unchanged. (In either case the literal is protected with a placeholder.)

      3. The remaining text (outside protected regions) is globally processed so any offending characters are replaced by: `│\PYG{l+s}{\\textNonLatin{<replacement>}}│`

    Finally, the placeholders are restored. This ensures that replacements in protected regions are not subject to a second round of processing.
    """
    matches = detect_non_latin(text)
    if not matches:
        return text

    placeholders = {}
    placeholder_id = 0

    def make_placeholder(segment):
        nonlocal placeholder_id
        key = f"@@PLACEHOLDER_{placeholder_id}@@"
        placeholders[key] = segment
        placeholder_id += 1
        return key

    # Process comments.
    # Assumes comments start with '//' and run until the end of the line.
    def process_comment(match):
        comment = match.group(0)
        for ch, replacement in matches.items():
            if ch in comment:
                comment = comment.replace(
                    ch, f"|\\PYG{{c+c1}}{{\\textNonLatin{{{replacement}}}}}|"
                )
        return make_placeholder(comment)

    text = re.sub(r"//.*$", process_comment, text, flags=re.MULTILINE)

    # Process string literals.
    # The following regex catches either double-quoted or single-quoted literals.
    def process_literal(match):
        literal = match.group(0)
        if len(literal) < 2 or (literal[0] != literal[-1]):
            return literal  # Invalid literal; leave unchanged.
        quote_char = literal[0]
        inner = literal[1:-1]
        new_inner = inner
        replaced_inside = False
        for ch, replacement in matches.items():
            if ch in new_inner:
                replaced_inside = True
                new_inner = new_inner.replace(
                    ch, f"|\\PYG{{l+s}}{{\\textNonLatin{{{replacement}}}}}|"
                )
        if replaced_inside:
            # If any offending character was replaced inside the literal,
            # replace the quotes with corresponding markup wrapped in vertical bars.
            if quote_char == '"':
                open_quote = r"|\PYG{l+s}{\PYGZdq{}}|"
                close_quote = r"|\PYG{l+s}{\PYGZdq{}}|"
            else:
                open_quote = r"|\PYG{l+s}{\PYGZsq{}}|"
                close_quote = r"|\PYG{l+s}{\PYGZsq{}}|"
            processed_literal = f"{open_quote}{new_inner}{close_quote}"
            return make_placeholder(processed_literal)
        else:
            # If no offending character was found, leave the literal untouched.
            return make_placeholder(literal)

    text = re.sub(r'(".*?"|\'.*?\')', process_literal, text)

    # Process any remaining occurrences outside protected regions.
    for ch, replacement in matches.items():
        text = text.replace(ch, f"|\\PYG{{l+s}}{{\\textNonLatin{{{replacement}}}}}|")

    # Restore the protected regions.
    for key, segment in placeholders.items():
        text = text.replace(key, segment)

    return text


def convert_inline_code(text: str) -> str:
    """
    Replace inline code delimited by unescaped backticks with
    `{\CodeStyle \texttt{...}}`.

    This converter supports two kinds of delimiters:
      • Double backticks (``...``): These blocks are processed first
        and “protected” so that any inner single backticks (as in “`x`”)
        are not processed a second time.
      • Single backticks (`...`): Handled afterward.

    Escaped backticks (preceded by a backslash) are not processed.
    """
    # Protect double-backtick replacements with placeholders.
    double_placeholder: dict[str, str] = {}

    def repl_double(match):
        inner = match.group(1)  # Everything between the double backticks.
        processed = r"{\CodeStyle \texttt{" + escape_texttt(inner).strip() + "}}"
        # Create a unique token unlikely to appear in the text.
        token = f"@@DOUBLE{len(double_placeholder)}@@"
        double_placeholder[token] = processed
        return token

    # Process double-backtick code first.
    # This regex matches two unescaped backticks on each side.
    text = re.sub(r"(?<!\\)``(.*?)``", repl_double, text)

    # Now process single-backtick code.
    def repl_single(match):
        inner = match.group(1)
        return r"{\CodeStyle \texttt{" + escape_texttt(inner).strip() + "}}"

    text = re.sub(r"(?<!\\)`(.*?)`", repl_single, text)

    # Finally, restore the double-backtick replacements.
    for token, replacement in double_placeholder.items():
        text = text.replace(token, replacement)

    return text


def convert_nested_block(block: Block, mode: RenderingMode) -> str:
    if isinstance(block, ParagraphBlock):
        para = " ".join(block.lines)
        para_conv = apply_formatting(convert_inline_code(para), mode)
        return para_conv
    elif isinstance(block, CodeBlock):
        out = (
            "\\parskip=0pt\n"
            r"\begin{swiftstyledbox}" + "\n"
        )
        for line in block.lines:
            line2 = line.replace("%", "\%")
            out += wrap_non_latin(wrap_emoji_string(line2)) + "\n"
        out += r"\end{swiftstyledbox}" + "\n"
        return out
    else:  # fallback
        text = " ".join(block.lines if "lines" in block.model_fields else [])
        text_conv = apply_formatting(convert_inline_code(text), mode)
        return text_conv


def convert_blocks_to_latex(
    blocks: list[Block],
    file_name: str,
    assets_dir: str,
    mode: RenderingMode,
    main_font: str,
) -> list[str]:
    """
    Convert parsed blocks into corresponding LaTeX lines.

    :param blocks: The parsed blocks to convert
    :param file_name: The name of the file being converted
    :param assets_dir: The directory containing the images
    :param mode: The rendering mode
    :param main_font: The font to be used for the main text
    :return: A list of LaTeX lines
    """
    output: list[str] = []
    for block in blocks:
        if isinstance(block, CodeBlock):
            output.append(
                "\\parskip=0pt\n" + r"\begin{flushleft}\begin{swiftstyledbox}"
            )
            for line in block.lines:
                # Escape % characters
                line = line.replace("%", "\%")
                # Escape non-latin and emoji characters
                output.append(wrap_non_latin(wrap_emoji_string(line)))
            output.append(r"\end{swiftstyledbox}" + "\n\\end{flushleft}\n")
        elif isinstance(block, UnorderedListBlock):
            output.append(r"\begin{itemize}")
            # Each item is a list (i.e. a list of nested blocks)
            for item in block.items:
                if not item:
                    continue
                first = True
                for sub_block in item:
                    latex_sub = convert_nested_block(sub_block, mode)
                    if first:
                        output.append(f"\\item \\ParagraphStyle{{{latex_sub}}}\n")
                        first = False
                    else:
                        if not latex_sub.startswith("\parskip"):
                            output.append(f"\\ParagraphStyle{{{latex_sub}}}\n")
                        else:
                            output.append(latex_sub)
            output.append(r"\end{itemize}" + "\n\global\AtPageTopfalse\n")
        elif isinstance(block, OrderedListBlock):
            output.append(r"\begin{enumerate}")
            for ol_item in block.items:
                item_conv = apply_formatting(convert_inline_code(ol_item), mode)
                output.append(f"\\item {item_conv}")
            output.append(r"\end{enumerate}" + "\n\global\AtPageTopfalse\n")
        elif isinstance(block, TermListBlock):
            output.append("\\ParagraphStyle{")
            for term in block.items:
                label_conv = apply_formatting(convert_inline_code(term.label), mode)
                content_conv = apply_formatting(convert_inline_code(term.content), mode)
                output.append(
                    f"\\needspace{{3\\baselineskip}} {label_conv} \\vspace*{{-0.09in}} \\begin{{quote}} {content_conv} \\end{{quote}}"
                )
            output.append(" }\n")
        elif isinstance(block, ImageBlock):
            # TODO: Add support for image captions
            _ = block.alt
            imgname = block.imgname

            img_path = os.path.join(assets_dir, f"{imgname}@2x.png")
            final_width = "auto"
            width = None
            try:
                with open(img_path, "rb") as f:
                    f.seek(16)  # Width and height are stored at byte 16 in a PNG
                    width, _ = struct.unpack(">II", f.read(8))
                width = width / 273.2  # Convert pixels to inches
            except Exception:
                continue

            if width is not None:
                if width > 6.5:
                    final_width = "6.5in"
                else:
                    final_width = f"{width}in"

            output.append(
                f"\\begin{{figure}}[H]\n\\centering\\includegraphics[width={final_width}]{{{img_path}}}\n\\end{{figure}}\n\\global\\AtPageTopfalse\n"
            )
        elif isinstance(block, Header2Block):
            content = convert_inline_code(block.content)
            label_name = "-".join(content.title().split()).lower()
            output.append(
                f"\\SectionHeader{{{apply_formatting(content, mode)}}}{{"
                + file_name.replace("'", "")
                + "_"
                + label_name.replace("'", "")
                + "}\n"
            )
        elif isinstance(block, Header3Block):
            content = convert_inline_code(block.content)
            label_name = "-".join(content.title().split()).lower()
            output.append(
                f"\\SubsectionHeader{{{apply_formatting(content, mode)}}}{{"
                + file_name.replace("'", "")
                + "_"
                + label_name.replace("'", "")
                + "}\n"
            )
        elif isinstance(block, Header4Block):
            content = convert_inline_code(block.content)
            label_name = "-".join(content.title().split()).lower()
            output.append(
                f"\\SubsubsectionHeader{{{apply_formatting(content, mode)}}}{{"
                + file_name.replace("'", "")
                + "_"
                + label_name.replace("'", "")
                + "}\n"
            )
        elif isinstance(block, NoteBlock):
            label = block.label
            aside_lines = []
            for sub_block in block.blocks:
                aside_lines.append(convert_nested_block(sub_block, mode))
            aside_content = "\n".join(aside_lines)
            output.append("\\begin{flushleft}\\begin{asideNote}")
            output.append(f" \\textbf{{{label}}} \\vspace*{{4pt}} \\\\")
            output.append(aside_content)
            output.append("\\end{asideNote}\\end{flushleft}" + "\n")
        elif isinstance(block, ParagraphBlock):
            para = " ".join(block.lines)
            para_conv = convert_inline_code(para)
            para_conv = apply_formatting(para_conv, mode)
            output.append(f"\\ParagraphStyle{{{para_conv}}}\n")
        elif isinstance(block, TableBlock):
            output.append(
                "\\begin{table}[H]\n\\centering\n\\setlength{\\tymin}{1in}\\arrayrulecolor{heroGray}\n\\renewcommand{\\arraystretch}{1.5}\n\\fontspec{"
                + main_font
                + "}\\fontsize{9pt}{1.15\\baselineskip}\\selectfont\\setlength{\\parskip}{0.09in}\\raggedright"
            )
            header_row = block.rows[0]
            output.append(
                f"\\begin{{tabulary}}{{1.0\\textwidth}}{{{'|'.join(['L' for _ in header_row])}}}"
            )
            # Add the header row
            output.append(
                " & ".join(
                    map(
                        lambda x: f"\\textbf{{{apply_formatting(convert_inline_code(x), mode)}}}",
                        header_row,
                    )
                )
                + " \\\\ \\hline"
            )
            for row in block.rows[1:-1]:
                output.append(
                    " & ".join(
                        map(
                            lambda x: apply_formatting(convert_inline_code(x), mode),
                            row,
                        )
                    )
                    + " \\\\ \\hline"
                )
            # Add the last row without a trailing hline
            if block.rows[-1]:
                output.append(
                    " & ".join(
                        map(
                            lambda x: apply_formatting(convert_inline_code(x), mode),
                            block.rows[-1],
                        )
                    )
                    + " \\\\"
                )
            output.append("\\end{tabulary}")
            output.append("\\end{table}")
            output.append("\n")
        else:
            text = " ".join(block.get("lines", []))
            text_conv = convert_inline_code(text)
            output.append(f"\\ParagraphStyle{{{text_conv}}}\n")
    return output
