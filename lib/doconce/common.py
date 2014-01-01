"""
This module contains data structures used in translation of the
Doconce format to other formats.  Some convenience functions used in
translation modules (latex.py, html.py, etc.) are also included in
here.
"""
import re, sys, urllib, os

# Identifiers in the text used to identify code and math blocks
_CODE_BLOCK = '<<<!!CODE_BLOCK'
_MATH_BLOCK = '<<<!!MATH_BLOCK'

# Comment lines used to identify parts that can later be removed.
# The lines below are wrapped as comments.
# Defined here once so different modules can utilize the same syntax.
envir_delimiter_lines = {
    'sol':
    ('--- begin solution of exercise ---',
     '--- end solution of exercise ---'),
    'ans':
    ('--- begin answer of exercise ---',
     '--- end answer of exercise ---'),
    'hint':
    ('--- begin hint in exercise ---',
     '--- end hint in exercise ---'),
    'exercise':
    ('--- begin exercise ---',
     '--- end exercise ---'),
}

_counter_for_html_movie_player = 0

def _abort():
    if '--no_abort' in sys.argv:
        print 'avoided abortion because of --no-abort'
    else:
        print 'Abort! (add --no_abort on the command line to avoid this abortion)'
        sys.exit(1)

def safe_join(lines, delimiter):
    try:
        filestr = delimiter.join(lines) + '\n' # will fail if ord(char) > 127
        return filestr
    except UnicodeDecodeError, e:
        if "'ascii' codec can't decode" in e and 'position' in e:
            pos = int(e.split('position')[1].split(':'))
            print filestr[pos-50:pos], '[problematic char]', filestr[pos+1:pos+51]
            _abort()
        else:
            print e
            _abort()

def fix_backslashes(text):
    """
    If some Doconce text is read from a doc string
    or from a GUI, backslashes are normally interpreted,
    and the Doconce text is then malformed. This function
    restores backslashes. For double backslash in LaTeX
    one needs to have the double backslash at the end of
    the line, otherwise they are not preserved.
    """
    # Preserve backslashes as in a raw string
    escape = {
        '\\'+ '\n':'\\\\' + '\n',
        '\a':r'\a',
        '\b':r'\b',
        '\c':r'\c',
        '\f':r'\f',
        '\r':r'\r',
        '\t':r'\t',
        '\v':r'\v',
        }
    for char in escape:
        text = text.replace(char, escape[char])
    return text


def where():
    """
    Return the location where the doconce package is installed.
    """
    # Technique: find the directory where this common.py file resides
    import os
    return os.path.dirname(__file__)

def is_file_or_url(filename, msg='checking existence of', debug=True):
    """
    Return "file" if filename is a file, "url" if filename
    is a URL (not an HTML file), and None otherwise.

    The string ``msg`` is written out together with ``filename``,
    unless ``msg=None``.
    """
    if debug and msg is None:
        msg = ''  # Avoid printing None

    if filename.startswith('http'):
        try:
            # Print a message in case the program hangs a while here
            if msg is not None or debug:
                print '...', msg, filename, '...',
            f = urllib.urlopen(filename)
            text = f.read()
            f.close()
            ext = os.path.splitext(filename)[1]
            if ext in ('.html', 'htm'):
                # Successful opening of an HTML file
                if msg or debug:
                    print 'found!'
                return 'url'
            elif ext == '':
                # Successful opening of a directory (meaning index.html)
                if msg or debug:
                    print 'found!'
                return 'url'
            else:
                # Seemingly successful opening of a file, but check if
                # this is a special GitHub error message file
                special_hosts = ('github.', 'www.uio.no')
                special_host = False
                for host in special_hosts:
                    if host in filename:
                        special_host = True
                        break
                if special_host and '>404' in text:
                    # HTML file with an error message: file not found
                    if msg or debug:
                        print 'not found (%s, 404 error)' % filename
                        return None
                else:
                    if msg or debug:
                        print 'found!'
                    return 'url'
        except IOError, e:
            if msg or debug:
                print 'not found!'
            if debug:
                print 'urllib.urlopen error:', e
            return None
    else:
        return ('file' if os.path.isfile(filename) else None)


