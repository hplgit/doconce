#!/bin/bash

set -x

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

name="pgf_tikz"
options="--encoding=utf-8 --figure_prefix=fig"

# HTML
system doconce format html $name --html_style=bootstrap_bluegray $options

# Sphinx
system doconce format sphinx $name $options
theme=alabastere
theme=cbc
system doconce sphinx_dir theme=$theme dirname=${theme} $name
python automake_sphinx.py

# LaTeX PDF
system doconce format pdflatex $name --latex_code_style=pyg-blue1 $options
pdflatex -shell-escape $name
makeindex $name
bibtex $name
pdflatex -shell-escape $name
pdflatex -shell-escape $name

# Index page
system doconce format html index --html_style=bootstrap $options

# Publish
dest=../../pub/pgf_tikz
cp *.html *.pdf $dest
cp -r fig $dest
rm -rf $dest/*-${theme}

cp -r ${theme}/_build/html $dest/${theme}
