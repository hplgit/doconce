"""
This module contains data structures used in translation of the
DocOnce format to other formats.  Some convenience functions used in
translation modules (latex.py, html.py, etc.) are also included in
here.
"""
import re, sys, urllib, os
from misc import option, _abort

format = None   # latex, pdflatex, html, plain, etc

# Identifiers in the text used to identify code and math blocks
_CODE_BLOCK = '<<<!!CODE_BLOCK'
_MATH_BLOCK = '<<<!!MATH_BLOCK'

# Chapter regex
chapter_pattern = r'^=========\s*[A-Za-z0-9].+?========='

emoji_url = 'https://raw.githubusercontent.com/hplgit/doconce/master/bundled/emoji/png/'

# Functions for creating and reading comment tags
def begin_end_comment_tags(tag):
    return '--- begin ' + tag + ' ---', '--- end ' + tag + ' ---'

def comment_tag(tag, comment_pattern='# %s'):
    return comment_pattern % tag

def begin_comment_tag(tag, comment_pattern='# %s'):
    return comment_pattern % (begin_end_comment_tags(tag)[0])

def end_comment_tag(tag, comment_pattern='# %s'):
    return comment_pattern % (begin_end_comment_tags(tag)[1])

# Comment lines used to identify parts that can later be removed.
# The lines below are wrapped as comments.
# Defined here once so different modules can utilize the same syntax.
envir_delimiter_lines = {
    'sol':
    begin_end_comment_tags('solution of exercise'),
    'ans':
    begin_end_comment_tags('answer of exercise'),
    'hint':
    begin_end_comment_tags('hint in exercise'),
    'exercise':
    begin_end_comment_tags('exercise'),
    'subex':
    begin_end_comment_tags('subexercise'),
}

_counter_for_html_movie_player = 0

def internet_access(timeout=1):
    """Return True if internet is on, else False."""
    import urllib2, socket
    try:
        # Check google.com with numerical IP-address (which avoids
        # DNS loopup) and set timeout to 1 sec so this does not
        # take much time (google.com should respond quickly)
       #response = urllib2.urlopen('http://8.8.8.8', timeout=timeout)
       response = urllib2.urlopen('http://vg.no', timeout=timeout)
       return True
    except (urllib2.URLError, socket.timeout) as err:
        pass
    return False

def safe_join(lines, delimiter):
    try:
        filestr = delimiter.join(lines) + '\n' # will fail if ord(char) > 127
        return filestr
    except UnicodeDecodeError, e:
        if "'ascii' codec can't decode":
            print '*** error: non-ascii character - rerun with --encoding=utf-8'
            _abort()
        else:
            print e
            _abort()

