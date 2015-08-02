#!/usr/bin/env python
"""
Usage of this setup.py script:

python setup.py install [, --prefix=$PREFIX]

"""
from __future__ import print_function
#from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import str
__author__ = 'Hans Petter Langtangen <hpl@simula.no>'
__acknowledgemets__ = 'Johannes H. Ring',

from distutils.core import setup

import os, sys, glob, gzip, tempfile

# Make sure we import from doconce in this package, not an installed one:
# (need this for extracting the version below)
sys.path.insert(0, os.path.join('lib')); import doconce

# Make doconce_config_default.py file (based on newest set of options)
import doconce.misc
config_variables = []  # list of (var, value) pairs
for opt in doconce.misc._legal_command_line_options:
    var = opt[2:]
    if var[-1] == '=':
        var = var[:-1]
        value = ''
    else:
        value = 'False'
    config_variables.append((var.replace('-', '_'), value))
config = open(os.path.join('lib', 'doconce', 'doconce_config_default.py'), 'w')
config.write(u'''\
"""
Configuration of Doconce parameters that can also be set
on the command line.
For example, a line in this file:

some_option = some_value

corresponds to a command-line option --some_option=some_value
"""

''')
for var, value in config_variables:
    line = '%s = %s' % (var, value)
    if value == '':
        line = '#' + line
    config.write(line + u'\n')
config.close()

setup(
    version = str(doconce.version),
    author = "Hans Petter Langtangen",
    author_email = "<hpl@simula.no>",
    description = __doc__,
    license = "BSD",
    name = "Doconce",
    url = "https://github.com/hplgit/doconce",
    package_dir = {'': 'lib'},
    packages = ['doconce'],
    # list individual modules if not all files are wanted as part
    # of the package (note: this does not work
    # with package_data - must just specify the package name)
    #py_modules = ['doconce.common', 'doconce.doconce', ...]
    package_data = {'': ['sphinx_themes.zip', 'html_images.zip', 'reveal.js.zip', 'deck.js.zip', 'csss.zip', 'latex_styles.zip']},
    scripts = [os.path.join('bin', f) for f in ['doconce']],
    )
