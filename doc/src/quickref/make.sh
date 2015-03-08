#!/bin/bash -x
name=quickref

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

set -x
sh ./clean.sh

# Make latest bin/doconce doc
doconce > doconce_program.sh

doconce format html $name --pygments_html_style=none --no_preprocess --no_abort --html_style=bootswatch_readable

# pdflatex
system doconce format pdflatex $name --no_preprocess --latex_font=helvetica --no_ampersand_quote --latex_code_style=vrb
# Since we have native latex table and --no_ampersand_quote, we need to
# manually fix the quote examples elsewhere
doconce subst '([^`])Guns & Roses([^`])' '\g<1>Guns {\&} Roses\g<2>' $name.tex
doconce subst '([^`])Texas A & M([^`])' '\g<2>Texas A {\&} M\g<2>' $name.tex
system pdflatex -shell-escape $name
system pdflatex -shell-escape $name

# Sphinx
system doconce format sphinx $name --no_preprocess
rm -rf sphinx-rootdir
system doconce sphinx_dir author='HPL' $name
doconce replace 'doconce format sphinx %s' 'doconce format sphinx %s --no-preprocess' automake_sphinx.py
system python automake_sphinx.py
cp $name.rst $name.sphinx.rst  # save

# reStructuredText:
system doconce format rst $name --no_preprocess
rst2xml.py $name.rst > $name.xml
rst2odt.py $name.rst > $name.odt
rst2html.py $name.rst > $name.rst.html
rst2latex.py $name.rst > $name.rst.tex
system latex $name.rst.tex
latex $name.rst.tex
dvipdf $name.rst.dvi

# Other formats:
system doconce format plain $name --no_preprocess
system doconce format gwiki $name --no_preprocess
system doconce format mwiki $name --no_preprocess
system doconce format cwiki $name --no_preprocess
system doconce format st $name --no_preprocess
system doconce format epytext $name --no_preprocess
system doconce format pandoc $name --no_preprocess --strict_markdown_output --github_md

rm -rf demo
mkdir demo
cp -r $name.do.txt $name.html $name.p.tex $name.tex $name.pdf $name.rst $name.xml $name.rst.html $name.rst.tex $name.rst.pdf $name.gwiki $name.mwiki $name.cwiki $name.txt $name.epytext $name.st $name.md sphinx-rootdir/_build/html demo

cd demo
cat > index.html <<EOF
<HTML><BODY>
<TITLE>Demo of Doconce formats</TITLE>
<H3>Doconce demo</H3>

Doconce is a minimum tagged markup language. The file
<a href="$name.do.txt">$name.do.txt</a> is the source of the
Doconce $name, written in the Doconce format.
Running
<pre>
doconce format html $name.do.txt
</pre>
produces the HTML file <a href="$name.html">$name.html</a>.
Going from Doconce to LaTeX is done by
<pre>
doconce format latex $name.do.txt
</pre>
resulting in the file <a href="$name.tex">$name.tex</a>, which can
be compiled to a PDF file <a href="$name.pdf">$name.pdf</a>
by running <tt>latex</tt> and <tt>dvipdf</tt> the standard way.
<p>
The reStructuredText (reST) format is of particular interest:
<pre>
doconce format rst    $name.do.txt  # standard reST
doconce format sphinx $name.do.txt  # Sphinx extension of reST
</pre>
The reST file <a href="$name.rst">$name.rst</a> is a starting point
for conversion to many other formats: OpenOffice,
<a href="$name.xml">XML</a>, <a href="$name.rst.html">HTML</a>,
<a href="$name.rst.tex">LaTeX</a>,
and from LaTeX to <a href="$name.rst.pdf">PDF</a>.
The <a href="$name.sphinx.rst">Sphinx</a> dialect of reST
can be translated to <a href="$name.sphinx.pdf">PDF</a>
and <a href="html/index.html">HTML</a>.
<p>
Doconce can also be converted to
<a href="$name.gwiki">Googlecode wiki</a>,
<a href="$name.mwiki">MediaWiki</a>,
<a href="$name.cwiki">Creole wiki</a>,
<a href="$name.md">aPandoc</a>,
<a href="$name.st">Structured Text</a>,
<a href="$name.epytext">Epytext</a>,
and maybe the most important format of all:
<a href="$name.txt">plain untagged ASCII text</a>.
</BODY>
</HTML>
EOF

echo
echo "Go to the demo directory and load index.html into a web browser."

cd ..
dest=../../pub/$name
cp -r demo/html demo/$name.pdf demo/$name.html $dest
dest=../../../../doconce.wiki
cp -r demo/$name.rst $dest
