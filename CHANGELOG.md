# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.3.1] - 2026-04-04
### Fixed
- Fix an issue where `Summary of the Grammar` generation could fall out of sync with the latest upstream `swift-book` repo after the summary build logic moved from `bin/publish-book` to `bin/generate-grammar`.

## [2.3.0] - 2026-04-01
### Added
- Add new `--ibooks-version` option to `swift-book-epub` to write Apple Books version metadata as `<meta property="ibooks:version">…</meta>` in the generated OPF package document.
- Include the full text of the Apache License 2.0 (with Runtime Library Exception) in the EPUB notices page.
- Add automatic detection of the original `swift-book` copyright year range and include it in the generated EPUB notices page when available.
- Add a non-affiliation disclaimer to the generated EPUB notices page stating that the edition is not published by, endorsed by, or affiliated with Apple Inc. or the Swift.org open source project.

### Changed
- Expand the generated EPUB notices page to clarify derivative-work attribution for editions produced with _swift-book-pdf_, including original-work credit to Apple Inc. and the Swift project authors.

### Fixed
- Fix an issue where line numbers in code blocks were not scaling properly at larger font sizes in the generated EPUB file.

### Internal
- Update 2.2.0 release date to 2026-03-31 in CHANGELOG.md.

## [2.2.0] - 2026-03-31
### Added
- Add new `swift-book-epub` CLI command to convert the DocC source for _The Swift Programming Language_ book into an EPUB file. The generated EPUB file follows the rendering style used by Apple Books for [TSPL publications up to Swift 5.7](https://books.apple.com/us/book/the-swift-programming-language-swift-5-7/id881256329) and retains all internal references and external links.
- Add new `--export-cover-image` / `-e` flag to save the generated cover image as a separate PNG file in the output directory when generating an EPUB file.
- Add new `--cover-footer-line` option to include a custom line of text in the cover image footer when generating an EPUB file.
- Add new `--override-version` option to override the version number when generating an EPUB file. Include "beta" for beta versions. If not provided, the version will be determined by parsing the table of contents.
- Add new `--publisher` option to include publisher metadata in the generated EPUB file.
- Add new `--contributor` option to include contributor metadata in the generated EPUB file.
- Add `--source-ref` and `--source-sha` options to build from a specific `swift-book` tag, branch, ref, or commit without manually preparing a local checkout.

### Changed
- Update ordering of CLI options in help message for better discoverability.

### Internal
- Add `pillow` dependency for image processing during EPUB generation.
- Add `pytest` development dependency.
- Add initial tests for CLI commands and options.
- Add testing step in `python.yml` to run the CLI tests.
- Update `pygments` (`2.19.2` -> `2.20.0`) to resolve [Pygments has Regular Expression Denial of Service (ReDoS) due to Inefficient Regex for GUID Matching](https://github.com/ekassos/swift-book-pdf/security/dependabot/5).
- Update `uv` (`0.10.12` -> `0.11.2`).

## [2.1.0] - 2026-03-23
### Added
- Add `swift-book-pdf` CLI alias for `swift_book_pdf`.
- Add `latexminted` version check to ensure compatibility with `minted.sty` versions older than 3.8.0.
- Detect missing LaTeX packages before typesetting and surface clearer package-specific errors during PDF generation.
- Add `--font-size` option to scale the PDF typography from a custom base paragraph font size.
- Generate `SummaryOfTheGrammar` during PDF assembly when the upstream `swift-book` repo no longer ships the chapter as a committed Markdown file, using `bin/publish-book` metadata and `bin/extract_grammar.awk` with a built-in fallback.

### Changed
- Make code and aside boxes breakable to support larger font sizes, while keeping short boxes intact by moving them to the next page when possible and only splitting boxes that are longer than a page.
- Switch to `uv` for dependency management.
- Update dependencies:
  - Update `pygments` (`2.9.0` -> `2.19.2`)
  - Update `tqdm` (`4.67.1` -> `4.67.3`)
  - Update `pydantic` (`2.10.6` -> `2.12.5`)
  - Update `click` (`8.1.8` -> `8.3.1`)
  - Update `latexminted` (`0.5.0` -> `0.6.0` for Python < 3.14, `0.7.1` for Python >= 3.14)
  - Update `filelock` (`3.20.1` -> `3.25.2`)
  - Update `pre-commit` (`4.1.0` -> `4.5.1`)

### Fixed
- Fix an issue where a chapter may appear multiple times in the generated PDF when the Markdown file for the subsequent chapter is missing.
- Escape literal dollar signs in paragraph text so generated LaTeX does not enter math mode and fail on currency amounts like `$1.23`.
- Fix an issue where `Summary of the Grammar` could be missing from the generated PDF when upstream generates it only during publication.

## [2.0.1] - 2026-01-13
### Security
- Update `virtualenv` (`20.35.4` -> `20.36.1`) to resolve [virtualenv Has TOCTOU Vulnerabilities in Directory Creation](https://github.com/ekassos/swift-book-pdf/security/dependabot/2). ([#51](https://github.com/ekassos/swift-book-pdf/pull/51))
- Update `filelock` (`3.20.1` -> `3.20.3`) to resolve [filelock Time-of-Check-Time-of-Use (TOCTOU) Symlink Vulnerability in SoftFileLock](https://github.com/ekassos/swift-book-pdf/security/dependabot/52). ([#49](https://github.com/ekassos/swift-book-pdf/pull/52))

## [2.0.0] - 2025-12-30
### Removed
- Remove support for Python v3.9. Update minimum Python version requirement to 3.10.

### Security
- Update `filelock` (`3.19.1` -> `3.20.1`) to resolve [filelock has a TOCTOU race condition which allows symlink attacks during lock file creation](https://github.com/ekassos/swift-book-pdf/security/dependabot/1). ([#49](https://github.com/ekassos/swift-book-pdf/pull/49))

### Changed
- Update dependencies:
  - Update `pygments` (`2.19.1` -> `2.19.2`)
  - Update `pydantic` (`2.10.6` -> `2.12.5`)
  - Update `click` (`8.1.8` -> `8.3.1`)
  - Update `latexminted` (`0.5.0` -> `0.5.1`)
  - Update `pre-commit` (`4.1.0` -> `4.5.1`)
- Use `click`’s own `click.version_option` option for more intuitive versioning info. ([#38](https://github.com/ekassos/swift-book-pdf/pull/38))
- Remove direct instructions from README and redirects to Wiki guides for more detailed information, including the new Customization page. ([#41](https://github.com/ekassos/swift-book-pdf/pull/41))

### Added
- Add dark mode chapter icon acknowledgement to README. ([#42](https://github.com/ekassos/swift-book-pdf/pull/42))

### Fixed
- Fix anchors for removed sections in README. ([#43](https://github.com/ekassos/swift-book-pdf/pull/43))

## [1.4.1] - 2025-08-17

### Changed
- Use `shutil.move` instead of `os.replace` to support saving files in a different partition from the one the temporary directory gets created in. ([#47](https://github.com/ekassos/swift-book-pdf/pull/47))

## [1.4.0] - 2025-04-05

### Added
- Add new `--dark` flag to enable rendering in dark mode. ([#33](https://github.com/ekassos/swift-book-pdf/pull/33))
- Add new `--input-path`/`-i` option to use local copy of the swift-book repo. ([#34](https://github.com/ekassos/swift-book-pdf/pull/34))
- Add a new detection mechanism for the minted requiring shell escape by typesetting a simple document containing a minted box. ([#35](https://github.com/ekassos/swift-book-pdf/pull/35))
- Add new `--gutter/--no-gutter` option to control whether the typeset document has a book gutter and different layout for left/right pages. ([#36](https://github.com/ekassos/swift-book-pdf/pull/36))

### Fixed
- Fix an issue where some 2024 TeX Live installations may not be able to typeset TSPL because minted still requires the `-shell-escape` option. ([#35](https://github.com/ekassos/swift-book-pdf/pull/35))

### Internal
- Change regular expression used for detecting URLs in Markdown that may have caused exponential backtracking on strings starting with '[\](http://' and containing many repetitions of '!'. ([#32](https://github.com/ekassos/swift-book-pdf/pull/32))

## [1.3.0] - 2025-03-23

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


[unreleased]: https://github.com/ekassos/swift-book-pdf/compare/v2.3.1...HEAD
[2.3.1]: https://github.com/ekassos/swift-book-pdf/compare/v2.3.0...v2.3.1
[2.3.0]: https://github.com/ekassos/swift-book-pdf/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/ekassos/swift-book-pdf/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/ekassos/swift-book-pdf/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/ekassos/swift-book-pdf/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.4.1...v2.0.0
[1.4.1]: https://github.com/ekassos/swift-book-pdf/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ekassos/swift-book-pdf/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/ekassos/swift-book-pdf/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/ekassos/swift-book-pdf/compare/v1.0...v1.0.1
[1.0.0]: https://github.com/ekassos/swift-book-pdf/releases/tag/v1.0
