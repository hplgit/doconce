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

cat > index.html <<EOF
<html><body>
<title></title>
<h1>Demo of native language support in DocOnce</h1>
EOF

languages="English German Norwegian"
for language in $languages; do
options="--encoding=utf-8 --language=$language"
name=$language

# HTML
system doconce format html $name --html_style=bootstrap_bluegray $options

cat >> index.html <<EOF
<h3>$language</h3>
<li><p><a href="$language.html" target="_blank">HTML</a></p></li>
EOF

# Sphinx
system doconce format sphinx $name $options
theme=alabaster
theme=cbc
system doconce sphinx_dir theme=$theme dirname=${name}-${theme} $name
python automake_sphinx.py

cat >> index.html <<EOF
<li><p><a href="${name}-${theme}/index.html" target="_blank">Sphinx</a></p></li>
EOF

# LaTeX PDF
system doconce format pdflatex $name --latex_code_style=pyg-blue1 $options
pdflatex -shell-escape $name
makeindex $name
bibtex $name
pdflatex -shell-escape $name
pdflatex -shell-escape $name

cat >> index.html <<EOF
<li><p><a href="$language.pdf" target="_blank">PDF</a></p></li>
EOF

done

cat >> index.html <<EOF
</ul>
</body></html>
EOF

# Publish
dest=../../pub/locale
cp *.html *.pdf $dest
rm -rf $dest/*-${theme}
for language in $languages; do
cp -r ${language}-${theme}/_build/html $dest/${language}-${theme}
done
