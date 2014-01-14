\ProvidesClass{numapde_preprint}% [2012/07/17]

% Declare all options, the corresponding code below then simply sets all variables to Y
\RequirePackage{ifthen}              % to define \ifthenelse, for conditional compilation
\newboolean{framedtheorems}
\setboolean{framedtheorems}{false}
\newboolean{framedproofs}
\setboolean{framedproofs}{false}

\newboolean{global_equation_numbers}
\setboolean{global_equation_numbers}{false}
\newboolean{global_theorem_numbers}
\setboolean{global_theorem_numbers}{false}
\newboolean{clean_pages}
\setboolean{clean_pages}{false}
\newboolean{language_defined}
\setboolean{language_defined}{false}

% Set up the options for the class.
\DeclareOption{german}{%
\long\def\langde#1{#1}
\long\def\langen#1{}
\setboolean{language_defined}{true}
\PassOptionsToPackage{\CurrentOption}{babel}%
}
\DeclareOption{ngerman}{%
\long\def\langde#1{#1}
\long\def\langen#1{}
\setboolean{language_defined}{true}
\PassOptionsToPackage{\CurrentOption}{babel}%
}
\DeclareOption{english}{%
\long\def\langde#1{}
\long\def\langen#1{#1}
\setboolean{language_defined}{true}
\PassOptionsToPackage{\CurrentOption}{babel}%
}
\newboolean{biber}
\setboolean{biber}{false}
\DeclareOption{biber}{
	\setboolean{biber}{true}
}

% Use theorems in colored frames
\DeclareOption{framed_theorems}{
	\setboolean{framedtheorems}{true}
}

% Use proofs in gray frames
\DeclareOption{framed_proofs}{
	\PassOptionsToPackage{proof}{framed_theorems}
	\setboolean{framedproofs}{true}
}

% Use global numbering of equations
\DeclareOption{global_equation_numbers}{
	\setboolean{global_equation_numbers}{true}
}

% Use global numbering of theorems
\DeclareOption{global_theorem_numbers}{
	\setboolean{global_theorem_numbers}{true}
}

% Produce _very_ clean pages (no numbers, headlines)
\DeclareOption{clean_pages}{
	\setboolean{clean_pages}{true}
}

% Pass other options to the base class scrartcl
\DeclareOption*{%
\PassOptionsToClass{\CurrentOption}{scrartcl}%
}
\ProcessOptions\relax

% Load bass class scrartcl
\LoadClass{scrartcl}

% Make english the default language
\ifthenelse{\boolean{language_defined}}%
{}%
{
	\long\def\langde#1{}
	\long\def\langen#1{#1}
	\PassOptionsToPackage{english}{babel}
}

\RequirePackage[utf8]{inputenx}      % for German umlauts
\RequirePackage[T1]{fontenc}         % to enable correct hyphenation of words with umlauts
\RequirePackage{babel}
\RequirePackage{amsmath}
\RequirePackage{amsfonts}            % to get \mathbb alphabet
\RequirePackage{amssymb}             % for AMS symbols
\RequirePackage{amsthm}              % for AMS theorems
\RequirePackage{graphicx}
\RequirePackage{booktabs}            % to get fancier tables
\RequirePackage[lowtilde]{url}       % to typeset URLs, see http://www.latex-community.org/viewtopic.php?f=44&t=3663
\RequirePackage{algorithmic}         % defines algorithmic environment
\ifthenelse{\boolean{biber}}{
	\usepackage[
		style=authoryear,
		style=authoryear-comp,
			 % sortlocale=de_DE,
			 % natbib=true,
		sorting=ynt,
		url=false,
		doi=true,                % Print the DOI.
		eprint=false,
		dashed=false,            % Do not use ---- to replace the authors in the bibliography (if the previous entry has the same authors)
		sortcites=true,          % Sort if multiple keys in one \cite{}
	]{biblatex}
	\renewcommand*{\nameyeardelim}{\addcomma\space}
	\renewcommand*{\multinamedelim}{\addcomma\space}
	\renewcommand*{\finalnamedelim}{\addcomma\space}
	\renewbibmacro{in:}{}
}
{
\RequirePackage{natbib}              % for citations with full names
}

% Load and configure hyperref
\IfFileExists{xr-hyper_mod.sty}{\RequirePackage{xr-hyper_mod}}{\RequirePackage{xr-hyper}}
\RequirePackage[pdftex,colorlinks=true,urlcolor=red,citecolor=blue,linkcolor=blue]{hyperref}
\IfFileExists{autoref_helper.sty}{\RequirePackage{autoref_helper}}{}

