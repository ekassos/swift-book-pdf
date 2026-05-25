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

from dataclasses import dataclass


@dataclass(frozen=True)
class FontOverrides:
    """User-provided PDF font overrides."""

    main_font: str | None = None
    mono_font: str | None = None
    emoji_font: str | None = None
    unicode_fonts: tuple[str, ...] = ()
    header_footer_font: str | None = None


@dataclass(frozen=True)
class FontConfig:
    """Resolved engine-agnostic PDF font names."""

    main_font: str
    mono_font: str
    emoji_font: str
    unicode_font_list: tuple[str, ...]
    header_footer_font: str

    def __str__(self) -> str:
        return (
            "Your font configuration:\n"
            f"Main font: {self.main_font}\n"
            f"Monospace font: {self.mono_font}\n"
            f"Emoji font: {self.emoji_font}\n"
            f"Unicode font(s): {', '.join(self.unicode_font_list)}\n"
            f"Header/Footer font: {self.header_footer_font}\n"
        )
