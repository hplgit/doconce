docstring_do = docstring.do.txt
docstring_txt = docstring.dst.txt

$(docstring_txt): $(docstring_do)
	doconce format plain $(docstring_do)
	mv docstring.txt $(docstring_txt)
