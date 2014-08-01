#!/bin/sh -x
set -x
doconce clean
rm -f automake_*

name=trouble

doconce format html ${name} --pygments_html_style=none --no_preprocess --latex_font=helvetica
doconce format pdflatex ${name}
doconce ptex2tex ${name} envir=minted
pdflatex -shell-escape ${name}.tex
# index??
pdflatex -shell-escape ${name}.tex

# Sphinx
doconce format sphinx ${name}
rm -rf sphinx-rootdir
doconce sphinx_dir author='HPL' version=0.2 ${name}
python automake_sphinx.py

doconce format rst ${name}

dest=../../pub/${name}
cp -r ${name}.pdf ${name}.html $dest
rm -rf $dest/html
mv -f sphinx-rootdir/_build/html $dest/
git add $dest/html
dest=../../../../doconce.wiki
cp -r ${name}.rst $dest
