#!/bin/bash
# Automatically generated script. Based on debpkg_doconce.txt.

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

function unix_command {
  "$@"
  if [ $? -ne 0 ]; then
    echo "could not run $@ - abort"
    exit 1
  fi
}

sudo apt-get update --fix-missing

# Translate this text file to .sh and .py scripts with
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# (git clone git@github.com:hplgit/vagrantbox.git)

# Version control systems
apt_install mercurial
apt_install git
apt_install subversion

unix_command cd srclib
unix_command hg clone https://code.google.com/p/doconce/
unix_command cd doconce
unix_command sudo python setup.py install
unix_command cd ../..

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

unix_command cd srclib
unix_command svn checkout http://ptex2tex.googlecode.com/svn/trunk/ ptex2tex
unix_command cd ptex2tex
unix_command sudo python setup.py install
unix_command cd latex
unix_command sh cp2texmf.sh
unix_command cd ../../..

# LaTeX
apt_install texinfo
# These lines are only necessary for Ubuntu 12.04 to install texlive 2012
unix_command ubuntu_version=`lsb_release -r | awl '{print $2}'`
unix_command if [ $ubuntu_version = "12.04" ]; then
unix_command sudo add-apt-repository ppa:texlive-backports/ppa
unix_command sudo apt-get update
unix_command fi
apt_install texlive
apt_install texlive-extra-utils
apt_install texlive-latex-extra
apt_install texlive-math-extra
apt_install texlive-font-utils
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
apt_install ffmpeg
apt_install libav-tools

# Misc
apt_install ispell
apt_install pandoc
apt_install libreoffice
apt_install unoconv
apt_install libreoffice-dmaths
pip_install -e svn+https://epydoc.svn.sourceforge.net/svnroot/epydoc/trunk/epydoc#egg=epydoc

apt_install curl
apt_install a2ps
apt_install wdiff
apt_install meld
apt_install xxdiff
apt_install diffpdf
apt_install kdiff3
apt_install diffuse

# tkdiff.tcl:
#tcl8.5-dev tk8.5-dev blt-dev
#https://sourceforge.net/projects/tkdiff/

# example on installing mdframed.sty (in texlive) manually
# curl -O http://ctan.uib.no/macros/latex/contrib/mdframed/mdframed.dtx
# alternative: git clone https://github.com/marcodaniel/mdframed
# texdir=~/texmf/tex/latex/misc
# if [ ! -d $texdir ]; then mkdir -p $texdir; fi
# cp mdframed.sty $texdir/
# cd $texdir/../../..
# mktexlsr .
# cd -
# rm -f md-frame-* mdframed.*
echo "Everything is successfully installed!"
