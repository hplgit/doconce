#!/bin/sh -x
set -x
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

d2f="doconce format"
# doconce html format:
$d2f html manual.do.txt --no_mako --no_pygments_html
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
# Need a fix: remove newcommands (and math) when displayed on googlecode
doconce subst -s '<!\-\- newcommands.*?\$\$.*?\$\$' '' manual.html

# Sphinx
$d2f sphinx manual.do.txt --no_mako
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

rm -rf sphinx-rootdir
# We have several examples on AUTHOR: so to avoid multiple
# authors we have to specify
doconce sphinx_dir author=HPL title='Doconce Manual' theme=cbc version=0.6 manual.do.txt
cp manual.rst manual.sphinx.rst
python automake_sphinx.py
# automake_sphinx.py can only copy figures in FIGURE lines, not
# the ones we have in the special figure table
mkdir sphinx-rootdir/_build/html/mov
cp -r mov/wave_frames sphinx-rootdir/_build/html/mov

# rst:
$d2f rst manual.do.txt --no_mako
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

rst2html.py manual.rst > manual.rst.html

rst2xml.py manual.rst > manual.xml

# The Mako generated HTML table must be removed before creating latex
doconce remove --from '.. end sphinx-figtable-in-html' --to '.. end sphinx-figtable-in-html' manual.rst > manual.4latex.rst
rst2latex.py manual.4latex.rst > manual.rst.tex

pdflatex manual.rst.tex
# fix figure extension: rst will use .png file for wave1D, but this is not
# legal for latex
# lookahead don't work: doconce subst '(?=includegraphics.+)\.png' '.eps' manual.rst.tex
doconce replace wave1D.png wave1D.eps manual.rst.tex
latex manual.rst.tex
latex manual.rst.tex
dvipdf manual.rst.dvi

# plain text:
$d2f plain manual.do.txt --skip_inline_comments --no_mako
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

$d2f epytext manual.do.txt --no_mako
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

#Problem with st
#$d2f st manual.do.txt --no_mako
#if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi


$d2f pandoc manual.do.txt --no_mako
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

# doconce pdflatex:
$d2f pdflatex manual.do.txt --no_mako --latex_font=helvetica
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

doconce ptex2tex manual envir=Verbatim
pdflatex -shell-escape manual
bibtex manual
makeindex manual
pdflatex -shell-escape manual
pdflatex -shell-escape manual
cp manual.pdf manual_pdflatex.pdf

# doconce latex:
$d2f latex manual.do.txt --no_mako --latex_font=helvetica  # produces ptex2tex: manual.p.tex
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
doconce ptex2tex manual envir=Verbatim
latex -shell-escape manual
latex -shell-escape manual
bibtex manual
makeindex manual
latex -shell-escape manual
latex -shell-escape manual
dvipdf manual.dvi

# Google Code wiki:
$d2f gwiki manual.do.txt --no_mako
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

# fix figure in wiki: (can also by done by doconce gwiki_figsubst)
doconce subst "\(the URL of the image file fig/wave1D.png must be inserted here\)" "(https://raw.github.com/hplgit/doconce/master/doc/src/manual/fig/wave1D.png" manual.gwiki

$d2f cwiki manual.do.txt --no_mako
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

$d2f mwiki manual.do.txt --no_mako
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

rm -f *.ps

rm -rf demo
mkdir demo
cp -r manual.do.txt manual.html fig mov manual.p.tex manual.tex manual.pdf manual_pdflatex.pdf manual.rst manual.sphinx.rst manual.xml manual.rst.html manual.rst.tex manual.rst.pdf manual.gwiki manual.cwiki manual.mwiki manual.txt manual.epytext manual.md sphinx-rootdir/_build/html demo

cd demo
cat > index.html <<EOF
<HTML><BODY>
<TITLE>Demo of Doconce formats</TITLE>
<H3>Doconce demo</H3>

Doconce is a minimum tagged markup language. The file
<a href="manual.do.txt">manual.do.txt</a> is the source of
a Doconce Description, written in the Doconce format.
Running
<pre>
doconce format html manual.do.txt
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
cp -r demo/html demo/manual.pdf demo/manual.html demo/fig demo/mov $dest
dest=../../../../doconce.wiki
cp -r demo/manual.rst $dest
