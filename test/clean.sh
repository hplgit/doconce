#!/bin/sh
files="tmp_* *~ .*~ verify* .*html_file_collection testdoc.*wiki testdoc*.html testdoc.rst* testdoc.txt testdoc.epytext testdoc*.tex* *.toc testdoc.st testdoc.md testdoc.sphinx.rst *.log *.loe sphinx-rootdir sphinx-rootdir-math sphinx-testdoc tmp_encoding.txt tmp1.do.txt tmp2.do.txt mjolnir.html tmp* *.aux *.dvi *.idx *.out *.pyg testdoc.pdf _static .tmp* .*.exerinfo test.output testdoc.tmp html_template.html author1.html author1.p.tex author1.md author1.pdf author1.rst author1.tex author1.txt automake_sphinx*.py ._part*.html html_images reveal.js slides.html slides_*.html mako_test*.html style_vagrant papers.* venues.list admon.rst admon*.tex admon.html admon.mwiki admon.pdf tmp_admon admon_*.* table_*.csv testtable.do.txt github_md.md testdoc.ilg testdoc.ind testdoc.ipynb testdoc.mkd testdoc.tdo slides*.html slides*.tex *.bbl *.blg *.snm latex_figs downloaded_figures math_test*.html math_test.rst math_test*.tex math_test*.pdf math_test.md movies*.tex movies*.html movies.pdf frame_* movie99x9.html movie_player* ._testdoc* deck.js encoding3.*tex* encoding3.html* template_vagrant.html ._admon* mdinput2do.do.txt markdown_input.html encoding1.html ipynb*src.tar.gz test_boots.html _ref_* ipynb*.tar.gz testdoc_exer.do.txt tailored_conf.py"
ls $files 2> /dev/null
rm -rf $files
rm -f test.v
rm -f \#*
cd Springer_T2
doconce clean
rm -rf tmp* Trash *.zip
cd ..
