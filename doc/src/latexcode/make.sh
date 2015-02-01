#!/bin/sh
doconce pygmentize doc.do.txt perldoc

doconce format pdflatex doc --latex_code_style=vrb
pdflatex doc
cp doc.pdf doc_vrb.pdf

doconce format pdflatex doc --latex_code_style=pyg
pdflatex -shell-escape doc
cp doc.pdf doc_pyg.pdf

doconce format pdflatex doc --latex_code_style=pyg --minted_latex_style=perldoc
pdflatex -shell-escape doc
cp doc.pdf doc_pyg_perldoc.pdf

doconce format pdflatex doc --latex_code_style=lst
pdflatex doc
cp doc.pdf doc_lst.pdf

doconce format pdflatex doc --latex_code_style=lst-fenicsbook
pdflatex doc
cp doc.pdf doc_lst_fenicsyellow.pdf

doconce format pdflatex doc "--latex_code_style=lst-fenicsbook[numbers=left,numberstyle=\\tiny,numbersep=15pt]"
pdflatex doc
cp doc.pdf doc_lst_fenicsyellow_linenos.pdf

doconce format pdflatex doc "--latex_code_style=default:lst-fenicsbook@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt]"
pdflatex doc
cp doc.pdf doc_lst_sys.pdf

doconce format pdflatex doc "--latex_code_style=default:lst[style=fenicsbook]"
pdflatex doc
cp doc.pdf doc_lst_stylefb.pdf

doconce format pdflatex doc "--latex_code_style=default:lst-blue1[style=redblue,numbers=left,numberstyle=\\tiny,stepnumber=3,numbersep=15pt,xleftmargin=1mm]@dat:vrb-gray@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt]"
pdflatex doc
cp doc.pdf doc_lots.pdf

doconce format html demo --html_style=bootstrap_bloodish --html_code_style=inherit

dest=../../pub/latexcode
cp doc.do.txt.html doc_*.pdf demo.html $dest
