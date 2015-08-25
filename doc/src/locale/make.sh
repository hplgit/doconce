#!/bin/sh
name=Norwegian
options="--encoding=utf-8"

doconce format pdflatex $name --latex_code_style=vrb $options
pdflatex $name

doconce format html $name --html_style=bootstrap $options

doconce format sphinx $name $options
doconce sphinx_dir theme=redcloud $name
python automake_sphinx.py
rm -rf sphinx
mv sphinx-rootdir/_build/html sphinx