def indent_lines(text, format, indentation=' '*8, trailing_newline=True):
    """
    Indent each line in the string text, provided in a format for
    HTML, LaTeX, epytext, ..., by the blank string indentation.
    Return new version of text.
    """
    if format == 'epytext':
        # some formats (Epytext) give wrong behavior if there is a \n
        # in code or tex blocks (\nabla is one example), hence we
        # comment out the block in those cases: (\b also gives problems...
        # it seems that Epytext is not capable of doing raw strings here)
        if re.search(r'\\n', text):
            comment_out = True
            text = """\

            NOTE: A verbatim block has been removed because
                  it causes problems for Epytext.

"""
            return text

    # indent X chars (choose X=6 for sufficient indent in lists)
    text = '\n'.join([indentation + line for line in text.splitlines()])
    if trailing_newline:
        text += '\n'
    return text

def cite_with_multiple_args2multiple_cites(filestr):
    """Fix cite{key1,key2,key3} to cite{key1}cite[key2]cite[key3]."""
    cite_args = re.findall(r'cite\{(.+?)\}', filestr)
    if cite_args:
        for arg in cite_args:
            args = [a.strip() for a in arg.split(',')]
            if len(args) > 1:
                args = ' '.join(['cite{%s}' % a for a in args])
                filestr = filestr.replace('cite{%s}' % arg, args)
    return filestr

def table_analysis(table):
    """Return max width of each column."""
    # Find max no of columns
    max_num_columns = 0
    for row in table:
        max_num_columns = max(max_num_columns, len(row))
    # Consistency checks
    if table[0] != ['horizontal rule'] or \
       table[2] != ['horizontal rule'] or \
       table[-1] != ['horizontal rule']:
        print '*** error: table lacks the right three horizontal rules'
    if len(table[1]) < max_num_columns:
        print '*** warning: table headline with entries'
        print '   ', '| ' + ' | '.join(table[1]) + ' |'
        print '   has %d columns while further down there are %d columns' % \
              (len(table[1]), max_num_columns)
    # Find width of the various columns
    column_list = []
    for i, row in enumerate(table):
        if row != ['horizontal rule']:
            if not column_list:
                column_list = [[]]*max_num_columns
            for j, column in enumerate(row):
                column_list[j].append(len(column))
    return [max(c) for c in column_list]

def online_python_tutor(code, return_tp='iframe'):
    """
    Return URL (return_tp is 'url') or iframe HTML code
    (return_tp is 'iframe') for code embedded in
    on pythontutor.com.
    """
    codestr = urllib.quote_plus(code.strip())
    if return_tp == 'iframe':
        urlprm = urllib.urlencode({'py': 2,
                                   'curInstr': 0,
                                   'cumulative': 'false'})
        iframe = """\
<iframe width="950" height="500" frameborder="0"
        src="http://pythontutor.com/iframe-embed.html#code=%s&%s">
</iframe>
""" % (codestr, urlprm) # must treat code separately (urlencode adds chars)
        return iframe
    elif return_tp == 'url':
        url = 'http://pythontutor.com/visualize.html#code=%s&mode=display&cumulative=false&heapPrimitives=false&drawParentPointers=false&textReferences=false&py=2&curInstr=0' % codestr
        url = url.replace('%', '\\%').replace('#', '\\#')
        return url
    else:
        print 'BUG'; _abort()

def align2equations(filestr, format):
    """Turn align environments into separate equation environments."""
    if not '{align}' in filestr:
        return filestr

    # sphinx: just replace align, pandoc/ipynb: replace align and align*
    # technique: add } if sphinx
    postfixes = ['}'] if format == 'sphinx' else ['}', '*}']

    lines = filestr.splitlines()
    inside_align = False
    inside_code = False
    for postfix in postfixes:
        for i in range(len(lines)):
            if lines[i].startswith('!bc'):
                inside_code = True
            if lines[i].startswith('!ec'):
                inside_code = False
            if inside_code:
                continue

            if r'\begin{align%s' % postfix in lines[i]:
                inside_align = True
                lines[i] = lines[i].replace(
                r'\begin{align%s' % postfix, r'\begin{equation%s' % postfix)
            if inside_align and '\\\\' in lines[i]:
                lines[i] = lines[i].replace(
                '\\\\', '\n' + r'\end{equation%s' % postfix + '\n!et\n\n!bt\n' + r'\begin{equation%s ' % postfix)
            if inside_align and '&' in lines[i]:
                lines[i] = lines[i].replace('&', '')
            if r'\end{align%s' % postfix in lines[i]:
                inside_align = False
                lines[i] = lines[i].replace(
                r'\end{align%s' % postfix, r'\end{equation%s' % postfix)
    filestr = '\n'.join(lines)
    return filestr


