# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.0]

### Added
- Add more accurate font checking mechanism by testing whether each font is accessible to package `fontspec` through a quick LaTeX typeset. ([#27](https://github.com/ekassos/swift-book-pdf/pull/27))
- Add support for specifying multiple Unicode fallback fonts through the `--unicode` CLI option. ([#28](https://github.com/ekassos/swift-book-pdf/pull/28))

### Fixed
- Fix an issue where the minted package could not shell escape in systems running MiKTeX. ([#18](https://github.com/ekassos/swift-book-pdf/pull/18))
- Fix an issue where internal references might not populate properly in Windows systems. ([#19](https://github.com/ekassos/swift-book-pdf/pull/19))
- Fix an issue where logs might not render properly because of an incorrect encoding issue, causing the entire typesetting process to fail. ([#20](https://github.com/ekassos/swift-book-pdf/pull/20))
- Fix an issue where image paths passed to LaTeX were not following the Unix style in Windows systems. ([#21](https://github.com/ekassos/swift-book-pdf/pull/21))
- Fix an issue where the output file could not be saved by overwriting an existing file in Windows systems. ([#22](https://github.com/ekassos/swift-book-pdf/pull/22))
- Fix an issue where an accepted Unicode font may not support all required glyphs. ([#23](https://github.com/ekassos/swift-book-pdf/pull/23))
- Fix an issue where the LaTeX typesetting process may continue even after a font error is raised. ([#24](https://github.com/ekassos/swift-book-pdf/pull/24))
- Fix an issue where fonts names may be incorrectly recognized as available to LuaTeX because of partial name matches. ([#25](https://github.com/ekassos/swift-book-pdf/pull/25))
- Fix an issue where some reference-style Markdown links may be missing from the LaTeX document. ([#26](https://github.com/ekassos/swift-book-pdf/pull/26)) ([#29](https://github.com/ekassos/swift-book-pdf/pull/29))

### Changed
- When rendering unsupported characters, fall through all available fonts in case the character is supported by one of the other available fonts. ([#17](https://github.com/ekassos/swift-book-pdf/pull/17))
- Change the order in which default fonts in the Mono Fonts category are checked for availability to LuaTeX. Courier New is now the final default font option checked, as it provides extremely thin glyphs. ([#25](https://github.com/ekassos/swift-book-pdf/pull/25))

### Internal
- Replace `wrap_emoji_string` and `detect_non_latin`/`wrap_non_latin` processing pipelines with `luaotfload` font fallbacks. ([#17](https://github.com/ekassos/swift-book-pdf/pull/17))
- Add new `override_characters` function for characters requiring special handling before typesetting. Previously handled within `wrap_non_latin`. ([#17](https://github.com/ekassos/swift-book-pdf/pull/17))
- Remove `emoji` dependency. ([#17](https://github.com/ekassos/swift-book-pdf/pull/17))
- Add `latexminted` package dependency to ensure that `minted` v3 can run correctly on all systems. ([#30](https://github.com/ekassos/swift-book-pdf/pull/30))
- Only use shell escape when using an unsupported system (TeX Live \< 2024 or MiKTeX). ([#30](https://github.com/ekassos/swift-book-pdf/pull/30))

## [1.2.0] - 2025-03-15

### Added

- Add more default font options, organized in five font categories. swift-book-pdf will typeset TSPL in any system where LuaTeX has access to at least one font in each font category. ([#12](https://github.com/ekassos/swift-book-pdf/pull/12))
- Add option to use custom fonts. ([#13](https://github.com/ekassos/swift-book-pdf/pull/13))
- Add error reporting when a font (custom or default) does not support a typeset character based on the assigned font category. ([#13](https://github.com/ekassos/swift-book-pdf/pull/13))
- Add `--version` CLI option. ([#13](https://github.com/ekassos/swift-book-pdf/pull/13))
- Add Github issue template for font issue reporting. ([#14](https://github.com/ekassos/swift-book-pdf/pull/14))

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


[unreleased]: https://github.com/ekassos/swift-book-pdf/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/ekassos/swift-book-pdf/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/ekassos/swift-book-pdf/compare/v1.0...v1.0.1
[1.0.0]: https://github.com/ekassos/swift-book-pdf/releases/tag/v1.0
