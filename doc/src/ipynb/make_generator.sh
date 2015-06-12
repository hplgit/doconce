#!/bin/sh
name=ipynb_generator

doconce format html $name --html_style=bootstrap_bluegray --html_code_style=inherit
# Note: --no_mako is not necessary although there is a lot of mako
# instructions not to be interpreted by mako, but these are all in
# inclueded files and therefore not seen by mako.

dest=../../pub/ipynb
cp $name.html $dest
