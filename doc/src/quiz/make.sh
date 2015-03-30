#!/bin/sh
sh -x clean.sh  # important to clean first to avoid wrong ._*.rst files
name=quiz

# Sphinx
doconce format sphinx $name
doconce split_rst $name
doconce sphinx_dir dirname=sphinx theme=default $name
python automake_sphinx.py

# Sphinx RunestoneInteractive
doconce format sphinx $name --runestone -DRUNESTONE
doconce split_rst $name
doconce sphinx_dir dirname=sphinx-rs $name
python automake_sphinx.py --runestone

# HTML Bootstrap format
doconce format html $name --html_style=bootstrap --html_code_style=inherit --quiz_horizontal_rule=off -DBOOTSTRAP
doconce split_html $name.html #--pagination

# HTML plain format
doconce format html $name --html_style=blueish --html_output=${name}-plain --quiz_horizontal_rule=off

# PDF via latex including full solutions
doconce format pdflatex $name --max_bc_linelength=67 --without_answers
doconce ptex2tex $name envir=minted
pdflatex -shell-escape $name
cp $name.pdf ${name}_wsol.pdf

# PDF via latex including short answers
doconce format pdflatex $name  --max_bc_linelength=67 --without_solutions
doconce ptex2tex $name envir=minted
pdflatex -shell-escape $name
cp $name.pdf ${name}_wans.pdf

# PDF via latex without solutions/answers
doconce format pdflatex $name  --max_bc_linelength=67 --without_answers --without_solutions --${name}_choice_prefix=number+box  # or letter+box
doconce ptex2tex $name envir=minted
pdflatex -shell-escape $name

# Index
doconce format html index --html_style=bootstrap_FlatUI --html_links_in_new_window --html_bootstrap_navbar=off

# publish
dest=../../pub/quiz
cp -r $name*.pdf $name*.html ._$name*.html fig index.html $dest
rm -rf $dest/sphinx*
cp -r sphinx/_build/html $dest/sphinx
cp -r sphinx-rs/RunestoneTools/build $dest/sphinx-rs
