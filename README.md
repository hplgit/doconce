### Document once, include anywhere

 * When writing a note, report, manual, etc., do you find it difficult to choose the typesetting format? That is, to choose between plain (email-like) text, wiki, MS Word or OpenOffice, LaTeX, HTML, reStructuredText, Sphinx, XML, Markdown, etc.? Would it be convenient to start with some very simple text-like format that easily converts to the formats listed above?
 * Do you find it problematic that you have the same information scattered around in different filess in different typesetting formats? Would it be a good idea to write things once, in one place, and include anywhere?
 * Would you like to write books, theses, or papers both in a traditional, printed LaTeX PDF format *and* in HTML for the web with a lot of modern fancy styles such as Bootstrap and Sphinx and their variants?

You should take a look at DocOnce if any of these questions are of interest.

*Users are strongly encouraged to use the most recent software in the [GitHub repository](https://github.com/hplgit/doconce) and not the tarballs!*

### Highlights

 * DocOnce is a minimally tagged markup language (like Markdown) with strong support for small and large scale projects involving *much math and code in the text*.
 * For documents with math and code, you can generate clean plain LaTeX (PDF), HTML (with MathJax and pygments - embedded in your own templates), Sphinx for attractive web design (especially for scientific material), Markdown, IPython notebooks, HTML for Google or Wordpress blog posts, and MediaWiki. LaTeX output is in the ptex2tex format for very flexible typesetting of computer code.
 * DocOnce can also output other formats (though without support for nicely typeset math and code): plain untagged text, Google wiki, Creole wiki, and reStructuredText. From Markdown or reStructuredText you can go to XML, DocBook, epub, OpenOffice/LibreOffice, MS Word, and other formats.
 * The document source is first preprocessed by Preprocess and Mako, which gives you full programming capabilities in the text. For example, with Mako it is easy to write a book with all computer code examples in two alternative languages (say Matlab and Python), and you can determine the language at compile time of the document.
 * DocOnce extends Sphinx, Markdown, and MediaWiki output such that LaTeX align environments with labels work for systems of equations. DocOnce also adjusts Sphinx and HTML code such that it is possible to refer to equations outside the current web page.
 * One source for the text can be used for different media, such as traditional paper-based books, ebooks in PDF, PDF documents for phones, documents in HTML with various layouts (including many Bootstrap and Sphinx styles), and blog posts.
 * DocOnce makes it very easy to write slides with math and code, especially if you have the contents already available as running text (basically you strip away text, insert bullet points or brief summary blocks, while keeping some figures, math, and code). Both LaTeX Beamer and HTML5 slides (reveal.js and deck.js) are supported. Slide elements can be arranged in a grid of cells to easily control the layout.

DocOnce looks similar to [Markdown](http://daringfireball.net/projects/markdown/), [Pandoc-extended
Markdown](http://johnmacfarlane.net/pandoc/), and in particular
[MultiMarkdown](http://fletcherpenney.net/multimarkdown/).  The main
advantage of DocOnce is the richer support for writing large documents
(books) with much math, code, and admonitions,
with tailored output both in HTML and
LaTeX. Books can be composed of many smaller documents that may exist
independently of the book.


### Installation

DocOnce is a pure Python package and installed by


```
Terminal> sudo python setup.py install
```

However, DocOnce has *a lot* of dependencies, depending on what type of
formats you want to work with. On Debian/Ubuntu it is fairly straightforward
to get the packages you need. See the [Installation Guide](http://hplgit.github.io/doconce/doc/pub/manual/html/manual.html#installation-of-doconce-and-its-dependencies) for
details.

### Demo

A [short scientific report](http://hplgit.github.io/teamods/writing_reports/index.html)
demonstrates the many formats that DocOnce can generate and how
mathematics and computer code look like. (Note that at the bottom of
the page there is a link to another version of the demo with complete
DocOnce commands for producing the different versions.)

<!-- Note: local links does not work since this README file is a source -->
<!-- code file and not part of the published gh-pages. Use full URL. -->

Another demo shows how DocOnce can be used to [create slides](http://hplgit.github.io/doconce/doc/pub/slides/demo/index.html) in
various formats (HTML5 reveal.js, deck.js, etc., as well as LaTeX
Beamer).

DocOnce has support for HTML documents with design and functionality
based on Bootstrap styles.  A [demo](http://hplgit.github.io/doconce/doc/pub/bootstrap/index.html)
illustrates the many possibilities for colors and layouts.

A [complete book](http://www.springer.com/mathematics/computational+science+%26+engineering/book/978-3-642-54958-8) (900 pages) has been written entirely
in DocOnce. The primary format is a publisher-specific LaTeX style,
but HTML or Sphinx formats can easily be generated, such as
this chapter in the popular [Bootstrap style](http://hplgit.github.io/primer.html/doc/pub/looplist/looplist-bootstrap.html) or the [solarized color style](http://hplgit.github.io/primer.html/doc/pub/looplist/looplist-solarized.html) as many prefer. Slides can quickly be generated from the raw text in the book.
Here are examples in the
[reveal.js](http://hplgit.github.io/scipro-primer/slides/looplist/html/looplist-reveal-beige.html) (HTML5) style, or the more traditional [LaTeX Beamer](http://hplgit.github.io/scipro-primer/slides/looplist/pdf/looplist-beamer.pdf) style, and even the modern [IPython notebook](http://nbviewer.ipython.org/url/hplgit.github.io/scipro-primer/slides/looplist/ipynb/looplist.ipynb) tool, which
allows for interactive experimentation and annotation.

### Documentation

*Warning.*\g<space>
These documents are under development...



 * Tutorial: [Sphinx](http://hplgit.github.io/doconce/doc/pub/tutorial/html/index.html),
   [HTML](http://hplgit.github.io/doconce/doc/pub/tutorial/tutorial.html),
   [PDF](http://hplgit.github.io/doconce/doc/pub/tutorial/tutorial.pdf)
 * Manual: [Sphinx](http://hplgit.github.io/doconce/doc/pub/manual/html/index.html),
   [HTML](http://hplgit.github.io/doconce/doc/pub/manual/manual.html),
   [PDF](http://hplgit.github.io/doconce/doc/pub/manual/manual.pdf)
 * Quick Reference: [Sphinx](http://hplgit.github.io/doconce/doc/pub/quickref/html/index.html),
   [HTML](http://hplgit.github.io/doconce/doc/pub/quickref/quickref.html),
   [PDF](http://hplgit.github.io/doconce/doc/pub/quickref/quickref.pdf)
 * Troubleshooting: [Sphinx](http://hplgit.github.io/doconce/doc/pub/trouble/html/index.html),
   [HTML](http://hplgit.github.io/doconce/doc/pub/trouble/trouble.html),
   [PDF](http://hplgit.github.io/doconce/doc/pub/trouble/trouble.pdf)

### License

DocOnce is licensed under the BSD license, see the included LICENSE file.

