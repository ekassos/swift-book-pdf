# Changelog

## [Unreleased]

## [1.0.2] - 2025-03-12

### Added

- Add check that all fonts used by `fontspec` while typesetting are accessible by LuaTeX before creating the LaTeX or PDF documents. ([#4](https://github.com/ekassos/swift-book-pdf/pull/4))
- _Docs:_ Add fonts required by `fontspec` in Requirements section. ([#4](https://github.com/ekassos/swift-book-pdf/pull/4))
- _Docs:_ Add details about making fonts known to LuaTeX. ([#4](https://github.com/ekassos/swift-book-pdf/pull/4))
- _Docs:_ Add changelog. ([#6](https://github.com/ekassos/swift-book-pdf/pull/6))

### Changed

- Streamline console logging and reduce redundant logs at the default logging level. ([#5](https://github.com/ekassos/swift-book-pdf/pull/5))

## [1.0.1] - 2025-03-11

### Fixed
- Fix an issue where external URLs were not being rendered as footnotes in print mode. ([#1](https://github.com/ekassos/swift-book-pdf/pull/1))

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


[unreleased]: https://github.com/ekassos/swift-book-pdf/compare/v1.0.2...HEAD
[1.0.2]: https://github.com/ekassos/swift-book-pdf/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/ekassos/swift-book-pdf/compare/v1.0...v1.0.1
[1.0.0]: https://github.com/ekassos/swift-book-pdf/releases/tag/v1.0
