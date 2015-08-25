#!/bin/bash
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
}

system doconce format pdflatex $name --latex_code_style=vrb $options --latex_font=palatino
# Tips: http://folk.uio.no/tobiasvl/latex.html
system common_replacements $name.tex
doconce replace '10pt]{' '10pt,norsk]{' $name.tex
doconce subst '% insert custom LaTeX commands...' '%\usepackage[norsk]{babel}\n\n% insert custom LaTeX commands...' $name.tex
system pdflatex $name; pdflatex $name

system doconce format html $name --html_style=bootstrap $options
common_replacements $name.html

system doconce format sphinx $name $options
common_replacements $name.rst
system doconce sphinx_dir theme=redcloud $name
system python automake_sphinx.py
rm -rf sphinx
mv sphinx-rootdir/_build/html sphinx

# Publish
dest=../../pub/locale
cp -r $name.pdf $name.html sphinx $dest