def ref2equations(filestr):
    """
    Replace references to equations:

    (ref{my:label}) -> Equation (my:label)
    (ref{my:label1})-(ref{my:label2}) -> Equations (my:label1)-(my:label2)
    (ref{my:label1}) and (ref{my:label2}) -> Equations (my:label1) and (my:label2)
    (ref{my:label1}), (ref{my:label2}) and (ref{my:label3}) -> Equations (my:label1), (my:label2) and (ref{my:label2})

    """
    filestr = re.sub(r'\(ref\{(.+?)\}\)-\(ref\{(.+?)\}\)',
                     r'Equations (\g<1>)-(\g<2>)', filestr)
    filestr = re.sub(r'\(ref\{(.+?)\}\)\s+and\s+\(ref\{(.+?)\}\)',
                     r'Equations (\g<1>) and (\g<2>)', filestr)
    filestr = re.sub(r'\(ref\{(.+?)\}\),\s*\(ref\{(.+?)\}\)(,?)\s+and\s+\(ref\{(.+?)\}\)',
                     r'Equations (\g<1>), (\g<2>)\g<3> and (\g<4>)', filestr)
    filestr = re.sub(r'\(ref\{(.+?)\}\)',
                     r'Equation (\g<1>)', filestr)

    # Note that we insert "Equation(s)" here, assuming that this word
    # is *not* used in running text prior to a reference. Sometimes
    # sentences are started with "Equation ref{...}" and this double
    # occurence of Equation must be fixed.

    filestr = re.sub('Equation\s+Equation', 'Equation', filestr)
    filestr = re.sub('Equations\s+Equations', 'Equations', filestr)
    return filestr

def default_movie(m):
    """
    Replace a movie entry by a proper URL with text.
    The idea is to link to an HTML file with the media element.
    """
    # Note: essentially same code as html_movie
    global _counter_for_html_movie_player
    filename = m.group('filename')
    caption = m.group('caption').strip()
    from html import html_movie
    text = html_movie(m)

    # Make an HTML file where the movie file can be played
    # (alternative to launching a player manually)
    _counter_for_html_movie_player += 1
    moviehtml = 'movie_player%d' % \
    _counter_for_html_movie_player + '.html'
    f = open(moviehtml, 'w')
    f.write("""
<html>
<body>
<title>Embedding media in HTML</title>
%s
</body>
</html>
""" % text)
    print '*** made link to new HTML file %s\n    with code to display the movie \n    %s' % (moviehtml, filename)
    text = '%s file: %s, load "`%s`" :"%s" into a browser' % \
       (caption, filename, moviehtml, moviehtml)
    return text

def begin_end_consistency_checks(filestr, envirs):
    """Perform consistency checks: no of !bc must equal no of !ec, etc."""
    for envir in envirs:
        begin = '!b' + envir
        end = '!e' + envir

        nb = len(re.compile(r'^%s' % begin, re.MULTILINE).findall(filestr))
        ne = len(re.compile(r'^%s' % end, re.MULTILINE).findall(filestr))

        lines = []
        if nb != ne:
            print 'ERROR: %d %s do not match %d %s directives' % \
                  (nb, begin, ne, end)
            if not lines:
                lines = filestr.splitlines()
            begin_ends = []
            for i, line in enumerate(lines):
                if line.startswith(begin):
                    begin_ends.append((begin, i))
                if line.startswith(end):
                    begin_ends.append((end, i))
            for k in range(1, len(begin_ends)):
                pattern, i = begin_ends[k]
                if pattern == begin_ends[k-1][0]:
                    print '\n\nTwo', pattern, 'after each other!\n'
                    for j in range(begin_ends[k-1][1], begin_ends[k][1]+1):
                        print lines[j]
                    _abort()
            if begin_ends[-1][0].startswith('!b'):
                print 'Missing %s after final %s' % \
                      (begin_ends[-1][0].replace('!b', '!e'),
                       begin_ends[-1][0])
                _abort()


