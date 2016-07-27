#!/bin/bash
set -x

# NOTE: There are many doconce errors arising when compiling this manual
# because it describes doconce syntax in the text, and this syntax is
# not in the right context for all the syntax checks in doconce.
# For "normal" documents not explaining doconce syntax, this is not a problem.

function system {
# Run operating system command and if failure, report and abort

  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

# Compile the Doconce manual, manual.do.txt, in a variety of
# formats to exemplify how different formats may look like.
# This is both a test of Doconce and an example.

# The following packages must be installed for this script to run:
# doconce, docutils, preprocess, sphinx, publish

sh -x ./clean.sh
echo; echo # Make space in output after deleting many files...

# First make the publish database
rm -rf papers.pub  venues.list # clean

publish import refs1.bib <<EOF
2
y
EOF
publish import refs2.bib <<EOF
2
2
EOF
# Simulate that we get new data, which is best put
# in a new file
publish import refs3.bib <<EOF
1
2
EOF

# doconce html format:
system doconce format html manual.do.txt --no_mako --html_style=bootswatch_readable --allow_refs_to_external_docs --html_code_style=inherit --cite_doconce --no_abort
# Must fix one \eqref{} to (ref{})
doconce replace '\eqref{my:special:eq}' '(ref{my:special:eq})' manual.html
doconce replace '\eqref{eq1}' '(ref{eq1})' manual.html
system doconce split_tmp.html manual.html

# Sphinx
system doconce format sphinx manual.do.txt --no_mako --cite_doconce --no_abort
# We have several examples on AUTHOR: so to avoid multiple
# authors we have to specify
system doconce sphinx_dir theme=bootstrap version=1.0 intersphinx manual.do.txt
cp manual.rst manual.sphinx.rst
python automake_sphinx.py
# automake_sphinx.py can only copy figures in FIGURE lines, not
# the ones we have in the special figure table
mkdir sphinx-rootdir/_build/html/mov
cp -r mov/wave_frames sphinx-rootdir/_build/html/mov

# rst:
system doconce format rst manual.do.txt --no_mako --cite_doconce --no_abort
system rst2html.py manual.rst > manual.rst.html
system rst2xml.py manual.rst > manual.xml

# The Mako generated HTML table must be removed before creating latex
doconce remove --from '.. end sphinx-figtable-in-html' --to '.. end sphinx-figtable-in-html' manual.rst > manual.4latex.rst
system rst2latex.py manual.4latex.rst > manual.rst.tex

system pdflatex manual.rst.tex
# fix figure extension: rst will use .png file for wave1D, but this is not
# legal for latex
# lookahead don't work: doconce subst '(?=includegraphics.+)\.png' '.eps' manual.rst.tex
doconce replace wave1D.png wave1D.eps manual.rst.tex
latex manual.rst.tex
latex manual.rst.tex
dvipdf manual.rst.dvi

system doconce format plain manual.do.txt --skip_inline_comments --cite_doconce  --no_mako --no_abort
system doconce format pandoc manual.do.txt --no_mako --strict_markdown_output --github_md --cite_doconce  --no_abort
system doconce format epytext manual.do.txt --cite_doconce --no_mako --no_abort

# doconce latex:
system doconce format latex manual.do.txt --no_mako --latex_font=helvetica --no_ampersand_quote --cite_doconce  --no_abort # produces ptex2tex: manual.p.tex
doconce ptex2tex manual envir=ans:nt
# Since we have native latex table and --no_ampersand_quote, we need to
# manually fix the quote examples elsewhere
doconce subst '([^`])Guns & Roses([^`])' '\g<1>Guns {\&} Roses\g<2>' manual.tex
doconce subst '([^`])Texas A & M([^`])' '\g<2>Texas A {\&} M\g<2>' manual.tex
# Must fix one \eqref{} to (ref{})
doconce replace '\eqref{my:special:eq}' '(ref{my:special:eq})' manual.tex
doconce replace '\eqref{eq1}' '(ref{eq1})' manual.tex
latex -shell-escape manual
latex -shell-escape manual
bibtex manual
makeindex manual
latex -shell-escape manual
latex -shell-escape manual
dvipdf manual.dvi
cp manual.pdf manual_latex.pdf

# doconce pdflatex:
system doconce format pdflatex manual.do.txt --no_mako --latex_font=helvetica --no_ampersand_quote --cite_doconce --no_abort

doconce ptex2tex manual envir=ans:nt
# Since we have native latex table and --no_ampersand_quote, we need to
# manually fix the quote examples elsewhere
doconce subst '([^`])Guns & Roses([^`])' '\g<1>Guns {\&} Roses\g<2>' manual.tex
doconce subst '([^`])Texas A & M([^`])' '\g<2>Texas A {\&} M\g<2>' manual.tex
# Must fix one \eqref{} to (ref{})
doconce replace '\eqref{my:special:eq}' '(ref{my:special:eq})' manual.tex
doconce replace '\eqref{eq1}' '(ref{eq1})' manual.tex
pdflatex -shell-escape manual
bibtex manual
makeindex manual
pdflatex -shell-escape manual
pdflatex -shell-escape manual

# Google Code wiki:
system doconce format gwiki manual.do.txt --cite_doconce --no_mako --no_abort
# fix figure in wiki: (can also by done by doconce gwiki_figsubst)
doconce subst "\(the URL of the image file fig/wave1D.png must be inserted here\)" "(https://raw.github.com/hplgit/doconce/master/doc/src/manual/fig/wave1D.png" manual.gwiki

system doconce format cwiki manual.do.txt --cite_doconce --no_mako --no_abort
system doconce format mwiki manual.do.txt --cite_doconce --no_mako --no_abort

rm -f *.ps

rm -rf demo
mkdir demo
cp -r manual.do.txt manual.html ._manual*.html fig mov manual.tex manual.tex manual.pdf manual_latex.pdf manual.rst manual.sphinx.rst manual.xml manual.rst.html manual.rst.tex manual.rst.pdf manual.gwiki manual.cwiki manual.mwiki manual.txt manual.epytext manual.md sphinx-rootdir/_build/html demo

cd demo
cat > index.html <<EOF
<HTML><BODY>
<TITLE>Demo of system doconce formats</TITLE>
<H3>Doconce demo</H3>

Doconce is a minimum tagged markup language. The file
<a href="manual.do.txt">manual.do.txt</a> is the source of
a Doconce Description, written in the system doconce format.
Running
<pre>
doconce format html manual.do.txt --no_mako --html_style=bootswatch_readings
</pre>
produces the HTML file <a href="manual.html">manual.html</a>.
(Note that on <tt>code.google.com</tt> the LaTeX mathematics
is not rendered properly with MathJax, so the mathematics looks
ugly!)
<p>
Going from Doconce to LaTeX is done by
<pre>
doconce format latex manual.do.txt
</pre>
resulting in the file <a href="manual.tex">manual.tex</a>, which can
be compiled to a PDF file <a href="manual.pdf">manual.pdf</a>
by running <tt>latex</tt> and <tt>dvipdf</tt> the standard way.
<p>
The reStructuredText (reST) format is of particular interest:
<pre>
doconce format rst    manual.do.txt  # standard reST
doconce format sphinx manual.do.txt  # Sphinx extension of reST
</pre>
The reST file <a href="manual.rst">manual.rst</a> is a starting point
for conversion to many other formats: OpenOffice,
<a href="manual.xml">XML</a>, <a href="manual.rst.html">HTML</a>,
<a href="manual.rst.tex">LaTeX</a>,
and from LaTeX to <a href="manual.rst.pdf">PDF</a>.
The <a href="manual.sphinx.rst">Sphinx</a> dialect of reST
can be translated to <a href="manual.sphinx.pdf">PDF</a>
and <a href="html/index.html">HTML</a>.
<p>
Doconce can also be converted to
<a href="manual.gwiki">Googlecode wiki</a>,
<a href="manual.cwiki">Creole wiki</a>,
<a href="manual.mwiki">MediaWiki</a>,
<a href="manual.md">Markdown</a> (Pandoc extended version),
<a href="manual.epytext">Epytext</a>,
and maybe the most important format of all:
<a href="manual.txt">plain untagged ASCII text</a>.
</BODY>
</HTML>
EOF

cd ..
dest=../../pub/manual
cp -r demo/html demo/manual.pdf demo/manual.html demo/._manual*.html demo/fig demo/mov $dest

dest=../../../../doconce.wiki
# rst is inferior to md
#cp demo/manual.rst $dest/manual_rst.rst
# mediawiki at github is too bad - very ugly result
#cp demo/manual.mwiki $dest/manual_mediawiki.mediawiki
cp demo/manual.md $dest
