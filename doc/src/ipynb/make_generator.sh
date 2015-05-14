#!/bin/sh
name=ipynb_generator

doconce format html $name --html_style=bootstrap_bluegray --html_code_style=inherit

dest=../../pub/ipynb
cp $name.html $dest