def remove_code_and_tex(filestr):
    """
    Remove verbatim and latex (math) code blocks from the file and
    store separately in lists (code_blocks and tex_blocks).
    The function insert_code_and_tex will insert these blocks again.
    """
    # Method:
    # store code and tex blocks in lists and substitute these blocks
    # by the contents of _CODE_BLOCK and _MATH_BLOCK (arguments after
    # !bc must be copied after _CODE_BLOCK).
    # later we replace _CODE_BLOCK by !bc and !ec and the code block again
    # (similarly for the tex/math block).

    # (recall that !bc can be followed by extra information that we must keep:)
    code = re.compile(r'^!bc(.*?)\n(.*?)^!ec *\n', re.DOTALL|re.MULTILINE)

    # Note: final \n is required and may be missing if there is a block
    # at the end of the file, so let us ensure that a blank final
    # line is appended to the text:
    if filestr[-1] != '\n':
        filestr = filestr + '\n'

    result = code.findall(filestr)
    code_blocks = [c for opt, c in result]
    code_block_types = [opt.strip() for opt, c in result]

    tex = re.compile(r'^!bt\n(.*?)^!et *\n', re.DOTALL|re.MULTILINE)
    tex_blocks = tex.findall(filestr)

    # Remove blocks and substitute by a one-line sign
    filestr = code.sub('%s \g<1>\n' % _CODE_BLOCK, filestr)
    filestr = tex.sub('%s\n' % _MATH_BLOCK, filestr)

    # Number the blocks
    lines = filestr.splitlines()
    code_block_counter = 0
    math_block_counter = 0
    for i in range(len(lines)):
        if lines[i].startswith(_CODE_BLOCK):
            lines[i] = '%d ' % code_block_counter + lines[i]
            code_block_counter += 1
        if lines[i].startswith(_MATH_BLOCK):
            lines[i] = '%d ' % math_block_counter + lines[i]
            math_block_counter += 1
    filestr = safe_join(lines, '\n')

    # Give error if blocks contain !bt

    return filestr, code_blocks, code_block_types, tex_blocks


def insert_code_and_tex(filestr, code_blocks, tex_blocks, format):
    # Consistency check
    n = filestr.count(_CODE_BLOCK)
    if len(code_blocks) != n:
        print '*** error: found %d code block markers for %d initial code blocks' % (n, len(code_blocks))
        print """    Possible causes:
           - mismatch of !bt and !et within one file, such that a !bt
             swallows code
           - mismatch of !bt and !et across files in multi-file documents
           - !bc and !ec inside code blocks - replace by |bc and |ec
    (run doconce on each file to locate the problem, then on
     smaller and smaller parts of each file)"""
        _abort()
    n = filestr.count(_MATH_BLOCK)
    if len(tex_blocks) != n:
        print '*** error: found %d tex block markers for %d initial tex blocks\nAbort!' % (n, len(tex_blocks))
        print """    Possible causes:
           - mismatch of !bc and !ec within one file, such that a !bc
             swallows tex blocks
           - mismatch of !bc and !ec across files in multi-file documents
           - !bt and !et inside code blocks - replace by |bt and |et
    (run doconce on each file to locate the problem, then on
     smaller and smaller parts of each file)"""
        _abort()

    lines = filestr.splitlines()

    # Note: re.sub cannot be used because newlines, \nabla, etc
    # are not handled correctly. Need str.replace.

    for i in range(len(lines)):
        if _CODE_BLOCK in lines[i] or _MATH_BLOCK in lines[i]:
            words = lines[i].split()
            # on a line: number block-indicator code-type
            n = int(words[0])
            if _CODE_BLOCK in lines[i]:
                words[1] = '!bc'
                code = code_blocks[n]
                lines[i] = ' '.join(words[1:]) + '\n' + code + '!ec'
            if _MATH_BLOCK in lines[i]:
                words[1] = '!bc'
                math = tex_blocks[n]
                lines[i] = '!bt\n' + math + '!et'

    filestr = safe_join(lines, '\n')
    return filestr


