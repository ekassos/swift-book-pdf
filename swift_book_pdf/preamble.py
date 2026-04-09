# Copyright 2025-2026 Evangelos Kassos
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

import logging
from string import Template

from swift_book_pdf.config import PDFConfig
from swift_book_pdf.typography import compute_font_sizes, compute_spacing

from .colors import get_document_colors
from .schema import PaperSize

logger = logging.getLogger(__name__)


def get_geometry_opts(paper_size: PaperSize, gutter: bool = True) -> str:
    return {
        PaperSize.A4: f"a4paper,{'inner=1.67in,outer=0.9in' if gutter else 'hmargin=1.285in'}",
        PaperSize.LETTER: f"letterpaper,{'inner=1.9in,outer=0.9in' if gutter else 'hmargin=1.4in'}",
        PaperSize.LEGAL: f"legalpaper,{'inner=1.9in,outer=0.9in' if gutter else 'hmargin=1.4in'}",
    }.get(
        paper_size,
        f"letterpaper,{'inner=1.9in,outer=0.9in' if gutter else 'hmargin=1.4in'}",
    )


def get_keep_whole_box_patch() -> str:
    r"""Return the LaTeX patch that keeps short breakable boxes intact.

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


def generate_preamble(config: PDFConfig) -> str:
    unicode_fallback = "\n".join(
        [
            f'      "{font}:mode=node;",'
            for font in config.font_config.unicode_font_list
        ],
    )
    colors = get_document_colors(
        config.doc_config.mode, config.doc_config.appearance
    )
    font_sizes = compute_font_sizes(config.doc_config.font_size)
    spacing = compute_spacing(config.doc_config.font_size)
    template_vars = {**font_sizes, **spacing}
    for key, value in sorted(font_sizes.items()):
        logger.debug(f"{key}: {value}pt")
    for key, value in sorted(spacing.items()):
        logger.debug(f"{key}: {value}")
    return PREAMBLE.substitute(
        background=colors.background,
        text=colors.text,
        header_background=colors.header_background,
        header_text=colors.header_text,
        hero_background=colors.hero_background,
        hero_text=colors.hero_text,
        link=colors.link,
        aside_background=colors.aside_background,
        aside_text=colors.aside_text,
        aside_border=colors.aside_border,
        table_border=colors.table_border,
        code_border=colors.code_border,
        code_background=colors.code_background,
        code_style=colors.code_style,
        geometry_opts=get_geometry_opts(
            config.doc_config.paper_size,
            config.doc_config.gutter,
        ),
        main_font=config.font_config.main_font,
        mono_font=config.font_config.mono_font,
        emoji_font=config.font_config.emoji_font,
        unicode_font=unicode_fallback,
        header_footer_font=config.font_config.header_footer_font,
        keep_whole_box_patch=get_keep_whole_box_patch(),
        fancyhead_fancyfoot_hero=(
            HEADER_FOOTER_HERO_WITH_GUTTER.substitute(
                header_footer_font=config.font_config.header_footer_font,
                **template_vars,
            )
            if config.doc_config.gutter
            else HEADER_FOOTER_HERO_NO_GUTTER.substitute(
                header_footer_font=config.font_config.header_footer_font,
                **template_vars,
            )
        ),
        **template_vars,
    )


HEADER_FOOTER_HERO_WITH_GUTTER = Template(r"""
\fancyhead[HO]{%
\global\AtPageToptrue%
\begin{tikzpicture}[remember picture, overlay]
  \fill[header_background] ([yshift=-0.5in]current page.north west)
  rectangle ([yshift=-0.9in]current page.north east);

  \node[anchor=east] at ([yshift=-0.7in,xshift=-0.7in]current page.north east) {
    \includegraphics[height=0.18in]{Swift_logo_color.png}
  };

  \node[anchor=east,white] at ([yshift=-0.70in,xshift=-0.95in]current page.north east) {
    \scalebox{1.10}[1]{\headerFontWithFallback{$header_footer_font}{LetterSpace=-3.5} \fontsize{13pt}{0pt}\selectfont \customheader}
  };
\end{tikzpicture}%
}

