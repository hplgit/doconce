#!/bin/sh -x
set -x
doconce clean
rm -f automake_*

# Suddenly some mako problem arose...
opt="--no_mako"  # because of `<%` in the text which starts comment block...

name=trouble

doconce format html ${name} --pygments_html_style=default --no_preprocess --html_style=bootswatch_journal $opt

doconce format pdflatex ${name} --latex_font=helvetica $opt --latex_code_style=pyg
pdflatex -shell-escape ${name}.tex
# index??
pdflatex -shell-escape ${name}.tex

# Sphinx
doconce format sphinx ${name}  $opt
rm -rf sphinx-rootdir
doconce sphinx_dir copyright='2006-2014 Hans Petter Langtangen, Simula Research Laboratory and University of Oslo' version=0.4 theme=cbc ${name}
python automake_sphinx.py

doconce format rst ${name}  $opt

dest=../../pub/${name}
cp -r ${name}.pdf ${name}.html $dest
rm -rf $dest/html
mv -f sphinx-rootdir/_build/html $dest/
git add $dest/html
dest=../../../../doconce.wiki
cp -r ${name}.rst $dest
