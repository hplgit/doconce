> DocOnce is a modestly tagged (Markdown-like) markup language targeting scientific reports, software documentation, books, blog posts, and slides involving much math and code in the text. From DocOnce source you can generate LaTeX, Sphinx, HTML, IPython notebooks, Markdown, MediaWiki, and other formats. This means that you from a single source can get the most up-to-date publishing technologies for paper, tablets, and phones.





### News

Here are some of the most recent features and enhancements in DocOnce:
 * MathJax, which is used to render LaTeX formulae in HTML, has shut down their CDN (Content Delivery Network) which serves the JavaScript files. DocOnce has been updated to use a new CDN. For the time being, the old URL redirects to the new CDN, and old DocOnce documents still display LaTeX correctly. However, at some point in the future, documents created before July 2017 will cease to display LaTeX formulae properly. **It is therefore recommended to rerun DocOnce on HTML documents which contain LaTeX formulae.**
 * On 10 October 2016, Hans Petter Langtangen, creator of DocOnce, [passed away](https://www.simula.no/news/hans-petter-langtangen-1962-2016). Kristian Gregorius Hustad, supported by the [Centre for Computing in Science Education](http://www.mn.uio.no/ccse/english/) at the University of Oslo, will assume the role of principal maintainer.
 * Language support for Basque has been added. Thanks to Josu M. Igartua for providing the translation.
 * DocOnce can now be used with both Python 2 and Python 3.
 * Kristian Gregorius Hustad has now made support for TikZ figures
   in DocOnce. This means that you can use TikZ (popular among LaTeX writers)
   to make a figure. The TikZ code will be used directly in `latex` or
   `pdflatex` output, while an SVG version is made for HTML and a PNG is made
   for all other formats. (This feature is still being developed. Please create
   an issue if your TikZ figure isn't displayed properly.)
 * Thanks to support from Mirco Meiners and Kristian Gregorius Hustad,
   DocOnce now supports documents in foreign languages, at the moment
   Norwegian and German. (Expect the code to still be a bit unstable as
   these features are being tested and used.)
 * It is easy to overlook the many warnings and non-fatal errors from
   DocOnce when compiling a document. Now all comments from DocOnce for
   a document `mydoc.do.txt` are collected in `mydoc.dlog` for
   careful inspection.

Here are some recent books written in DocOnce:

<!-- <img src="doc/src/manual/fig/doconce_books.jpg" width=600> -->
![](doc/src/manual/fig/doconce_books.jpg)

### Installation

DocOnce is a pure Python package and can be installed with `pip`.


```
Terminal> sudo pip install --upgrade git+https://github.com/doconce/preprocess
Terminal> sudo pip install --upgrade .
```

*Notice.* 
If you first installed DocOnce prior to February 2017, you must remove the old installation before upgrading. See instructions in [issue #110](https://github.com/hplgit/doconce/issues/110).


However, DocOnce has *a lot* of dependencies, depending on what type of
formats you want to work with and how advanced constructions that are
used in the text.

With Anaconda it is trivial to install DocOnce and all
dependencies by


```
Terminal> conda config --add channels conda-forge
Terminal> conda install doconce
```

*Warning.* 
As of March 2017, a few dependencies have yet to be added to the `conda-forge` channel, but most formats should work fine.




On Debian/Ubuntu it is fairly straightforward
to get the packages you need. Basically, you can run a [Bash script](https://raw.githubusercontent.com/hplgit/doconce/master/doc/src/manual/install_doconce.sh) or an equivalent [Python script](https://raw.githubusercontent.com/hplgit/doconce/master/doc/src/manual/install_doconce.py). Such a script installs
a very comprehensive bundle of software. You can read the
[Installation Guide](http://hplgit.github.io/doconce/doc/pub/manual/html/manual.html#installation-of-doconce-and-its-dependencies) to get a more
detailed description of what is needed of software for various purposes.
For HTML output, for example, you can usually get away with just installing
the pure DocOnce source (and perhaps the preprocessors if you use them).

*Install from GitHub repo, not from Debian.* 
Although DocOnce is in Debian, do not run `sudo apt-get install python-doconce`
as this gives a very old version of DocOnce that is out of sync with the
documentation. Instead, clone the DocOnce GitHub repo as shown above
and run `pip install` or use `conda install`.






### Highlights


 * DocOnce is a modestly tagged markup language (see [syntax example](http://hplgit.github.io/teamods/writing_reports/_static/report.do.txt.html)), quite like Markdown, but with many more features, aimed at documents with
   *much math and code in the text* (see [demo](http://hplgit.github.io/teamods/writing_reports/index.html)).
 * There is extensive support for book projects. In addition to classical LaTeX-based paper books one gets for free fully responsive, modern-looking, HTML-based ebooks for tablets and phones. Parts of books can, e.g., appear in blog posts for discussion and as IPython notebooks for experimentation and annotation.
 * For documents with math and code, you can generate *clean* plain LaTeX (PDF), HTML (with MathJax and Pygments - embedded in your own templates), Sphinx for attractive web design, Markdown, IPython notebooks, HTML for Google or Wordpress blog posts, and MediaWiki. The LaTeX output has many fancy layouts for typesetting of computer code.
 * DocOnce can also output other formats (though without support for nicely typeset math and code): plain untagged text, Google wiki, Creole wiki, and reStructuredText. From Markdown or reStructuredText you can go to XML, DocBook, epub, OpenOffice/LibreOffice, MS Word, and other formats.
 * The document source is first preprocessed by Preprocess and Mako, which gives you full programming capabilities in the document's text. For example, with Mako it is easy to write a book with all computer code examples in two alternative languages (say Matlab and Python), and you can determine the language at compile time of the document. New user-specific features of DocOnce can also be implemented via Mako.
 * DocOnce extends Sphinx, Markdown, and MediaWiki output such that LaTeX align environments with labels work for systems of equations. DocOnce also adjusts Sphinx and HTML code such that it is possible to refer to equations outside the current web page.
 * DocOnce makes it very easy to write slides with math and code by stripping down running text in a report or book. LaTeX Beamer slides, HTML5 slides (reveal.js, deck.js, dzslides), and Remark (Markdown) slides are supported. Slide elements can be arranged in a grid of cells to easily control the layout.

DocOnce looks similar to [Markdown](http://daringfireball.net/projects/markdown/), [Pandoc-extended
Markdown](http://johnmacfarlane.net/pandoc/), and in particular
[MultiMarkdown](http://fletcherpenney.net/multimarkdown/).  The main
advantage of DocOnce is the richer support for writing large documents
(books) with much math and code and with
tailored output both in HTML and
LaTeX. DocOnce also has special support for exercises, [quizzes](http://hplgit.github.io/doconce/doc/pub/quiz/quiz.html), and [admonitions](http://hplgit.github.io/doconce/doc/pub/manual/._manual017.html#___sec55),
three very desired features when developing educational material.
Books can be composed of many smaller documents that may exist
independently of the book, thus lowering the barrier of writing books
(see [example](https://github.com/hplgit/setup4book-doconce)).


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

DocOnce has support for *responsive* HTML documents with design and
functionality based on Bootstrap styles.  A [Bootstrap demo](http://hplgit.github.io/doconce/doc/pub/bootstrap/index.html)
illustrates the many possibilities for colors and layouts.

DocOnce also has support for exercises in [quiz format](http://hplgit.github.io/doconce/doc/pub/quiz/quiz.html). Pure quiz
files can be *automatically uploaded* to [Kahoot!](https://getkahoot.com) online quiz games operated through smart
phones (with the aid of [quiztools](https://github.com/hplgit/quiztools) for DocOnce to Kahoot!
translation).



Several books (up to over 1000 pages) have been written entirely in
DocOnce. The primary format is a publisher-specific LaTeX style, but
HTML or Sphinx formats can easily be generated, such as [this chapter
in Bootstrap style](http://hplgit.github.io/primer.html/doc/pub/looplist/looplist-bootstrap.html),
or the [solarized color style](http://hplgit.github.io/primer.html/doc/pub/looplist/looplist-solarized.html)
as many prefer. Slides can quickly be generated from the raw text in
the book.  Here are examples in the [reveal.js](http://hplgit.github.io/scipro-primer/slides/looplist/html/looplist-reveal-beige.html)
(HTML5) style, or the more traditional [LaTeX Beamer](http://hplgit.github.io/scipro-primer/slides/looplist/pdf/looplist-beamer.pdf)
style, and even the modern [IPython notebook](http://nbviewer.ipython.org/url/hplgit.github.io/scipro-primer/slides/looplist/ipynb/looplist.ipynb)
tool, which allows for interactive experimentation and annotation.

### Documentation

*Warning.* 
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
 * Troubleshooting and FAQ: [Sphinx](http://hplgit.github.io/doconce/doc/pub/trouble/html/index.html),
   [HTML](http://hplgit.github.io/doconce/doc/pub/trouble/trouble.html),
   [PDF](http://hplgit.github.io/doconce/doc/pub/trouble/trouble.pdf)

The tutorial presents the basic syntax and the most fundamental
elements of a scientific document, while the manual has accumulated
all the different features available. The most efficient way to get
started is to look at the [report demo](http://hplgit.github.io/teamods/writing_reports/index.html) and study
the [source code](http://hplgit.github.io/teamods/writing_reports/_static/report.do.txt.html)
(it has all the basic elements such as title, author, abstract, table
of contents, headings, comments, inline mathematical formulas,
single/multiple equations, with and without numbering, labels,
cross-references to sections and equations, bullet lists, enumerated
lists, copying of computer code from files, inline computer code,
index entries, figures, tables, and admonitions).

### License

DocOnce is licensed under the BSD license, see the included `LICENSE` file.

### Author

DocOnce is written by Hans Petter Langtangen ([hpl@simula.no](mailto:hpl@simula.no)) 2006-2016. A lot of people have contributed to testing the software and suggesting improvements.

### How to cite

#### Link in the copyright

The command-line option `--cite_doconce` can be used
to equip the copyright field with a link to the present page.
Here is an example involving some document `mydoc.do.txt`:


```
TITLE: Some document
AUTHOR: Joe Doe
...
```

Compile to HTML with DocOnce link:


```
Terminal> doconce format html mydoc --cite_doconce
```

The footer of the first page will now contain "Made with DocOnce".

#### Traditional citation in a bibliography

BibTeX format:


```
@misc{DocOnce,
  title = {{DocOnce} markup language},
  author = {H. P. Langtangen},
  url = {https://github.com/hplgit/doconce},
  key = {DocOnce},
  note = {\url{https://github.com/hplgit/doconce}},
}
```

Publish format:


```
* misc
** {DocOnce} markup language
   key:       DocOnce
   author:    H. P. Langtangen
   url:       https://github.com/hplgit/doconce
   status:    published
   sortkey:   DocOnce
   note:      \url{https://github.com/hplgit/doconce}
```