\fancyhead[HE]{%
\global\AtPageToptrue%
\begin{tikzpicture}[remember picture, overlay]
\fill[header_background] ([yshift=-0.5in]current page.north west)
 rectangle ([yshift=-0.9in]current page.north east);

\node[anchor=west] at ([yshift=-0.7in,xshift=0.7in]current page.north west) {
  \includegraphics[height=0.18in]{Swift_logo_color.png}
};

\node[anchor=west,white] at ([yshift=-0.71in,xshift=0.95in]current page.north west) {
  \scalebox{1.10}[1]{\headerFontWithFallback{$header_footer_font}{LetterSpace=-3.5} \fontsize{13pt}{0pt}\selectfont The Swift Programming Language}
};
\end{tikzpicture}%
}

\fancyfoot[FO]{%
\begin{tikzpicture}[remember picture, overlay]
\fill[header_background] ([yshift=0.5in]current page.south west)
 rectangle ([yshift=0.9in]current page.south east);

\node[anchor=east] at ([yshift=0.7in,xshift=-0.7in]current page.south east) {
  \includegraphics[height=0.18in]{Swift_logo_white.png}
};

\node[anchor=east,white] at ([yshift=0.7in,xshift=-1in]current page.south east) {
  \headerFontWithFallback{$header_footer_font}{} \fontsize{13pt}{0pt}\selectfont \thepage
};
\end{tikzpicture}%
}

\fancyfoot[FE]{%
\begin{tikzpicture}[remember picture, overlay]
\fill[header_background] ([yshift=0.5in]current page.south west)
 rectangle ([yshift=0.9in]current page.south east);

\node[anchor=west] at ([yshift=0.7in,xshift=0.7in]current page.south west) {
  \includegraphics[height=0.18in]{Swift_logo_white.png}
};

\node[anchor=west,white] at ([yshift=0.7in,xshift=1in]current page.south west) {
  \headerFontWithFallback{$header_footer_font}{} \fontsize{13pt}{0pt}\selectfont \thepage
};
\end{tikzpicture}%
}

\fancypagestyle{firstpagestyle}{
  \fancyhf{}
  \fancyfoot[FO]{%
  \begin{tikzpicture}[remember picture, overlay]
  \fill[header_background] ([yshift=0.5in]current page.south west)
   rectangle ([yshift=0.9in]current page.south east);

  \node[anchor=east] at ([yshift=0.7in,xshift=-0.7in]current page.south east) {
    \includegraphics[height=0.18in]{Swift_logo_white.png}
  };

  \node[anchor=east,white] at ([yshift=0.7in,xshift=-1in]current page.south east) {
    \headerFontWithFallback{$header_footer_font}{} \fontsize{13pt}{0pt}\selectfont \thepage
  };
  \end{tikzpicture}%
  }

  \fancyfoot[FE]{%
  \begin{tikzpicture}[remember picture, overlay]
  \fill[header_background] ([yshift=0.5in]current page.south west)
   rectangle ([yshift=0.9in]current page.south east);

  \node[anchor=west] at ([yshift=0.7in,xshift=0.7in]current page.south west) {
    \includegraphics[height=0.18in]{Swift_logo_white.png}
  };

  \node[anchor=west,white] at ([yshift=0.7in,xshift=1in]current page.south west) {
    \headerFontWithFallback{$header_footer_font}{} \fontsize{13pt}{0pt}\selectfont \thepage
  };
  \end{tikzpicture}%
  }
}

