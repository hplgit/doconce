#!/bin/sh
sh -x clean.sh

# Sphinx
doconce format sphinx quiz
doconce split_rst quiz
doconce sphinx_dir dirname=sphinx quiz
python automake_sphinx.py

# Sphinx RunestoneInteractive
doconce format sphinx quiz --runestone
doconce split_rst quiz
doconce sphinx_dir dirname=sphinx-rs quiz
python automake_sphinx.py --runestone
exit

# HTML Bootstrap format
doconce format html quiz --html_style=bootstrap --html_code_style=inherit -DDOCONCE --quiz_horizontal_rule=off
doconce split_html quiz.html #--pagination

# HTML solarized format
doconce format html quiz --html_style=solarized --html_output=quiz-solarized -DDOCONCE --quiz_horizontal_rule=off

# PDF via latex including full solutions
doconce format pdflatex quiz --max_bc_linelength=67 --without_answers
doconce ptex2tex quiz envir=minted
pdflatex -shell-escape quiz
cp quiz.pdf quiz_wsol.pdf

# PDF via latex including short answers
doconce format pdflatex quiz  --max_bc_linelength=67 --without_solutions
doconce ptex2tex quiz envir=minted
pdflatex -shell-escape quiz
cp quiz.pdf quiz_wans.pdf

# PDF via latex without solutions/answers
doconce format pdflatex quiz  --max_bc_linelength=67 --without_answers --without_solutions --quiz_choice_prefix=number+box  # or letter+box
doconce ptex2tex quiz envir=minted
pdflatex -shell-escape quiz

# publish
cp -r quiz*.pdf quiz*.html ._quiz*.html fig ../../pub/quiz