def fix_backslashes(text):
    """
    If some DocOnce text is read from a doc string
    or from a GUI, backslashes are normally interpreted,
    and the DocOnce text is then malformed. This function
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
                print '...', msg, filename, '...'
            f = urllib.urlopen(filename)
            text = f.read()
            f.close()
            ext = os.path.splitext(filename)[1]
            if ext in ('.html', 'htm'):
                # Successful opening of an HTML file
                if msg or debug:
                    print '    found!'
                return 'url'
            elif ext == '':
                # Successful opening of a directory (meaning index.html)
                if msg or debug:
                    print '    found!'
                return 'url'
            else:
                # Seemingly successful opening of a file, but check if
                # this is a special GitHub error message file
                special_hosts = ('github', 'www.uio.no', 'openclipart.org')
                special_host = False
                for host in special_hosts:
                    if host in filename:
                        special_host = True
                        break
                if special_host and (
                    '>404' in text # <title>404 ...?
                    or 'Not Found' in text):
                    # HTML file with an error message: file not found
                    if msg or debug:
                        print '    %s not found' % filename
                        return None
                else:
                    if msg or debug:
                        print '    found!'
                    return 'url'
        except IOError, e:
            if msg or debug:
                print '    NOT found!'
            if debug:
                print '    urllib.urlopen error:', e
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

def unindent_lines(text, format=None, trailing_newline=True):
    """
    Unindent each line in the string text.
    Return new version of text.
    """
    # Find the indent
    lines = text.splitlines()
    indents = []
    for line in lines:
        if line == '':
            continue
        m = re.search('^( +)', line)
        indents.append(len(m.group(1)) if m else 0)
    indent = min(indents)
    text = '\n'.join([line[indent:] for line in lines])
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
        print '   the list of columns in the headline reads'
        print table[1]
    # Find the width of the various columns
    column_width = [0]*max_num_columns
    for i, row in enumerate(table):
        if row != ['horizontal rule']:
            for j, column in enumerate(row):
                column_width[j] = max(column_width[j], len(column))
    return column_width

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
        raise ValueError('BUG!')

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
    Replace references to equations. Unless "Equation(s)" already
    precedes the reference, the following transformations are done:

    (ref{my:label}) -> Equation (my:label)
    (ref{my:label1})-(ref{my:label2}) -> Equations (my:label1)-(my:label2)
    (ref{my:label1}) and (ref{my:label2}) -> Equations (my:label1) and (my:label2)
    (ref{my:label1}), (ref{my:label2}) and (ref{my:label3}) -> Equations (my:label1), (my:label2) and (ref{my:label2})

    """
    # "Store away" references that are prefixed by Equation/Eq.
    filestr = re.sub(r'(Equations?|Eqs?\.)([ ~]) *(\(ref\{)',
                     r'XXX___\g<1>\g<2>___XXX',  # coding of the prefix
                     filestr)
    filestr = re.sub(r'\(ref\{(.+?)\}\)-\(ref\{(.+?)\}\)',
                     r'Equations (\g<1>)-(\g<2>)', filestr)
    filestr = re.sub(r'\(ref\{(.+?)\}\)\s+and\s+\(ref\{(.+?)\}\)',
                     r'Equations (\g<1>) and (\g<2>)', filestr)
    filestr = re.sub(r'\(ref\{(.+?)\}\),\s*\(ref\{(.+?)\}\)(,?)\s+and\s+\(ref\{(.+?)\}\)',
                     r'Equations (\g<1>), (\g<2>)\g<3> and (\g<4>)', filestr)
    filestr = re.sub(r'\(ref\{(.+?)\}\)',
                     r'Equation (\g<1>)', filestr)

    # Restore Equation/Eq. prefix
    filestr = re.sub(r'XXX___(.+?)___XXX', r'\g<1>(ref{', filestr)
    return filestr

def default_movie(m):
    """
    Replace a movie entry by a proper URL with text.
    The idea is to link to an HTML file with the media element.
    """
    # Note: essentially same code as html_movie, but
    # the HTML code is embedded in a file.

    global _counter_for_html_movie_player
    filename = m.group('filename')
    caption = m.group('caption').strip()
    from html import html_movie
    text = html_movie(m)

    # Make an HTML file where the movie file can be played
    # (alternative to launching a player manually).
    _counter_for_html_movie_player += 1
    moviehtml = 'movie_player%d' % \
    _counter_for_html_movie_player + '.html'
    f = open(moviehtml, 'w')
    f.write("""
<html>
<head>
</head>
<body>
<title>Embedding media in HTML</title>
%s
</body>
</html>
""" % text)
    print '*** made link to new HTML file %s\n    with code to display the movie \n    %s' % (moviehtml, filename)
    text = '%s `%s`: load "`%s`": "%s" into a browser' % \
       (caption, filename, moviehtml, moviehtml)
    return text

def begin_end_consistency_checks(filestr, envirs):
    """Perform consistency checks: no of !bc must equal no of !ec, etc."""
    for envir in envirs:
        begin = '!b' + envir
        end = '!e' + envir

        nb = len(re.findall(r'^%s' % begin, filestr, flags=re.MULTILINE))
        ne = len(re.findall(r'^%s' % end, filestr, flags=re.MULTILINE))

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


