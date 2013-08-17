#!/bin/sh

# make Epydoc API manual of doconce module:
cd ../../lib/doconce/docstrings
doconce format epytext docstring.do.txt
mv -f docstring.epytext docstring.dst.txt
cd ..
preprocess __init__.p.py > __init__.py
cd ..
rm -rf html
epydoc doconce


# make Sphinx API manual of doconce module:
cd doconce/docstrings
doconce format sphinx docstring.do.txt
mv -f docstring.rst docstring.dst.txt
cd ..
preprocess __init__.p.py > __init__.py
cd ../../doc/api-source/sphinx-rootdir
make clean
make html

# make ordinary Python module files with doc strings:
cd ../../../lib/doconce/docstrings
doconce format plain docstring.do.txt
mv -f docstring.txt docstring.dst.txt
cd ..
preprocess __init__.p.py > __init__.py

# copy to api if ok:
cd ../../doc
rm -rf api/sphinx api/epydoc
cp -r api-source/sphinx-rootdir/_build/html api/sphinx
cp -r ../lib/html api/epydoc
rm -rf ../lib/html
