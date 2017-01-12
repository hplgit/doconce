"""
DocWriter is a tool for writing documents in ASCII, HTML,
LaTeX, DocOnce, and other formats based on input from Python
datastructures.

The base class _BaseWriter defines common functions and data
structures, while subclasses HTML, DocOnce, etc.  implement (i.e.,
write to) various formats.

This module works, but is unifinished and needs documentation!
"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import str
from builtins import range
from past.builtins import basestring
from builtins import object

from io import StringIO
import re, os, glob, subprocess

class _BaseWriter(object):
    """
    Base class for document writing classes.
    Each subclass implements a specific format (html, latex,
    rst, etc.).
    """
    def __init__(self, format, filename_extension):
        # use StringIO as a string "file" for writing the document:
        self.file = StringIO()
        self.filename_extension = filename_extension
        self.format = format
        self._footer_called = False

    document = property(fget=lambda self: self.file.getvalue(),
                        doc='Formatted document as a string')

    def write_to_file(self, filename):
        """
        Write formatted document to a file.
        Just give the stem of the file name;
        the extension will be automatically added (depending on the
        document format).
        """
        # footer?
        if not self._footer_called:
            self.footer()
            self._footer_called = True

        f = open(filename + self.filename_extension, 'w')
        f.write(self.document)
        f.close()

    def __str__(self):
        """Return formatted document."""
        return self.document

    def header(self):
        """Header as required by format. Called in constructor."""
        pass

    def footer(self):
        """Footer as required by format. Called in write_to_file."""
        pass

    def not_impl(self, method):
        raise NotImplementedError('method "%s" in class "%s" is not implemented' % \
              (method, self.__class__.__name__))

    def title(self, title, authors_and_institutions=[], date='today'):
        """
        Provide title and authors.

        @param title: document title (string).
        @param authors_and_institutions: list of authors and their
        associated institutions, where each list item is a tuple/list
        with author as first element followed by the name of all
        institutions this author is associated with.
        @param date: None implies no date, while 'today' generates
        the current date, otherwise a string is supplied.
        """
        self.not_impl('title')

    def today_date(self):
        """Return a string with today's date suitably formatted."""
        import time
        return time.strftime('%a, %d %b %Y (%H:%M)')

    def section(self, title, label=None):
        """
        Write a section heading with the given title and an optional
        label (for navigation).
        """
        self.not_impl('section')

    def subsection(self, title, label=None):
        """
        Write a subsection heading with the given title and an optional
        label (for navigation).
        """
        self.not_impl('subsection')

    def subsubsection(self, title, label=None):
        """
        Write a subsubsection heading with the given title and an optional
        label (for navigation).
        """
        self.not_impl('subsubsection')

    def paragraph(self, title, ending='.', label=None):
        """
        Write a paragraph heading with the given title and an ending
        (period, question mark, colon) and an optional label (for navigation).
        """
        self.not_impl('paragraph')

    def paragraph_separator(self):
        """
        Add a (space) separator between running paragraphs.
        """
        self.not_impl('paragraph_separator')

    def text(self, text, indent=0):
        """
        Write plain text. Each line can be idented by a given number
        of spaces.
        """
        # do the indentation here, subclasses should call this method first
        text = '\n'.join([' '*indent + line for line in text.split('\n')])
        # subclasses must substitute DocOnce simple formatting
        # using the expandtext method
        return text

    def expandtext(self, text, tags, tags_replacements):
        """
        In a string text, replace all occurences of strings defined in tags
        by the corresponding strings defined in tags_replacements.
        Both tags and tags_replacements are dictionaries with keys such
        as 'bold', 'emphasize', 'verbatim', 'math', and values consisting of
        regular expression patterns.

        This method allows application code to use some generic ways of
        writing emphasized, boldface, and verbatim text, typically in the
        DocOnce format with *emphasized text*, _boldface text_, and
        `verbatim fixed font width text`.
        """
        for tag in tags:
            tag_pattern = tags[tag]
            c = re.compile(tag_pattern, re.MULTILINE)
            try:
                tag_replacement = tags_replacements[tag]
            except KeyError:
                continue
            if tag_replacement is not None:
                text = c.sub(tag_replacement, text)
        return text

    def list(self, items, listtype='itemize'):
        """
        Write list or nested lists.

        @param items: list of items.
        @param listtype: 'itemize', 'enumerate', or 'description'.
        """
        # call _BaseWriter.unfold_list to traverse the list
        # and use self.item_handler to typeset each item
        self.not_impl('list')

    def unfold_list(self, items, item_handler, listtype, level=0):
        """
        Traverse a possibly nested list and call item_handler for
        each item. To be used in subclasses for easy list handling.

        @param items: list to be processed.
        @param item_handler: callable, see that method for doc of arguments.
        @param listtype: 'itemize', 'enumerate', or 'description'.
        @param level: the level of a sublist (0 is main list, increased by 1
        for each sublevel).
        """
        # check for common error (a trailing comma...):
        if isinstance(items, tuple) and len(items) == 1:
            raise ValueError('list is a 1-tuple, error? If there is '\
                  'only one item in the list, make a real Python list '\
                  'object instead - current list is\n(%s,)' % items)
        item_handler('_begin', listtype, level)
        for i, item in enumerate(items):
            if isinstance(item, (list,tuple)):
                self.unfold_list(item, item_handler, listtype, level+1)
            elif isinstance(item, basestring):
                if listtype == 'description':
                    # split out keyword in a description list:
                    parts = item.split(':')
                    keyword = parts[0]
                    item = ':'.join(parts[1:])
                    item_handler(item, listtype, level, keyword)
                else:
                    item_handler(item, listtype, level)
            else:
                raise TypeError('wrong %s for item' % type(item))
        item_handler('_end', listtype, level)

    def item_handler(self, item, listtype, level, keyword=None):
        """
        Write out the syntax for an item in a list.

        @param item: text assoicated with the current list item. If item
        equals '_begin' or '_end', appropriate begin/end formatting of
        the list is written instead of an ordinary item.
        @param listtype: 'itemize, 'enumerate', or 'description'.
        @param level: list level number, 0 is the mainlist, increased by 1
        for each sublist (the level number implies the amount of indentation).
        @param keyword: the keyword of the item in a 'description' list.
        """
        self.not_impl('item_handler')

    def verbatim(self, code):
        """
        Write verbatim text in fixed-width form
        (typically for computer code).
        """
        self.not_impl('verbatim')

    def math(self, text):
        """Write block of mathematical text (equations)."""
        # default: dump raw
        self.raw(text)

    def raw(self, text):
        """Write text directly 'as is' to output."""
        self.file.write(text)

    def figure_conversion(self, filename, extensions):
        """
        Convert filename to an image with type according to
        extension(s).

        The first existing file with an extension encountered in the extensions
        list is returned. If no files with the right extensions are found,
        the convert utility from the ImageMagick suite is used to
        convert filename.ps or filename.eps to filename + extensions[0].
        """
        if not isinstance(extensions, (list,tuple)):
            extensions = [extensions]
        for ext in extensions:
            final = filename + ext
            if os.path.isfile(final):
                return final

        final = filename + extensions[0]  # convert to first mentioned type
        files = glob.glob(filename + '*')
        # first convert from ps or eps to other things:
        for file in files:
            stem, ext = os.path.splitext(file)
            if ext == '.ps' or ext == '.eps':
                cmd = 'convert %s %s' % (file, final)
                print(cmd)
                failure = os.system(cmd)
                if failure:
                    print('Could not convert;\n  %s' % cmd)
                return final
        # try to convert from the first file to the disired format:
        file = files[0]
        cmd = 'convert %s %s' % (file, final)
        print(cmd)
        try:
            output = subprocess.check_output(cmd, shell=True,
                                             stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print('Could not convert;\n  %s' % cmd)
        return final

    def figure(self, filename, caption, width=None, height=None, label=None):
        """
        Insert a figure into the document.
        filename should be without extension; a proper extension is added,
        and if the figure is not available in that image format, the
        convert utility from ImageMagick is called to convert the format.
        """
        self.not_impl('figure')

    def table(self, table, column_headline_pos='c', column_pos='c'):
        """
        Translates a two-dimensional list of data, containing strings or
        numbers, to a suitable "tabular" environment in the output.

        @param table: list of list with rows/columns in table, including
        (optional) column-headline 1st row and row-headline 1st column.
        @param column_pos: specify the l/c/r position of data
        entries in columns, give either (e.g.) 'llrrc' or one char
        (if all are equal).
        @param column_headline_pos : position l/c/r for the headline row
        """
        self.not_impl('table')

    def url(self, url_address, link_text=None):
        """Typeset an URL (with an optional link)."""
        self.not_impl('url')

    def link(self, link_text, link_target):
        """Typeset a hyperlink."""
        self.not_impl('link')

    # what about LaTeX references to labels in equations, pages, labels?

def makedocstr(parent_class, subclass_method):
    """
    Compose a string (to be used as doc string) from a method's
    doc string in a parent class and an additional doc string
    in a subclass version of the method.

    @param parent_class: class object for parent class.
    @param subclass_method: method object for subclass.
    @return: parent_class.method.__doc__ + subclass_method.__doc__
    """
    parent_method = getattr(parent_class, subclass_method.__name__)
    docstr = parent_method.__doc__
    if subclass_method.__doc__ is not None and \
           subclass_method is not parent_method:
        docstr += subclass_method.__doc__
    return docstr


# regular expressions for inline tags:
# (these are taken from doconce.common.INLINE_TAGS)
inline_tag_begin = r'(?P<begin>(^|[(\s]))'
inline_tag_end = r'(?P<end>($|[.,?!;:)\s]))'
INLINE_TAGS = {
    # math: text inside $ signs, as in $a = b$, with space before the
    # first $ and space, comma, period, colon, semicolon, or question
    # mark after the enclosing $.
    'math':
    r'%s\$(?P<subst>[^ `][^$`]*)\$%s' % \
    (inline_tag_begin, inline_tag_end),

    # $latex text$|$pure text alternative$
    'math2':
    r'%s\$(?P<latexmath>[^ `][^$`]*)\$\|\$(?P<puretext>[^ `][^$`]*)\$%s' % \
    (inline_tag_begin, inline_tag_end),

    # *emphasized words*
    'emphasize':
    r'%s\*(?P<subst>[^ `][^*`]*)\*%s' % \
    (inline_tag_begin, inline_tag_end),

    # `verbatim inline text is enclosed in back quotes`
    'verbatim':
    r'%s`(?P<subst>[^ ][^`]*)`%s' % \
    (inline_tag_begin, inline_tag_end),

    # _underscore before and after signifies bold_
    'bold':
    r'%s_(?P<subst>[^ `][^_`]*)_%s' % \
    (inline_tag_begin, inline_tag_end),
    }

class DocOnce(_BaseWriter):
    def __init__(self):
        _BaseWriter.__init__(self, 'DocOnce', '.do.txt')

    def title(self, title, authors_and_institutions=[], date='today'):
        s = '\nTITLE: %s\n' % title
        for ai in authors_and_institutions:
            authorinfo = '; '.join(ai)
            s += 'AUTHOR: %s\n' % authorinfo
        if date is not None:
            if date == 'today':
                date = self.today_date()
            s += 'DATE: %s\n' % date
        self.file.write(s)
        self.paragraph_separator()

    def heading(self, level, title, label=None):
        decoration = '='*level
        self.file.write('\n%s %s %s\n\n' % (decoration, title, decoration))

    def section(self, title, label=None):
        self.heading(7, title, label)

    def subsection(self, title, label=None):
        self.heading(5, title, label)

    def subsubsection(self, title, label=None):
        self.heading(3, title, label)

    def paragraph(self, title, ending='.', label=None):
        s = '\n\n__%s%s__ ' % (title, ending)
        self.file.write(s)

    def paragraph_separator(self):
        self.file.write('\n\n')

    def text(self, text, indent=0):
        text = _BaseWriter.text(self, text, indent)
        # not necessary since DocOnce is the format for text:
        #text = _BaseWriter.expandtext(self, text,
        #                              INLINE_TAGS, HTML.INLINE_TAGS_SUBST)
        self.file.write(text)

    def list(self, items, listtype='itemize'):
        self.unfold_list(items, self.item_handler, listtype)

    def item_handler(self, item, listtype, level, keyword=None):
        indent = '  '*level
        s = ''
        if item == '_begin':
            if level == 1:
                s += '\n'
        elif item == '_end':
            if level == 1:
                s += '\n'
        else:
            # ordinary item:
            if item is not None:
                if listtype == 'itemize':
                    s += '\n%s%s* %s' % (indent, indent, item)
                elif listtype == 'enumerate':
                    s += '\n%s%so %s' % (indent, indent, item)
                elif listtype == 'description':
                    s += '\n%s%s- %s: %s' % (indent, indent, keyword, item)
        self.file.write(s)

    def verbatim(self, code):
        self.file.write('\n!bc\n' + r'%s' % code + '\n!ec\n')

    def figure(self, filename, caption, width=None, height=None, label=None):
        filename = self.figure_conversion(filename, \
                            ('.jpg', '.gif', '.png', '.ps', '.eps'))
        s = '\nFIGURE:[%s,' % filename
        if width:
            s += '  width=%s ' % width
        if height:
            s += '  height=%s ' % width
        s += '] ' + caption + '\n'
        self.file.write(s)

    def table(self, table, column_headline_pos='c', column_pos='c'):
        # Better to factor out code in misc.csv2table!
        # See how we do it with html movie...
        # find max column width
        mcw = 0
        for row in table:
            mcw = max(mcw, max([len(str(c)) for c in row]))
        formatted_table = []  # table where all columns have equal width
        column_format = '%%-%ds' % mcw
        for row in table:
            formatted_table.append([column_format % c for c in row])
        width = len(' | '.join(formatted_table[0])) + 4
        s = '\n\n   |' + '-'*(width-2) + '|\n'
        for row in formatted_table:
            s += '   | ' + ' | '.join(row) + ' |\n'
        s += '   |' + '-'*(width-2) + '|\n\n'
        self.file.write(s)

    def url(self, url_address, link_text=None):
        if link_text is None:
            link_text = 'link'  # problems with DocOnce and empty link text
        self.file.write(' %s<%s>' % (url_address, link_text))

    def link(self, link_text, link_target):
        self.file.write('%s (%s)' % (link_text, link_target))

    # autogenerate doc strings by combining parent class doc strings
    # with subclass doc strings:
    for method in [title, section, subsection, subsubsection,
                   paragraph, text,
                   verbatim, # not defined here: math, raw,
                   figure, table, url,
                   list, item_handler,]:
        method.__doc__ = makedocstr(_BaseWriter, method)



class HTML(_BaseWriter):
    # class variables:
    table_border = '2'
    table_cellpadding = '5'
    table_cellspacing = '2'

    INLINE_TAGS_SUBST = {  # from inline tags to HTML tags
        # keep math as is:
        'math': None,  # indicates no substitution
        'math2':         r'\g<begin>\g<puretext>\g<end>',
        'emphasize':     r'\g<begin><em>\g<subst></em>\g<end>',
        'bold':          r'\g<begin><b>\g<subst></b>\g<end>',
        'verbatim':      r'\g<begin><tt>\g<subst></tt>\g<end>',
        }

    def __init__(self):
        _BaseWriter.__init__(self, 'html', '.html')
        self.header()

    def header(self):
        s = """\
<!-- HTML document generated by %s.%s -->
<html>
<body bgcolor="white">
""" % (__name__, self.__class__.__name__)
        self.file.write(s)

    def footer(self):
        s = """
</body>
</html>
"""
        self.file.write(s)

    def title(self, title, authors_and_institutions=[], date='today'):
        s = """
<title>%s</title>
<center><h1>%s</h1></center>
""" % (title, title)
        for ai in authors_and_institutions:
            author = ai[0]
            s += """
<center>
<h4>%s</h4>""" % author
            for inst in ai[1:]:
                s += """
<h6>%s</h6>""" % inst
            s += """\n</center>\n\n"""
        if date is not None:
            if date == 'today':
                date = self.today_date()
            s += """<center>%s</center>\n\n\n""" % date
        self.file.write(s)
        self.paragraph_separator()

    def heading(self, level, title, label=None):
        if label is None:
            s = """\n<h%d>%s</h%d>\n""" % (level, title, level)
        else:
            s = """\n<h%d><a href="%s">%s</h%d>\n""" % \
                (level, label, title, level)
        self.file.write(s)

    def section(self, title, label=None):
        self.heading(1, title, label)

    def subsection(self, title, label=None):
        self.heading(3, title, label)

    def subsubsection(self, title, label=None):
        self.heading(4, title, label)

    def paragraph(self, title, ending='.', label=None):
        s = '\n\n<p><!-- paragraph with heading -->\n<b>%s%s</b>\n' \
            % (title, ending)
        if label is not None:
            s += '<a name="%s">\n' % label
        self.file.write(s)

    def paragraph_separator(self):
        self.file.write('\n<p>\n')

    def text(self, text, indent=0):
        text = _BaseWriter.text(self, text, indent)
        text = _BaseWriter.expandtext(self, text,
                                      INLINE_TAGS, HTML.INLINE_TAGS_SUBST)
        self.file.write(text)

    def list(self, items, listtype='itemize'):
        self.unfold_list(items, self.item_handler, listtype)

    def item_handler(self, item, listtype, level, keyword=None):
        indent = '  '*level
        s = ''
        if item == '_begin':
            if listtype == 'itemize':
                s += '\n%s<ul>' % indent
            elif listtype == 'enumerate':
                s += '\n%s<ol>' % indent
            elif listtype == 'description':
                s += '\n%s<dl>' % indent
            s += ' <!-- start of "%s" list -->\n' % listtype
        elif item == '_end':
            if listtype == 'itemize':
                s += '%s</ul>' % indent
            elif listtype == 'enumerate':
                s += '%s</ol>' % indent
            elif listtype == 'description':
                s += '%s</dl>' % indent
            s += ' <!-- end of "%s" list -->\n' % listtype
        else:
            # ordinary item:
            if item is not None:
                if listtype in ('itemize', 'enumerate'):
                    s += '%s%s<p><li> %s\n' % (indent, indent, item)
                else:
                    s += '%s%s<p><dt>%s</dt><dd>%s</dd>\n' % \
                         (indent, indent, keyword, item)
        self.file.write(s)

    def verbatim(self, code):
        self.file.write('\n<pre>' + r'%s' % code + '\n</pre>\n')

    def figure(self, filename, caption, width=None, height=None, label=None):
        filename = self.figure_conversion(filename, ('.jpg', '.gif', '.png'))
        if width:
            width = ' width=%s ' % width
        else:
            width = ''
        if height:
            height = ' width=%s ' % width
        else:
            height = ''
        s = '\n<hr><img src="%s"%s%s>\n<p><em>%s</em>\n<hr><p>\n' % \
            (filename, width, height, caption)
        self.file.write(s)

    def table(self, table, column_headline_pos='c', column_pos='c'):
        s = '\n<p>\n<table border="%s" cellpadding="%s" cellspacing="%s">\n' %\
            (HTML.table_border, HTML.table_cellpadding, HTML.table_cellspacing)
        for line in table:
            s += '<tr>'
            for column in line:
                s += '<td>%s</td>' % column
            s += '</tr>\n'
        s += '</table>\n\n'
        self.file.write(s)

    def url(self, url_address, link_text=None):
        if link_text is None:
            link_text = url_address
        self.file.write('\n<a href="%s">%s</a>\n' % (url_address, link_text))

    def link(self, link_text, link_target):
        self.file.write('\n<a href="%s">%s</a>\n' % (link_text, link_target))

    # autogenerate doc strings by combining parent class doc strings
    # with subclass doc strings:
    for method in [title, section, subsection, subsubsection,
                   paragraph, text,
                   verbatim, # not defined here: math, raw,
                   figure, table, url,
                   list, item_handler,]:
        method.__doc__ = makedocstr(_BaseWriter, method)


class LaTeX(_BaseWriter):
    def __init__(self):
        raise NotImplementedError('Use DocOnce class instead and filter to LaTeX')

# Efficient way of generating class DocWriter.
# A better way (for pydoc and other API references) is to
# explicitly list all methods and their arguments and then add
# the body for writer in self.writers: writer.method(arg1, arg2, ...)

class DocWriter(object):
    """
    DocWriter can write documents in several formats at once.
    """
    methods = 'title', 'section', 'subsection', 'subsubsection', \
              'paragraph', 'paragraph_separator', 'text', 'list', \
              'verbatim', 'math', 'raw', 'url', 'link', \
              'write_to_file', 'figure', 'table',


    def __init__(self, *formats):
        """
        @param formats: sequence of strings specifying the desired formats.
        """
        self.writers = [eval(format)() for format in formats]

    def documents(self):
        return [writer.document for writer in self.writers]

    def __str__(self):
        s = ''
        for writer in self.writers:
            s += '*'*60 + \
                  '\nDocWriter: format=%s (without footer)\n' % \
                  writer.__class__.__name__ + '*'*60
            s += str(writer)
        return s

    def dispatcher(self, *args, **kwargs):
        #print 'in dispatcher for', self.method_name, 'with args', args, kwargs
        #self.history = (self.method_name, args, kwargs)
        for writer in self.writers:
            s = getattr(writer, self.method_name)(*args, **kwargs)
        # unfinished method

    '''
    Alternative to attaching separate global functions:
    def __getattribute__(self, name):
        print 'calling __getattribute__ with', name
        if name in DocWriter.methods:
            self.method_name = name
            return self.dispatcher
        else:
            return object.__getattribute__(self, name)

    # can use inspect module to extract doc of all methods and
    # put this doc in __doc__
    '''

# Autogenerate methods in class DocWriter (with right
# method signature and doc strings stolen from class _BaseWriter (!)):

import inspect

def func_to_method(func, class_, method_name=None):
    setattr(class_, method_name or func.__name__, func)

for method in DocWriter.methods:
    docstring = eval('_BaseWriter.%s.__doc__' % method)
    # extract function signature:
    a = inspect.getargspec(eval('_BaseWriter.%s' % method))
    if a[3] is not None:  # keyword arguments?
        kwargs = ['%s=%r' % (arg, value) \
                  for arg, value in zip(a[0][-len(a[3]):], a[3])]
        args = a[0][:-len(a[3])]
        allargs = args + kwargs
    else:
        allargs = a[0]
    #print method, allargs, '\n', a
    signature_def = '%s(%s)' % (method, ', '.join(allargs))
    signature_call = '%s(%s)' % (method, ', '.join(a[0][1:]))  # exclude self
    code = """\
def _%s:
    '''\
%s
    '''
    for writer in self.writers:
        writer.%s

func_to_method(_%s, DocWriter, '%s')
""" % (signature_def, docstring, signature_call, method, method)
    #print 'Autogenerating\n', code
    exec(code)

def html_movie(plotfiles, interval_ms=300, width=800, height=600,
               casename=None):
    """
    Takes a list plotfiles, such as::

        'frame00.png', 'frame01.png', ...

    and creates javascript code for animating the frames as a movie in HTML.

    The `plotfiles` argument can be of three types:

      * A Python list of the names of the image files, sorted in correct
        order. The names can be filenames of files reachable by the
        HTML code, or the names can be URLs.
      * A filename generator using Unix wildcard notation, e.g.,
        ``frame*.png`` (the files most be accessible for the HTML code).
      * A filename generator using printf notation for frame numbering
        and limits for the numbers. An example is ``frame%0d.png:0->92``,
        which means ``frame00.png``, ``frame01.png``, ..., ``frame92.png``.
        This specification of `plotfiles` also allows URLs, e.g.,
        ``http://mysite.net/files/frames/frame_%04d.png:0->320``.

    If `casename` is None, a casename based on the full relative path of the
    first plotfile is used as tag in the variables in the javascript code
    such that the code for several movies can appear in the same file
    (i.e., the various code blocks employ different variables because
    the variable names differ).

    The returned result is text strings that incorporate javascript to
    loop through the plots one after another.  The html text also features
    buttons for controlling the movie.
    The parameter `iterval_ms` is the time interval between loading
    successive images and is in milliseconds.

    The `width` and `height` parameters do not seem to have any effect
    for reasons not understood.

    The following strings are returned: header, javascript code, form
    with movie and buttons, footer, and plotfiles::

       header, jscode, form, footer, plotfiles = html_movie('frames*.png')
       # Insert javascript code in some HTML file
       htmlfile.write(jscode + form)
       # Or write a new standalone file that act as movie player
       filename = plotfiles[0][:-4] + '.html'
       htmlfile = open(filename, 'w')
       htmlfile.write(header + jscode + form + footer)
       htmlfile.close

    This function is based on code written by R. J. LeVeque, based on
    a template from Alan McIntyre.
    """
    # Alternative method:
    # http://stackoverflow.com/questions/9486961/animated-image-with-javascript

    # Start with expanding plotfiles if it is a filename generator
    if not isinstance(plotfiles, (tuple,list)):
        if not isinstance(plotfiles, basestring):
            raise TypeError('plotfiles must be list or filename generator, not %s' % type(plotfiles))

        filename_generator = plotfiles
        if '*' in filename_generator:
            # frame_*.png
            if filename_generator.startswith('http'):
                raise ValueError('Filename generator %s cannot contain *; must be like http://some.net/files/frame_%%04d.png:0->120' % filename_generator)

            plotfiles = glob.glob(filename_generator)
            if not plotfiles:
                raise ValueError('No plotfiles on the form %s' %
                                 filename_generator)
            plotfiles.sort()
        elif '->' in filename_generator:
            # frame_%04d.png:0->120
            # http://some.net/files/frame_%04d.png:0->120
            p = filename_generator.split(':')
            filename = ':'.join(p[:-1])
            if not re.search(r'%0?\d+', filename):
                raise ValueError('Filename generator %s has wrong syntax; missing printf specification as in frame_%%04d.png:0->120' % filename_generator)
            if not re.search(r'\d+->\d+', p[-1]):
                raise ValueError('Filename generator %s has wrong syntax; must be like frame_%%04d.png:0->120' % filename_generator)
            p = p[-1].split('->')
            lo, hi = int(p[0]), int(p[1])
            plotfiles = [filename % i for i in range(lo,hi+1,1)]

    # Check that the plot files really exist, if they are local on the computer
    if not plotfiles[0].startswith('http'):
        missing_files = [fname for fname in plotfiles
                         if not os.path.isfile(fname)]
        if missing_files:
            raise ValueError('Missing plot files: %s' %
                             str(missing_files)[1:-1])

    if casename is None:
        # Use plotfiles[0] as the casename, but remove illegal
        # characters in variable names since the casename will be
        # used as part of javascript variable names.
        casename = os.path.splitext(plotfiles[0])[0]
        # Use _ for invalid characters
        casename = re.sub('[^0-9a-zA-Z_]', '_', casename)
        # Remove leading illegal characters until we find a letter or underscore
        casename = re.sub('^[^a-zA-Z_]+', '', casename)

    filestem, ext = os.path.splitext(plotfiles[0])
    if ext == '.png' or ext == '.jpg' or ext == '.jpeg' or ext == 'gif':
        pass
    else:
        raise ValueError('Plotfiles (%s, ...) must be PNG, JPEG, or GIF files with '\
                         'extension .png, .jpg/.jpeg, or .gif' % plotfiles[0])

    header = """\
<html>
<head>
</head>
<body>
"""
    no_images = len(plotfiles)
    jscode = """
<script language="Javascript">
<!---
var num_images_%(casename)s = %(no_images)d;
var img_width_%(casename)s = %(width)d;
var img_height_%(casename)s = %(height)d;
var interval_%(casename)s = %(interval_ms)d;
var images_%(casename)s = new Array();

function preload_images_%(casename)s()
{
   t = document.getElementById("progress");
""" % vars()

    i = 0
    for fname in plotfiles:
        jscode += """
   t.innerHTML = "Preloading image ";
   images_%(casename)s[%(i)s] = new Image(img_width_%(casename)s, img_height_%(casename)s);
   images_%(casename)s[%(i)s].src = "%(fname)s";
        """ % vars()
        i = i+1
    jscode += """
   t.innerHTML = "";
}

function tick_%(casename)s()
{
   if (frame_%(casename)s > num_images_%(casename)s - 1)
       frame_%(casename)s = 0;

   document.name_%(casename)s.src = images_%(casename)s[frame_%(casename)s].src;
   frame_%(casename)s += 1;
   tt = setTimeout("tick_%(casename)s()", interval_%(casename)s);
}

function startup_%(casename)s()
{
   preload_images_%(casename)s();
   frame_%(casename)s = 0;
   setTimeout("tick_%(casename)s()", interval_%(casename)s);
}

function stopit_%(casename)s()
{ clearTimeout(tt); }

function restart_%(casename)s()
{ tt = setTimeout("tick_%(casename)s()", interval_%(casename)s); }

function slower_%(casename)s()
{ interval_%(casename)s = interval_%(casename)s/0.7; }

function faster_%(casename)s()
{ interval_%(casename)s = interval_%(casename)s*0.7; }

// --->
</script>
""" % vars()
    plotfile0 = plotfiles[0]
    form = """
<form>
&nbsp;
<input type="button" value="Start movie" onClick="startup_%(casename)s()">
<input type="button" value="Pause movie" onClick="stopit_%(casename)s()">
<input type="button" value="Restart movie" onClick="restart_%(casename)s()">
&nbsp;
<input type="button" value="Slower" onClick="slower_%(casename)s()">
<input type="button" value="Faster" onClick="faster_%(casename)s()">
</form>

<p><div ID="progress"></div></p>
<img src="%(plotfile0)s" name="name_%(casename)s" border=2/>
""" % vars()
    footer = '\n</body>\n</html>\n'
    return header, jscode, form, footer, plotfiles

def html_movie_embed(moviefile, width=400, height=400):
    """
    Return HTML for embedding a moviefile using the default
    handling of such files.
    """
    text = """
<embed src="%(moviefile)s"
width="%(width)s"
height="%(height)s"
autoplay="false"
loop="true">
</embed>
""" % vars()
    return text

def html_movie_embed_wmp(moviefile, width=400, height=400):
    """Return HTML text for embedding a movie file
    (Windows Media Player code)."""
    text = """
<object id="MediaPlayer1" width="180" height="200"
classid="CLSID:22D6F312-B0F6-11D0-94AB-0080C74C7E95"
codebase="http://activex.microsoft.com/activex/controls/mplayer/en/nsmp2inf.cab#Version=5,1,52,701"
standby="Loading Microsoft Windows Media Player components..."
type="application/x-oleobject" align="middle">
<param name="FileName" value="%(moviefile)s">
<param name="ShowStatusBar" value="True">
<param name="DefaultFrame" value="mainFrame">
<param name="autostart" value="false">
<embed type="application/x-mplayer2"
pluginspage = "http://www.microsoft.com/Windows/MediaPlayer/"
src="%(moviefile)s"
autostart="false"
align="middle"
width="%(width)s"
height="%(height)s"
loop="100"
defaultframe="rightFrame"
showstatusbar="true">
</embed>
</object>
<!--
<a href="%(moviefile)s"><font size="2">Download movie file</font></a>
<a href="http://www.microsoft.com/windows/windowsmedia/mp10/default.aspx">
<font size="1">Download Windows Media Player</font></a></p>
-->
<!--
Attributes of the <embed> tag are:
src - tells what file to use.
autostart="true" - tells the computer to start the Video playing upon loading the page.
autostart="false" - tells the computer not to start the Video playing upon loading the page. You must click the start button to make the Video play.
align=middle - tells the computer to put the start/stop buttons to the middle.
width= and height= - are the dimensions of a small button panel that will appear when the page loads and contains both a START & STOP button so the visitor can start/stop the Video.
loop=2 - will play the Video for two complete loops.
-->
""" % vars()
    return text

def html_movie_embed_qt(moviefile, width=400, height=400):
    """Return HTML for embedding a moviefile (QuickTime code)."""
    text = """
<object classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B"
codebase="http://www.apple.com/qtactivex/qtplugin.cab"
width="%(width)s" height="%(height)s" >
<param name="src" value="%(moviefile)s" >
<param name="autoplay" value="false" >
<embed src="%(moviefile)s"
pluginspage="http://www.apple.com/quicktime/download"
width="%(width)s" height="%(height)s" autoplay="false">
</embed>
</object>
""" % vars()
    return text



def _test(d):
    # d is formatclass() or DocWriter(HTML, LaTeX, ...)
    print('\n\n', '*'*70, \
          '\n*** Testing class "%s"\n' % d.__class__.__name__, '*'*70)

    d.title('My Test of Class %s' % d.__class__.__name__,
            [('Hans Petter Langtangen',
              'Simula Research Laboratory',
              'Dept. of Informatics, Univ. of Oslo'),
             ])
    d.section('First Section')
    d.text("""
Here is some
text for section 1.

This is a *first* example of using the _DocWriter
module_ for writing documents from *Python* scripts.
It could be a nice tool since we do not need to bother
with special typesetting, such as `fixed width fonts`
in plain text.
""")
    d.subsection('First Subsection')
    d.text('Some text for the subsection.')
    d.paragraph('Test of a Paragraph')
    d.text("""
Some paragraph text taken from "Documenting Python": The Python language
has a substantial body of documentation, much of it contributed by various
authors. The markup used for the Python documentation is based on
LaTeX and requires a significant set of macros written specifically
for documenting Python. This document describes the macros introduced
to support Python documentation and how they should be used to support
a wide range of output formats.

This document describes the document classes and special markup used
in the Python documentation. Authors may use this guide, in
conjunction with the template files provided with the distribution, to
create or maintain whole documents or sections.

If you're interested in contributing to Python's documentation,
there's no need to learn LaTeX if you're not so inclined; plain text
contributions are more than welcome as well.
""")
    d.text('Here is an enumerate list:')
    samplelist = ['item1', 'item2',
                  ['subitem1', 'subitem2'],
                  'item3',
                  ['subitem3', 'subitem4']]
    d.list(samplelist, listtype='enumerate')
    d.text('...with some trailing text.')
    d.subsubsection('First Subsubsection with an Itemize List')
    d.list(samplelist, listtype='itemize')
    d.text('Here is some Python code:')
    d.verbatim("""
class A:
    pass

class B(A):
    pass

b = B()
b.item = 0  # create a new attribute
""")
    d.section('Second Section')
    d.text('Here is a description list:')
    d.list(['keyword1: item1', 'keyword2: item2 goes here, with a colon : and some text after',
        ['key3: subitem1', 'key4: subitem2'],
        'key5: item3',
        ['key6: subitem3', 'key7: subitem4']],
           listtype='description')
    d.paragraph_separator()
    d.text('And here is a table:')
    d.table([['a', 'b'], ['c', 'd'], ['e', 'and a longer text']])
    print(d)
    d.write_to_file('tmp_%s' % d.__class__.__name__)

if __name__ == '__main__':
    formats = HTML, DocOnce
    for format in formats:
        d = format()
        _test(d)
    formats_str = [format.__name__ for format in formats]
    d = DocWriter(*formats_str)
    _test(d)