def remove_code_and_tex(filestr, format):
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

    # ipynb (and future interactive executable documents) needs to
    # see if a code is to be executed or just displayed as text.
    # !bc *cod-t and !bc *pro-t is used to indicate pure text.
    if format not in ('ipynb', 'matlabnb'):
        filestr = re.sub(r'^!bc +([a-z0-9]+)-t', r'!bc \g<1>',
                         filestr, flags=re.MULTILINE)

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

    tex = re.compile(r'^!bt *\n(.*?)^!et *\n', re.DOTALL|re.MULTILINE)
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

    # Number all equations?
    if option('number_all_equations'):
        subst = [('\\begin{equation*}', '\\begin{equation}'),
                 ('\\end{equation*}', '\\end{equation}'),
                 ('\\[', '\\begin{equation} '),
                 ('\\]', '\\end{equation} '),
                 ('\\begin{align*}', '\\begin{align}'),
                 ('\\end{align*}', '\\end{align}'),
                 ]
    if option('denumber_all_equations'):
        # Remove equation numbers and also labels in those equations
        subst = [('\\begin{equation}', '\\begin{equation*}'),
                 ('\\end{equation}', '\\end{equation*}'),
                 ('\\begin{align}', '\\begin{align*}'),
                 ('\\end{align}', '\\end{align*}'),
                 ]
        removed_labels = []
        for i in range(len(tex_blocks)):
            found = False
            for construction, dummy in subst:
                if construction in tex_blocks[i]:
                    found = True
                    break
            if found:
                for from_, to_ in subst:
                    tex_blocks[i] = tex_blocks[i].replace(from_, to_)
                removed_labels += re.findall(r'label\{(.+?)\}', tex_blocks[i])
                tex_blocks[i] = re.sub(r'label\{.+?\}\n', '', tex_blocks[i])
                tex_blocks[i] = re.sub(r'label\{.+?\}', '', tex_blocks[i])
        all_refs = re.findall(r'ref\{(.+?)\}', filestr)
        problematic_refs = []
        for ref in all_refs:
            if ref in removed_labels:
                problematic_refs.append(ref)
        if problematic_refs:
            print '*** error: removed all equation labels from the DocOnce source,'
            print '    but there are still references (ref{...}) to equation labels:'
            print '\n   ', ', '.join(problematic_refs)
            print '\n    remove all these references!'
            _abort()

    # Give error if blocks contain !bt
    for i in range(len(tex_blocks)):
        if '!bt' in tex_blocks[i] or '!et' in tex_blocks[i]:
            print '*** error: double !bt or !et in latex block:'
            print tex_blocks[i]
            _abort()

    # Check that math blocks do not contain edit markup or comments
    for block in tex_blocks:
        m = re.search(INLINE_TAGS['inlinecomment'], block, flags=re.DOTALL)
        if m:
            print '*** error: tex block with mathematics cannot contain'
            print '    inline comment or edit markup!'
            if m.group('name') in ('del', 'add') or '->' in m.group('comment'):
                # edit markup
                print '    Place info about editing after the block.'
            print block
            _abort()

    # Remove |\pause| in code blocks if not latex
    if format not in ('latex', 'pdflatex'):
        for i in range(len(code_blocks)):
            if r'|\pause|' in code_blocks[i]:
                code_blocks[i] = re.sub(r'^\|\\pause\|\n', '', code_blocks[i], flags=re.MULTILINE)

    return filestr, code_blocks, code_block_types, tex_blocks


