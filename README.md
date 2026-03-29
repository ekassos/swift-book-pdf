# PDF and EPUB Generator for _The Swift Programming Language_

Convert the DocC source for _The Swift Programming Language_ book into PDF and EPUB documents. The generated books follow the DocC rendering style and retain all internal references and external links.

## Preview Books

Read the EPUB editions on [Apple Books: Swift Programming Series](https://books.apple.com/us/book-series/swift-programming-series/id1887443754).

Download the latest PDF previews:

| Theme | Digital Mode<br><sub>Clickable links, best for on-screen reading</sub> | Print Mode<br><sub>Page numbers and full URLs, best for printing</sub> |
| --- | --- | --- |
| Light | [Open PDF](https://github.com/ekassos/swift-book-pdf-archive/raw/main/swift-book/latest/swift_book_digital.pdf) | [Open PDF](https://github.com/ekassos/swift-book-pdf-archive/raw/main/swift-book/latest/swift_book_print.pdf) |
| Dark | [Open PDF](https://github.com/ekassos/swift-book-pdf-archive/raw/main/swift-book/latest/swift_book_digital_dark.pdf) | [Open PDF](https://github.com/ekassos/swift-book-pdf-archive/raw/main/swift-book/latest/swift_book_print_dark.pdf) |

Looking for older releases? See [swift-book-archive](https://github.com/ekassos/swift-book-archive) for versioned archives.

![The image showcases three pages of a PDF version of "The Swift Programming Language" book. The first page displays a table of contents, listing chapters like "Welcome to Swift" and "Language Guide" with page numbers. The second page contains Swift code examples and explanations about loops, including how to use a for-in loop. The third page continues discussing while loops with a visual example of a snakes and ladders game board. The pages maintain DocC styling with black headers and highlighted code sections.](https://github.com/user-attachments/assets/466408bd-ff63-470e-a1fb-e84cb0b9412f)

## Features

### PDF generation (`swift-book-pdf`)
- Generate a PDF version of the _The Swift Programming Language_ book, perfect for offline browsing or printing.
- Choose from one of two [rendering modes](https://github.com/ekassos/swift-book-pdf/wiki/Customization-Options#rendering-modes--):
   - Digital mode with hyperlinks for cross-references between chapters and external links.
   - Print mode with page numbers accompanying cross-references between chapters and full URLs shown in footnotes for external links.
- Both versions follow the DocC rendering style used in [docs.swift.org](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/), including code highlighting.

### EPUB generation (`swift-book-epub`)
- Generate an EPUB version of the _The Swift Programming Language_ book, ideal for e-readers and mobile devices.
- The generated EPUB file follows the rendering style used by TSPL publications up to Swift 5.7 [published on Apple Books](https://books.apple.com/us/book/the-swift-programming-language-swift-5-7/id881256329) and retains all internal references and external links.

## Requirements
- Python 3.10+
- Git
- LuaTeX. If you don't have an existing LaTeX installation, see [MacTeX](https://www.tug.org/mactex/), [TeX Live](https://www.tug.org/texlive/), or [MiKTeX](https://miktex.org).
- Fonts for typesetting. Learn [which fonts are required to typeset the TSPL book](https://github.com/ekassos/swift-book-pdf/wiki/Fonts).

## Installation
### Latest PyPI stable release
```
pip install swift-book-pdf
```

## Usage
### Basic usage
#### PDF generation
Call `swift-book-pdf` without any arguments to save the resulting PDF as `swift_book.pdf` in the current directory. The package defaults to the digital [rendering mode](https://github.com/ekassos/swift-book-pdf/wiki/Customization-Options#rendering-modes--) in Letter [paper size](https://github.com/ekassos/swift-book-pdf/wiki/Customization-Options#paper-sizes--).
```
$ swift-book-pdf

[INFO]: Downloading TSPL files...
[INFO]: Creating PDF in digital (light) mode...
[INFO]: PDF saved to ./swift-book.pdf
```

When invoked, `swift-book-pdf` will:
1. Clone the `swift-book` [repository](https://github.com/swiftlang/swift-book)
2. Convert all Markdown source files into a single LaTeX document
3. Render the LaTeX document into the final PDF document

#### EPUB generation
Call `swift-book-epub` without any arguments to save the resulting EPUB as `swift_book.epub` in the current directory.
```
$ swift-book-epub
[INFO]: Downloading TSPL files...
[INFO]: Creating EPUB...
[INFO]: EPUB saved to ./swift_book.epub
```

> [!NOTE]
> Starting with version 2.1.0, you can use either `swift-book-pdf` or `swift_book_pdf` to run the tool. If you're using an earlier version, use `swift_book_pdf`.
>
> swift-book-pdf will create a temporary directory to store the swift-book repository, LaTeX file and intermediate files produced during typesetting. This temporary directory is removed after the PDF is generated.

### Customization
swift-book-pdf offers a range of options to customize your rendering of _The Swift Programming Language_ book. Learn how to [make the TSPL book your own](https://github.com/ekassos/swift-book-pdf/wiki/Customization-Options).

## Acknowledgments

At runtime, the swift-book [repository](https://github.com/swiftlang/swift-book) is temporarily cloned for processing, but no part of the repository is directly redistributed here.

`chapter-icon.png` and `chapter-icon~dark.png` are derived from the [`ArticleIcon.vue`](https://github.com/swiftlang/swift-docc-render/blob/1fe0a7a032b11272d0407317995169f79bba0d84/src/components/Icons/ArticleIcon.vue) component in the swift-docc-render [repository](https://github.com/swiftlang/swift-docc-render/).

The swift-book and swift-docc-render repositories are part of the Swift.org open source project, which is licensed under the Apache License v2.0 with Runtime Library Exception. See https://swift.org/LICENSE.txt for more details. The Swift project authors are credited at https://swift.org/CONTRIBUTORS.txt.

The Swift logo is a trademark of Apple Inc.
