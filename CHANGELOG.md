# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Check that all fonts used while typesetting by `fontspec` are accessible by LuaTeX before creating the LaTeX or PDF documents.

### Changed

- Streamline console logging.

## [1.0.1] - 2025-03-11

### Fixed
- **Markdown to LaTeX Conversion:** External URLs are not rendered as footnotes in print mode. (#1)

## [1.0.0] - 2025-03-11

### Added

- Initial release.
- Convert the DocC source for _The Swift Programming Language_ book into a print-ready PDF document.
- The final document follows the DocC rendering style and retains all internal references and external links.
- Generate a PDF version of the _The Swift Programming Language_ book, perfect for offline browsing or printing.
- Choose from one of two rendering modes: digital and print.
- Best for browsing _The Swift Programming Language_ book as a PDF, the `digital` mode renders internal references and external links in blue hyperlinks.
- Best for reading through _The Swift Programming Language_ book in print, the `print` mode includes page numbers for all internal references and complete URLs in footnotes for external links.
- Both modes follow the DocC rendering style used in [docs.swift.org](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/), including code highlighting.

### Fixed

[unreleased]: https://github.com/ekassos/swift-book-pdf/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/ekassos/swift-book-pdf/compare/v1.0...v1.0.1
[1.0.0]: https://github.com/ekassos/swift-book-pdf/releases/tag/v1.0