def insert_code_and_tex(filestr, code_blocks, tex_blocks, format,
                        complete_doc=True):
    # Consistency check (only for complete documents):
    # find no of distinct code and math blocks
    # (can be duplicates when solutions are copied at the end)
    pattern = r'^\d+ ' + _CODE_BLOCK
    code_lines = re.findall(pattern, filestr, flags=re.MULTILINE)
    n = len(set(code_lines))
    if complete_doc and len(code_blocks) != n:
        print '*** error: found %d code block markers for %d initial code blocks' % (n, len(code_blocks))
        print """    Possible causes:
           - mismatch of !bt and !et within one file, such that a !bt
             swallows code
           - mismatch of !bt and !et across files in multi-file documents
           - !bc and !ec inside code blocks - replace by |bc and |ec
    (run doconce on each individual file to locate the problem, then on
     smaller and smaller parts of each file)"""
        numbers = range(len(code_blocks))  # expected numbers in code blocks
        for e in code_lines:
            # remove number
            number = int(e.split()[0])
            if number not in numbers:
                print '   Problem: found %s, but the number %d was unexpected' % (e, number)
            else:
                numbers.remove(number)
        if numbers:
            print '    Problem: did not find XX <<<!!CODE_BLOCK for XX in', numbers

        _abort()
    pattern = r'^\d+ ' + _MATH_BLOCK
    n = len(set(re.findall(pattern, filestr, flags=re.MULTILINE)))
    if complete_doc and len(tex_blocks) != n:
        print '*** error: found %d tex block markers for %d initial tex blocks\nAbort!' % (n, len(tex_blocks))
        print """    Possible causes:
           - mismatch of !bc and !ec within one file, such that a !bc
             swallows tex blocks
           - mismatch of !bc and !ec across files in multi-file documents
           - !bt and !et inside code blocks - replace by |bt and |et
    (run doconce on each file to locate the problem, then on
     smaller and smaller parts of each file)"""
        _abort()

    from misc import option
    max_linelength = option('max_bc_linelength=', None)
    if max_linelength is not None:
        max_linelength = int(max_linelength)

        for i in range(len(code_blocks)):
            lines = code_blocks[i].splitlines()
            truncated = False
            for j in range(len(lines)):
                if len(lines[j]) > max_linelength:
                    lines[j] = lines[j][:max_linelength] + '...'
                    truncated = True
            if truncated:
                code_blocks[i] = '\n'.join(lines) + '\n'


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

    # All formats except sphinx and ipynb must remove !bc *hid blocks
    # (maybe html will get the possibility to run hidden blocks)
    if format not in ('sphinx', 'ipynb'):
        filestr = remove_hidden_code_blocks(filestr, format)

    return filestr

def remove_hidden_code_blocks(filestr, format):
    """
    Remove text encolsed in !bc *hid and !ec tags.
    Some formats need this for executable code blocks to work,
    but they should be invisible in the text.
    """
    pattern = r'^!bc +[a-z]*hid\n.+?!ec'
    filestr = re.sub(pattern, '', filestr, flags=re.MULTILINE|re.DOTALL)
    return filestr

