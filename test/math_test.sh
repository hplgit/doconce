#!/bin/sh
name=math_test

rm -rf "${name}_html.html ${name}_pandoc.html sphinx-rootdir"  # clean

doconce format latex $name
doconce ptex2tex $name
latex $name
latex $name
dvipdf $name
cp $name.pdf ${name}_latex.pdf

doconce format html $name
cp $name.html ${name}_html.html

doconce sphinx_dir dirname=sphinx-rootdir-math $name
python automake_sphinx.py

doconce format pandoc $name
# Do not use pandoc directly because it does not support MathJax enough
doconce md2html $name.md
cp $name.html ${name}_pandoc.html

doconce format pandoc $name
doconce md2latex $name
latex $name
latex $name
dvipdf $name
cp $name.pdf ${name}_pandoc.pdf

#exit 0
for name in "${name}_html.html ${name}_pandoc.html sphinx-rootdir/_build/html/math_test.html"
do
  echo $name
  google-chrome $name
done

