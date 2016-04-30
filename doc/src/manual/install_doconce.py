#!/usr/bin/env python
# Automatically generated script by
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# where vagrantbox is the directory arising from
# git clone git@github.com:hplgit/vagrantbox.git

# The script is based on packages listed in debpkg_doconce.txt.

logfile = 'tmp_output.log'  # store all output of all operating system commands
f = open(logfile, 'w'); f.close()  # touch logfile so it can be appended

import subprocess, sys

def system(cmd):
    """Run system command cmd."""
    print cmd
    try:
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print 'Command\n  %s\nfailed.' % cmd
        print 'Return code:', e.returncode
        print e.output
        sys.exit(1)
    print output
    f = open(logfile, 'a'); f.write(output); f.close()

system('sudo apt-get update --fix-missing')
# Installation script for doconce and all dependencies

# This script is translated from
# doc/src/manual/debpkg_doconce.txt
# in the doconce source tree, with help of
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# (git clone git@github.com:hplgit/vagrantbox.git)

# Python v2.7 must be installed (doconce does not work with v3.x)


cmd = """
pyversion=`python -c 'import sys; print sys.version[:3]'`
if [ $pyversion != '2.7' ]; then echo "Python v${pyversion} cannot be used with DocOnce"; exit 1; fi
# Install downloaded source code in subdirectory srclib

if [ ! -d srclib ]; then mkdir srclib; fi
# Version control systems

"""
system(cmd)
system('sudo apt-get -y install mercurial')
system('sudo apt-get -y install git')
system('sudo apt-get -y install subversion')

# --- Python-based packages and tools ---
system('sudo apt-get -y install python-pip')
system('sudo apt-get -y install idle')
system('sudo apt-get -y install python-dev')
system('sudo apt-get -y install python-setuptools')
# upgrade
system('sudo pip install setuptools')
system('sudo apt-get -y install python-pdftools')
system('sudo pip install ipython')
system('sudo pip install tornado')
system('sudo pip install pyzmq')
system('sudo pip install traitlets')
system('sudo pip install pickleshare')
system('sudo pip install jsonschema')
# If problems with IPython.nbformat.v4: clone ipython and run setup.py
# to get the latest version

# Preprocessors
system('sudo pip install future')
system('sudo pip install mako')
system('sudo pip install -e git+https://github.com/hplgit/preprocess#egg=preprocess')

# Publish for handling bibliography
system('sudo pip install python-Levenshtein')
system('sudo apt-get -y install libxml2-dev')
system('sudo apt-get -y install libxslt1-dev')
system('sudo apt-get -y install zlib1g-dev')
system('sudo pip install lxml')
system('sudo pip install -e hg+https://bitbucket.org/logg/publish#egg=publish')

# Sphinx (with additional third/party themes)
system('sudo pip install sphinx')

system('sudo pip install alabaster')
system('sudo pip install sphinx_rtd_theme')
system('sudo pip install -e hg+https://bitbucket.org/ecollins/cloud_sptheme#egg=cloud_sptheme')
system('sudo pip install -e git+https://github.com/ryan-roemer/sphinx-bootstrap-theme#egg=sphinx-bootstrap-theme')
system('sudo pip install -e hg+https://bitbucket.org/miiton/sphinxjp.themes.solarized#egg=sphinxjp.themes.solarized')
system('sudo pip install -e git+https://github.com/shkumagai/sphinxjp.themes.impressjs#egg=sphinxjp.themes.impressjs')
system('sudo pip install -e git+https://github.com/kriskda/sphinx-sagecell#egg=sphinx-sagecell')
system('sudo pip install tinkerer')

# Runestone sphinx books
system('sudo pip install sphinxcontrib-paverutils')
system('sudo pip install paver')
system('sudo pip install cogapp')

#pip install -e git+https://bitbucket.org/sanguineturtle/pygments-ipython-console#egg=pygments-ipython-console
system('sudo pip install -e git+https://bitbucket.org/hplbit/pygments-ipython-console#egg=pygments-ipython-console')
system('sudo pip install -e git+https://github.com/hplgit/pygments-doconce#egg=pygments-doconce')

# XHTML
system('sudo pip install beautifulsoup4')
system('sudo pip install html5lib')

# ptex2tex is not needed if --latex_code_style= option is used

cmd = """
cd srclib
svn checkout http://ptex2tex.googlecode.com/svn/trunk/ ptex2tex
cd ptex2tex
sudo python setup.py install
cd latex
sh cp2texmf.sh
cd ../../..
# LaTeX

"""
system(cmd)
system('sudo apt-get -y install texinfo')
system('sudo apt-get -y install texlive')
system('sudo apt-get -y install texlive-extra-utils')
system('sudo apt-get -y install texlive-latex-extra')
system('sudo apt-get -y install texlive-latex-recommended')
system('sudo apt-get -y install texlive-math-extra')
system('sudo apt-get -y install texlive-font-utils')
system('sudo apt-get -y install texlive-humanities')
system('sudo apt-get -y install latexdiff')
system('sudo apt-get -y install auctex')

# Image manipulation
system('sudo apt-get -y install imagemagick')
system('sudo apt-get -y install netpbm')
system('sudo apt-get -y install mjpegtools')
system('sudo apt-get -y install pdftk')
system('sudo apt-get -y install giftrans')
system('sudo apt-get -y install gv')
system('sudo apt-get -y install evince')
system('sudo apt-get -y install smpeg-plaympeg')
system('sudo apt-get -y install mplayer')
system('sudo apt-get -y install totem')
system('sudo apt-get -y install libav-tools')

# Misc
system('sudo apt-get -y install ispell')
system('sudo apt-get -y install pandoc')
system('sudo apt-get -y install libreoffice')
system('sudo apt-get -y install unoconv')
system('sudo apt-get -y install libreoffice-dmaths')
#epydoc is an old-fashioned output format, will any doconce user use it?
#pip install -e svn+https://epydoc.svn.sourceforge.net/svnroot/epydoc/trunk/epydoc#egg=epydoc

system('sudo apt-get -y install curl')
system('sudo apt-get -y install a2ps')
system('sudo apt-get -y install wdiff')
system('sudo apt-get -y install meld')
system('sudo apt-get -y install diffpdf')
system('sudo apt-get -y install kdiff3')
system('sudo apt-get -y install diffuse')

# tkdiff.tcl:
#tcl8.5-dev tk8.5-dev blt-dev
#https://sourceforge.net/projects/tkdiff/

# example on installing mdframed.sty manually (it exists in texlive,
# but sometimes needs to be in its newest version)

print 'Everything is successfully installed!'
