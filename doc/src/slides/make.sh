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

html=${name}-reveal
system doconce format html $name --pygments_html_style=native --keep_pygments_html_bg --html_links_in_new_window --html_output=$html
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
system doconce slides_html $html reveal --html_slide_theme=darkgray
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

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

editfix $html.html

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
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
system doconce slides_html $html deck --html_slide_theme=sandstone.default
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
editfix $html.html

# Plain HTML documents
html=${name}-solarized
system doconce format html $name --pygments_html_style=perldoc --html_style=solarized --html_admon=apricot --html_links_in_new_window --html_output=$html
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
editfix $html.html

html=${name}-plain
system doconce format html $name --pygments_html_style=default --html_links_in_new_window --html_output=$html
editfix $html.html
system doconce split_html $html.html
# Remove top navigation in all parts
doconce subst -s '<!-- begin top navigation.+?end top navigation -->' '' ${name}-plain.html ._${name}*.html

# One big HTML file with space between the slides
html=${name}-1
system doconce format html $name --html_style=bloodish --html_links_in_new_window --html_output=$html
editfix $html.html
# Add space:
doconce replace '<!-- !split -->' '<!-- !split --><br><br><br><br><br><br><br><br>' $html.html

# LaTeX Beamer slides
beamertheme=red_shadow
system doconce format pdflatex $name
editfix ${name}.p.tex
system doconce ptex2tex $name -DLATEX_HEADING=beamer envir=minted
system doconce slides_beamer $name --beamer_slide_theme=$beamertheme
cp $name.tex ${name}-beamer-${beamertheme}.tex
system pdflatex -shell-escape ${name}-beamer-$beamertheme

# LaTeX documents
system doconce format pdflatex $name --minted_latex_style=trac
editfix ${name}.p.tex
system doconce ptex2tex $name envir=minted -DBOOK
doconce replace 'section{' 'section*{' $name.tex
system pdflatex -shell-escape $name
mv -f $name.pdf ${name}-minted.pdf
cp $name.tex ${name}-minted.tex

system doconce format pdflatex $name
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
editfix ${name}.p.tex
doconce replace 'section{' 'section*{' ${name}.p.tex
system doconce ptex2tex $name envir=ans:nt -DBOOK
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
system pdflatex $name
mv -f $name.pdf ${name}-anslistings.pdf
cp $name.tex ${name}-anslistings.tex

# sphinx doesn't handle math inside code well, we drop it since
# other formats demonstrate doconce writing this way
system doconce format sphinx $name
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
editfix ${name}.rst
system doconce sphinx_dir author="H. P. Langtangen" theme=pyramid $name
system python automake_sphinx.py

system doconce format pandoc $name  # Markdown (pandoc extended)
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
system doconce format gwiki  $name  # Googlecode wiki
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

# These don't like slides with code after heading:
#doconce format rst    $name  # reStructuredText
#doconce format plain  $name  # plain, untagged text for email

pygmentize -l text -f html -o ${name}-doconce.html ${name}.do.txt

dest=../../pub/slides

cp -r ${name}*.pdf ._${name}*.html *.md *.gwiki ${name}*.html deck.js reveal.js fig $dest/

doconce format html sw_index.do.txt
cp sw_index.html $dest/index.html

#drop demo part
#echo 'STOPPED HERE AND SKIPPED COMPILING DEMO TALK!'
#exit

# --------- short demo talk ------------

system doconce format html demo SLIDE_TYPE=dummy SLIDE_THEME=dummy # test
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi

# Make all the styles for the short demo talk
system doconce slides_html demo all  # generates tmp_slides_html_all.sh
pygmentize -l text -f html -o demo_doconce.html demo.do.txt
sh -x tmp_slides_html_all.sh

# Redo cbc, simula, and uio themes with logo

# CBC
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=cbc
doconce slides_html demo reveal --html_slide_theme=cbc --html_footer_logo=cbc_footer
doconce replace 'controls: true,' 'controls: false,' demo.html  # turn off nav.
cp demo.html demo_reveal_cbc.html

