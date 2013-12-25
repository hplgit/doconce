#!/bin/sh
# Make demo of movie handling in Doconce
name=movies

doconce format html $name --html_output=movies_3choices.html
doconce format html $name --no_mp4_webm_ogg_alternatives
doconce format pdflatex $name
doconce ptex2tex $name
pdflatex $name
pdflatex $name
