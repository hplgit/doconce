#!/bin/sh -x
set -x
doconce clean
rm -f automake_*

opt="--no_mako --no_abort"
opt="--no_mako"
# --no_mako because of `<%` in the text which starts comment block (why?...)
# --no_abort because of multiple lables with the same name (e.g., my:fig
# is needed in doconce code and a rendered demo of it)

name=trouble

doconce format html ${name} --pygments_html_style=default --no_preprocess --html_style=bootswatch_journal $opt

doconce format pdflatex ${name} --latex_font=helvetica $opt --latex_code_style=pyg
pdflatex -shell-escape ${name}.tex
# index??
pdflatex -shell-escape ${name}.tex

# Sphinx
doconce format sphinx ${name}  $opt
rm -rf sphinx-rootdir
doconce sphinx_dir version=0.4 theme=cbc ${name}
python automake_sphinx.py

doconce format rst ${name}  $opt

doconce format pandoc ${name} --github_md --strict_markdown_output $opt

dest=../../pub/${name}
cp -r ${name}.pdf ${name}.html $dest
rm -rf $dest/html
mv -f sphinx-rootdir/_build/html $dest/
git add $dest/html

dest=../../../../doconce.wiki
cp -r ${name}.md $dest
