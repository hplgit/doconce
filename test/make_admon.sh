# Test admonitions
doconce format html admon
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
cp admon.html admon_white.html

doconce format html admon --html_admon=colors
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
cp admon.html admon_colors.html

doconce format html admon --html_admon=gray
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
cp admon.html admon_gray.html

doconce format html admon --html_style=vagrant --pygments_html_style=default --html_template=style_vagrant/template_vagrant.html
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
cp admon.html admon_yellow.html

doconce format html admon --html_admon=apricot --html_style=solarized
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
cp admon.html admon_yellow_solarized.html

exit

doconce sphinx_dir dirname=tmp_admon admon
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
python automake_sphinx.py
if [ $? -ne 0 ]; then echo "make.sh: abort"; exit 1; fi
cp tmp_admon/_build/html/admon.html admon_sphinx.html

#google-chrome admon_*.html