def doconce_exercise_output(exer,
                            solution_header = '__Solution.__',
                            answer_header = '__Answer.__ ',
                            hint_header = '__Hint.__ ',
                            include_numbering=True,
                            include_type=True):
    """
    Write exercise in Doconce format. This output can be
    reused in most formats.
    """
    # Note: answers, solutions, and hints must be written out and not
    # removed here, because if they contain math or code blocks,
    # there will be fewer blocks in the end that what was extracted
    # at the beginning of the translation process.

    s = '\n\n# ' + envir_delimiter_lines['exercise'][0] + '\n\n'
    s += exer['heading']  # result string
    if include_numbering and not include_type:
        include_type = True
    if not exer['type_visible']:
        include_type = False
    if include_type:
        s += ' ' + exer['type']
        if include_numbering:
            s += ' ' + str(exer['no'])
        s += ':'
    s += ' ' + exer['title'] + ' ' + exer['heading'] + '\n'

    if exer['label']:
        s += 'label{%s}' % exer['label'] + '\n'

    if exer['keywords']:
        s += '# keywords = %s' % '; '.join(exer['keywords']) + '\n'

    if exer['text']:
        s += '\n' + exer['text'] + '\n'

    if exer['hints']:
        for i, hint in enumerate(exer['hints']):
            if len(exer['hints']) == 1 and i == 0:
                hint_header_ = hint_header
            else:
                hint_header_ = hint_header.replace('Hint.', 'Hint %d.' % (i+1))
            if exer['type'] != 'Example':
                s += '\n# ' + envir_delimiter_lines['hint'][0] + '\n'
            s += '\n' + hint_header_ + hint + '\n'
            if exer['type'] != 'Example':
                s += '\n# ' + envir_delimiter_lines['hint'][1] + '\n'

    if exer['answer']:
        s += '\n'
        # Leave out begin-end answer comments if example since we want to
        # avoid marking such sections for deletion (--without_answers)
        if exer['type'] != 'Example':
            s += '\n# ' + envir_delimiter_lines['ans'][0] + '\n'
        s += answer_header + '\n' + exer['answer'] + '\n'
        if exer['type'] != 'Example':
            s += '\n# ' + envir_delimiter_lines['ans'][1] + '\n'


    if exer['solution']:
        s += '\n'
        # Leave out begin-end solution comments if example since we want to
        # avoid marking such sections for deletion (--without_solutions)
        if exer['type'] != 'Example':
            s += '\n# ' + envir_delimiter_lines['sol'][0] + '\n'
        s += solution_header + '\n'
        # Make sure we have a sentence after the heading
        if re.search(r'^\d+ %s' % _CODE_BLOCK, exer['solution'].lstrip()):
            print '\nwarning: open the solution in exercise "%s" with a line of\ntext before the code! (Now "Code:" is inserted)' % exer['title'] + '\n'
            s += 'Code:\n'
        s += exer['solution'] + '\n'
        if exer['type'] != 'Example':
            s += '\n# ' + envir_delimiter_lines['sol'][1] + '\n'

    if exer['subex']:
        s += '\n'
        import string
        for i, subex in enumerate(exer['subex']):
            letter = string.ascii_lowercase[i]
            s += '\n__%s)__ ' % letter

            if subex['text']:
                s += '\n' + subex['text'] + '\n'

                for i, hint in enumerate(subex['hints']):
                    if len(subex['hints']) == 1 and i == 0:
                        hint_header_ = hint_header
                    else:
                        hint_header_ = hint_header.replace(
                            'Hint.', 'Hint %d.' % (i+1))
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['hint'][0] + '\n'
                    s += '\n' + hint_header_ + hint + '\n'
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['hint'][1] + '\n'

                if subex['file']:
                    if len(subex['file']) == 1:
                        s += 'Filename: `%s`' % subex['file'][0] + '.\n'
                    else:
                        s += 'Filenames: %s' % \
                             ', '.join(['`%s`' % f for f in subex['file']]) + '.\n'

                if subex['answer']:
                    s += '\n'
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['ans'][0] + '\n'
                    s += answer_header + '\n' + subex['answer'] + '\n'
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['ans'][1] + '\n'

                if subex['solution']:
                    s += '\n'
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['sol'][0] + '\n'
                    s += solution_header + '\n'
                    # Make sure we have a sentence after the heading
                    if re.search(r'^\d+ %s' % _CODE_BLOCK,
                                 subex['solution'].lstrip()):
                        print '\nwarning: open the solution in exercise "%s" with a line of\ntext before the code! (Now "Code:" is inserted)' % exer['title'] + '\n'
                        s += 'Code:\n'
                    s += subex['solution'] + '\n'
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['sol'][1] + '\n'

    if exer['file']:
        if exer['subex']:
            # Place Filename: ... as a list paragraph if subexercises,
            # otherwise let it proceed at the end of the exercise text.
            s += '\n'
        if len(exer['file']) == 1:
            s += 'Filename: `%s`' % exer['file'][0] + '.\n'
        else:
            s += 'Filenames: %s' % \
                 ', '.join(['`%s`' % f for f in exer['file']]) + '.\n'
        #s += '*Filename*: `%s`' % exer['file'] + '.\n'
        #s += '\n' + '*Filename*: `%s`' % exer['file'] + '.\n'

    if exer['closing_remarks']:
        s += '\n# Closing remarks for this %s\n\n=== Remarks ===\n\n' % \
             exer['type'] + exer['closing_remarks'] + '\n\n'

    if exer['solution_file']:
        if len(exer['solution_file']) == 1:
            s += '# solution file: %s\n' % exer['solution_file'][0]
        else:
            s += '# solution files: %s\n' % ', '.join(exer['solution_file'])

    s += '\n# ' + envir_delimiter_lines['exercise'][1] + '\n\n'
    return s

