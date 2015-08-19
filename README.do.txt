!bquote
DocOnce is a modestly tagged (Markdown-like) markup language targeting scientific reports, software documentation, books, blog posts, and slides involving much math and code in the text. From DocOnce source you can generate LaTeX, Sphinx, HTML, IPython notebooks, Markdown, MediaWiki, and other formats. This means that you from a single source can get the most up-to-date publishing technologies for paper, tablets, and phones.
!equote

##DocOnce is aimed at LaTeX writers who want to target
##different media: paper, phones, tablets, and different publising
##formats: books, papers, manuals, wikis, blog posts.
##DocOnce provides up-to-date publishing technologies for such media
##and formts using *one single text source*.


===== News =====

Here are some of the most recent features in DocOnce:

 * DocOnce supports interactive Bokeh plots for data exploration in
   HTML documents, see "demo": "http://hplgit.github.io/doconce/doc/pub/manual/manual.html#___sec13".
 * DocOnce can generate Matlab notebooks in the publish format
   (output format `matlabnb`).
 * Exercises can now be extracted as individual files (e.g., for distribution
   to students). The files are in DocOnce format and can be compiled to, e.g.,
   LaTeX or IPython notebooks, see "a quick description": "http://hplgit.github.io/doconce/doc/pub/manual/._manual013.html#exercises:standalone".
 * DocOnce and all its dependencies are now trivial to install with Anaconda Python: `sudo conda install --channel johannr doconce` (thanks to Johannes Ring).
 * Bootstrap HTML styles features hints, answers, and solutions in
   exercises as *unfolded text*.
 * `doconce extract_exercises`
   extracts all exercises from a document (can be used, e.g., to publish exercises separately or to extract only those exercises suitable to being published as IPython notebooks).
 * DocOnce features "user-defined environments": "http://hplgit.github.io/doconce/doc/pub/manual/html/manual.html#user-defined-environments" with begin-end tags, doing
   exactly what you want: you may (e.g.) use your favorite *native* example
   LaTeX environment when writing LaTeX.
 * Documents can have interactive Python code in HTML and Sphinx via the `pyscpro` code
   environment (Sage Math Cells).
 * New support for "RunestoneInteractive books": "http://runestoneinteractive.org"
   (as a special case of the Sphinx output format).
 * New support for "verbatim code blocks in LaTeX": "http://hplgit.github.io/doconce/doc/pub/latexcode/demo.html" with a lot of flexibility for fancy typesetting via the Pygments and Listings packages (i.e., no more need for the `ptex2tex` step).
 * "New document": "http://hplgit.github.io/setup4book-doconce/doc/web/index.html" explaining the effient way to use DocOnce for book writing.
 * Embedded "quizzes or multiple-choice questions": "http://hplgit.github.io/doconce/doc/pub/quiz/quiz.html", which can be automatically uploaded to
   "Kahoot online games": "https://getkahoot.com".
 * "Admonitions": "http://hplgit.github.io/doconce/doc/pub/manual/html/manual.html#admonitions", i.e., boxes for notifications, tips, warnings, etc., with
   great "flexibility in the typesetting": "http://hplgit.github.io/doconce/doc/pub/admon/index.html" (at least in HTML and LaTeX).

===== Installation =====

DocOnce is a pure Python v2.7 package and installed by

!bc sys
Terminal> sudo python setup.py install
!ec
However, DocOnce has *a lot* of dependencies, depending on what type of
formats you want to work with and how advanced constructions that are
used in the text.

With Anaconda Python v2.7 it is trivial to install DocOnce and all
dependencies by

!bc sys
Terminal> sudo conda install --channel johannr doconce
!ec

On Debian/Ubuntu it is fairly straightforward
to get the packages you need. Basically, you can run a "Bash script": "https://raw.githubusercontent.com/hplgit/doconce/master/doc/src/manual/install_doconce.sh" or an equivalent "Python script": "https://raw.githubusercontent.com/hplgit/doconce/master/doc/src/manual/install_doconce.py". Such a script installs
a very comprehensive bundle of software. You can read the
"Installation Guide": "http://hplgit.github.io/doconce/doc/pub/manual/html/manual.html#installation-of-doconce-and-its-dependencies" to get a more
detailed description of what is needed of software for various purposes.
For HTML output, for example, you can usually get away with just installing
the pure DocOnce source (and perhaps the preprocessors if you use them).

