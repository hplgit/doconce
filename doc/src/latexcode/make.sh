#!/bin/sh

doconce format pdflatex doc --latex_code_style=lst-blue1[style=redblue,numbers=left=numberstyle=\\tiny,stepnumber=3,numbersep=15pt]
pdflatex doc
cp doc.pdf doc_lst_blue1_redblue.pdf