def plain_exercise(exer):
    return doconce_exercise_output(exer)


def bibliography(pubdata, citations, format='doconce'):
    """
    Return Doconce formatted list of references, based on the keys
    in the ordered dictionary ``citations`` (``pubdata`` is a list
    of dicts loaded from a Publish database file).
    """
    import publish_doconce
    if format == 'doconce':
        formatter = publish_doconce.doconce_format
    elif format in ('rst', 'sphinx'):
        formatter = publish_doconce.rst_format

    citation_keys = list(citations.keys())
    # Reduce the database to the minimum
    pubdata = [pub for pub in pubdata if pub['key'] in citation_keys]
    # Sort publications in the order of citations
    pubs = []
    for key in citations:
        for pub in pubdata:
            if pub['key'] == key:
                pubs.append(pub)
                break
    #text = '\n======= Bibliography =======\n\n' # the user writes the heading
    text = ''
    for pub in pubs:
        text += formatter[pub['category']](pub)
    text += '\n\n'
    return text

BLANKLINE = {}
FILENAME_EXTENSION = {}
LIST = {}
CODE = {}
# listing of function parameters/arguments and return values:
ARGLIST = {}
DEFAULT_ARGLIST = {
    'parameter': 'argument',
    'keyword': 'keyword argument',
    'return': 'return value(s)',
    'instance variable': 'instance variable',
    'class variable': 'class variable',
    'module variable': 'module variable',
    }
TABLE = {}
FIGURE_EXT = {}
CROSS_REFS = {}
INDEX_BIB = {}
INTRO = {}
OUTRO = {}
EXERCISE = {}
TOC = {}
ENVIRS = {}


# regular expressions for inline tags:
inline_tag_begin = r"""(?P<begin>(^|[(\s]))"""
inline_tag_end = r"""(?P<end>($|[.,?!;:)}\s-]))"""
# alternatives using positive lookbehind and lookahead (not tested!):
inline_tag_before = r"""(?<=(^|[(\s]))"""
inline_tag_after = r"""(?=$|[.,?!;:)\s])"""
# the begin-end works, so don't touch (must be tested in a safe branch....)

