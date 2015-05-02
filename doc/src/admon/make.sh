#!/bin/bash

latex_admon="mdfbox traybox2 grayicon yellowicon colors1 colors2 paragraph"
latex_admon_color=bluestyle
#latex_admon_envir_map=
html_admon1="gray yellow apricot lyx colors paragraph"
html_admon2="bootstrap_panel bootstrap_alert"
#html_admon_shadow
#html_admon_bg_color
#html_admon_bd_color
ipynb_admon="quote paragraph hrule"
sphinx_styles="default agni basicstrap classy fenics-minimal2 scrolls"

doconce format pdflatex admon --latex_code_style=lst --latex_admon=mdfbox --latex_admon_color=bluestyle --latex_section_headings=blue "OPTIONS=--latex_admon=mdfbox --latex_admon_color=bluestyle --latex_section_headings=blue"
pdflatex admon
cp admon.pdf admon_mdfbox_blue.pdf

for admon_style in $latex_admon; do
doconce format pdflatex admon --latex_code_style=lst --latex_admon=$admon_style "OPTIONS=--latex_admon=$admon_style"
rm -f *.aux
pdflatex admon
cp admon.pdf admon_${admon_style}.pdf
done

for admon_style in $html_admon2; do
doconce format html admon --html_style=bootswatch_readable --html_admon=$admon_style --html_output=admon_${admon_style}  --html_box_shadow "OPTIONS=--html_style=bootswatch_readable --html_admon$admon_style --html_box_shadow"
done

for admon_style in $html_admon1; do
doconce format html admon --html_style=blueish --html_admon=$admon_style --html_output=admon_${admon_style} "OPTIONS=--html_style=bootswatch_readable --html_admon$admon_style"
done

for admon_style in $ipynb_admon; do
doconce format ipynb admon --ipynb_admon=$admon_style "OPTIONS=--ipynb_admon=$admon_style"
cp admon.ipynb admon_${admon_style}.ipynb
done

doconce format sphinx admon --sphinx_keep_splits "OPTIONS=None"
doconce sphinx_dir theme=default admon
python automake_sphinx.py
cd sphinx-rootdir
bash make_themes.sh $sphinx_styles
cd ..

doconce pygmentize admon.do.txt
doconce format html index --html_style=bootstrap --html_links_in_new_window

# Publish
dest=../../pub/admon
mv -f admon_*.pdf admon_*.html admon_*.ipynb index.html admon.do.txt.html $dest
cp -r sphinx-rootdir/sphinx-* $dest
