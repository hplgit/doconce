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

doconce format pdflatex doc --latex_code_style=lst-yellow2
pdflatex doc
cp doc.pdf doc_lst_yellow2.pdf

doconce format pdflatex doc "--latex_code_style=lst-yellow2[numbers=left,numberstyle=\\tiny,numbersep=15pt,breaklines=true]"
pdflatex doc
cp doc.pdf doc_lst_yellow2_linenos.pdf

doconce format pdflatex doc "--latex_code_style=default:lst-yellow2@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt,fontsize=\fontsize{9pt}{9pt}]"
pdflatex doc
cp doc.pdf doc_lst_sys.pdf

doconce format pdflatex doc "--latex_code_style=default:lst[style=yellow2_fb]"
pdflatex doc
cp doc.pdf doc_lst_style_fenicsbook.pdf

doconce format pdflatex doc "--latex_code_style=default:lst[style=blue1]@pypro:lst[style=blue1bar]@dat:lst[style=gray]@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt,fontsize=\fontsize{9pt}{9pt}]"
pdflatex doc
cp doc.pdf doc_lst_style_primer.pdf

doconce format pdflatex doc "--latex_code_style=default:pyg-blue1@dat:lst[style=gray]@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt,fontsize=\fontsize{9pt}{9pt}]" --latex_code_bg_vpad
pdflatex -shell-escape doc
cp doc.pdf doc_pyg_style_primer_vpad.pdf

doconce format pdflatex doc "--latex_code_style=default:vrb-blue1@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt,fontsize=\fontsize{9pt}{9pt}]"
pdflatex doc
cp doc.pdf doc_vrb_style_primer.pdf

doconce format pdflatex doc "--latex_code_style=default:vrb-blue1@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt,fontsize=\fontsize{9pt}{9pt}]" --latex_code_bg_vpad
pdflatex doc
cp doc.pdf doc_vrb_style_primer_vpad.pdf

doconce format pdflatex doc
ptex2tex doc
pdflatex doc
cp doc.pdf doc_ptex2tex_primer.pdf

doconce format pdflatex doc "--latex_code_style=default:lst-blue1[style=redblue,numbers=left,numberstyle=\\tiny,stepnumber=3,numbersep=15pt,xleftmargin=1mm]@dat:vrb-gray@sys:vrb[frame=lines,label=\\fbox{{\\tiny Terminal}},framesep=2.5mm,framerule=0.7pt,fontsize=\fontsize{9pt}{9pt}]"
pdflatex doc
cp doc.pdf doc_lots.pdf

doconce format pdflatex doc_udef --latex_code_style=lst
pdflatex doc_udef

doconce format html demo --html_style=bootstrap_bloodish --html_code_style=inherit

dest=../../pub/latexcode
cp doc.do.txt.html doc_*.pdf demo.html $dest