_linked_files = '''\s*"(?P<url>([^"]+?\.html?|[^"]+?\.html?\#[^"]+?|[^"]+?\.txt|[^"]+?\.pdf|[^"]+?\.f|[^"]+?\.c|[^"]+?\.cpp|[^"]+?\.cxx|[^"]+?\.py|[^"]+?\.java|[^"]+?\.pl|[^"]+?\.sh|[^"]+?\.csh|[^"]+?\.zsh|[^"]+?\.ksh|[^"]+?\.tar\.gz|[^"]+?\.tar|[^"]+?\.f77|[^"]+?\.f90|[^"]+?\.f95|_static-?[^/]*/[^"]+?))"'''

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
    # simpler (not tested):
    #r'%s\$(?P<latexmath>[^$]+?)\$\|\$(?P<puretext>[^$]+)\$%s' % \
    #(inline_tag_begin, inline_tag_end),

    # *emphasized words*
    'emphasize':
    r'%s\*(?P<subst>[^ `][^*`]*)\*%s' % \
    (inline_tag_begin, inline_tag_end),

    # `verbatim inline text is enclosed in back quotes`
    'verbatim':
    r'%s`(?P<subst>[^ ][^`]*)`%s' % \
    (inline_tag_begin, r"(?P<end>($|[.,?!;:)}'\s-]))"), # inline_tag_end and '

    # _underscore before and after signifies bold_
    'bold':
    r'%s_(?P<subst>[^ `][^\]_`]*)_%s' % \
    (inline_tag_begin, inline_tag_end),

    # color{col}{text} (\b is useful, but :.;`? is not word boundary)
    'colortext':
    r'\bcolor\{(?P<color>[^}]+?)\}\{(?P<text>[^}]+)\}',

    # http://some.where.org/mypage<link text>  # old outdated syntax
    'linkURL':
    r'%s(?P<url>https?://[^<\n]+)<(?P<link>[^>]+)>%s' % \
    (inline_tag_begin, inline_tag_end),

    'linkURL2':  # "some link": "https://bla-bla"
    r'''"(?P<link>[^"]+?)" ?:\s*"(?P<url>(file:///|https?://|ftp://|mailto:).+?)"''',
    #r'"(?P<link>[^>]+)" ?: ?"(?P<url>https?://[^<]+?)"'

    'linkURL2v':  # verbatim link "`filelink`": "https://bla-bla"
    r'''"`(?P<link>[^"]+?)`" ?:\s*"(?P<url>(file:///|https?://|ftp://|mailto:).+?)"''',

    'linkURL3':  # "some link": "some/local/file/name.html" or .txt/.pdf/.py/.c/.cpp/.cxx/.f/.java/.pl files
    #r'''"(?P<link>[^"]+?)" ?:\s*"(?P<url>([^"]+?\.html?|[^"]+?\.txt|[^"]+?.pdf))"''',
    r'''"(?P<link>[^"]+?)" ?:''' + _linked_files,
    #r'"(?P<link>[^>]+)" ?: ?"(?P<url>https?://[^<]+?)"'
    'linkURL3v':  # "`somefile`": "some/local/file/name.html" or .txt/.pdf/.py/.c/.cpp/.cxx/.f/.java/.pl files
    r'''"`(?P<link>[^"]+?)`" ?:''' +  _linked_files,

    'plainURL':
    #r'"URL" ?: ?"(?P<url>.+?)"',
    #r'"?(URL|url)"? ?: ?"(?P<url>.+?)"',
    r'("URL"|"url"|URL|url) ?:\s*"(?P<url>.+?)"',

    'inlinecomment':  # needs re.DOTALL|re.MULTILINE
    r'''\[(?P<name>[ A-Za-z0-9_'+-]+?):(?P<space>\s+)(?P<comment>.*?)\]''',

    # __Abstract.__ Any text up to a headline === or toc-like keywords
    # (TOC is already processed)
    'abstract':  # needs re.DOTALL | re.MULTILINE
    r"""^\s*__(?P<type>Abstract|Summary).__\s*(?P<text>.+?)(?P<rest>TOC:|\\tableofcontents|Table of [Cc]ontents|\s*[_=]{3,9})""",
    #r"""^\s*__(?P<type>Abstract|Summary).__\s*(?P<text>.+?)(?P<rest>\s*[_=]{3,9})""",

    # ======= Seven Equality Signs for Headline =======
    # (the old underscores instead of = are still allowed)
    'section':
    #r'^_{7}(?P<subst>[^ ].*)_{7}\s*$',
    # previous: r'^\s*_{7}(?P<subst>[^ ].*?)_+\s*$',
    #r'^\s*[_=]{7}\s*(?P<subst>[^ ].*?)\s*[_=]+\s*$',
    #r'^\s*[_=]{7}\s*(?P<subst>[^ =-].+?)\s*[_=]+\s*$',
    r'^ *[_=]{7}\s*(?P<subst>[^ =-].+?)\s*[_=]{7} *$',

    'chapter':
    #r'^\s*[_=]{9}\s*(?P<subst>[^ =-].+?)\s*[_=]+\s*$',
    r'^ *[_=]{9}\s*(?P<subst>[^ =-].+?)\s*[_=]{9} *$',

    'subsection':
    #r'^\s*_{5}(?P<subst>[^ ].*?)_+\s*$',
    #r'^\s*[_=]{5}\s*(?P<subst>[^ ].*?)\s*[_=]+\s*$',
    #r'^\s*[_=]{5}\s*(?P<subst>[^ =-].+?)\s*[_=]+\s*$',
    r'^ *[_=]{5}\s*(?P<subst>[^ =-].+?)\s*[_=]{5} *$',

    'subsubsection':
    #r'^\s*_{3}(?P<subst>[^ ].*?)_+\s*$',
    #r'^\s*[_=]{3}\s*(?P<subst>[^ ].*?)\s*[_=]+\s*$',
    #r'^\s*[_=]{3}\s*(?P<subst>[^ =-].+?)\s*[_=]+\s*$',
    r'^ *[_=]{3}\s*(?P<subst>[^ =-].+?)\s*[_=]{3}\s*$',  # final \s for latex

    # __Two underscores for Inline Paragraph Title.__
    'paragraph':
    r'(?P<begin>^)__(?P<subst>.+?)__\s+',
    #r'(?P<begin>^)[_=]{2}\s*(?P<subst>[^ =-].+?)[_=]{2}\s+',

    # TITLE: My Document Title
    'title':
    r'^TITLE:\s*(?P<subst>.+)\s*$',

    # AUTHOR: Some Name
    'author':
    #r'^AUTHOR:\s*(?P<name>.+?)\s+at\s+(?P<institution>.+)\s*$',
    # for backward compatibility (comma or at as separator):
    r'^AUTHOR:\s*(?P<name>.+?)(,|\s+at\s+)(?P<institution>.+)\s*$',

    # DATE: Jan 27, 2010
    'date':
    r'^DATE:\s*(?P<subst>.+)\s*$',

    # FIGURE:[filename, options] some caption text label{some:label}
    # (until blank line ^\s*$)
    'figure':
    r'^FIGURE:\s*\[(?P<filename>[^,\]]+),?(?P<options>[^\]]*)\]\s*?(?P<caption>.*)$',

    # MOVIE:[filename, options] some caption text label{some:label}
    'movie':
    r'^MOVIE:\s*\[(?P<filename>[^,\]]+),?(?P<options>[^\]]*)\]\s*?(?P<caption>.*)$',
    }
INLINE_TAGS_SUBST = {}

# frequent syntax errors that we can test for: (not yet used)
heading_error = (r'(^ [_=]+[^_=]*|^[_=]+[^ _=]*$)',
                 'Initial spaces or missing underscore(s) or = at the end')
INLINE_TAGS_BUGS = {
    # look for space after first special character ($ ` _ etc)
    'math': (r'%s(?P<subst>\$ [^$]*\$)%s' % (inline_tag_begin, inline_tag_end),
             'Space after first $ in inline math expressions'),
    'emphasize': None, # *item with *emph* word is legal (no error)
    'verbatim': (r'%s(?P<subst>` [^`]*`)%s' % \
                 (inline_tag_begin, inline_tag_end),
                 'Space after first ` in inline verbatim expressions'),
    'bold': (r'%s(?P<subst>_ [^_]*_)%s' % \
             (inline_tag_begin, inline_tag_end),
             'Space after first _ in inline boldface expressions'),
    'section': heading_error,
    'subsection': heading_error,
    'subsubsection': heading_error,
    'paragraph': heading_error,
    }

LIST_SYMBOL = {'*': 'itemize', 'o': 'enumerate', '-': 'description'}
