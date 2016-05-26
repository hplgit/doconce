#!/bin/sh -x
set -x
sh -x ./clean.sh

function system {
# Run operating system command and if failure, report and abort
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

# Main document lives in test directory
cp ../../../test/math_test_slides.do.txt .

rm -f *.aux
name=math_test_slides

# Because we exemplify all math blocks with latex code blocks,
# we get multiple defined lables and need --no_abort.
# Also, pure rst math blocks in .do.txt are not inside !bt-!et
# directives and result in error messages.
options="--no_abort"


# Note: since Doconce syntax is demonstrated inside !bc/!ec
# blocks we need a few fixes

function editfix {
# Fix selected backslashes inside verbatim envirs that doconce has added
# (only a problem when we want to show full doconce code with
# labels in !bc-!ec envirs as in this presentation).
doconce replace '\label{this:section}' 'label{this:section}' $1
doconce replace '\label{fig1}' 'label{fig1}' $1
doconce replace '\label{demo' 'label{demo' $1
doconce replace '\eqref{eq1}' '(ref{eq1})' $1
doconce replace '\eqref{myeq}' '(ref{myeq})' $1
doconce replace '\eqref{mysec:eq:Dudt}' '(ref{mysec:eq:Dudt})' $1
}

rawgit="--html_raw_github_url=raw.github"

# HTML5 Slides
html=${name}-reveal
system doconce format html $name --pygments_html_style=native --keep_pygments_html_bg --html_links_in_new_window --html_output=$html
system doconce slides_html $html reveal --html_slide_theme=darkgray --copyright=titlepage

# Remark slides
system doconce format pandoc ${name} --github_md SLIDE_TYPE=remark SLIDE_THEME=dark
system doconce slides_markdown ${name} remark --slide_theme=dark
mv ${name}.html ${name}-remark.html

# LaTeX Beamer slides
theme=blue_shadow
system doconce format pdflatex ${name} SLIDE_TYPE="beamer" SLIDE_THEME="$theme" --latex_title_layout=beamer --latex_code_style=pyg
system doconce slides_beamer ${name} --beamer_slide_theme=$theme
mv ${name}.tex ${name}-beamer.tex
system pdflatex -shell-escape ${name}-beamer
system pdflatex -shell-escape ${name}-beamer

# Sphinx document
system doconce format sphinx ${name}
# editfix ${name}.rst
system doconce sphinx_dir theme=pyramid ${name}
system python automake_sphinx.py

# IPython notebook
system doconce format ipynb ${name} --encoding=utf-8 ${options}
pygmentize -l json -o ${name}.ipynb.html ${name}.ipynb

# Create HTML view from DocOnce source
system doconce format html $name --html_output=${name}_html $options

doconce pygmentize ${name}.do.txt perldoc
doconce format html index_slides --html_style=bootstrap_FlatUI --html_links_in_new_window --html_bootstrap_navbar=off

dest=../../pub/mathjax
cp -r index_slides.html ${name}-beamer.pdf ${name}.do.txt.html ${name}-reveal.html reveal.js ${name}-remark.html ${name}.ipynb sphinx-rootdir/_build/html $dest
