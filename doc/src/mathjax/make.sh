#!/bin/bash
set -x

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

# Main document lives in test directory
cp ../../../test/math_test.do.txt .

rm -f *.aux
name=math_test

# Because we exemplify all math blocks with latex code blocks,
# we get multiple defined lables and need --no_abort.
# Also, pure rst math blocks in .do.txt are not inside !bt-!et
# directives and result in error messages.
options="--no_abort"

# in error messages from DocOnce. But if we neglect them, the code works
# as intended.

system doconce format pdflatex $name --no_abort --latex_code_style=pyg $options
system pdflatex -shell-escape $name
pdflatex -shell-escape $name

system doconce format html $name --html_output=${name}_html $options

system doconce format sphinx $name $options
#system doconce sphinx_dir theme=fenics_minimal1 $name
system doconce sphinx_dir theme=cbc $name
system python automake_sphinx.py

system doconce format ipynb $name $options

system doconce format pandoc $name $options
# Do not use pandoc directly because it does not support MathJax sufficiently well
system doconce md2html $name.md
cp $name.html ${name}_pandoc.html

doconce pygmentize ${name}.do.txt perldoc
doconce format html index --html_style=bootstrap_FlatUI --html_links_in_new_window --html_bootstrap_navbar=off

dest=../../pub/mathjax
cp -r index.html ${name}.pdf ${name}.do.txt.html ${name}_html.html ${name}.ipynb ${name}_pandoc.html sphinx-rootdir/_build/html $dest