\newcommand{\HeroBox}[3]{%
  \checkoddpage
  \ifoddpage
    % -- Odd page
    \hspace*{-2in}
    \fcolorbox{hero_background}{hero_background}{%
      \begin{minipage}{\dimexpr\textwidth+2.3in\relax}
        \hspace{1.9in}
        \begin{minipage}[t]{0.7\textwidth}
          \color{hero_text}
          \vspace*{${spacing_hero_top}}
          \TitleSection{#1}{#2}  % Title
          {\SubtitleStyle #3\par}  % Subtitle
          \vspace*{${spacing_hero_bottom}}
        \end{minipage}%
      \end{minipage}
    }
  \else
    % -- Even page
    \hspace*{-0.53in}
    \fcolorbox{hero_background}{hero_background}{%
      \begin{minipage}{\dimexpr\textwidth+2.3in\relax}
        \color{hero_text}
        \hspace{0.4in}
        \begin{minipage}[t]{0.7\textwidth}
          \vspace*{${spacing_hero_top}}
          \TitleSection{#1}{#2}  % Title
          {\SubtitleStyle #3\par}  % Subtitle
          \vspace*{${spacing_hero_bottom}}
        \end{minipage}%
      \end{minipage}
    }
  \fi
}
""")

HEADER_FOOTER_HERO_NO_GUTTER = Template(r"""
\fancyhead{%
\global\AtPageToptrue%
\begin{tikzpicture}[remember picture, overlay]
  \fill[header_background] ([yshift=-0.5in]current page.north west)
  rectangle ([yshift=-0.9in]current page.north east);

  \node[anchor=east] at ([yshift=-0.7in,xshift=-0.7in]current page.north east) {
    \includegraphics[height=0.18in]{Swift_logo_color.png}
  };

  \node[anchor=east,white] at ([yshift=-0.70in,xshift=-0.95in]current page.north east) {
    \scalebox{1.10}[1]{\headerFontWithFallback{$header_footer_font}{LetterSpace=-3.5} \fontsize{13pt}{0pt}\selectfont \customheader}
  };
\end{tikzpicture}%
}

\fancyfoot{%
\begin{tikzpicture}[remember picture, overlay]
\fill[header_background] ([yshift=0.5in]current page.south west)
 rectangle ([yshift=0.9in]current page.south east);

\node[anchor=east] at ([yshift=0.7in,xshift=-0.7in]current page.south east) {
  \includegraphics[height=0.18in]{Swift_logo_white.png}
};

\node[anchor=east,white] at ([yshift=0.7in,xshift=-1in]current page.south east) {
  \headerFontWithFallback{$header_footer_font}{} \fontsize{13pt}{0pt}\selectfont \thepage
};
\end{tikzpicture}%
}

\fancypagestyle{firstpagestyle}{
  \fancyhf{}
  \fancyfoot{%
  \begin{tikzpicture}[remember picture, overlay]
  \fill[header_background] ([yshift=0.5in]current page.south west)
   rectangle ([yshift=0.9in]current page.south east);

  \node[anchor=east] at ([yshift=0.7in,xshift=-0.7in]current page.south east) {
    \includegraphics[height=0.18in]{Swift_logo_white.png}
  };

  \node[anchor=east,white] at ([yshift=0.7in,xshift=-1in]current page.south east) {
    \headerFontWithFallback{$header_footer_font}{} \fontsize{13pt}{0pt}\selectfont \thepage
  };
  \end{tikzpicture}%
  }
}

\newcommand{\HeroBox}[3]{%
  \hspace*{-2in}
  \fcolorbox{hero_background}{hero_background}{%
    \begin{minipage}{\dimexpr\textwidth+2.3in\relax}
      \hspace{1.9in}
      \begin{minipage}[t]{0.7\textwidth}
        \color{hero_text}
        \vspace*{${spacing_hero_top}}
        \TitleSection{#1}{#2}  % Title
        {\SubtitleStyle #3\par}  % Subtitle
        \vspace*{${spacing_hero_bottom}}
      \end{minipage}%
    \end{minipage}
  }
}
""")

PREAMBLE = Template(r"""
% main.tex
\documentclass[twoside]{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{fancyhdr}
\usepackage[$geometry_opts,top=1.2in,headheight=0.8in,headsep=0.3in,bottom=1.2in]{geometry}
\usepackage{adjustbox}
\usepackage{ifoddpage}
\usepackage{enumitem}
\usepackage{listings}
\usepackage{minted}
\usepackage[most]{tcolorbox}
\usepackage{tikz}
\usepackage{needspace}
\usepackage{textcomp}
\usepackage{hyperref}
\usepackage{parskip}
\usepackage{tabulary}
\usepackage{ragged2e}
\usepackage[table]{xcolor}
\usepackage[hang,flushmargin,bottom,perpage,ragged]{footmisc}
\usepackage{lua-ul}

% ----------------------------------------
% Define custom colors
% ----------------------------------------
\definecolor{background}{RGB}{$background}
\definecolor{text}{RGB}{$text}
\definecolor{header_background}{RGB}{$header_background}
\definecolor{header_text}{RGB}{$header_text}
\definecolor{hero_background}{RGB}{$hero_background}
\definecolor{hero_text}{RGB}{$hero_text}
\definecolor{link}{RGB}{$link}
\definecolor{aside_background}{RGB}{$aside_background}
\definecolor{aside_text}{RGB}{$aside_text}
\definecolor{aside_border}{RGB}{$aside_border}
\definecolor{table_border}{RGB}{$table_border}
\definecolor{code_border}{RGB}{$code_border}
\definecolor{code_background}{RGB}{$code_background}

\pagecolor{background}
\color{text}
% ----------------------------------------
% Define fonts and small helpers
% ----------------------------------------
\setlength\parindent{0pt}
\setcounter{secnumdepth}{4}

\directlua{luaotfload.add_fallback
   ("monoFallback",
    {
      "$main_font:mode=node;",
      $unicode_font
      "$emoji_font:mode=harf;",
      "$header_footer_font:mode=node;"
    }
   )
}

\directlua{luaotfload.add_fallback
   ("mainFontFallback",
    {
      $unicode_font
      "$emoji_font:mode=harf;",
      "$header_footer_font:mode=node;",
      "$mono_font:mode=node;"
    }
   )
}

\directlua{luaotfload.add_fallback
   ("headerFallback",
    {
      "$main_font:mode=node;",
      $unicode_font
      "$emoji_font:mode=harf;",
      "$mono_font:mode=node;"
    }
   )
}

\newcommand{\mainFontWithFallback}[1]{%
 \fontspec{#1}[RawFeature={fallback=mainFontFallback}]%
}

\newcommand{\monoFontWithFallback}[1]{%
  \fontspec{#1}[RawFeature={fallback=monoFallback}]%
}

\newcommand{\headerFontWithFallback}[2]{%
  \fontspec{#1}[RawFeature={fallback=headerFallback},#2]\color{header_text}%
}

\renewcommand{\footnotesize}{\monoFontWithFallback{$mono_font}\fontsize{${font_size_footnote}pt}{${font_size_footnote}pt}\selectfont}
\setlength{\footnotesep}{${spacing_footnotesep}}
\makeatletter
\renewcommand{\@makefnmark}{\mainFontWithFallback{$main_font}\selectfont\textsuperscript\@thefnmark}
\renewcommand{\@makefntext}[1]{%
  \@hangfrom{\hbox{\@makefnmark\ }}#1%
}
\makeatother
\renewcommand{\thempfootnote}{\arabic{mpfootnote}}

\newcommand{\TitleStyle}{%
  \mainFontWithFallback{$main_font}\fontsize{${font_size_title}pt}{${spacing_baselineskip_title}}\selectfont
}

\newcommand{\SubtitleStyle}{%
\global\precededbyboxfalse\mainFontWithFallback{$main_font}\fontsize{${font_size_subtitle}pt}{${spacing_baselineskip_subtitle}}\selectfont
}

\newcommand{\BodyStyle}{%
\mainFontWithFallback{$main_font}\fontsize{${font_size_body}pt}{${spacing_baselineskip_body}}\selectfont\setlength{\parskip}{${spacing_parskip}}\raggedright
}

\newcommand{\ParagraphStyle}[1]{%
\ifprecededbybox\vspace{${spacing_para_after_box}}\fi%
\ifprecededbysection\vspace{-${spacing_section_adjust}}\fi%
\ifprecededbynote\vspace{${spacing_para_after_box}}\fi%
\global\precededbyboxfalse%
\global\precededbysectionfalse%
\global\precededbyparagraphtrue%
\global\precededbynotefalse%
\global\AtPageTopfalse%
\setlength{\parskip}{${spacing_parskip}}%
\begin{flushleft}%
#1%
\end{flushleft}%
}

\makeatletter
\def\section{\@startsection{section}{1}{0pt}%
   {${spacing_section_before}}
   {${spacing_section_after}}
   {\mainFontWithFallback{$main_font}\fontsize{${font_size_section}pt}{${spacing_baselineskip_section}}\selectfont\global\AtPageTopfalse}}
\makeatother

\newcommand{\TitleSection}[2]{%
  {%
    \pdfbookmark[1]{#1}{#2}\section*{#1}\label{#2}\par
  }%
}

\makeatletter
\def\subsection{\@startsection{subsection}{2}{0pt}%
   {\ifprecededbyparagraph ${spacing_subsection_before_para} \else ${spacing_subsection_before} \fi}
   {${spacing_heading_after}}
   {\mainFontWithFallback{$main_font}\fontsize{${font_size_subsection}pt}{${spacing_baselineskip_subsection}}\selectfont\global\precededbysectiontrue\global\precededbyparagraphfalse\global\precededbyboxfalse\global\precededbynotefalse\global\AtPageTopfalse}}
\makeatother

\newcommand{\SectionHeader}[2]{%
  {%
    \setlength{\parskip}{0pt}
    \ifprecededbyparagraph\vspace*{-${spacing_section_adjust}}\fi
    \pdfbookmark[2]{#1}{#2}\subsection*{#1}\label{#2}
    \vspace*{-${spacing_section_adjust}}
  }%
}

\newcommand{\SectionHeaderTOC}[2]{%
  {%
    \setlength{\parskip}{0pt}
    \pdfbookmark[2]{#1}{#2}\subsection*{#1}\label{#2}
    \vspace*{${spacing_toc_section_after}}
  }%
}

\makeatletter
\def\subsubsection{\@startsection{subsubsection}{3}{0pt}%
   {\ifAtPageTop \ifintoc 0in \else \ifprecededbyparagraph ${spacing_subsubsection_before_para} \else ${spacing_subsubsection_before} \fi \fi \else \ifprecededbyparagraph ${spacing_subsubsection_before_para} \else ${spacing_subsubsection_before} \fi \fi}
   {${spacing_heading_after}}
   {\mainFontWithFallback{$main_font}\fontsize{${font_size_subsubsection}pt}{${spacing_baselineskip_subsubsection}}\selectfont\global\precededbysectiontrue\global\precededbyparagraphfalse\global\precededbyboxfalse\global\precededbynotefalse\global\AtPageTopfalse}}
\makeatother

\newcommand{\SubsectionHeader}[2]{%
  {%
    \setlength{\parskip}{0pt}
    \ifprecededbyparagraph\vspace*{-${spacing_section_adjust}}\fi
    \pdfbookmark[3]{#1}{#2}\subsubsection*{#1}\label{#2}
    \vspace*{-${spacing_section_adjust}}
  }%
}

\newcommand{\SubsectionHeaderTOC}[2]{%
  {%
    \needspace{5\baselineskip}%
    \checkTopOfPage
    \intoctrue
    \setlength{\parskip}{0pt}
    \nopagebreak
    \vspace*{-${spacing_toc_adjust}}
    \nopagebreak
    \pdfbookmark[3]{#1}{#2}\subsubsection*{#1}\label{#2}
    \nopagebreak
    \vspace*{-${spacing_toc_adjust}}
    \nopagebreak
    \intocfalse
  }%
}

\makeatletter
\def\paragraph{\@startsection{paragraph}{4}{0pt}%
   {\ifprecededbyparagraph ${spacing_paragraph_before_para} \else ${spacing_paragraph_before} \fi}
   {${spacing_heading_after}}
   {\bfseries\mainFontWithFallback{$main_font}\fontsize{${font_size_paragraph}pt}{${spacing_baselineskip_paragraph}}\selectfont\global\precededbysectiontrue\global\precededbyparagraphfalse\global\precededbyboxfalse\global\precededbynotefalse\global\AtPageTopfalse}}
\makeatother

\newcommand{\SubsubsectionHeader}[2]{%
  {%
    \setlength{\parskip}{0pt}
    \ifprecededbyparagraph\vspace*{-${spacing_section_adjust}}\fi
    \pdfbookmark[4]{#1}{#2}\paragraph*{#1}\label{#2}
    \vspace*{-${spacing_section_adjust}}
  }%
}

\newcommand{\CodeStyle}{%
  \monoFontWithFallback{$mono_font}\fontsize{${font_size_code}pt}{${spacing_baselineskip_code}}\selectfont
  \setlength{\parskip}{${spacing_code_parskip}}\raggedright
}
\setmonofont{$mono_font}[RawFeature={fallback=monoFallback}, Scale=1]

% ----------------------------------------
% Define custom property for padding
% ----------------------------------------
\newif\ifprecededbybox
\precededbyboxfalse

\newif\ifprecededbynote
\precededbynotefalse

\newif\ifprecededbysection
\precededbysectionfalse

\newif\ifprecededbyparagraph
\precededbyparagraphfalse

\newif\ifinitemize
\initemizefalse

\newif\ifintoc
\intocfalse

% ----------------------------------------
% Define custom property for top of page
% ----------------------------------------

\makeatletter
\newif\ifAtTopOfPage

\newcommand{\checkTopOfPage}{%
  \ifdim\pagetotal=0pt
    \AtTopOfPagetrue
  \else
    \AtTopOfPagefalse
  \fi
}
\makeatother

\newif\ifAtPageTop
\AtPageToptrue % initialize the flag

\makeatletter
\newcommand{\debugline}[1]{%
  \message{[DEBUG] \jobname.tex:\the\inputlineno: #1}%
}
\makeatother

% ----------------------------------------
% Define list properties
% ----------------------------------------
\setlist[itemize]{
  left=0pt,
  labelsep=0.5em,
  itemsep=${spacing_list_itemsep},
  topsep=0.0em,
  partopsep=0.0em
}

\setlist[enumerate]{
  left=0pt,
  labelsep=0.5em,
  itemsep=${spacing_list_itemsep},
  topsep=0.0em,
  partopsep=0.0em
}

% ----------------------------------------
% Define custom Swift style for code
% ----------------------------------------
\tcbuselibrary{minted}
\tcbset{listing engine=minted}
$keep_whole_box_patch
\newcommand{\customsmall}{\fontsize{${font_size_minted}pt}{${font_size_minted_leading}pt}\selectfont}
\newtcblisting{swiftstyledbox}{
  listing only,
  breakable,
  whole on next page if possible,
  minted language=swift,
  minted options={
    fontsize=\customsmall,
    style=$code_style,
    breaklines=true,
    autogobble=true,
    breakautoindent=false,
    tabsize=2,
    frame=none,
    framesep=0pt,
    escapeinside=||,
  },
  colback=code_background,
  colframe=code_border,
  boxrule=0.5pt,
  arc=4pt,
  top=${spacing_code_box_tb}, bottom=${spacing_code_box_tb},
  left=${spacing_code_box_lr}, right=${spacing_code_box_lr},
  boxsep=0pt,
  before skip={\dimexpr\ifprecededbybox${spacing_box_before_preceded}\else${spacing_box_before}\fi},
  after skip=0in,
  before lower=\color{text},
  after app={\global\precededbyboxtrue\global\precededbysectionfalse\global\precededbyparagraphfalse\global\precededbynotefalse\global\AtPageTopfalse},
}

\newtcblisting{plainlistingbox}{
  listing engine=listings,
  listing only,
  breakable,
  whole on next page if possible,
  listing options={
    basicstyle=\monoFontWithFallback{$mono_font}\fontsize{${font_size_minted}pt}{${font_size_minted_leading}pt}\selectfont,
    breaklines=true,
    breakatwhitespace=false,
    columns=fullflexible,
    keepspaces=true,
    showstringspaces=false,
  },
  colback=code_background,
  colframe=code_border,
  boxrule=0.5pt,
  arc=4pt,
  top=${spacing_code_box_tb}, bottom=${spacing_code_box_tb},
  left=${spacing_code_box_lr}, right=${spacing_code_box_lr},
  boxsep=0pt,
  before skip={\dimexpr\ifprecededbybox${spacing_box_before_preceded}\else${spacing_box_before}\fi},
  after skip=0in,
  before upper=\color{text},
  after app={\global\precededbyboxtrue\global\precededbysectionfalse\global\precededbyparagraphfalse\global\precededbynotefalse\global\AtPageTopfalse},
}

% ----------------------------------------
% Define custom note style
% ----------------------------------------
\newtcolorbox{asideNote}{%
  enhanced,
  breakable,
  whole on next page if possible,
  colback=aside_background,
  arc=4pt,
  borderline west={3pt}{0pt}{aside_border},
  boxrule=0pt,
  frame empty,
  before skip={\dimexpr\ifprecededbybox${spacing_box_before_preceded}\else${spacing_box_before}\fi},
  after skip=0in,
  after app={\global\precededbyboxfalse\global\precededbysectionfalse\global\precededbyparagraphfalse\global\precededbynotetrue\global\AtPageTopfalse},
  left=${spacing_aside_left}, right=${spacing_aside_pad}, top=${spacing_aside_pad}, bottom=${spacing_aside_pad},
  before upper={\raggedright\color{aside_text}},
}


\hypersetup{
  colorlinks=true,    % Make links colored
  linkcolor=link,     % Color of internal links
  urlcolor=link,      % Color for URLs
  pdfstartview=FitH,   % Ensure the view fits horizontally on page
  bookmarksdepth=4
}

% ----------------------------------------
% Define header and footer
% ----------------------------------------
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\newcommand{\customheader}{ } % Default header text

$fancyhead_fancyfoot_hero

\raggedbottom

\newcommand{\fallbackrefbook}[1]{%
  \ifcsname r@#1\endcsname
    \underLine[top=-1.5pt]{\nameref{#1} (p.\,\pageref{#1})}%
  \else
    \underLine[top=-1.5pt]{[Reference not found]}%
  \fi
}

\newcommand{\fallbackrefdigital}[1]{%
  \ifcsname r@#1\endcsname
    \nameref{#1}%
  \else
    [Reference not found]%
  \fi
}


% ----------------------------------------
% Main Document
% ----------------------------------------
\begin{document}
""")
