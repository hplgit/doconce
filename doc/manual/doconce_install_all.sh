#!/bin/bash
# Automatically generated script. Based on debpkg.txt.

sudo apt-get update

# Version control systems

yes | sudo apt-get install mercurial
if [ $? -ne 0 ]; then echo "mercurial failed"; exit 1; fi

yes | sudo apt-get install git
if [ $? -ne 0 ]; then echo "git failed"; exit 1; fi

yes | sudo apt-get install subversion
if [ $? -ne 0 ]; then echo "subversion failed"; exit 1; fi

cd srclib
hg clone https://code.google.com/p/doconce/
cd doconce
sudo python setup.py install
cd ../..
# Python

yes | sudo apt-get install idle
if [ $? -ne 0 ]; then echo "idle failed"; exit 1; fi

yes | sudo apt-get install ipython
if [ $? -ne 0 ]; then echo "ipython failed"; exit 1; fi

yes | sudo apt-get install python-pip
if [ $? -ne 0 ]; then echo "python-pip failed"; exit 1; fi

yes | sudo apt-get install python-pdftools
if [ $? -ne 0 ]; then echo "python-pdftools failed"; exit 1; fi

pip install sphinx  # installs pygments and docutils too
pip install mako
pip install -e svn+http://preprocess.googlecode.com/svn/trunk#egg=preprocess
pip install -e hg+https://bitbucket.org/logg/publish#egg=publish
pip install -e hg+https://bitbucket.org/ecollins/cloud_sptheme#egg=cloud_sptheme
pip install -e git+https://github.com/ryan-roemer/sphinx-bootstrap-theme#egg=sphinx-bootstrap-theme
pip install -e hg+https://bitbucket.org/miiton/sphinxjp.themes.solarized#egg=sphinxjp.themes.solarized
pip install -e git+https://github.com/shkumagai/sphinxjp.themes.impressjs#egg=sphinxjp.themes.impressjs
cd srclib
svn checkout http://ptex2tex.googlecode.com/svn/trunk/ ptex2tex
cd ptex2tex
sudo python setup.py install
cd latex
sh cp2texmf.sh  # copy stylefiles to ~/texmf directory
cd ../../..
# LaTeX

yes | sudo apt-get install latex-beamer
if [ $? -ne 0 ]; then echo "latex-beamer failed"; exit 1; fi

yes | sudo apt-get install latex-xcolor
if [ $? -ne 0 ]; then echo "latex-xcolor failed"; exit 1; fi

yes | sudo apt-get install texinfo
if [ $? -ne 0 ]; then echo "texinfo failed"; exit 1; fi

yes | sudo apt-get install texlive-extra-utils
if [ $? -ne 0 ]; then echo "texlive-extra-utils failed"; exit 1; fi

yes | sudo apt-get install texlive-latex-base
if [ $? -ne 0 ]; then echo "texlive-latex-base failed"; exit 1; fi

yes | sudo apt-get install texlive-latex-recommended
if [ $? -ne 0 ]; then echo "texlive-latex-recommended failed"; exit 1; fi

yes | sudo apt-get install texlive-latex-extra
if [ $? -ne 0 ]; then echo "texlive-latex-extra failed"; exit 1; fi

yes | sudo apt-get install texlive-math-extra
if [ $? -ne 0 ]; then echo "texlive-math-extra failed"; exit 1; fi

yes | sudo apt-get install texlive-bibtex-extra
if [ $? -ne 0 ]; then echo "texlive-bibtex-extra failed"; exit 1; fi

yes | sudo apt-get install texlive-xetex
if [ $? -ne 0 ]; then echo "texlive-xetex failed"; exit 1; fi

yes | sudo apt-get install texlive-humanities
if [ $? -ne 0 ]; then echo "texlive-humanities failed"; exit 1; fi

yes | sudo apt-get install texlive-pictures
if [ $? -ne 0 ]; then echo "texlive-pictures failed"; exit 1; fi

