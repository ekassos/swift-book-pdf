# Copyright 2026 Evangelos Kassos
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

"""Bundled package asset paths."""

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
"""Root directory for bundled package assets."""

SWIFT_LOGO_ASSETS_DIR = ASSETS_DIR / "swift-logo"
"""Directory containing shared Swift logo artwork."""

ICON_ASSETS_DIR = ASSETS_DIR / "icons"
"""Directory containing shared icon artwork."""

FONT_ASSETS_DIR = ASSETS_DIR / "fonts"
"""Directory containing shared font assets."""

IBM_PLEX_FONT_DIR = FONT_ASSETS_DIR / "ibm-plex"
"""Directory containing bundled IBM Plex fonts."""

EPUB_ASSETS_DIR = ASSETS_DIR / "epub"
"""Directory containing EPUB-specific bundled assets."""

EPUB_COVERS_DIR = EPUB_ASSETS_DIR / "covers"
"""Directory containing EPUB cover templates."""

EPUB_STATIC_DIR = EPUB_ASSETS_DIR / "static"
"""Directory containing EPUB CSS and other static files."""

NOTICES_DIR = ASSETS_DIR / "notices"
"""Directory containing bundled notice text."""