!bwarning Install from GitHub repo, not from Debian
Although DocOnce is in Debian, do not run `sudo apt-get install python-doconce`
as this gives a very old version of DocOnce that is out of sync with the
documentation. Instead, clone the DocOnce GitHub repo as shown above
and run `setup.py` or use `conda install`.
!ewarning




===== Highlights =====

## scientific reports, software documentation, books, blog posts, web pages, and slides

 * DocOnce is a modestly tagged markup language (see "syntax example": "http://hplgit.github.io/teamods/writing_reports/_static/report/do.txt.html"), quite like Markdown, but with many more features, aimed at documents with
   *much math and code in the text* (see "demo": "http://hplgit.github.io/teamods/writing_reports/index.html").
 * There is extensive support for book projects. In addition to classical LaTeX-based paper books one gets for free fully responsive, modern-looking, HTML-based ebooks for tablets and phones. Parts of books can, e.g., appear in blog posts for discussion and as IPython notebooks for experimentation and annotation.
 * For documents with math and code, you can generate *clean* plain LaTeX (PDF), HTML (with MathJax and Pygments - embedded in your own templates), Sphinx for attractive web design, Markdown, IPython notebooks, HTML for Google or Wordpress blog posts, and MediaWiki. The LaTeX output has many fancy layouts for typesetting of computer code.
 * DocOnce can also output other formats (though without support for nicely typeset math and code): plain untagged text, Google wiki, Creole wiki, and reStructuredText. From Markdown or reStructuredText you can go to XML, DocBook, epub, OpenOffice/LibreOffice, MS Word, and other formats.
 * The document source is first preprocessed by Preprocess and Mako, which gives you full programming capabilities in the document's text. For example, with Mako it is easy to write a book with all computer code examples in two alternative languages (say Matlab and Python), and you can determine the language at compile time of the document. New user-specific features of DocOnce can also be implemented via Mako.
 * DocOnce extends Sphinx, Markdown, and MediaWiki output such that LaTeX align environments with labels work for systems of equations. DocOnce also adjusts Sphinx and HTML code such that it is possible to refer to equations outside the current web page.
 * DocOnce makes it very easy to write slides with math and code by stripping down running text in a report or book. LaTeX Beamer slides, HTML5 slides (reveal.js, deck.js, dzslides), and Remark (Markdown) slides are supported. Slide elements can be arranged in a grid of cells to easily control the layout.

DocOnce looks similar to "Markdown":
"http://daringfireball.net/projects/markdown/", "Pandoc-extended
Markdown":"http://johnmacfarlane.net/pandoc/", and in particular
"MultiMarkdown": "http://fletcherpenney.net/multimarkdown/".  The main
advantage of DocOnce is the richer support for writing large documents
(books) with much math and code and with
tailored output both in HTML and
LaTeX. DocOnce also has special support for exercises, "quizzes": "http://hplgit.github.io/doconce/doc/pub/quiz/quiz.html", and "admonitions":
"http://hplgit.github.io/doconce/doc/pub/manual/._manual017.html#___sec55",
three very desired features when developing educational material.
Books can be composed of many smaller documents that may exist
independently of the book, thus lowering the barrier of writing books
(see "example": "https://github.com/hplgit/setup4book-doconce").


===== Demo =====

A "short scientific report":
"http://hplgit.github.io/teamods/writing_reports/index.html"
demonstrates the many formats that DocOnce can generate and how
mathematics and computer code look like. (Note that at the bottom of
the page there is a link to another version of the demo with complete
DocOnce commands for producing the different versions.)

# Note: local links does not work since this README file is a source
# code file and not part of the published gh-pages. Use full URL.

Another demo shows how DocOnce can be used to "create slides":
"http://hplgit.github.io/doconce/doc/pub/slides/demo/index.html" in
various formats (HTML5 reveal.js, deck.js, etc., as well as LaTeX
Beamer).

