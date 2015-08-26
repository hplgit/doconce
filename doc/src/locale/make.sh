#!/bin/bash
#
# Compile a Norwegian document to PDF, HTML, and Sphinx.
#

name=Norwegian
options="--encoding=utf-8"

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

function common_replacements {
  filename=$1
  # Replace English phrases
  # __Summary.__ is needed for identifying the abstract
  doconce replace Summary Sammendrag $1
  doconce replace "Tables of Contents" "Innholdsfortegnelse" $1
  doconce replace "Figure" "Figur" $1
}

system doconce format pdflatex $name --latex_code_style=vrb $options --latex_font=palatino
# Tips: http://folk.uio.no/tobiasvl/latex.html
system common_replacements $name.tex
doconce replace '10pt]{' '10pt,norsk]{' $name.tex
# package [norsk]{label} requires texlive-lang-norwegian package
doconce subst '% insert custom LaTeX commands...' '\usepackage[norsk]{babel}\n\n% insert custom LaTeX commands...' $name.tex
system pdflatex $name
system bibtex $name
system makeindex $name
pdflatex $name
pdflatex $name

system doconce format html $name --html_style=bootstrap $options
common_replacements $name.html

system doconce format sphinx $name $options
common_replacements $name.rst
system doconce sphinx_dir theme=redcloud author="H. P. Langtangen (mannen bak pseudonymet Å. Ødegården)" $name
# Fix language in conf.py and heading in index.rst
doconce replace "language = None" "language = 'nb_NO'" sphinx-rootdir/conf.py
doconce replace "Indices and tables" "Indeks og tabeller" sphinx-rootdir/index.rst
system python automake_sphinx.py
rm -rf sphinx
mv sphinx-rootdir/_build/html sphinx
# Fix headings that Sphinx did not provide in Norwegian
cd sphinx
files="*.html"
doconce replace "Previous page" "Forrige side" $files
doconce replace "Next page" "Neste side" $files
doconce replace "Page contents" "Sideinnhold" $files
cd ..

# Publish
dest=../../pub/locale
cp -r $name.pdf $name.html sphinx $dest
