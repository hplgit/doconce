#!/bin/bash -x
# Compile the book to LaTeX/PDF.
#
# Usage: make.sh [nospell]
#
# With nospell, spellchecking is skipped.

set -x

name=book
topicname=my

encoding="--encoding=utf-8"

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

rm -rf tmp_* *.dolog

if [ $# -ge 1 ]; then
  spellcheck=$1
else
  spellcheck=spell
fi

# No spellchecking of local files here since book.do.txt just includes files.
# Spellcheck all *.do.txt files in each chapter.
if [ "$spellcheck" != 'nospell' ]; then
system doconce spellcheck -d .dict4spell.txt *.do.txt
fi

system preprocess -DFORMAT=pdflatex newcommands.p.tex > newcommands.tex
# svmono requires this:
doconce replace 'newcommand{\E}' 'renewcommand{\E}' newcommands.tex
doconce replace 'newcommand{\I}' 'renewcommand{\I}' newcommands.tex

opt1=

function edit_solution_admons {
    # We use question admon for typesetting solution, but let's edit to
    # somewhat less eye catching than the std admon
    # (also note we use --latex_admon_envir_map= in compile)
    doconce replace 'notice_mdfboxadmon}[Solution.]' 'question_mdfboxadmon}[Solution.]' ${mainname}.tex
    doconce replace 'end{notice_mdfboxadmon} % title: Solution.' 'end{question_mdfboxadmon} % title: Solution.' ${mainname}.tex
    doconce subst -s '% "question" admon.+?question_mdfboxmdframed\}' '% "question" admon
\colorlet{mdfbox_question_background}{gray!5}
\\newmdenv[        % edited for solution admons in exercises
  skipabove=15pt,
  skipbelow=15pt,
  outerlinewidth=0,
  backgroundcolor=white,
  linecolor=black,
  linewidth=1pt,       % frame thickness
  frametitlebackgroundcolor=blue!5,
  frametitlerule=true,
  frametitlefont=\\normalfont\\bfseries,
  shadow=false,        % frame shadow?
  shadowsize=11pt,
  leftmargin=0,
  rightmargin=0,
  roundcorner=5,
  needspace=0pt,
]{question_mdfboxmdframed}' ${mainname}.tex
}

function compile {
    options="$@"
    system doconce format pdflatex $name $opt1 --exercise_numbering=chapter   --latex_style=Springer_sv --latex_title_layout=std --latex_list_of_exercises=none --latex_admon=mdfbox --latex_admon_color=1,1,1 --latex_table_format=left --latex_admon_title_no_period --latex_no_program_footnotelink "--latex_code_style=default:lst[style=graycolor]@pypro2:lst[style=greenblue]@pycod2:lst[style=greenblue]@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt,fontsize=\fontsize{9pt}{9pt}]" --exercises_as_subsections $encoding $options --exercise_solution=admon --latex_admon_envir_map=2
#No syntax highlighting: "--latex_code_style=default:vrb-gray@sys:vrb[frame=lines,label=\\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt,fontsize=\fontsize{9pt}{9pt}]"

# Auto edits
edit_solution_admons
system doconce replace 'linecolor=black,' 'linecolor=darkblue,' $name.tex
system doconce subst 'frametitlebackgroundcolor=.*?,' 'frametitlebackgroundcolor=blue!5,' $name.tex
# Fix UTF-8 problem with svmono
#system doconce replace '%\usepackage[utf8x]' '\usepackage[utf8x]'  $name.tex

rm -rf $name.aux $name.ind $name.idx $name.bbl $name.toc $name.loe

system pdflatex $name
system bibtex $name
system makeindex $name
system pdflatex $name
system pdflatex $name
system makeindex $name
system pdflatex $name
}

# Important: run with solutions first such that the .aux file
# for the book, referred to by other documents, uses the .aux
# file corresponding to a version without solutions.

# EXV: Extended version
# Printed book has EXV False, all other versions on github has
# EXV True

# With solutions, PDF for screen, password protected
compile --device=screen EXV=True
newname=${topicname}-book-4screen-sol
password="s!c!ale"
#pdftk $name.pdf output $newname.pdf owner_pw foo user_pw $password
cp $name.pdf $newname.pdf
cp $name.log ${newname}.log

# Without solutions, PDF for screen
compile --device=screen --without_solutions --without_answers EXV=True
newname=${topicname}-book-4screen
cp $name.pdf $newname.pdf
cp $name.log ${newname}.log

# Printed book without exercises and extra material
compile --device=paper --without_solutions --without_answers EXV=False --allow_refs_to_external_docs
newname=${topicname}-book-4print
cp $name.pdf $newname.pdf
pdfnup --frame true --outfile ${newname}-2up.pdf $newname.pdf
cp $name.aux ${newname}.aux-final
cp $name.tex ${newname}.tex
cp $name.log ${newname}.log

# Check grammar in MS Word:
# doconce spellcheck tmp_mako__book.do.txt
# load tmp_stripped_book.do.txt into Word

# Publish
repo=../pub
dest=${repo}/book
if [ ! -d $dest ]; then mkdir $dest; fi
if [ ! -d $dest/pdf ]; then mkdir $dest/pdf; fi
cp ${topicname}-book*.pdf $dest/pdf

src_dest=../../src
if [ ! -d $src_dest ]; then
echo "No directory $src_dest"
exit 1
fi
cd src

if [ -f clean.sh ]; then
sh clean.sh
fi
# Pack all Python, C++, Cython, C source code for the book and publish in src directory
cd ..
files=`find src \( -name '*.py' -o -name '*.pyx' -o -name '*.f' -o -name '*.c' -o -name '*.cpp' -o -name 'make*.sh' \) -print`
tar cfz tmp.tar.gz $files
mv -f tmp.tar.gz $src_dest
cd $src_dest
tar xfz tmp.tar.gz
rm -f tmp.tar.gz
cd -

cd $dest; git add .; cd -

# Report typical problems with the book (too long lines,
# undefined labels, etc.). Here we report lines that are more than 10pt
# too long.
doconce latex_problems $name.log 10
