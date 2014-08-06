#!/bin/sh
name=editex

doconce format pdflatex $name
doconce ptex2tex $name
pdflatex $name

doconce format html $name

doconce format sphinx $name
doconce sphinx_dir $name
python automake_sphinx.py

doconce format html index

dest=../../pub/edit
mv -f index.html editex.html editex.pdf $dest
cp -r sphinx-rootdir/_build/html $dest
doconce clean