def doconce_exercise_output(
    exer,
    solution_header = '__Solution.__',
    answer_header = '__Answer.__',
    hint_header = '__Hint.__',
    include_numbering=True,
    include_type=True,
    ):
    """
    Write exercise in DocOnce format. This output can be
    reused in most formats.
    """
    # Note: answers, solutions, and hints must be written out and not
    # removed here, because if they contain math or code blocks,
    # there will be fewer blocks in the end that what was extracted
    # at the beginning of the translation process.

    latex_style = option('latex_style=', 'std')

    # Store solutions in a separate string
    has_solutions = False
    if exer['solution']:
        has_solutions = True
    if exer['answer']:
        has_solutions = True
    for subex in exer['subex']:
        if subex['solution']:
            has_solutions = True
        if subex['answer']:
            has_solutions = True

    sol = ''  # Solutions
    # s holds the formatted exercise in doconce format
    s = '\n\n# ' + envir_delimiter_lines['exercise'][0] + '\n\n'
    s += exer['heading']  # result string
    if has_solutions:
        sol += '\n\n# ' + envir_delimiter_lines['exercise'][0] + ' solution\n\n'
        if latex_style == 'Springer_sv':
            sol += r"""
\begin{sol}{%s}
\textbf{%s}\\

""" % (exer['label'], exer['title'])
        else:
            sol += exer['heading']

    comments = ''  # collect comments at the end of the exercises

    if include_numbering and not include_type:
        include_type = True
    if not exer['type_visible']:
        include_type = False
    if include_type:
        s += ' ' + exer['type']
        if sol:
            sol += ' Solution to ' + exer['type']
        if include_numbering:
            exer_numbering = option('exercise_numbering=', 'absolute')
            if exer_numbering == 'chapter' and exer['chapter_type'] is not None:
                s += ' %s.%s' % (exer['chapter_no'], exer['chapter_exercise'])
            else:
                s += ' ' + str(exer['no'])

            if sol:
                sol += ' ' + str(exer['no'])
        s += ':'
        if sol:
            sol += ':'
    s += ' ' + exer['title'] + ' ' + exer['heading'] + '\n'
    if sol:
        sol += ' ' + exer['title'] + ' ' + exer['heading'] + '\n'

    if exer['label']:
        s += 'label{%s}' % exer['label'] + '\n'
        if sol:
            sol += '# Solution to Exercise ref{%s}' % exer['label'] + '\n'

    if exer['keywords']:
        s += '# keywords = %s' % '; '.join(exer['keywords']) + '\n'

    if exer['text']:
        # Let comments at the end of the text come very last, if there
        # are no subexercises. Just outputting comments at the end
        # makes Filename: ... on a separate line, which does not look good.
        # We extract the final comments and print them after anything else.
        # Final comments often contain fruitful comments about the solution.
        if (not exer['subex']) and '\n#' in exer['text']:
            lines = exer['text'].splitlines()
            newlines = []
            comments = []
            for i, line in enumerate(reversed(lines)):
                if (line.startswith('#') or line.isspace() or line == '') \
                and not line.startswith('# ---'):
                    # (do not touch # --- begin/end type of comments!)
                    comments.append(line)
                else:
                    break
            comments = '\n'.join(reversed(comments))
            if i == 0:
                exer['text'] = '\n'.join(lines)
            elif i > 0:
                exer['text'] = '\n'.join(lines[:-i])

        s += '\n' + exer['text'] + '\n'

    if exer['hints']:
        for i, hint in enumerate(exer['hints']):
            if len(exer['hints']) == 1 and i == 0:
                hint_header_ = hint_header
            else:
                hint_header_ = hint_header.replace('Hint.', 'Hint %d.' % (i+1))
            if exer['type'] != 'Example':
                s += '\n# ' + envir_delimiter_lines['hint'][0] + '\n'
            s += '\n' + hint_header_ + '\n' + hint + '\n'
            if exer['type'] != 'Example':
                s += '\n# ' + envir_delimiter_lines['hint'][1] + '\n'

    if exer['subex']:
        s += '\n'
        if sol:
            sol += '\n'
        import string
        for i, subex in enumerate(exer['subex']):
            letter = string.ascii_lowercase[i]
            s += '\n__%s)__\n' % letter

            if subex['solution'] or (subex['answer'] and not option('without_answers')):
                sol += '\n__%s)__\n' % letter

            if subex['text']:
                s += subex['text'] + '\n'

                for i, hint in enumerate(subex['hints']):
                    if len(subex['hints']) == 1 and i == 0:
                        hint_header_ = hint_header
                    else:
                        hint_header_ = hint_header.replace(
                            'Hint.', 'Hint %d.' % (i+1))
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['hint'][0] + '\n'
                    s += '\n' + hint_header_ + '\n' + hint + '\n'
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
                        sol += '\n# ' + envir_delimiter_lines['ans'][0] + '\n'
                    s += answer_header + '\n' + subex['answer'] + '\n'
                    sol += answer_header + '\n' + subex['answer'] + '\n'
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['ans'][1] + '\n'
                        sol += '\n# ' + envir_delimiter_lines['ans'][1] + '\n'

                if subex['solution']:
                    s += '\n'
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['sol'][0] + '\n'
                    s += solution_header + '\n'
                    # Make sure we have a sentence after the heading
                    if solution_header.endswith('===') and \
                       re.search(r'^\d+ %s' % _CODE_BLOCK,
                                 subex['solution'].lstrip()):
                        print '\nwarning: open the solution in exercise "%s" with a line of\ntext before the code! (Now "Code:" is inserted)' % exer['title'] + '\n'
                        s += 'Code:\n'
                        sol += '\nCode:\n'
                    s += subex['solution'] + '\n'
                    sol += '\n' + subex['solution'] + '\n'
                    if exer['type'] != 'Example':
                        s += '\n# ' + envir_delimiter_lines['sol'][1] + '\n'

            if 'aftertext' in subex:
                s += subex['aftertext']

    if exer['answer']:
        s += '\n'
        # Leave out begin-end answer comments if example since we want to
        # avoid marking such sections for deletion (--without_answers)
        if exer['type'] != 'Example':
            s += '\n# ' + envir_delimiter_lines['ans'][0] + '\n'
            sol += '\n# ' + envir_delimiter_lines['ans'][0] + '\n'
        s += answer_header + '\n' + exer['answer'] + '\n'
        sol += answer_header + '\n' + exer['answer'] + '\n'

        if exer['type'] != 'Example':
            s += '\n# ' + envir_delimiter_lines['ans'][1] + '\n'
            sol += '\n# ' + envir_delimiter_lines['ans'][1] + '\n'

    if exer['solution']:
        s += '\n'
        # Leave out begin-end solution comments if example since we want to
        # avoid marking such sections for deletion (--without_solutions)
        if exer['type'] != 'Example':
            s += '\n# ' + envir_delimiter_lines['sol'][0] + '\n'
        s += solution_header + '\n'
        # Make sure we have a sentence after the heading if real heading
        if solution_header.endswith('===') and \
           re.search(r'^\d+ %s' % _CODE_BLOCK, exer['solution'].lstrip()):
            print '\nwarning: open the solution in exercise "%s" with a line of\ntext before the code! (Now "Code:" is inserted)' % exer['title'] + '\n'
            s += 'Code:\n'
            sol += '\nCode:\n'
        s += exer['solution'] + '\n'
        sol += '\n'+ exer['solution'] + '\n'
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

    if comments:
        s += '\n' + comments

    s += '\n# ' + envir_delimiter_lines['exercise'][1] + '\n\n'
    if sol:
        if latex_style == 'Springer_sv':
            sol += r'\end{sol}' + '\n'
        else:
            sol += '\n# ' + envir_delimiter_lines['exercise'][1] + ' solution\n\n'

    return s, sol

