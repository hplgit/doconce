# Test of tufte-book style for the Springer T2/T4 trial manu
name=Springer_T2_book
style=T4

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

rm -f tmp_*

system doconce format pdflatex $name CHAPTER=chapter BOOK=book APPENDIX=appendix -DPRIMER_BOOK ALG=code --encoding=utf-8 --device=paper --exercise_numbering=chapter --latex_admon_color=1,1,1 --latex_admon=mdfbox  --latex_style=tufte-book --latex_title_layout=titlepage --latex_list_of_exercises=loe --latex_table_format=center --latex_admon_title_no_period --exercises_in_zip --exercises_in_zip_filename=chapter --allow_refs_to_external_docs "--latex_code_style=default:vrb-blue1@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt,fontsize=\fontsize{9pt}{9pt}]" --latex_fancy_header

rm -rf $name.aux $name.ind $name.idx $name.bbl $name.toc $name.loe

system pdflatex $name
system bibtex $name
system makeindex $name
system pdflatex $name
system pdflatex $name
