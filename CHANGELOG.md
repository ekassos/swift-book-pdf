# Changelog

## [Unreleased]

### Added
- Add new "Global" font category as a unicode font for additional characters not supported by the main font, e.g. Chinese characters. The same font can be used both for Global and Unicode categories if it includes all required glyphs (e.g. Arial Unicode MS).

### Fixed
- Fix an issue where the minted package could not shell escape in systems running MiKTeX.
- Fix an issue where internal references might not populate properly in Windows systems.
- Fix an issue where logs might not render properly because of an incorrect encoding issue, causing the entire typesetting process to fail.
- Fix an issue where image paths passed to LaTeX were not following the Unix style in Windows systems.
- Fix an issue where the output file could not be saved by overwriting an existing file in Windows systems.
- Fix an issue where an accepted Unicode font may not support all required glyphs.
- Fix an issue where the LaTeX typesetting process may continue even after a font error is raised.
- Fix an issue where fonts names may be incorrectly recognized as available to LuaTeX because of partial name matches.

### Changed
- When rendering unsupported characters, fall through all available fonts in case the character is supported by one of the other available fonts.
- Change the order in which default fonts in the Mono Fonts category are checked for availability to LuaTeX. Courier New is now the final default font option checked, as it provides extremely thin glyphs.

### Internal
- Replace `wrap_emoji_string` and `detect_non_latin`/`wrap_non_latin` processing pipelines with `luaotfload` font fallbacks.
- Add new `override_characters` function for characters requiring special handling before typesetting. Previously handled within `wrap_non_latin`.
- Remove `emoji` dependency.

## [1.2.0] - 2025-03-15

### Added

- Add more default font options, organized in five font categories. swift-book-pdf will typeset TSPL in any system where LuaTeX has access to at least one font in each font category.
- Add option to use custom fonts.
- Add error reporting when a font (custom or default) does not support a typeset character based on the assigned font category.
- Add `--version` CLI option.
- Add Github issue template for font issue reporting.

## [1.1.0] - 2025-03-13

### Added

- Add CLI `--paper` option to generate book in letter, legal, or A4 paper sizes. ([#7](https://github.com/ekassos/swift-book-pdf/pull/7))

### Changed

- Changed the footer's bottom margin to mirror the header's top margin. ([#7](https://github.com/ekassos/swift-book-pdf/pull/7))

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


[unreleased]: https://github.com/ekassos/swift-book-pdf/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/ekassos/swift-book-pdf/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/ekassos/swift-book-pdf/compare/v1.0...v1.0.1
[1.0.0]: https://github.com/ekassos/swift-book-pdf/releases/tag/v1.0
