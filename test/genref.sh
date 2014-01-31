doconce format pdflatex genref1
doconce format pdflatex genref2
doconce ref_external genref2
cp _genref2.do.txt _tmp_genref2.do.txt
doconce replace "files=*.do.txt" "files=_tmp_genref2.do.txt" tmp_subst_references.sh
sh -x tmp_subst_references.sh