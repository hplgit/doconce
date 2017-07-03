basename = practical-guide
practical_guide_src = practical-guide.do.txt examples/*.do.txt
OUTDIR = ../../pub/practical-guide
practical_guide_html = $(OUTDIR)/practical-guide.html
practical_guide_pdf = $(OUTDIR)/practical-guide.pdf
practical_guide_tex = practical-guide.tex

HTML_OPTS = --encoding=utf-8 --html_style=bootswatch_readable --cite_doconce
PDF_OPTS = --encoding=utf-8 --cite_doconce --latex_code_style=vrb --latex_packages=parskip --siunits
#cannot use minted with doconce code

all: $(practical_guide_html) $(practical_guide_pdf)
$(practical_guide_html): $(practical_guide_src)
	@mkdir -p $(@D)
	doconce format html practical-guide $(HTML_OPTS)
	mv -f practical-guide.html $(practical_guide_html)

$(practical_guide_pdf): $(practical_guide_src)
	@mkdir -p $(@D)
	doconce format pdflatex practical-guide $(PDF_OPTS)
	pdflatex -shell-escape $(basename)
	#bibtex $(basename)
	makeindex $(basename)
	pdflatex -shell-escape $(basename)
	mv -f $(basename).pdf $(practical_guide_pdf)
	#pdflatex -shell-escape $(basename)