yes | sudo apt-get install latexdiff
if [ $? -ne 0 ]; then echo "latexdiff failed"; exit 1; fi

yes | sudo apt-get install auctex
if [ $? -ne 0 ]; then echo "auctex failed"; exit 1; fi

yes | sudo apt-get install biblatex
if [ $? -ne 0 ]; then echo "biblatex failed"; exit 1; fi

# Image manipulation

yes | sudo apt-get install imagemagick
if [ $? -ne 0 ]; then echo "imagemagick failed"; exit 1; fi

yes | sudo apt-get install netpbm
if [ $? -ne 0 ]; then echo "netpbm failed"; exit 1; fi

yes | sudo apt-get install mjpegtools
if [ $? -ne 0 ]; then echo "mjpegtools failed"; exit 1; fi

yes | sudo apt-get install pdftk
if [ $? -ne 0 ]; then echo "pdftk failed"; exit 1; fi

yes | sudo apt-get install giftrans
if [ $? -ne 0 ]; then echo "giftrans failed"; exit 1; fi

yes | sudo apt-get install gv
if [ $? -ne 0 ]; then echo "gv failed"; exit 1; fi

yes | sudo apt-get install evince
if [ $? -ne 0 ]; then echo "evince failed"; exit 1; fi

yes | sudo apt-get install smpeg-plaympeg
if [ $? -ne 0 ]; then echo "smpeg-plaympeg failed"; exit 1; fi

yes | sudo apt-get install mplayer
if [ $? -ne 0 ]; then echo "mplayer failed"; exit 1; fi

yes | sudo apt-get install totem
if [ $? -ne 0 ]; then echo "totem failed"; exit 1; fi

yes | sudo apt-get install ffmpeg
if [ $? -ne 0 ]; then echo "ffmpeg failed"; exit 1; fi

yes | sudo apt-get install libav-tools
if [ $? -ne 0 ]; then echo "libav-tools failed"; exit 1; fi

# Misc

yes | sudo apt-get install ispell
if [ $? -ne 0 ]; then echo "ispell failed"; exit 1; fi

yes | sudo apt-get install pandoc
if [ $? -ne 0 ]; then echo "pandoc failed"; exit 1; fi

yes | sudo apt-get install libreoffice
if [ $? -ne 0 ]; then echo "libreoffice failed"; exit 1; fi

yes | sudo apt-get install unoconv
if [ $? -ne 0 ]; then echo "unoconv failed"; exit 1; fi

yes | sudo apt-get install libreoffice-dmaths
if [ $? -ne 0 ]; then echo "libreoffice-dmaths failed"; exit 1; fi

pip install -e svn+https://epydoc.svn.sourceforge.net/svnroot/epydoc/trunk/epydoc#egg=epydoc
yes | sudo apt-get install curl
if [ $? -ne 0 ]; then echo "curl failed"; exit 1; fi

yes | sudo apt-get install a2ps
if [ $? -ne 0 ]; then echo "a2ps failed"; exit 1; fi

yes | sudo apt-get install wdiff
if [ $? -ne 0 ]; then echo "wdiff failed"; exit 1; fi

yes | sudo apt-get install meld
if [ $? -ne 0 ]; then echo "meld failed"; exit 1; fi

yes | sudo apt-get install xxdiff
if [ $? -ne 0 ]; then echo "xxdiff failed"; exit 1; fi

yes | sudo apt-get install diffpdf
if [ $? -ne 0 ]; then echo "diffpdf failed"; exit 1; fi

yes | sudo apt-get install kdiff3
if [ $? -ne 0 ]; then echo "kdiff3 failed"; exit 1; fi

yes | sudo apt-get install diffuse
if [ $? -ne 0 ]; then echo "diffuse failed"; exit 1; fi

# tkdiff.tcl:

#tcl8.5-dev tk8.5-dev blt-dev

#https://sourceforge.net/projects/tkdiff/

echo "Everything is successfully installed!"
