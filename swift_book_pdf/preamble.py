# Copyright 2025 Evangelos Kassos
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

from swift_book_pdf.config import Config
from .schema import PaperSize
from string import Template
from .colors import get_document_colors


def get_geometry_opts(paper_size: PaperSize, gutter: bool = True) -> str:
    return {
        PaperSize.A4: f"a4paper,{'inner=1.67in,outer=0.9in' if gutter else 'hmargin=1.285in'}",
        PaperSize.LETTER: f"letterpaper,{'inner=1.9in,outer=0.9in' if gutter else 'hmargin=1.4in'}",
        PaperSize.LEGAL: f"legalpaper,{'inner=1.9in,outer=0.9in' if gutter else 'hmargin=1.4in'}",
    }.get(
        paper_size,
        f"letterpaper,{'inner=1.9in,outer=0.9in' if gutter else 'hmargin=1.4in'}",
    )


def generate_preamble(config: Config) -> str:
    unicode_fallback = "\n".join(
        [f'      "{font}:mode=node;",' for font in config.font_config.unicode_font_list]
    )
    colors = get_document_colors(config.doc_config.mode, config.doc_config.appearance)
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
            config.doc_config.paper_size, config.doc_config.gutter
        ),
        main_font=config.font_config.main_font,
        mono_font=config.font_config.mono_font,
        emoji_font=config.font_config.emoji_font,
        unicode_font=unicode_fallback,
        header_footer_font=config.font_config.header_footer_font,
        fancyhead_fancyfoot_hero=(
            HEADER_FOOTER_HERO_WITH_GUTTER.substitute(
                header_footer_font=config.font_config.header_footer_font,
            )
            if config.doc_config.gutter
            else HEADER_FOOTER_HERO_NO_GUTTER.substitute(
                header_footer_font=config.font_config.header_footer_font,
            )
        ),
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
          \vspace*{0.4in}
          \TitleSection{#1}{#2}  % Title
          {\SubtitleStyle #3\par}  % Subtitle
          \vspace*{0.28in}
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
          \vspace*{0.4in}
          \TitleSection{#1}{#2}  % Title
          {\SubtitleStyle #3\par}  % Subtitle
          \vspace*{0.28in}
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
        \vspace*{0.4in}
        \TitleSection{#1}{#2}  % Title
        {\SubtitleStyle #3\par}  % Subtitle
        \vspace*{0.28in}
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

\renewcommand{\footnotesize}{\monoFontWithFallback{$mono_font}\fontsize{8pt}{8pt}\selectfont}
\setlength{\footnotesep}{9pt}
\makeatletter
\renewcommand{\@makefnmark}{\mainFontWithFallback{$main_font}\selectfont\textsuperscript\@thefnmark}
\renewcommand{\@makefntext}[1]{%
  \@hangfrom{\hbox{\@makefnmark\ }}#1%
}
\makeatother
\renewcommand{\thempfootnote}{\arabic{mpfootnote}}

\newcommand{\TitleStyle}{%
  \mainFontWithFallback{$main_font}\fontsize{22pt}{1.2\baselineskip}\selectfont
}

\newcommand{\SubtitleStyle}{%
\global\precededbyboxfalse\mainFontWithFallback{$main_font}\fontsize{11.07pt}{1.2\baselineskip}\selectfont
}

\newcommand{\BodyStyle}{%
\mainFontWithFallback{$main_font}\fontsize{9pt}{1.15\baselineskip}\selectfont\setlength{\parskip}{0.09in}\raggedright
}

\newcommand{\ParagraphStyle}[1]{%
\ifprecededbybox\vspace{0.12in}\fi%
\ifprecededbysection\vspace{-0.09in}\fi%
\ifprecededbynote\vspace{0.12in}\fi%
\global\precededbyboxfalse%
\global\precededbysectionfalse%
\global\precededbyparagraphtrue%
\global\precededbynotefalse%
\global\AtPageTopfalse%
\setlength{\parskip}{0.09in}%
\begin{flushleft}%
#1%
\end{flushleft}%
}

\makeatletter
\def\section{\@startsection{section}{1}{0pt}%
   {0.4in}
   {0.1in}
   {\mainFontWithFallback{$main_font}\fontsize{22pt}{1.5\baselineskip}\selectfont\global\AtPageTopfalse}}
\makeatother

\newcommand{\TitleSection}[2]{%
  {%
    \pdfbookmark[1]{#1}{#2}\section*{#1}\label{#2}\par
  }%
}

\makeatletter
\def\subsection{\@startsection{subsection}{2}{0pt}%
   {\ifprecededbyparagraph 0.44in \else 0.41in \fi}
   {0.16in}
   {\mainFontWithFallback{$main_font}\fontsize{16.88pt}{1.5\baselineskip}\selectfont\global\precededbysectiontrue\global\precededbyparagraphfalse\global\precededbyboxfalse\global\precededbynotefalse\global\AtPageTopfalse}}
\makeatother

\newcommand{\SectionHeader}[2]{%
  {%
    \setlength{\parskip}{0pt}
    \ifprecededbyparagraph\vspace*{-0.09in}\fi
    \pdfbookmark[2]{#1}{#2}\subsection*{#1}\label{#2}
    \vspace*{-0.09in}
  }%
}

\newcommand{\SectionHeaderTOC}[2]{%
  {%
    \setlength{\parskip}{0pt}
    \pdfbookmark[2]{#1}{#2}\subsection*{#1}\label{#2}
    \vspace*{0.20in}
  }%
}

\makeatletter
\def\subsubsection{\@startsection{subsubsection}{3}{0pt}%
   {\ifAtPageTop \ifintoc 0in \else \ifprecededbyparagraph 0.37in \else 0.35in \fi \fi \else \ifprecededbyparagraph 0.37in \else 0.35in \fi \fi}
   {0.16in}
   {\mainFontWithFallback{$main_font}\fontsize{14.77pt}{1.5\baselineskip}\selectfont\global\precededbysectiontrue\global\precededbyparagraphfalse\global\precededbyboxfalse\global\precededbynotefalse\global\AtPageTopfalse}}
\makeatother

\newcommand{\SubsectionHeader}[2]{%
  {%
    \setlength{\parskip}{0pt}
    \ifprecededbyparagraph\vspace*{-0.09in}\fi
    \pdfbookmark[3]{#1}{#2}\subsubsection*{#1}\label{#2}
    \vspace*{-0.09in}
  }%
}

\newcommand{\SubsectionHeaderTOC}[2]{%
  {%
    \needspace{5\baselineskip}%
    \checkTopOfPage
    \intoctrue
    \setlength{\parskip}{0pt}
    \nopagebreak
    \vspace*{-0.15in}
    \nopagebreak
    \pdfbookmark[3]{#1}{#2}\subsubsection*{#1}\label{#2}
    \nopagebreak
    \vspace*{-0.15in}
    \nopagebreak
    \intocfalse
  }%
}

\makeatletter
\def\paragraph{\@startsection{paragraph}{4}{0pt}%
   {\ifprecededbyparagraph 0.34in \else 0.32in \fi}
   {0.16in}
   {\bfseries\mainFontWithFallback{$main_font}\fontsize{12.66}{1.5\baselineskip}\selectfont\global\precededbysectiontrue\global\precededbyparagraphfalse\global\precededbyboxfalse\global\precededbynotefalse\global\AtPageTopfalse}}
\makeatother

\newcommand{\SubsubsectionHeader}[2]{%
  {%
    \setlength{\parskip}{0pt}
    \ifprecededbyparagraph\vspace*{-0.09in}\fi
    \pdfbookmark[4]{#1}{#2}\paragraph*{#1}\label{#2}
    \vspace*{-0.09in}
  }%
}

\newcommand{\CodeStyle}{%
  \monoFontWithFallback{$mono_font}\fontsize{9pt}{1.1\baselineskip}\selectfont
  \setlength{\parskip}{7pt}\raggedright
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
  itemsep=0.02in,
  topsep=0.0em,
  partopsep=0.0em
}

\setlist[enumerate]{
  left=0pt,
  labelsep=0.5em,
  itemsep=0.02in,
  topsep=0.0em,
  partopsep=0.0em
}

% ----------------------------------------
% Define custom Swift style for code
% ----------------------------------------
\tcbuselibrary{minted}
\tcbset{listing engine=minted}
\newcommand{\customsmall}{\fontsize{7.9pt}{13.2pt}\selectfont}
\newtcblisting{swiftstyledbox}{
  listing only,
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
  top=0.05in, bottom=0.05in,
  left=0.10in, right=0.10in,
  boxsep=0pt,
  before skip={\dimexpr\ifprecededbybox0.19in\else0.21in\fi},
  after skip=0in,
  before lower=\color{text},
  after app={\global\precededbyboxtrue\global\precededbysectionfalse\global\precededbyparagraphfalse\global\precededbynotefalse\global\AtPageTopfalse},
}

% ----------------------------------------
% Define custom note style
% ----------------------------------------
\newtcolorbox{asideNote}{%
  enhanced,
  colback=aside_background,
  arc=4pt,
  borderline west={3pt}{0pt}{aside_border},
  boxrule=0pt,
  frame empty,
  before skip={\dimexpr\ifprecededbybox0.19in\else0.21in\fi},
  after skip=0in,
  after app={\global\precededbyboxfalse\global\precededbysectionfalse\global\precededbyparagraphfalse\global\precededbynotetrue\global\AtPageTopfalse},
  left=8.8pt, right=8pt, top=8pt, bottom=8pt,
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
