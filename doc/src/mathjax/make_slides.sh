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

options="--no_abort"


# HTML5 Slides
html=${name}-reveal
system doconce format html $name --pygments_html_style=native --keep_pygments_html_bg --html_links_in_new_window --html_output=$html
system doconce slides_html $html reveal --html_slide_theme=darkgray --copyright=titlepage

# Remark slides
system doconce format pandoc ${name} --github_md --align2equations SLIDE_TYPE=remark SLIDE_THEME=dark
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
system doconce sphinx_dir theme=pyramid ${name}
system python automake_sphinx.py

# IPython notebook
system doconce format ipynb ${name} --encoding=utf-8
pygmentize -l json -o ${name}.ipynb.html ${name}.ipynb

# Create HTML view from DocOnce source
system doconce format html $name --html_output=${name}-html

doconce pygmentize ${name}.do.txt perldoc
doconce format html index_slides --html_style=bootstrap_FlatUI --html_links_in_new_window --html_bootstrap_navbar=off

dest=../../pub/mathjax
cp -r index_slides.html ${name}-beamer.pdf ${name}.do.txt.html ${name}-reveal.html ${name}-html.html reveal.js ${name}-remark.html ${name}.ipynb sphinx-rootdir/_build/html $dest
