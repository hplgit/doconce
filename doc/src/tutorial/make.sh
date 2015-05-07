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

# html (need no_abort because of equation ref demo)
system doconce format html tutorial  --html_style=bootswatch_readable --html_code_style=inherit --no_abort
# references in blocks of doconce code are not treated right
doconce replace XXX1 '(ref{myeq1})' tutorial.html

# latex
system doconce format latex tutorial --latex_font=helvetica --latex_code_style=pyg
doconce replace XXX1 '(ref{myeq1})' tutorial.p.tex
latex -shell-escape tutorial.tex
latex -shell-escape tutorial.tex
dvipdf tutorial.dvi

# Sphinx
system doconce format sphinx tutorial
doconce replace XXX1 '(ref{myeq1})' tutorial.rst
rm -rf sphinx-rootdir
system doconce sphinx_dir tutorial
cp tutorial.rst tutorial.sphinx.rst
mv tutorial.rst sphinx-rootdir
cd sphinx-rootdir
make clean
make html
make latex
cd _build/latex
make clean
make all-pdf
cp DocOnceDocumentOnceIncludeAnywhere.pdf ../../../tutorial.sphinx.pdf
cd ../../..
#firefox sphinx-rootdir/_build/html/index.html

# reStructuredText:
system doconce format rst tutorial
doconce replace XXX1 '(ref{myeq1})' tutorial.rst
rst2xml.py tutorial.rst > tutorial.xml
rst2odt.py tutorial.rst > tutorial.odt
rst2html.py tutorial.rst > tutorial.rst.html
rst2latex.py tutorial.rst > tutorial.rst.tex
latex tutorial.rst.tex
dvipdf tutorial.rst.dvi

# Other formats:
system doconce format plain tutorial.do.txt
doconce replace XXX1 '(ref{myeq1})' tutorial.txt
system doconce format gwiki tutorial.do.txt
doconce replace XXX1 '(ref{myeq1})' tutorial.gwiki
system doconce format cwiki tutorial.do.txt
doconce replace XXX1 '(ref{myeq1})' tutorial.cwiki
system doconce format mwiki tutorial.do.txt
doconce replace XXX1 '(ref{myeq1})' tutorial.mwiki
system doconce format st tutorial.do.txt
doconce replace XXX1 '(ref{myeq1})' tutorial.st
system doconce format epytext tutorial.do.txt
doconce replace XXX1 '(ref{myeq1})' tutorial.epytext
system doconce format pandoc tutorial.do.txt --strict_markdown_output --github_md
doconce replace XXX1 '(ref{myeq1})' tutorial.md

rm -f *.ps

dest=../../pub/tutorial
cp -r sphinx-rootdir/_build/html $dest/html
cp tutorial.pdf tutorial.html $dest
dest=../../../../doconce.wiki
cp tutorial.rst $dest/tutorial_rst.rst
# mediawiki at github is too bad - very ugly result
#cp demo/tutorial.mwiki $dest/tutorial_mediawiki.mediawiki
cp tutorial.md $dest/tutorial_markdown.md
