name=pyembed
doconce format html $name --html_style=bootstrap_bluegray --html_code_style=inherit --html_box_shadow=True

doconce format pdflatex $name --latex_code_style=pyg
pdflatex -shell-escape $name

dest=../../pub/pyembed
cp $name.pdf $name.html $dest