% Fix the numbering scheme
\numberwithin{table}{section}    % for Table 1.1
\numberwithin{figure}{section}   % for Figure 1.1
\ifthenelse{\boolean{global_equation_numbers}}
{}
{
	\numberwithin{equation}{section} % for equation (1.1)
}

% Set some length parameters
\setlength{\parindent}{0cm}
\setlength{\parskip}{1ex plus 0.5ex minus 0.5ex}
% \addtolength{\textheight}{2cm}

% Require our packages
% \RequirePackage{LaTeX_boldsymbols}
% \RequirePackage{LaTeX_mathcals}
% \RequirePackage{LaTeX_others}
% \RequirePackage{LaTeX_sets}
% \RequirePackage{LaTeX_vectors}
% \RequirePackage{LaTeX_abbrevs}
\RequirePackage{LaTeX_colors}

% Load framed_theorems.sty if required
\ifthenelse{\boolean{framedtheorems}}
{
	\IfFileExists{framed_theorems.sty}{\RequirePackage{framed_theorems}}{\newcommand\maketheoremcolored[1]{}}
}{}

\ifthenelse{\not{\boolean{framedtheorems}}}
{
% see http://www.tug.org.in/tutorial/src/mystyles.thm
% and http://web.mat.bham.ac.uk/R.W.Kaye/latex/thm.pdf
	\newtheoremstyle{Theorem}{}{}{}{}{\bfseries}{}{\newline}{{\thmname{#1}\thmnumber{ #2}}\thmnote{ (#3)}}
	\newtheoremstyle{Lemma}{}{}{}{}{\bfseries}{}{\newline}{{\thmname{#1}\thmnumber{ #2}}\thmnote{ (#3)}}
	\newtheoremstyle{Example}{}{}{}{}{\bfseries}{}{\newline}{{\thmname{#1}\thmnumber{ #2}}\thmnote{ (#3)}}
	\newtheoremstyle{Remark}{}{}{}{}{\bfseries}{}{\newline}{{\thmname{#1}\thmnumber{ #2}}\thmnote{ (#3)}}
	\newtheoremstyle{Definition}{}{}{}{}{\bfseries}{}{\newline}{{\thmname{#1}\thmnumber{ #2}}\thmnote{ (#3)}}
	\newtheoremstyle{Algorithm}{}{}{}{}{\bfseries}{}{\newline}{{\thmname{#1}\thmnumber{ #2}}\thmnote{ (#3)}}
}{}

% Use the \theoremstyle{Theorem} (etc) if \framedtheorems=N
% otherwise, use \theoremstyle{colored}
\ifthenelse{\not{\boolean{framedtheorems}}}{
	\theoremstyle{Theorem} % used for all \newtheorem commands below
}{\theoremstyle{colored}}

\ifthenelse{\boolean{global_theorem_numbers}}
{
	\newtheorem{theorem}{Theorem}
}
{
	\newtheorem{theorem}{Theorem}[section]
}

\newtheorem*{theorem*}{Theorem}

\ifthenelse{\not{\boolean{framedtheorems}}}{
	\theoremstyle{Lemma} % used for all \newtheorem commands below
}{}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{proposition}[theorem]{Proposition}

\ifthenelse{\not{\boolean{framedtheorems}}}{
	\theoremstyle{Example} % used for all \newtheorem commands below
}{}
\newtheorem{example}[theorem]{Example}
\newtheorem*{example*}{Example}
\newtheorem{assumption}[theorem]{Assumption}
\newtheorem*{assumption*}{Assumption}

\ifthenelse{\not{\boolean{framedtheorems}}}{
	\theoremstyle{Remark} % used for all \newtheorem commands below
}{}
\newtheorem{remark}[theorem]{Remark}
\newtheorem*{remark*}{Remark}

\ifthenelse{\not{\boolean{framedtheorems}}}{
	\theoremstyle{Definition} % used for all \newtheorem commands below
}{}
\newtheorem{definition}[theorem]{Definition}
\newtheorem*{definition*}{Definition}

\ifthenelse{\not{\boolean{framedtheorems}}}{
	\theoremstyle{Algorithm} % used for all \newtheorem commands below
}{}
\newtheorem{algorithm}[theorem]{Algorithm}

\ifthenelse{\boolean{framedtheorems}}{
	% Make everything colored by default
	\maketheoremcolored{theorem}
	\maketheoremcolored{lemma}
	\maketheoremcolored{corollary}
	\maketheoremcolored{proposition}
	\maketheoremcolored{example}
	\maketheoremcolored{assumption}
	\maketheoremcolored{remark}
	\maketheoremcolored{definition}
	\maketheoremcolored{definition*}
	\maketheoremcolored{algorithm}
}{}

% Define proof and comment environments
\ifthenelse{\boolean{framedproofs}}{
	\maketheoremcolored{proof}
	}{
	\renewenvironment{proof}[1][]{\emph{Proof{#1}: }}{\hfill $\Box$ \par}
}
\newenvironment{comment}{\begin{footnotesize}}{\end{footnotesize}}

% Define email command
\newcommand{\email}[1]{\href{mailto:#1}{#1}}

% Tweak the typesetting of DOIs in the references
\newcommand\doi[1]{\href{http://dx.doi.org/#1}{doi: \nolinkurl{#1}}}

% Load and configure the changes package
\usepackage[ulem=normalem]{changes}       % show changes in draft version

\@ifpackagelater{changes}{2012/01/11}{
	\definechangesauthor[name={Roland Herzog},color=red]{RH}        % define author and initials
	\definechangesauthor[name={Headline},color=darkgreen]{HEAD}     % define author and initials
	\newcommand{\headline}[1]{\medskip \added[id=HEAD]{#1} \medskip}
	\setauthormarkup{}                                              % do not show initials
}{
	\definechangesauthor[Roland Herzog]{RH}{red}                    % define author and initials
	\definechangesauthor[Headline]{HEAD}{darkgreen}                 % define author and initials
	\newcommand{\headline}[1]{\added[HEAD]{#1}}
	\setauthormarkup[right]{}                                       % do not show initials
}

% Setup of page layout
\titlehead{
Some title head...
}

\usepackage{scrpage2}
\ifthenelse{\boolean{clean_pages}}{
	\deftripstyle{plain}[0pt][0pt]{}{}{}{}{}{}
	\deftripstyle{numapde_headings}[0pt][0pt]{}{}{}{}{}{}
}
{
	\deftripstyle{numapde_headings}[0pt][0.5pt]{\shorttitle}{}{\shortauthor}{}{\pagemark}{}
}
\pagestyle{numapde_headings}


\renewcommand\title[2][]{%
	\gdef\@title{#2}%
	\ifthenelse{\equal{#1}{}}%
	{%
		% The optional argument is empty => use the long version also for the short one, but remove \footnotes.
		\gdef\shorttitle{\let\footnote\@gobble\let\thanks\@gobble#2}%
	}%
	{%
		\gdef\shorttitle{#1}%
	}%
}

\renewcommand\author[2][]{%
	\gdef\@author{#2}%
	\ifthenelse{\equal{#1}{}}%
	{%
		% The optional argument is empty => use the long version also for the short one, but remove \footnotes.
		\gdef\shortauthor{\let\footnote\@gobble\let\thanks\@gobble#2}%
	}%
	{%
		\gdef\shortauthor{#1}%
	}%
}

% \subject{Preprint}

% Change section and title fonts
\renewcommand{\sectfont}{\scshape\bfseries}

% Auto-reference to sections and subsections should produce ``Section'' instead of ``section'' and ``subsection''
\langen{
	\publishers{Research Group\\Numerical Mathematics\\(Partial Differential Equations)}
	% Use AtBeginDocument here, otherwise it will be redefined by babel
	\AtBeginDocument{
		\renewcommand{\sectionautorefname}{Section}
	}
}
\langde{
	\publishers{Arbeitsgruppe\\Numerische Mathematik\\(Partielle Differentialgleichungen)}
	% \renewcommand{\sectionautorefname}{Abschnitt}
}


%% Support for MSC (Mathematics Subject Classification):
\newenvironment{msc}%
{{\sectfont MSC:}\ }{}

\newcommand{\mscLink}[1]{\href{http://www.ams.org/mathscinet/msc/msc2010.html?t=#1}{#1}}

%% Support for key words
\newenvironment{keywords}%
{\begin{trivlist}\item[]{\textbf{Keywords:}}}{\end{trivlist}}

% Use AtBeginDocument here, otherwise it will be redefined by babel
\AtBeginDocument{
	\let\subsectionautorefname\sectionautorefname
	\let\subfigureautorefname\figureautorefname
}
