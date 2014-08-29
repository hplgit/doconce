#!/bin/bash
set -x
bash clean.sh

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

# ----- scientific_writing talk -------
name=scientific_writing

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

html=${name}-reveal
system doconce format html $name --pygments_html_style=native --keep_pygments_html_bg --html_links_in_new_window --html_output=$html
system doconce slides_html $html reveal --html_slide_theme=darkgray
editfix $html.html
# Crank up the font:
#doconce replace 'pre style="' 'pre style="font-size: 120%; ' $html.html

html=${name}-reveal-beige
system doconce format html $name --pygments_html_style=perldoc --keep_pygments_html_bg --html_links_in_new_window --html_output=$html
system doconce slides_html $html reveal --html_slide_theme=beige
editfix $html.html

html=${name}-reveal-white
system doconce format html $name --pygments_html_style=default --keep_pygments_html_bg --html_links_in_new_window --html_output=$html
system doconce slides_html $html reveal --html_slide_theme=simple
editfix $html.html

html=${name}-deck
system doconce format html $name --pygments_html_style=perldoc --keep_pygments_html_bg --html_links_in_new_window --html_output=$html
system doconce slides_html $html deck --html_slide_theme=sandstone.default
editfix $html.html

# Plain HTML documents
html=${name}-solarized
system doconce format html $name --pygments_html_style=perldoc --html_style=solarized3 --html_links_in_new_window --html_output=$html
editfix $html.html
system doconce split_html $html.html

html=${name}-plain
system doconce format html $name --pygments_html_style=default --html_style=bloodish --html_links_in_new_window --html_output=$html
editfix $html.html
system doconce split_html $html.html

# One big HTML file with space between the slides
html=${name}-1
system doconce format html $name --html_style=bloodish --html_links_in_new_window --html_output=$html
editfix $html.html
# Add space between splits
system doconce split_html $html --method=space8
#doconce replace '<!-- !split -->' '<!-- !split --><br><br><br><br><br><br><br><br>' $html.html

# LaTeX Beamer slides
beamertheme=red_shadow
system doconce format pdflatex $name --latex_title_layout=beamer
editfix ${name}.p.tex
system doconce ptex2tex $name envir=minted
system doconce slides_beamer $name --beamer_slide_theme=$beamertheme
cp $name.tex ${name}-beamer.tex
system pdflatex -shell-escape ${name}-beamer

# LaTeX documents
system doconce format pdflatex $name --minted_latex_style=trac
editfix ${name}.p.tex
system doconce ptex2tex $name envir=minted
doconce replace 'section{' 'section*{' $name.tex
# Hack: suddenly \subex{} didn't work in this document
doconce subst -m '^\\subex\{' '\paragraph{' $name.tex
system pdflatex -shell-escape $name
mv -f $name.pdf ${name}-minted.pdf
cp $name.tex ${name}-minted.tex

system doconce format pdflatex $name
editfix ${name}.p.tex
doconce replace 'section{' 'section*{' ${name}.p.tex
system doconce ptex2tex $name envir=ans:nt
# Hack: suddenly \subex{} didn't work in this document
doconce subst -m '^\\subex\{' '\paragraph{' $name.tex
system pdflatex $name
mv -f $name.pdf ${name}-anslistings.pdf
cp $name.tex ${name}-anslistings.tex

# sphinx doesn't handle math inside code well, we drop it since
# other formats demonstrate doconce writing this way
system doconce format sphinx $name
editfix ${name}.rst
system doconce sphinx_dir author="H. P. Langtangen" theme=pyramid $name
system python automake_sphinx.py

system doconce format pandoc $name  # Markdown (pandoc extended)
system doconce format gwiki  $name  # Googlecode wiki

# These don't like slides with code after heading:
#doconce format rst    $name  # reStructuredText
#doconce format plain  $name  # plain, untagged text for email

pygmentize -l text -f html -o ${name}-doconce.html ${name}.do.txt

dest=../../pub/slides

cp -r ${name}*.pdf ._${name}*.html *.md *.gwiki ${name}*.html deck.js reveal.js fig $dest/

