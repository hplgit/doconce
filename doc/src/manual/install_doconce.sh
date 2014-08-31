#!/bin/bash
# Automatically generated script by
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# where vagrantbox is the directory arising from
# git clone git@github.com:hplgit/vagrantbox.git

# The script is based on packages listed in debpkg_doconce.txt.

set -x  # make sure each command is printed in the terminal

function apt_install {
  sudo apt-get -y install $1
  if [ $? -ne 0 ]; then
    echo "could not install $1 - abort"
    exit 1
  fi
}

function pip_install {
  sudo pip install "$@"
  if [ $? -ne 0 ]; then
    echo "could not install $p - abort"
    exit 1
  fi
}

sudo apt-get update --fix-missing

# Installation script for doconce and all dependencies

# Translate this text file to .sh and .py scripts with
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# (git clone git@github.com:hplgit/vagrantbox.git)

# Install downloaded source code in ~/srclib
# cd
if [ ! -d srclib ]; then mkdir srclib; fi

# Version control systems
apt_install mercurial
apt_install git
apt_install subversion

cd srclib
git clone https://github.com/hplgit/doconce.git
if [ -d doconce ]; then cd doconce; sudo python setup.py install; cd ../..; fi

# Python
apt_install idle
apt_install ipython
apt_install python-pip
apt_install python-pdftools
pip_install sphinx
pip_install mako
pip_install -e svn+http://preprocess.googlecode.com/svn/trunk#egg=preprocess
pip_install -e hg+https://bitbucket.org/logg/publish#egg=publish

pip_install -e hg+https://bitbucket.org/ecollins/cloud_sptheme#egg=cloud_sptheme
pip_install -e git+https://github.com/ryan-roemer/sphinx-bootstrap-theme#egg=sphinx-bootstrap-theme
pip_install -e hg+https://bitbucket.org/miiton/sphinxjp.themes.solarized#egg=sphinxjp.themes.solarized
pip_install -e git+https://github.com/shkumagai/sphinxjp.themes.impressjs#egg=sphinxjp.themes.impressjs
pip_install -e git+https://github.com/kriskda/sphinx-sagecell#egg=sphinx-sagecell

pip_install -e git+https://bitbucket.org/sanguineturtle/pygments-ipython-console#egg=pygments-ipython-console

cd srclib
svn checkout http://ptex2tex.googlecode.com/svn/trunk/ ptex2tex
cd ptex2tex
sudo python setup.py install
cd latex
sh cp2texmf.sh
cd ../../..

# LaTeX
apt_install texinfo
apt_install texlive
apt_install texlive-extra-utils
apt_install texlive-latex-extra
apt_install texlive-latex-recommended
apt_install texlive-math-extra
apt_install texlive-font-utils
apt_install texlive-humanities
apt_install latexdiff
apt_install auctex

# Image manipulation
apt_install imagemagick
apt_install netpbm
apt_install mjpegtools
apt_install pdftk
apt_install giftrans
apt_install gv
apt_install evince
apt_install smpeg-plaympeg
apt_install mplayer
apt_install totem
apt_install libav-tools

# Misc
apt_install ispell
apt_install pandoc
apt_install libreoffice
apt_install unoconv
apt_install libreoffice-dmaths
#epydoc is old-fashioned
#pip install -e svn+https://epydoc.svn.sourceforge.net/svnroot/epydoc/trunk/epydoc#egg=epydoc

apt_install curl
apt_install a2ps
apt_install wdiff
apt_install meld
apt_install diffpdf
apt_install kdiff3
apt_install diffuse

# tkdiff.tcl:
#tcl8.5-dev tk8.5-dev blt-dev
#https://sourceforge.net/projects/tkdiff/

# example on installing mdframed.sty manually (it exists in texlive,
# but sometimes needs to be in its newest version)
git clone https://github.com/marcodaniel/mdframed
if [ -d mdframed ]; then cd mdframed; make localinstall; cd ..; fi
#$ echo "remove the mdframe directory (if successful install of mdframed.sty): rm -rf mdframed"
echo "Everything is successfully installed!"
