basename = practical-guide
practical_guide_src = practical-guide.do.txt examples/*.do.txt
OUTDIR = ../../pub/practical-guide
practical_guide_html = $(OUTDIR)/practical-guide.html
practical_guide_pdf = $(OUTDIR)/practical-guide.pdf
practical_guide_tex = practical-guide.tex
primer_on_primes_src = examples/a_primer_on_primes.do.txt
primer_on_primes_includable = examples/a_primer_on_primes_.do.txt


HTML_OPTS = --encoding=utf-8 --html_style=bootswatch_readable --cite_doconce
PDF_OPTS = --encoding=utf-8 --cite_doconce --latex_code_style=vrb --latex_packages=parskip
#cannot use minted with doconce code

all: $(practical_guide_html) $(practical_guide_pdf)
# create copy of DocOnce source with `!b` and `!e` replaced by `|b` and `|e`
$(primer_on_primes_includable): $(primer_on_primes_src)
	cp -f $(primer_on_primes_src) $(primer_on_primes_includable)
	sed -r -i 's/^!([be])/\|\1/' $(primer_on_primes_includable)


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
