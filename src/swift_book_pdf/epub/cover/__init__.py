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

from .svg import (
    CoverPageOptions,
    CoverTextSpan,
    SVGTextStyle,
    render_cover_page,
    render_cover_text,
)
from .variants import (
    COVER_VARIANTS,
    CoverVariant,
    cover_png_version_fill,
    cover_png_version_text,
    cover_template_path,
    cover_version_label,
    resolve_cover_banner,
    resolve_cover_variant,
    resolve_cover_variant_name,
)

__all__ = [
    "COVER_VARIANTS",
    "CoverPageOptions",
    "CoverTextSpan",
    "CoverVariant",
    "SVGTextStyle",
    "cover_png_version_fill",
    "cover_png_version_text",
    "cover_template_path",
    "cover_version_label",
    "render_cover_page",
    "render_cover_text",
    "resolve_cover_banner",
    "resolve_cover_variant",
    "resolve_cover_variant_name",
]
