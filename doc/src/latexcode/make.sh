#!/bin/sh

doconce format pdflatex doc "--latex_code_style=default:lst-blue1[style=redblue,numbers=left=numberstyle=\\tiny,stepnumber=3,numbersep=15pt,xleftmargin=1mm]@dat:vrb-gray@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt]"
pdflatex doc
cp doc.pdf doc_1.pdf
