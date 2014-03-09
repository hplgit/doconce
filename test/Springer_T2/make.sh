# Test of Springer T2 style for books
name=Springer_T2_book

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

rm -f tmp_*

system doconce format pdflatex $name CHAPTER=chapter BOOK=book APPENDIX=appendix -DPRIMER_BOOK ALG=code --encoding=utf-8 --device=paper --latex_exercise_numbering=chapter --latex_admon_color=1,1,1 --latex_admon=mdfbox  --latex_style=Springer_T2 --latex_title_layout=titlepage --latex_list_of_exercises=loe --latex_table_align=center --latex_admon_title_no_period

system ptex2tex $name
rm -rf $name.aux $name.ind $name.idx $name.bbl $name.toc $name.loe

system pdflatex $name
system bibtex $name
system makeindex $name
system pdflatex $name
system pdflatex $name
