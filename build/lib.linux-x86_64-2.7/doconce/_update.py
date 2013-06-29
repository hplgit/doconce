#!/usr/bin/env python

def system(cmd):
    print cmd
    failure = os.system(cmd)
    if failure:
        print 'could not run\n%s\in%s' % (cmd, os.getcwd())

def rmtree(directory):
    try:
        shutil.rmtree(directory)
    except OSError:
        pass # OK if the directory does not exist

def zip_dir(dirname):
    os.system('rm -rf %s/.git' % dirname)  # remove .git, all will be removed...
    system('zip -r %s.zip %s' % (dirname, dirname))

if __name__ == '__main__':
    # (important to not execute anything for epydoc)
    import os, shutil
    # the insertdocstr script is part of the Doconce package
    ##system('python ../../bin/doconce insertdocstr plain . ')

    # pack zip files distributed as data with doconce
    ##system('zip -r sphinx_themes.zip sphinx_themes')
    software_dir = 'misc_software'
    os.chdir(software_dir)
    system('zip -r html_images.zip html_images')
    rmtree('reveal.js')
    system('git clone git://github.com/hakimel/reveal.js.git')
    os.system('cp doconce_modifications/reveal/css/reveal*.css reveal.js/css/')
    os.system('cp doconce_modifications/reveal/css/theme/*.css reveal.js/css/theme/')
    zip_dir('reveal.js')

    rmtree('csss')
    system('git clone git://github.com/LeaVerou/csss.git')
    os.system('cp doconce_modifications/csss/*.css csss/')
    zip_dir('csss')

    rmtree('deck.js')
    system('git clone git://github.com/imakewebthings/deck.js.git')
    rmtree('mnml')
    system('git clone git://github.com/duijf/mnml.git')
    system('cp mnml/mnml.css deck.js/themes/style')
    rmtree('deckjs-theme-mozilla')
    system('git clone git://github.com/groovecoder/deckjs-theme-mozilla.git')
    system('cp deckjs-theme-mozilla/*.*css deck.js/themes/style')
    rmtree('deck.js-codemirror')
    system('git clone git://github.com/iros/deck.js-codemirror.git')
    os.mkdir('deck.js/extensions/codemirror')
    system('cp -r deck.js-codemirror/* deck.js/extensions/codemirror/')
    rmtree('deck.ext.js')
    system('git clone git://github.com/barraq/deck.ext.js.git')
    system('cp -r deck.ext.js/themes/style/*.*css deck.js/themes/style/')
    rmtree('deck.pointer.js')
    system('git clone git://github.com/mikeharris100/deck.pointer.js.git')
    os.mkdir('deck.js/extensions/pointer')
    system('cp -r deck.pointer.js/deck.pointer.* deck.js/extensions/pointer/')
    rmtree('presenterview')
    system('git clone git://github.com/stvnwrgs/presenterview.git')
    system('cp -r presenterview/ deck.js/extensions/')
    rmtree('deck.annotate.js')
    system('git clone git://github.com/nemec/deck.annotate.js.git')
    system('cp -r deck.annotate.js deck.js/extensions/')

    os.system('cp doconce_modifications/deck/core/*.css deck.js/core/')
    #os.system('cp doconce_modifications/deck/themes/style/*.css deck.js/themes/style/')

    system("find deck.js/extensions -name '.git' -exec rm -rf {} \;")
    zip_dir('deck.js')

    # minted.sty and anslistings.sty are not copied every time, get
    # the latest versions from ptex2tex (manually)
    zip_dir('latex_styles')

    """
    # No need to pack these - the styles and scripts are embedded
    if not os.path.isdir('dzslides'):
        system('git clone git://github.com/paulrouget/dzslides.git')
    else:
        system('cd dzslides; git pull origin master; cd ..')
    system('zip -r dzslides.zip dzslides')
    system('zip -d .git dzslides.zip')
    """
    system('cp *.zip ..')
    os.chdir(os.pardir)

    # remove files that are to be regenerated:
    #system('sh clean.sh')
    os.chdir(os.path.join(os.pardir, os.pardir))
    thisdir = os.getcwd()
    os.chdir(os.path.join('lib', 'doconce', 'docstrings'))
    system('sh ./clean.sh')
    os.chdir(thisdir)
    os.chdir(os.path.join('doc', 'tutorial'))
    system('sh ./clean.sh')
    os.chdir(thisdir)
    os.chdir(os.path.join('doc', 'manual'))
    system('sh ./clean.sh')
    os.chdir(thisdir)
    os.chdir(os.path.join('doc', 'quickref'))
    system('sh ./clean.sh')
    os.chdir(thisdir)
    os.chdir(os.path.join('doc', 'slides'))
    system('sh ./clean.sh')
    os.chdir(thisdir)
    os.chdir('test')
    system('sh ./clean.sh')
    os.chdir(thisdir)
    os.chdir('test')
    system('sh ./clean.sh')
    os.chdir(thisdir)

