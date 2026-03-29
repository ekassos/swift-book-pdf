# PDF and EPUB Generator for _The Swift Programming Language_

Convert the DocC source for _The Swift Programming Language_ book into polished PDF and EPUB editions.

<img width="3840" height="1920" alt="The image shows The Swift Programming Language book displayed across three devices: a 14-inch MacBook Pro (M4) in Silver, an 11-inch iPad Pro (M4) in Space Gray, and an iPhone 17 Pro in Deep Blue. Each screen shows pages from the book titled Collection Types, featuring diagrams, code snippets, and explanations about arrays, sets, and dictionaries in Swift. Below the devices, centered text reads 'Swift Book PDF' followed by a large bold headline, 'Learn Swift anywhere.' The background is clean and light gray, emphasizing the devices and text." src="https://github.com/user-attachments/assets/87ccccc0-0d41-4768-be03-bb91a083207d" />

## Get the book

<table>
  <tr>
    <td valign="middle" width="70%">
    <a href="https://books.apple.com/us/book-series/swift-programming-series/id1887443754"><img alt="Read the latest edition. Click this image to get it on Apple Books." src="https://github.com/user-attachments/assets/7682de0f-35ae-4391-8a01-2b802475725e"/></a>
    </td>
    <td valign="middle" width="30%">
      <p><i>The Swift Programming Language</i>, optimized for Apple Books.</p>
      <p><a href=https://books.apple.com/us/book-series/swift-programming-series/id1887443754">Open in Apple Books &#8599;</a></p>
      <a href="https://books.apple.com/us/book-series/swift-programming-series/id1887443754"><img src="https://toolbox.marketingtools.apple.com/api/v2/badges/get-it-on-apple-books/badge/en-us" alt="Get it on Apple Books"/></a>    
    </td>
  </tr>
</table>

<table>
  <tr>
    <td valign="top" width="50%">
      <a id="apple-books"></a>
      <h3>EPUB on Apple Books</h3>
      <p><strong>Best for:</strong> Apple Books, iPhone, iPad, and e-reader-style reading.</p>
      <p>Read the EPUB editions in the <em>Swift Programming Series</em> on Apple Books.</p>
      <p>
        <a href="https://books.apple.com/us/book-series/swift-programming-series/id1887443754"><img src="https://toolbox.marketingtools.apple.com/api/v2/badges/get-it-on-apple-books/badge/en-us" alt="Get it on Apple Books" /></a>
      </p>
      <p><a href="https://books.apple.com/us/book-series/swift-programming-series/id1887443754"><strong>Read on Apple Books</strong></a></p>
      <p>The Apple Books listing is the EPUB edition of the series, optimized for on-device reading.</p>
    </td>
    <td valign="top" width="50%">
      <a id="pdf-previews"></a>
      <h3>PDF Previews</h3>
      <p><strong>Best for:</strong> desktop reading, offline reference, and printing.</p>
      <p>Choose between Digital and Print renderings in Light or Dark mode.</p>
      <p><strong>Digital</strong>: clickable links and cross-references<br><strong>Print</strong>: page references and full URLs</p>
      <table>
        <tr>
          <td><a href="https://github.com/ekassos/swift-book-archive/releases/latest/download/swift_book_digital.pdf " target="_blank"><img src="https://img.shields.io/badge/Digital%20%C2%B7%20Light-Open%20PDF-064789?style=for-the-badge&logo=googledocs&logoColor=white" alt="Open Digital Light PDF"></a></td>
          <td><a href="https://github.com/ekassos/swift-book-archive/releases/latest/download/swift_book_print.pdf" target="_blank"><img src="https://img.shields.io/badge/Print%20%C2%B7%20Light-Open%20PDF-941b0c?style=for-the-badge&logo=googledocs&logoColor=white" alt="Open Print Light PDF"></a></td>
        </tr>
        <tr>
          <td><a href="https://github.com/ekassos/swift-book-archive/releases/latest/download/swift_book_digital_dark.pdf" target="_blank"><img src="https://img.shields.io/badge/Digital%20%C2%B7%20Dark-Open%20PDF-0d3b66?style=for-the-badge&logo=googledocs&logoColor=white" alt="Open Digital Dark PDF"></a></td>
          <td><a href="https://github.com/ekassos/swift-book-archive/releases/latest/download/swift_book_print_dark.pdf" target="_blank"><img src="https://img.shields.io/badge/Print%20%C2%B7%20Dark-Open%20PDF-6d1f1f?style=for-the-badge&logo=googledocs&logoColor=white" alt="Open Print Dark PDF"></a></td>
        </tr>
      </table>
      <p>Need older versions? Browse <a href="https://github.com/ekassos/swift-book-archive">swift-book-archive</a>.</p>
    </td>
  </tr>
</table>

## Features

### PDF Generation (`swift-book-pdf`)
- Generate a PDF edition of _The Swift Programming Language_, optimized for offline reading or printing.
- Choose from one of two [rendering modes](https://github.com/ekassos/swift-book-pdf/wiki/Customization-Options#rendering-modes--):
   - Digital mode with hyperlinks for cross-references between chapters and external links.
   - Print mode with page numbers accompanying cross-references between chapters and full URLs shown in footnotes for external links.
- Both versions follow the DocC rendering style used in [docs.swift.org](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/), including code highlighting.

### EPUB Generation (`swift-book-epub`)
- Generate an EPUB edition of _The Swift Programming Language_, ideal for e-readers and mobile devices.
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
