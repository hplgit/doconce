#!/bin/bash
name=Norwegian
options="--encoding=utf-8"

function common_replacements {
  filename=$1
  # Replace English phrases
  # __Summary.__ is needed for identifying the abstract
  doconce replace Summary Sammendrag $1
}

doconce format pdflatex $name --latex_code_style=vrb $options --latex_font=palatino
# Tips: http://folk.uio.no/tobiasvl/latex.html
common_replacements $name.tex
doconce replace '10pt]{' '10pt,norsk]{' $name.tex
doconce subst '% insert custom LaTeX commands...' '%\usepackage[norsk]{babel}\n\n% insert custom LaTeX commands...' $name.tex
pdflatex $name; pdflatex $name

doconce format html $name --html_style=bootstrap $options
common_replacements $name.html

doconce format sphinx $name $options
doconce sphinx_dir theme=redcloud $name
python automake_sphinx.py
rm -rf sphinx
mv sphinx-rootdir/_build/html sphinx

# Publish
dest=../../pub/locale
cp -r $name.pdf $name.html sphinx $dest
