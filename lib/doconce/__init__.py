'''


What Is DocOnce?
================

DocOnce is two things:

 1. DocOnce is a very simple and minimally tagged markup language that
    looks like ordinary ASCII text (much like what you would use in an
    email), but the text can be transformed to numerous other formats,
    including HTML, Wiki, LaTeX, PDF, reStructuredText (reST), Sphinx,
    Epytext, and also plain text (where non-obvious formatting/tags are
    removed for clear reading in, e.g., emails). From reStructuredText
    you can go to XML, HTML, LaTeX, PDF, OpenOffice, and from the
    latter to RTF and MS Word.
    (An experimental translator to Pandoc is under development, and from
    Pandoc one can generate Markdown, reST, LaTeX, HTML, PDF, DocBook XML,
    OpenOffice, GNU Texinfo, MediaWiki, RTF, Groff, and other formats.)

 2. DocOnce is a working strategy for never duplicating information.
    Text is written in a single place and then transformed to
    a number of different destinations of diverse type (software
    source code, manuals, tutorials, books, wikis, memos, emails, etc.).
    The DocOnce markup language support this working strategy.
    The slogan is: "Write once, include anywhere".

What Does DocOnce Look Like?
============================

DocOnce text looks like ordinary text, but there are some almost invisible
text constructions that allow you to control the formating. For example,

  * bullet lists arise from lines starting with an asterisk,

  * *emphasized words* are surrounded by asterisks,

  * _words in boldface_ are surrounded by underscores,

  * words from computer code are enclosed in back quotes and
    then typeset verbatim (monospace font),

  * section headings are recognied by equality (=) signs before
    and after the text, and the number of = signs indicates the
    level of the section (7 for main section, 5 for subsection,
    3 for subsubsection),

  * paragraph headings are recognized by a double underscore
    before and after the heading,

  * blocks of computer code can easily be included by placing
    !bc (begin code) and !ec (end code) commands at separate lines
    before and after the code block,

  * blocks of computer code can also be imported from source files,

  * blocks of LaTeX mathematics can easily be included by placing
    !bt (begin TeX) and !et (end TeX) commands at separate lines
    before and after the math block,

  * there is support for both LaTeX and text-like inline mathematics,

  * tables, figures, movies with captions, URLs with links, index list,
    labels and references are supported,

  * comments can be inserted throughout the text (# at the beginning
    of a line),

  * with a simple preprocessor, Preprocess or Mako, one can include
    other documents (files) and large portions of text can be defined
    in or out of the text,

  * with the Mako preprocessor one can even embed Python
    code and use this to steer generation of DocOnce text.

Documentation of DocOnce is found in

  * The tutorial in doc/tutorial/tutorial.do.txt (file paths are here given
    relative to the root of the DocOnce source code).

  * The more comprehensive documentation in doc/manual/manual.do.txt.

  * There is web access to the tutorial (http://hplgit.github.io/doconce/doc/pub/tutorial/html/tutorial.html) the manual (http://hplgit.github.io/doconce/doc/pub/manual/html/manual.html)

Both directories contain a make.sh file for creating various formats.

'''
from __future__ import absolute_import

__version__ = '1.3'
version = __version__
__author__ = 'Hans Petter Langtangen', 'Johannes H. Ring', 'Kristian Gregorius Hustad'
author = __author__

__acknowledgments__ = ''

from .doconce import doconce_format, DocOnceSyntaxError