def plain_exercise(exer):
    return doconce_exercise_output(exer)


def bibliography(pubdata, citations, format='doconce'):
    """
    Return DocOnce formatted list of references, based on the keys
    in the ordered dictionary ``citations`` (``pubdata`` is a list
    of dicts loaded from a Publish database file).
    """
    import publish_doconce
    if format == 'doconce':
        formatter = publish_doconce.doconce_format
    elif format in ('rst', 'sphinx'):
        formatter = publish_doconce.rst_format
    elif format == 'xml':
        formatter = publish_doconce.xml_format

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

def get_legal_pygments_lexers():
    from pygments.lexers import get_all_lexers
    lexers = []
    for classname, names, dummy, dymmy in list(get_all_lexers()):
        for name in names:
            lexers.append(name)
    return lexers

def has_custom_pygments_lexer(name):
    from pygments.lexers import get_lexer_by_name
    if name == 'ipy':
        try:
            get_lexer_by_name('ipy')
        except Exception as e:
            print '*** warning: !bc ipy used for IPython sessions, but'
            print '    ipython is not supported for syntax highlighting!'
            print '    install:'
            print '    git clone https://hplbit@bitbucket.org/hplbit/pygments-ipython-console.git; cd pygments-ipython-console; sudo python setup.py install'
            print e
            return False
    if name == 'doconce':
        try:
            get_lexer_by_name(name)
        except Exception as e:
            print '*** warning: !bc do used for DocOnce code, but'
            print '    not supported for syntax highlighting!'
            print '    install:'
            print '    sudo pip install -e git+https://github.com/hplgit/pygments-doconce#egg=pygments-doconce'
            print '\n    or manually:'
            print '    git clone https://github.com/hplgit/pygments-doconce.git; cd pygments-doconce; sudo python setup.py install'
            print e
            return False
    return True

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
QUIZ = {}


# regular expressions for inline tags:
#inline_tag_begin = r"""(?P<begin>(^|[(\s~>]|^__))"""
inline_tag_begin = r"""(?P<begin>(^|[(\s~>-]|^__))"""
# ' is included as apostrophe in end tag
inline_tag_end = r"""(?P<end>($|[.,?!;:)<}'\s~\[<-]))"""
# alternatives using positive lookbehind and lookahead (not tested!):
inline_tag_before = r"""(?<=(^|[(\s]))"""
inline_tag_after = r"""(?=$|[.,?!;:)\s])"""
# the begin-end works, so don't touch (must be tested in a safe branch....)

