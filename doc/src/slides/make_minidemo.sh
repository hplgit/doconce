# Minimalistic script for translating a mini demo of slides into
# IPython notebook format, Beamer slides, and Reveal slides.
name=minidemo

# IPython notebook
doconce format ipynb $name

# LaTeX Beamer
doconce format pdflatex $name --latex_title_layout=beamer
doconce ptex2tex $name envir=minted  # pygments code style
doconce slides_beamer $name --beamer_slide_theme=red_shadow
pdflatex -shell-escape $name

# Reveal
doconce format html $name --pygments_html_style=perldoc --keep_pygments_html_bg
doconce slides_html $name reveal --html_slide_theme=beige

cp $name.pdf $name.html $name.ipynb minidemo_fig.png ../../pub/slides
