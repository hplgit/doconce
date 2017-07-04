#!/usr/bin/env python
"""
Usage of this setup.py script:

python setup.py install [, --prefix=$PREFIX]

"""
from __future__ import print_function
#from builtins import str
__author__ = 'Hans Petter Langtangen <hpl@simula.no>'
__acknowledgements__ = 'Johannes H. Ring',

from setuptools import setup

import os, sys, glob, gzip, tempfile

# Make sure we import from doconce in this package, not an installed one:
# (need this for extracting the version below)
sys.path.insert(0, os.path.join('lib'))
#import doconce
__version__ = '1.4.1'

man_filename = os.path.join("doc", "man", "man1", "doconce.1")
if "install" in sys.argv:
    # Compresses the man page
    try:
        man_inputfile = open(man_filename, 'rb')
        man_contents = man_inputfile.read()
        man_inputfile.close()

        # Temporary destination for the man page
        tmp_filename = tempfile.mktemp(os.path.sep + os.path.basename(man_filename) + ".gz")

        # Make dir if the path doesn't already exist
        base_dir = os.path.dirname(tmp_filename)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        man_outputfile = gzip.open(tmp_filename, 'wb')
        man_outputfile.write(man_contents)
        man_outputfile.close()

        man_filename = tmp_filename
    except IOError as msg:
        print("Unable to compress man page: %s" % msg)



setup(
    version = __version__,
    author = "Hans Petter Langtangen",
    author_email = "<hpl@simula.no>",
    maintainer = "Kristian Gregorius Hustad",
    maintainer_email = "<krihus@ifi.uio.no>",
    description = __doc__,
    license = "BSD",
    name = "DocOnce",
    url = "https://github.com/hplgit/doconce",
    package_dir = {'': 'lib'},
    packages = ['doconce'],
    # list individual modules if not all files are wanted as part
    # of the package (note: this does not work
    # with package_data - must just specify the package name)
    #py_modules = ['doconce.common', 'doconce.doconce', ...]
    package_data = {'': ['sphinx_themes.zip', 'html_images.zip', 'reveal.js.zip', 'deck.js.zip', 'csss.zip', 'latex_styles.zip']},
    scripts = [os.path.join('bin', f) for f in ['doconce']],
    data_files=[(os.path.join("share", "man", "man1"),[man_filename,]),],
    install_requires=[
        'pygments',
        'preprocess',
        'mako',
        'future'
    ],
    dependency_link=[
        'git+https://github.com/doconce/preprocess#egg=preprocess',
    ],
    )

# Clean up the temporary compressed man page
if man_filename.endswith(".gz") and os.path.isfile(man_filename):
    if "-q" not in sys.argv or "--quiet" not in sys.argv:
        print("Removing %s" % man_filename)
    os.remove(man_filename)
