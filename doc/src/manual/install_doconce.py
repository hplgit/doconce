\
#!/usr/bin/env python
# Automatically generated script. Based on debpkg_doconce.txt.

import commands, sys

def system(cmd):
    """Run system command cmd."""
    failure, output = commands.getstatusoutput(cmd)
    if failure:
       print 'Command\n  %s\nfailed.' % cmd
       print output
       sys.exit(1)

system('sudo apt-get update --fix-missing')
# Translate this text file to .sh and .py scripts with
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# (git clone git@github.com:hplgit/vagrantbox.git)

# Version control systems
system('sudo apt-get -y install mercurial')
system('sudo apt-get -y install git')
system('sudo apt-get -y install subversion')

system('cd srclib')
system('hg clone https://code.google.com/p/doconce/')
system('cd doconce')
system('sudo python setup.py install')
system('cd ../..')

# Python
system('sudo apt-get -y install idle')
system('sudo apt-get -y install ipython')
system('sudo apt-get -y install python-pip')
system('sudo apt-get -y install python-pdftools')
sudo pip install sphinx 
sudo pip install mako

sudo pip install -e svn+http://preprocess.googlecode.com/svn/trunk#egg=preprocess

sudo pip install -e hg+https://bitbucket.org/logg/publish#egg=publish


sudo pip install -e hg+https://bitbucket.org/ecollins/cloud_sptheme#egg=cloud_sptheme

sudo pip install -e git+https://github.com/ryan-roemer/sphinx-bootstrap-theme#egg=sphinx-bootstrap-theme

sudo pip install -e hg+https://bitbucket.org/miiton/sphinxjp.themes.solarized#egg=sphinxjp.themes.solarized

sudo pip install -e git+https://github.com/shkumagai/sphinxjp.themes.impressjs#egg=sphinxjp.themes.impressjs

sudo pip install -e git+https://github.com/kriskda/sphinx-sagecell#egg=sphinx-sagecell


system('cd srclib')
system('svn checkout http://ptex2tex.googlecode.com/svn/trunk/ ptex2tex')
system('cd ptex2tex')
system('sudo python setup.py install')
system('cd latex')
system('sh cp2texmf.sh')
system('cd ../../..')

# LaTeX
system('sudo apt-get -y install texinfo')
# These lines are only necessary for Ubuntu 12.04 to install texlive 2012
system('ubuntu_version=`lsb_release -r | awl '{print $2}'`')
system('if [ $ubuntu_version = "12.04" ]; then')
system('sudo add-apt-repository ppa:texlive-backports/ppa')
system('sudo apt-get update')
system('fi')
system('sudo apt-get -y install texlive')
system('sudo apt-get -y install texlive-extra-utils')
system('sudo apt-get -y install texlive-latex-extra')
system('sudo apt-get -y install texlive-math-extra')
system('sudo apt-get -y install texlive-font-utils')
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
system('sudo apt-get -y install ffmpeg')
system('sudo apt-get -y install libav-tools')

# Misc
system('sudo apt-get -y install ispell')
system('sudo apt-get -y install pandoc')
system('sudo apt-get -y install libreoffice')
system('sudo apt-get -y install unoconv')
system('sudo apt-get -y install libreoffice-dmaths')
sudo pip install -e svn+https://epydoc.svn.sourceforge.net/svnroot/epydoc/trunk/epydoc#egg=epydoc


system('sudo apt-get -y install curl')
system('sudo apt-get -y install a2ps')
system('sudo apt-get -y install wdiff')
system('sudo apt-get -y install meld')
system('sudo apt-get -y install xxdiff')
system('sudo apt-get -y install diffpdf')
system('sudo apt-get -y install kdiff3')
system('sudo apt-get -y install diffuse')

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
print 'Everything is successfully installed!'