DocOnce has support for *responsive* HTML documents with design and
functionality based on Bootstrap styles.  A "Bootstrap demo":
"http://hplgit.github.io/doconce/doc/pub/bootstrap/index.html"
illustrates the many possibilities for colors and layouts.

DocOnce also has support for exercises in "quiz format":
"http://hplgit.github.io/doconce/doc/pub/quiz/quiz.html". Pure quiz
files can be *automatically uploaded* to "Kahoot!":
"https://getkahoot.com" online quiz games operated through smart
phones (with the aid of "quiztools":
"https://github.com/hplgit/quiztools" for DocOnce to Kahoot!
translation).


##"http://www.springer.com/mathematics/computational+science+%26+engineering/book/978-3-642-54958-8"

A "complete book": "http://www.amazon.com/Scientific-Programming-Computational-Science-Engineering/dp/3642549586/ref=sr_1_1?s=books&ie=UTF8&qid=1419162166&sr=1-1&keywords=langtangen"
(900 pages) has been written entirely in DocOnce. The primary format
is a publisher-specific LaTeX style, but HTML or Sphinx formats can
easily be generated, such as "this chapter in Bootstrap style":
"http://hplgit.github.io/primer.html/doc/pub/looplist/looplist-bootstrap.html",
or the "solarized color style":
"http://hplgit.github.io/primer.html/doc/pub/looplist/looplist-solarized.html"
as many prefer. Slides can quickly be generated from the raw text in
the book.  Here are examples in the "reveal.js":
"http://hplgit.github.io/scipro-primer/slides/looplist/html/looplist-reveal-beige.html"
(HTML5) style, or the more traditional "LaTeX Beamer":
"http://hplgit.github.io/scipro-primer/slides/looplist/pdf/looplist-beamer.pdf"
style, and even the modern "IPython notebook":
"http://nbviewer.ipython.org/url/hplgit.github.io/scipro-primer/slides/looplist/ipynb/looplist.ipynb"
tool, which allows for interactive experimentation and annotation.

===== Documentation =====

!bwarning
These documents are under development...
!ewarning

 * Tutorial: "Sphinx": "http://hplgit.github.io/doconce/doc/pub/tutorial/html/index.html",
   "HTML": "http://hplgit.github.io/doconce/doc/pub/tutorial/tutorial.html",
   "PDF": "http://hplgit.github.io/doconce/doc/pub/tutorial/tutorial.pdf"
 * Manual: "Sphinx": "http://hplgit.github.io/doconce/doc/pub/manual/html/index.html",
   "HTML": "http://hplgit.github.io/doconce/doc/pub/manual/manual.html",
   "PDF": "http://hplgit.github.io/doconce/doc/pub/manual/manual.pdf"
 * Quick Reference: "Sphinx": "http://hplgit.github.io/doconce/doc/pub/quickref/html/index.html",
   "HTML": "http://hplgit.github.io/doconce/doc/pub/quickref/quickref.html",
   "PDF": "http://hplgit.github.io/doconce/doc/pub/quickref/quickref.pdf"
 * Troubleshooting and FAQ: "Sphinx": "http://hplgit.github.io/doconce/doc/pub/trouble/html/index.html",
   "HTML": "http://hplgit.github.io/doconce/doc/pub/trouble/trouble.html",
   "PDF": "http://hplgit.github.io/doconce/doc/pub/trouble/trouble.pdf"

The tutorial presents the basic syntax and the most fundamental
elements of a scientific document, while the manual has accumulated
all the different features available. The most efficient way to get
started is to look at the "report demo":
"http://hplgit.github.io/teamods/writing_reports/index.html" and study
the "source code":
"http://hplgit.github.io/teamods/writing_reports/_static/report.do.txt.html"
(it has all the basic elements such as title, author, abstract, table
of contents, headings, comments, inline mathematical formulas,
single/multiple equations, with and without numbering, labels,
cross-references to sections and equations, bullet lists, enumerated
lists, copying of computer code from files, inline computer code,
index entries, figures, tables, and admonitions).

===== License =====

DocOnce is licensed under the BSD license, see the included LICENSE file.

===== Author =====

DocOnce is written by Hans Petter Langtangen ("hpl@simula.no": "mailto:hpl@simula.no") 2006-2015. A lot of people have contributed to testing the software and suggesting improvements.
