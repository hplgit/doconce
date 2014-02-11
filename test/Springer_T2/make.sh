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

rm tmp_*

system doconce format pdflatex $name CHAPTER=chapter BOOK=book APPENDIX=appendix -DPRIMER_BOOK -DDOCONCE ALG=code --encoding=utf-8 --device=paper --latex_exercise_numbering=chapter --latex_admon_color=1,1,1

system ptex2tex -DLATEX_STYLE=Springer_T2 -DLATEX_HEADING=titlepage -DLIST_OF_EXERCISES=loe $name
rm -rf $name.aux $name.ind $name.idx $name.bbl $name.toc $name.loe

system pdflatex $name
system bibtex $name
system makeindex $name
system pdflatex $name
system pdflatex $name
