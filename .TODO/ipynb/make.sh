#!/bin/sh
name=test_ipynb
fig_prefix=https://raw.githubusercontent.com/hplgit/wavebc/master/doc/pub/
bootsdark="--pygments_html_style=monokai --keep_pygments_html_bg --html_code_style=inherit --html_pre_style=inherit"

doconce format ipynb $name --figure_prefix=$fig_prefix --movie_prefix=$fig_prefix --ipynb_movie=HTML  # --ipynb_movie=md, local
cp $name.ipynb ${name}_HTML.ipynb

doconce format ipynb $name --figure_prefix=$fig_prefix --movie_prefix=$fig_prefix --ipynb_movie=md
cp $name.ipynb ${name}_md.ipynb

# Just for test
doconce format html $name --figure_prefix=$fig_prefix --html_style=bootswatch_darkly $bootsdark --figure_prefix=$fig_prefix --movie_prefix=$fig_prefix
