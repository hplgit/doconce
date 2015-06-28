'''

# #include "docstrings/docstring.dst.txt"

'''
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import *

__version__ = '1.0.3'
version = __version__
__author__ = 'Hans Petter Langtangen', 'Johannes H. Ring'
author = __author__

__acknowledgments__ = ''

from .doconce import doconce_format, DocOnceSyntaxError