# Simula
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=simula
doconce slides_html demo reveal --html_slide_theme=simula --html_footer_logo=simula_symbol
cp demo.html demo_reveal_simula.html

# UiO
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=uio
doconce slides_html demo reveal --html_slide_theme=simple --html_footer_logo=uio_symbol
cp demo.html demo_reveal_uio.html

# Combined UiO and Simula footer
doconce format html demo --no_pygments_html SLIDE_TYPE=reveal SLIDE_THEME="uio+simula"
doconce slides_html demo reveal --html_slide_theme=simula --html_footer_logo=uio_simula_symbol
cp demo.html demo_reveal_uio_simula.html

# Solarized without pygments
doconce format html demo --no_pygments_html SLIDE_TYPE=reveal SLIDE_THEME=solarized
doconce slides_html demo reveal --html_slide_theme=solarized
cp demo.html demo_reveal_solarized_plainpre.html

# LaTeX Beamer slides
themes="blue_plain blue_shadow red_plain red_shadow cbc simula"
beamer_pdfs=""
for theme in $themes; do
doconce format pdflatex demo SLIDE_TYPE="beamer" SLIDE_THEME="$theme"
doconce ptex2tex demo -DLATEX_HEADING=beamer envir=minted
doconce slides_beamer demo --beamer_slide_theme=$theme
cp demo.tex demo_${theme}.tex
pdflatex -shell-escape demo_${theme}
beamer_pdfs="$beamer_pdfs <a href=\"demo_$theme.pdf\">$theme</a>"
done

# LaTeX document
doconce format pdflatex demo SLIDE_TYPE="latex document" SLIDE_THEME="no theme"
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
doconce ptex2tex demo -DPALATINO envir=minted
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
pdflatex -shell-escape demo

cp -r demo*.pdf demo_*.html reveal.js deck.js csss fig $dest/demo/
cat > $dest/demo/index.html <<EOF
<h1>Autogenerated slide styles</h1>
<b>Note:</b>

These slides are normally best viewed in Chrome in full screen mode,
but some functionality in reveal works in Chrome and not in Firefox.
Bring slide shows up in separate tabs. You may need to reload some
pages to get the mathematics correctly rendered.

