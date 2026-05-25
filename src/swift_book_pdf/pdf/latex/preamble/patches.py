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

"""LaTeX runtime patches used by the generated preamble."""


def get_keep_whole_box_patch() -> str:
    """Return the LaTeX patch that keeps short breakable boxes intact.

    `tcolorbox`'s `breakable` mode decides whether to split a box based on the
    *remaining* space on the current page. That is usually correct for long
    prose boxes, but it produces awkward output for highlighted content near
    the bottom of a page: a box that would fit perfectly on the next page is
    still split immediately because the current page does not have enough room.

    The Swift book looks better when styled code examples and aside notes
    follow a stricter rule: if a box fits on a fresh page, move the entire box
    to the next page; only boxes that are genuinely taller than a page should
    be split. There is no public `tcolorbox` option for that exact behavior, so
    we patch the internal split-start routine and guard the behavior behind a
    dedicated option, `whole on next page if possible`.

    The option defaults to false so the patch does not affect other breakable
    `tcolorbox` environments. `swiftstyledbox` and `asideNote` opt into it
    explicitly.
    """
    return r"""
\makeatletter
\newif\iftcb@wholeonnextpageifpossible
\tcbset{
  whole on next page if possible/.is if=tcb@wholeonnextpageifpossible,
  whole on next page if possible/.default=true,
  whole on next page if possible=false,
}

\def\tcb@split@start{%
  \tcb@breakat@init%
  \tcb@comp@h@page%
  \tcb@comp@h@total@standalone%
  \iftcb@wholeonnextpageifpossible%
    \ifdim\tcb@h@total>\tcb@h@page\relax%
      \ifdim\tcb@h@total<\dimexpr\vsize+\kvtcb@enlargepage@flex\relax%
        \tcb@split@pagebreak%
        \tcb@comp@h@page%
      \fi%
    \fi%
  \fi%
  \let\tcb@split@next=\relax%
  \tcb@check@for@final@box%
  \iftcb@final@box%
    \tcb@drawcolorbox@standalone%
  \else%
    \iftcb@break@allowed%
      \ifdim\dimexpr\tcb@h@page-\tcb@h@padding-\tcb@h@padtitle<\kvtcb@breakminlines\baselineskip\relax%
        \tcb@split@pagebreak%
        \tcb@comp@h@page%
        \tcb@check@for@final@box%
        \iftcb@final@box%
          \tcb@drawcolorbox@standalone%
        \else%
          \let\tcb@split@next=\tcb@split@first%
        \fi%
      \else%
        \let\tcb@split@next=\tcb@split@first%
      \fi%
    \else%
      \let\tcb@split@next=\tcb@split@first%
    \fi%
  \fi%
  \tcb@split@next%
}
\makeatother
"""
