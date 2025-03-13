# PDF Generator for _The Swift Programming Language_

Convert the DocC source for _The Swift Programming Language_ book into a print-ready PDF document. The final document follows the DocC rendering style and retains all internal references and external links.

<table>
  <tr>
    <td colspan="2"><b>Preview Books</b></td>
  </tr>
  <tr>
    <td><a href="https://github.com/ekassos/swift-book-pdf/releases/download/v1.1.0/swift_book_digital.pdf" target="_blank"><img src="https://img.shields.io/badge/download_book_(digital_mode)-064789?style=for-the-badge&logo=googledocs&logoColor=white" alt="Download book in digital mode"></a></td>
    <td><a href="https://github.com/ekassos/swift-book-pdf/releases/download/v1.1.0/swift_book_print.pdf" target="_blank"><img src="https://img.shields.io/badge/download_book_(print_mode)-941b0c?style=for-the-badge&logo=googledocs&logoColor=white" alt="Download book in print mode"></a></td>
  </tr>
</table>

![The image showcases three pages of a PDF version of "The Swift Programming Language" book. The first page displays a table of contents, listing chapters like "Welcome to Swift" and "Language Guide" with page numbers. The second page contains Swift code examples and explanations about loops, including how to use a for-in loop. The third page continues discussing while loops with a visual example of a snakes and ladders game board. The pages maintain DocC styling with black headers and highlighted code sections.](https://github.com/user-attachments/assets/466408bd-ff63-470e-a1fb-e84cb0b9412f)

## Features
- Generate a PDF version of the _The Swift Programming Language_ book, perfect for offline browsing or printing.
- Choose from one of two [rendering modes](#rendering-modes):
   - Digital mode with hyperlinks for cross-references between chapters and external links.
   - Print mode with page numbers accompanying cross-references between chapters and full URLs shown in footnotes for external links.
- Both versions follow the DocC rendering style used in [docs.swift.org](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/), including code highlighting.

## Requirements
- Python 3.9+
- Git
- LuaTeX (see [MacTeX](https://www.tug.org/mactex/), [TeX Live](https://www.tug.org/texlive/), or [MiKTeX](https://miktex.org))
- The following fonts accessible by LuaTeX[^1]:
   - Apple Color Emoji
   - Arial Unicode MS
   - Helvetica Neue
   - Helvetica Neue Bold
   - Menlo
   - [SF Compact Display](https://developer.apple.com/fonts/)

[^1]: If LuaTeX cannot find a font used by the package, you may see an error like:<pre><code>Can't build The Swift Programming Language book: Font "Apple Color Emoji" is not accessible by LuaTeX.</pre></code>These fonts should come preinstalled in recent versions of macOS, except for SF Compact Display, which must be downloaded separately from the [Apple Developer website](https://developer.apple.com/fonts/).</br></br>Accessible by, or known to LuaTeX in this case generally means _exists in a standard fonts location_ such as `~/Library/Fonts/` on macOS, or `C:\Windows\Fonts` on Windows. On Linux, common font locations include `/usr/share/fonts/`, `~/.local/share/fonts/`, and `~/.fonts/`. If a font isn't detected, running `fc-cache -fv` may help update the font cache. Fonts are also accessible if found in the TEXMF tree. See the [fontspecs package documentation](https://ctan.org/pkg/fontspec) for more details.

## Installation
### Latest PyPI stable release
```
pip install swift-book-pdf
```

## Usage
### Basic usage
Call `swift_book_pdf` without any arguments to save the resulting PDF as `swift_book.pdf` in the current directory. The package defaults to the digital [rendering mode](#rendering-modes) in Letter [paper size](#paper-sizes).
```
$ swift_book_pdf

[INFO]: Downloading TSPL files...
[INFO]: Creating PDF in digital mode...
[INFO]: PDF saved to ./swift-book.pdf
```

When invoked, `swift_book_pdf` will:
1. Clone the `swift-book` [repository](https://github.com/swiftlang/swift-book)
2. Convert all Markdown source files into a single LaTeX document
3. Render the LaTeX document into the final PDF document

> [!NOTE]
> swift_book_pdf will create a temporary directory to store the swift-book repository, LaTeX file and intermediate files produced during typesetting. This temporary directory is removed after the PDF is generated.

### Output path
You can also specify an output path:
```
swift_book_pdf /path/to/output.pdf
```

### Rendering modes
`swift_book_pdf` supports two rendering modes:

1. `digital` (default): Best for browsing _The Swift Programming Language_ book as a PDF, the `digital` mode renders internal references and external links in blue hyperlinks.
2. `print`: Best for reading through _The Swift Programming Language_ book in print, the `print` mode includes page numbers for all internal references and complete URLs in footnotes for external links.

Use the `--mode` option to set your preferred rendering option:

```
swift_book_pdf /path/to/output.pdf --mode print
```

### Paper sizes
`swift_book_pdf` supports three paper sizes:

1. `letter` (default)
2. `legal`
3. `A4`

Use the `--paper` option to set your preferred paper size:
```
swift_book_pdf --paper legal
```

### Number of typesetting passes
This package uses LaTeX to typeset the TSPL book. LaTeX arranges page elements dynamically, so references added in the second pass may shift the page content, and alter the placement of headers and footers. To ensure everything is properly rendered, swift_book_pdf typesets the document four times.

If needed, you can adjust the number of typesets:
```
swift_book_pdf /path/to/output.pdf --typesets 5
```

> [!CAUTION]
> Only increase the number of typesets if the document has missing references or misaligned headers or footers.
>
> Do not decrease the number of typesets. Given the document's complexity (650+ pages with relative anchors), the extra typesets ensure proper rendering of headers and footers.
>
> **Always run at least two typesets.** Skipping this may break internal references to other sections.

## Acknowledgments

At runtime, the swift-book [repository](https://github.com/swiftlang/swift-book) is temporarily cloned for processing, but no part of the repository is directly redistributed here.

`chapter-icon.png` is derived from the [`ArticleIcon.vue`](https://github.com/swiftlang/swift-docc-render/blob/1fe0a7a032b11272d0407317995169f79bba0d84/src/components/Icons/ArticleIcon.vue) component in the swift-docc-render [repository](https://github.com/swiftlang/swift-docc-render/).

The swift-book and swift-docc-render repositories are part of the Swift.org open source project, which is licensed under the Apache License v2.0 with Runtime Library Exception. See https://swift.org/LICENSE.txt for more details. The Swift project authors are credited at https://swift.org/CONTRIBUTORS.txt.

The Swift logo is a trademark of Apple Inc.