<ul>
<p><li> reveal.js: (the css style files are slightly changed: left-adjusted,
lower case headings with smaller fonts; "darkgray" corresponds to
the original "default" theme; and pygments is used for typesetting
code in most of the demos below)
<ul>
<p><li><a target="_blank" href="demo_reveal_beige.html">reveal, beige theme</a>
<pre>
doconce format html demo --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=beige
doconce slides_html demo reveal --html_slide_theme=beige
</pre>
(Note that <tt>SLIDE_TYPE</tt> and <tt>SLIDE_THEME</tt> are user-defined Mako variables used in the <tt>demo.do.txt</tt> file - they are very specific to these slides and other presentations will most likely not use such variables, but perhaps others.)
<p><li><a target="_blank" href="demo_reveal_beigesmall.html">reveal, beigesmall theme</a>
<pre>
doconce format html demo --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=beigesmall
doconce slides_html demo reveal --html_slide_theme=beigesmall
</pre>
<p><li><a target="_blank" href="demo_reveal_solarized.html">reveal, solarized theme</a>
<pre>
doconce format html demo --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=solarized
doconce slides_html demo reveal --html_slide_theme=solarized
</pre>
<p><li><a target="_blank" href="demo_reveal_solarized_plainpre.html">reveal, solarized theme with plain pre, no pygments</a>
<pre>
doconce format html demo --no_pygments_html SLIDE_TYPE=reveal SLIDE_THEME=solarized
doconce slides_html demo reveal --html_slide_theme=solarized
</pre>
<li><a target="_blank" href="demo_reveal_darkgray.html">reveal, darkgray theme</a>
<pre>
doconce format html demo --pygments_html_style=native --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=darkgray
doconce slides_html demo reveal --html_slide_theme=darkgray
</pre>
<li><a target="_blank" href="demo_reveal_serif.html">reveal, serif theme</a>
<pre>
doconce format html demo --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=serif
doconce slides_html demo reveal --html_slide_theme=serif
</pre>
<li><a target="_blank" href="demo_reveal_night.html">reveal, night theme</a>
<pre>
doconce format html demo --pygments_html_style=fruity --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=night
doconce slides_html demo reveal --html_slide_theme=night
</pre>
<li><a target="_blank" href="demo_reveal_moon.html">reveal, moon theme</a>
<pre>
doconce format html demo --pygments_html_style=fruity --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=moon
doconce slides_html demo reveal --html_slide_theme=moon
</pre>
<li><a target="_blank" href="demo_reveal_simple.html">reveal, simple theme</a>
<pre>
doconce format html demo --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=simple
doconce slides_html demo reveal --html_slide_theme=simple
</pre>
<li><a target="_blank" href="demo_reveal_blood.html">reveal, blood theme</a>
<pre>
doconce format html demo --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=blood
doconce slides_html demo reveal --html_slide_theme=blood
</pre>
<li><a target="_blank" href="demo_reveal_cbc.html">reveal, cbc theme</a>
<pre>
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=cbc
doconce slides_html demo reveal --html_slide_theme=cbc --html_footer_logo=cbc_footer
#doconce slides_html demo reveal --html_slide_theme=cbc --html_footer_logo=cbc_symbol
</pre>
<li><a target="_blank" href="demo_reveal_simula.html">reveal, simula theme</a>
<pre>
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=simula
doconce slides_html demo reveal --html_slide_theme=simula --html_footer_logo=simula_symbol
</pre>
<li><a target="_blank" href="demo_reveal_uio.html">reveal, Univ. of Oslo (simple) theme with logo</a>
<pre>
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=reveal SLIDE_THEME=uio
doconce slides_html demo reveal --html_slide_theme=simple --html_footer_logo=uio_symbol
</pre>
<li><a target="_blank" href="demo_reveal_uio_simula.html">reveal, combined uio+simula theme</a>
<pre>
doconce format html demo --no_pygments_html SLIDE_TYPE=reveal SLIDE_THEME="uio+simula"
doconce slides_html demo reveal --html_slide_theme=simple --html_footer_logo=uio_simula_symbol
</pre>
<li><a target="_blank" href="demo_reveal_sky.html">reveal, sky theme</a>
</ul>
<p><li> deck.js: (the css styles are slightly changed, mainly somewhat
smaller fonts for verbatim code)
<ul>
<p><li><a target="_blank" href="demo_deck_beamer.html">deck, beamer theme</a>
<pre>
doconce format html demo --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=beamer
doconce slides_html demo deck --html_slide_theme=beamer
</pre>
<li><a target="_blank" href="demo_deck_mnml.html">deck, mnml theme</a>
<pre>
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=mnml
doconce slides_html demo deck --html_slide_theme=mnml
</pre>
<li><a target="_blank" href="demo_deck_neon.html">deck, neon theme</a>
<pre>
doconce format html demo --pygments_html_style=fruity --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=neon
doconce slides_html demo deck --html_slide_theme=neon
</pre>
<li><a target="_blank" href="demo_deck_sandstone_aurora.html">deck, sandstone.aurora theme</a>
<pre>
doconce format html demo --pygments_html_style=fruity --keep_pygments_html_bg    SLIDE_TYPE=deck SLIDE_THEME=sandstone-aurora
doconce slides_html demo deck --html_slide_theme=sandstone.aurora
</pre>
<li><a target="_blank" href="demo_deck_sandstone_dark.html">deck, sandstone.dark theme</a>
<pre>
doconce format html demo --pygments_html_style=native --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.dark
doconce slides_html demo deck --html_slide_theme=sandstone.dark
</pre>
<li><a target="_blank" href="demo_deck_sandstone_default.html">deck, sandstone.default theme</a>
<pre>
doconce format html demo --pygments_html_style=perldoc --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.default
doconce slides_html demo deck --html_slide_theme=sandstone.default
</pre>
<li><a target="_blank" href="demo_deck_sandstone_firefox.html">deck, sandstone.firefox theme</a>
<pre>
doconce format html demo --pygments_html_style=default --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.firefox
doconce slides_html demo deck --html_slide_theme=sandstone.firefox
</pre>
<li><a target="_blank" href="demo_deck_sandstone_light.html">deck, sandstone.light theme</a>
<li><a target="_blank" href="demo_deck_sandstone_mdn.html">deck, sandstone.mdn theme</a>
<pre>
doconce format html demo --pygments_html_style=emacs --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.light
doconce slides_html demo deck --html_slide_theme=sandstone.light
</pre>
<li><a target="_blank" href="demo_deck_sandstone_mightly.html">deck, sandstone.mightly theme</a>
<pre>
doconce format html demo --pygments_html_style=fruity --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=sandstone.mightly
doconce slides_html demo deck --html_slide_theme=sandstone.mightly
</pre>
<li><a target="_blank" href="demo_deck_swiss.html">deck, swiss theme</a>
<pre>
doconce format html demo --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=swiss
doconce slides_html demo deck --html_slide_theme=swiss
</pre>
<li><a target="_blank" href="demo_deck_web-2_0.html">deck, web-2_0 theme</a>
<pre>
doconce format html demo --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=deck SLIDE_THEME=web-2.0
doconce slides_html demo deck --html_slide_theme=web-2.0
</pre>
</ul>
<li><a target="_blank" href="demo_dzslides_dzslides_default.html">dzslides</a>
<pre>
doconce format html demo --pygments_html_style=autumn --keep_pygments_html_bg SLIDE_TYPE=dzslides SLIDE_THEME=dzslides_default
doconce slides_html demo dzslides --html_slide_theme=dzslides_default
</pre>
<li><a target="_blank" href="demo_csss_csss_default.html">csss</a> (black background instead
of the original rainbow background)
<pre>
doconce format html demo --pygments_html_style=monokai --keep_pygments_html_bg SLIDE_TYPE=csss SLIDE_THEME=csss_default
doconce slides_html demo csss --html_slide_theme=csss_default
</pre>
<li>LaTeX Beamer PDF: $beamer_pdfs
<pre>
doconce format pdflatex demo SLIDE_TYPE="beamer" SLIDE_THEME="red_shadow"
doconce ptex2tex demo -DLATEX_HEADING=beamer envir=minted
doconce slides_beamer demo --beamer_slide_theme=red_shadow
pdflatex -shell-escape demo
cp demo.pdf demo_red_shadow.pdf
</pre>
<li><a target="_blank" href="demo.pdf">Handouts in PDF</a> (generated via LaTeX)
<pre>
doconce format pdflatex demo SLIDE_TYPE="latex" SLIDE_THEME="std. latex"
doconce ptex2tex demo envir=minted
pdflatex -shell-escape demo
</pre>
<li><a target="_blank" href="demo_doconce.html">Doconce source code for the slides</a>
<li>Doconce: Why and How,
<a target="_blank" href="../scientific_writing-reveal.html">reveal w/darkgrey</a>,
<a target="_blank" href="../scientific_writing-deck.html">deck w/sandstone.default</a>,
<a target="_blank" href="../scientific_writing-beamer-$beamertheme.pdf">beamer</a>,
<a target="_blank" href="../scientific_writing-plain.html">plain HTML slides</a>
<a target="_blank" href="../scientific_writing-1.html">one big HTML file</a>
<a target="_blank" href="../scientific_writing-solarized.html">solarized HTML</a>,
</ul>
EOF