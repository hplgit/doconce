#!/bin/sh
doconce format sphinx demo
doconce sphinx_dir theme=redcloud demo
python automake_sphinx.py

doconce format html demo