doconce format html sw_index.do.txt --html_style=bootstrap_bloodish --html_links_in_new_window
cp sw_index.html $dest/index.html

#drop demo part
#echo 'STOPPED HERE AND SKIPPED COMPILING DEMO TALK!'
#exit

# --------- short demo talk ------------

system doconce format html demo SLIDE_TYPE=dummy SLIDE_THEME=dummy # test

# Make all the styles for the short demo talk
system doconce slides_html demo all  # generates tmp_slides_html_all.sh
pygmentize -l text -f html -o demo_doconce.html demo.do.txt
sh -x tmp_slides_html_all.sh

# Redo cbc, simula, and uio themes with logo

slide_types="reveal deck"
footer_types="footer symbol"
for slide_tp in $slide_types; do
for footer_tp in $footer_types; do
# CBC
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=${slide_tp} SLIDE_THEME=cbc
doconce slides_html demo ${slide_tp} --html_slide_theme=cbc --html_footer_logo=cbc_${footer_tp}
doconce replace 'controls: true,' 'controls: false,' demo.html  # turn off nav.
cp demo.html demo_${slide_tp}_cbc_${footer_tp}.html
done
done

# Do just reveal for the following (no deck simula and uio style yet)
slide_tp=reveal

# Simula
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=${slide_tp} SLIDE_THEME=simula
doconce slides_html demo ${slide_tp} --html_slide_theme=simula --html_footer_logo=simula_symbol
cp demo.html demo_${slide_tp}_simula.html

# UiO
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=${slide_tp} SLIDE_THEME=uio
doconce slides_html demo ${slide_tp} --html_slide_theme=simple --html_footer_logo=uio_symbol
cp demo.html demo_${slide_tp}_uio.html

# Combined UiO and Simula footer
doconce format html demo --pygments_html_style=none SLIDE_TYPE=${slide_tp} SLIDE_THEME="uio+simula"
doconce slides_html demo ${slide_tp} --html_slide_theme=simula --html_footer_logo=uio_simula_symbol
cp demo.html demo_${slide_tp}_uio_simula.html

# Solarized without pygments
doconce format html demo --pygments_html_style=none SLIDE_TYPE=reveal SLIDE_THEME=solarized
doconce slides_html demo reveal --html_slide_theme=solarized
cp demo.html demo_reveal_solarized_plainpre.html

# LaTeX Beamer slides
themes="blue_plain blue_shadow red_plain red_shadow dark_gradient vintage cbc simula"
for theme in $themes; do
doconce format pdflatex demo SLIDE_TYPE="beamer" SLIDE_THEME="$theme" --latex_title_layout=beamer
doconce ptex2tex demo envir=minted
doconce slides_beamer demo --beamer_slide_theme=$theme
cp demo.tex demo_${theme}.tex
pdflatex -shell-escape demo_${theme}
done

# Beamer handouts
theme=red_shadow
doconce format pdflatex demo SLIDE_TYPE="beamer" SLIDE_THEME="$theme" --latex_title_layout=beamer
doconce ptex2tex demo envir=minted
doconce slides_beamer demo --beamer_slide_theme=$theme --handout  # note --handout!
pdflatex -shell-escape demo
# Merge slides to 2x3 per page
pdfnup --nup 2x3 --frame true --delta "1cm 1cm" --scale 0.9 --outfile demo.pdf demo.pdf
cp demo.pdf demo_${theme}_handouts2x3.pdf

# Ordinary plain LaTeX document (no slides)
rm -f demo.aux  # important after beamer
system doconce format pdflatex demo SLIDE_TYPE="latex document" SLIDE_THEME="no theme" --latex_font=palatino
system doconce ptex2tex demo envir=minted
pdflatex -shell-escape demo

cp -r demo*.pdf demo_*.html ._demo*.html reveal.js deck.js csss fig $dest/demo/
doconce format html index --html_style=bootstrap_bloodish --html_links_in_new_window
cp index.html $dest/demo/index.html
