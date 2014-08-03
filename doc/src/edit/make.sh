#!/bin/sh
name=editex

doconce format pdflatex $name
doconce ptex2tex $name
pdflatex $name

doconce format html $name

doconce format sphinx $name
doconce sphinx_dir $name
python automake_sphinx.py
