#!/bin/sh
doconce format ipynb example

ipynb_figure=imgtag
ipynb_movie=ipynb
ipynb_admon=hrule
nbv=3

doconce format ipynb info --no_preprocess --ipynb_figure=${ipynb_figure} ipynb_figure=${ipynb_figure} --ipynb_movie=${ipynb_movie} ipynb_movie=${ipynb_movie} --ipynb_admon=${ipynb_admon} ipynb_admon=${ipynb_admon} --ipynb_version=$nbv --encoding=utf-8
# Must fix instructions since doconce performs certain actions for
# some of the code segments we demonstrate
doconce subst '" +%matplotlib inline\\n",\n +" +\\n",\n +' '' info.ipynb
doconce subst '"import numpy as np\\n"', '"%matplotlib inline\\n",\n      "import numpy as np\\n",' info.ipynb
doconce subst 'Plot\. \\\\label' 'Plot. label' info.ipynb

# Publish
dest=../../pub/ipynb
cp info.ipynb example.ipynb $dest
# All figs and movies are external on the web
