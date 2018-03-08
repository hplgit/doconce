#!/bin/bash
# Automatically generated script by deb2sh.py.

# The script is based on packages listed in debpkg_doconce.txt.

set -x  # make sure each command is printed in the terminal

function apt_install {
  sudo apt-get -y --no-install-recommends install $1
  if [ $? -ne 0 ]; then
    echo "could not install $1 - abort"
    exit 1
  fi
}

function pip_install {
  sudo pip install --upgrade "$@"
  if [ $? -ne 0 ]; then
    echo "could not install $p - abort"
    exit 1
  fi
}

sudo apt-get update --fix-missing -qq

# Installation script for doconce and all dependencies

# This script is translated from
# doc/src/manual/debpkg_doconce.txt
# in the doconce source tree, with help of
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# (git clone git@github.com:hplgit/vagrantbox.git)

# If no python installation available, install default python
command -v python >/dev/null 2>&1 || apt_install python

# Python v2.7 must be installed (doconce does not work with v3.x)
pyversion=`python -c 'import sys; print sys.version[:3]'`
if [ $pyversion != '2.7' ]; then echo "Python v${pyversion} cannot be used with DocOnce"; exit 1; fi

# Install downloaded source code in subdirectory srclib
if [ ! -d srclib ]; then mkdir srclib; fi

# Build essentials
apt_install build-essential

# Version control systems
apt_install mercurial
apt_install git
apt_install subversion

# --- Python-based packages and tools ---
apt_install python-pip
apt_install idle
apt_install python-dev
apt_install python-setuptools
# upgrade
pip_install setuptools
apt_install python-pdftools
pip_install ipython
pip_install tornado
pip_install pyzmq
pip_install traitlets
pip_install pickleshare
pip_install jsonschema
# If problems with IPython.nbformat.v4: clone ipython and run setup.py
# to get the latest version

# Preprocessors
pip_install future
pip_install mako
pip_install -e git+https://github.com/doconce/preprocess#egg=preprocess

# Publish for handling bibliography
pip_install python-Levenshtein
apt_install libxml2-dev
apt_install libxslt1-dev
apt_install zlib1g-dev
pip_install lxml
pip_install -e hg+https://bitbucket.org/logg/publish#egg=publish

# Sphinx (with additional third/party themes)
pip_install sphinx

pip_install alabaster
pip_install sphinx_rtd_theme
pip_install -e hg+https://bitbucket.org/ecollins/cloud_sptheme#egg=cloud_sptheme
pip_install -e git+https://github.com/ryan-roemer/sphinx-bootstrap-theme#egg=sphinx-bootstrap-theme
pip_install -e hg+https://bitbucket.org/miiton/sphinxjp.themes.solarized#egg=sphinxjp.themes.solarized
pip_install -e git+https://github.com/shkumagai/sphinxjp.themes.impressjs#egg=sphinxjp.themes.impressjs
pip_install -e git+https://github.com/kriskda/sphinx-sagecell#egg=sphinx-sagecell
# tinkerer has several themes: minimal5, modern5, flat, dark, responsive
#pip install tinkerer --upgrade

# Runestone sphinx books
pip_install sphinxcontrib-paverutils
pip_install paver
pip_install cogapp

#pip install -e git+https://bitbucket.org/sanguineturtle/pygments-ipython-console#egg=pygments-ipython-console
pip_install -e git+https://bitbucket.org/hplbit/pygments-ipython-console#egg=pygments-ipython-console
pip_install -e git+https://github.com/hplgit/pygments-doconce#egg=pygments-doconce

# XHTML
pip_install beautifulsoup4
pip_install html5lib

# ptex2tex is not needed if the --latex_code_style= option is used
cd srclib
git clone git@github.com:hplgit/ptex2tex.git
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
apt_install texlive-fonts-extra
apt_install texlive-humanities
apt_install texlive-generic-extra
apt_install texlive-xetex
apt_install latexdiff
apt_install auctex

# Image manipulation
apt_install imagemagick
apt_install inkscape
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
#epydoc is an old-fashioned output format, will any doconce user use it?
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

# DocOnce itself
cd srclib
git clone https://github.com/hplgit/doconce.git
if [ -d doconce ]; then cd doconce; sudo python setup.py install; cd ../..; fi
echo "Everything is successfully installed!"