_linked_files = '''\s*"(?P<url>([^"]+?\.html?|[^"]+?\.html?\#[^"]+?|[^"]+?\.txt|[^"]+?\.tex|[^"]+?\.pdf|[^"]+?\.f|[^"]+?\.c|[^"]+?\.cpp|[^"]+?\.cxx|[^"]+?\.py|[^"]+?\.ipynb|[^"]+?\.java|[^"]+?\.pl|[^"]+?\.sh|[^"]+?\.csh|[^"]+?\.zsh|[^"]+?\.ksh|[^"]+?\.tar\.gz|[^"]+?\.tar|[^"]+?\.zip|[^"]+?\.f77|[^"]+?\.f90|[^"]+?\.f95|[^"]+?\.png|[^"]+?\.jpe?g|[^"]+?\.gif|[^"]+?\.pdf|[^"]+?\.flv|[^"]+?\.webm|[^"]+?\.ogg|[^"]+?\.mp4|[^"]+?\.mpe?g|[^"]+?\.e?ps|_static-?[^/]*/[^"]+?))"'''
#_linked_files = '''\s*"(?P<url>([^"]+?))"'''  # any file is accepted

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
    r'%s`(?P<subst>[^ `][^`]*)`%s' % \
    (inline_tag_begin, inline_tag_end),
    #(inline_tag_begin, r"(?P<end>($|[.,?!;:)}'\s|-]))"),

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

    'inlinecomment':  # needs re.DOTALL
    r'''\[(?P<name>[A-Za-z0-9 '+-]+?):(?P<space>\s+)(?P<comment>.*?)\]''',
    # looks more robust for names with non-English characters,
    # but caused problems (should not match \[ a:\quad ...\] and not footnotes)
    #r'''(?<=[^\\])\[(?P<name>[^:\^]+?):(?P<space>\s+)(?P<comment>.*?)\]''',

    # __Abstract.__ Any text up to a headline === or toc-like keywords
    # (TOC is already processed)
    # Abstract can also appear on the front page of books, then insert
    # it before DATE (not recommended for papers)
    # 'abstract' is in doconce.py processed before chapter, section, etc
    'abstract':  # needs re.DOTALL | re.MULTILINE
    r"""^\s*__(?P<type>Abstract|Summary|Preface).__\s*(?P<text>.+?)(?P<rest>TOC:|\\tableofcontents|Table of [Cc]ontents|DATE:|% --- begin date|\\date\{|<!-- date|__[A-Z].+[.?:]__|^={3,9})""",

    'keywords':
    r'^__Keywords.__\s+(?P<subst>.+)\s*$',

    # ======= Seven Equality Signs for Headline =======
    'section':
    r'^={7}\s*(?P<subst>[^ =-].+?)\s*={7} *$',

    'chapter':
    r'^={9}\s*(?P<subst>[^ =-].+?)\s*={9} *$',

    'subsection':
    r'^={5}\s*(?P<subst>[^ =-].+?)\s*={5} *$',

    'subsubsection':
    # final \s is needed for latex to make \paragraph attached to text
    # with no blank line
    r'^={3}\s*(?P<subst>[^ =-].+?)\s*={3}\s*$',

    # __Two underscores for Inline Paragraph Title.__
    'paragraph':
    r'(?P<begin>^)__(?P<subst>.+?)__(?P<space>(\n| +))',

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
    'linebreak': '^(?P<text>.*)<linebreak> *$',
    #'footnote':  # definition is in doconce.py since no regular re.sub in loop is to be performed
    # The tilde is used in URLs and computer code
    # Must be substituted before inline math, color, etc., if the next
    # regex is to work (but then &nbsp;$math$ breaks later...)
    #'non-breaking-space': r'(?<=[$A-Za-z0-9])~(?=[$A-Za-z0-9])',
    # This one allows HTML MathJax formulas and HTML tags to surround the ~
    # (i.e., after substitutions of $...$, color, etc.)
    'non-breaking-space': r'(?<=[})>$A-Za-z0-9_`.])~(?=[{(\\<$A-Za-z0-9`:])',
    'horizontal-rule': r'^----+$',
    # ampersand1: Guns & Roses -> Guns {\&} Roses in latex
    'ampersand1': r'(?P<pre>[A-Za-z0-9]) +& +(?P<post>[A-Za-z0-9])',  # \1 & \2
    # Texas A & M (doconce) -> Texas A{\&}M in latex (no spaces around &)
    'ampersand2': r' (?P<pre>[A-Z]) +& +(?P<post>[A-Z](?=\n|[ .,;-?:`]))',
    'emoji': r'(\s):([a-z_]+):(\s)',
    }

INLINE_TAGS_SUBST = {}

LIST_SYMBOL = {'*': 'itemize', 'o': 'enumerate', '-': 'description'}
