#!/usr/bin/env python
import re, os, sys, shutil, commands, pprint, time, glob, codecs
try:
    from collections import OrderedDict   # v2.7 and v3.1
except ImportError:
    # use standard arbitrary-ordered dict instead (original order of
    # citations is then lost)
    OrderedDict = dict


def debugpr(heading='', text=''):
    """Add `heading` and `text` to the log/debug file."""
    if option('debug'):
        global _log
        if encoding:
            if isinstance(text, str):
                text = text.decode(encoding)
            _log = codecs.open('_doconce_debugging.log','a', encoding)
        else:
            _log = open('_doconce_debugging.log','a')
        out_class = str(type(text)).split("'")[1]
        pre = '\n' + '*'*60 + '\n%s>>> ' % out_class if text else ''
        _log.write(pre + heading + '\n\n')
        _log.write(text + '\n')
        _log.close()


from common import *
from common import _abort  # needs explicit import because of leading _
from misc import option, which
import html, latex, pdflatex, rst, sphinx, st, epytext, plaintext, gwiki, mwiki, cwiki, pandoc, ipynb

def supported_format_names():
    return 'html', 'latex', 'pdflatex', 'rst', 'sphinx', 'st', 'epytext', 'plain', 'gwiki', 'mwiki', 'cwiki', 'pandoc', 'ipynb'

def doconce_envirs():                     # begin-end environments
    return ['c', 't',                     # verbatim and tex blocks
            'ans', 'sol', 'subex',        # exercises
            'pop', 'slidecell', 'notes',  # slides
            'hint', 'remarks',            # exercises
            'quote', 'box',
            'notice', 'summary', 'warning', 'question', 'block', # admon
            ]

admons = 'notice', 'summary', 'warning', 'question', 'block'

main_content_char = '-'
main_content_begin = main_content_char*19 + ' main content ' + \
                     main_content_char*22
main_content_end = main_content_char*19 + ' end of main content ' + \
                   main_content_char*15

#----------------------------------------------------------------------------
# Translators: (do not include, use import as shown above)
# include "common.py"
# include "html.py"
# include "latex.py"
#----------------------------------------------------------------------------

def fix(filestr, format, verbose=0):
    """Fix issues with the text (correct wrong syntax)."""
    # Fix a special case:
    # `!bc`, `!bt`, `!ec`, and `!et` at the beginning
    # of a line gives wrong consistency checks for plaintext format,
    # so we avoid having these at the beginning of a line.
    if format == 'plain':
        for directive in 'bc', 'ec', 'bt', 'et':
            # could test for bsol, bhint, etc. as well...
            cpattern = re.compile(r'^`!%s' % directive, re.MULTILINE)
            filestr = cpattern.sub('  `!%s' % directive,
                                   filestr)  # space avoids beg.of line

    num_fixes = 0

    # Fix figure and movie captions that span several lines (the
    # replacement via re.sub works line by line so the caption *must*
    # be on one line, but this might be forgotten by many writers...)
    pattern = r'^\s*(?P<type>FIGURE|MOVIE):\s*\[(?P<filename>[^,\]]+),?(?P<options>[^\]]*)\]\s*?(?P<caption>.*?)^\s*$'
    figs = re.findall(pattern, filestr, flags=re.MULTILINE|re.DOTALL)

    for fig in figs:
        caption = fig[3]
        if '\n' in caption.strip():   # multiline caption?
            # Do not allow figures and movies without a nice blank line after
            if 'FIGURE:' in caption or 'MOVIE:' in caption:
                print '*** error: missing blank line between multiple figures/movies\n    %s: [%s, ...' % (fig[1], fig[2])
                _abort()
            # Allow environments to the figure
            if not '!e' in caption:
                #and not 'FIGURE:' in caption \
                #and not 'MOVIE:' in caption:
                caption1 = caption.replace('\n', ' ') + '\n'
                filestr = filestr.replace(caption, caption1)
                num_fixes += 1
                if verbose > 0:
                    print '\n*** warning: found multi-line caption for %s\n\n%s\n    fix: collected this text to one single line (right?)' % (fig[1], caption)

    # Space before commands that should begin in 1st column at a line?
    commands = 'FIGURE MOVIE TITLE AUTHOR DATE TOC BIBFILE'.split()
    commands += ['!b' + envir for envir in doconce_envirs()]
    commands += ['!e' + envir for envir in doconce_envirs()]
    for command in commands:
        pattern = r'^ +' + command
        m = re.search(pattern, filestr, flags=re.MULTILINE)
        if m:
            lines = '\n'.join(re.findall(r'^ +%s.*$' % command, filestr, flags=re.MULTILINE)) + '\n'
            filestr, n = re.subn(pattern, command, filestr, flags=re.MULTILINE)
            num_fixes += n

            if verbose > 0:
                print '\nFIX: %s not at the beginning of the line - %d fixes' % (command, n)
                print lines

    if verbose and num_fixes:
        print '\n*** warning: the total of %d fixes above should be manually edited in the file!!\n    (also note: some fixes may not be what you want)\n' % num_fixes
    return filestr



def syntax_check(filestr, format):
    """Check for common errors in the doconce syntax."""

    # URLs with just one /
    m = re.findall(r'https?:/[A-Za-z].+', filestr)
    if m:
        print '*** error: missing double // in URLs'
        print '   ', '\n'.join(m)
        _abort()

    # Check that are environments !bc, !ec, !bans, !eans, etc.
    # appear at the beginning of the line
    for envir in doconce_envirs():
        pattern = re.compile(r'^ +![eb]%s' % envir, re.MULTILINE)
        m = pattern.search(filestr)
        if m:
            print '\n*** error: !b%s and/or !e%s not at the beginning of the line' % (envir, envir)
            print repr(filestr[m.start():m.start()+120])
            _abort()

    # Verbatim words must be the whole link, otherwise issue
    # warnings for the formats where this may look strange
    if format not in ('pandoc',):
        links  = re.findall(INLINE_TAGS['linkURL2'], filestr)
        links += re.findall(INLINE_TAGS['linkURL3'], filestr)
        for link, url1, url2 in links:
            if '`' in link[1:-1]:
                print '\n*** error: verbatim code in part of link is not allowed in format', format
                print '   ', '"%s": "%s"' % (link, url1)
                print '    use either link as verbatim code only, %s,' % '"`%s`"' % link.replace('`', '')
                print '    or no verbatim: "%s"' % link.replace('`', '')
                print '    or use only the verbatim part as link'
                _abort()

    pattern = re.compile(r'[^\n:.?!,]^(!b[ct]|@@@CODE)', re.MULTILINE)
    m = pattern.search(filestr)
    if m:
        print '\n*** error: line before !bc/!bt/@@@CODE block\nends with wrong character (must be among [\\n:.?!, ]):'
        print repr(filestr[m.start():m.start()+80])
        _abort()

    # Code blocks cannot come directly after tables or headings.
    # Remove idx{} and label{} before checking
    # since these will be moved for rst.
    # Also remove all comments since these are also "invisible".
    filestr2 = filestr
    for tag in 'label', 'idx':
        filestr2 = re.sub('%s\{.+?\}' % tag, '', filestr2)
    pattern = re.compile(r'^#.*$', re.MULTILINE)
    filestr2 = pattern.sub('', filestr2)
    for linetp in '===', r'-\|', '__':  # section, table, paragraph
        pattern = re.compile(r'%s\s+^(!b[ct]|@@@CODE)' % linetp,
                             re.MULTILINE)
        m = pattern.search(filestr2)
        if m and format in ('rst', 'plain', 'epytext', 'st'):
            print '\n*** error: must have a plain sentence before\na code block like !bc/!bt/@@@CODE, not a section/paragraph heading,\ntable, or comment:'
            print filestr2[m.start()-40:m.start()+80]
            _abort()

    # Double quotes and not double single quotes in *plain text*:
    inside_code = False
    inside_math = False
    for line in filestr.splitlines():
        if line.startswith('!bc'):
            inside_code = True
        if line.startswith('!bt'):
            inside_math = True
        if line.startswith('!ec'):
            inside_code = False
        if line.startswith('!et'):
            inside_math = False

    commands = [
        r'\[',
        r'\]',
        'begin{equation}',
        'end{equation}',
        'begin{equation*}',
        'end{equation*}',
        'begin{eqnarray}',
        'end{eqnarray}',
        'begin{eqnarray*}',
        'end{eqnarray*}',
        'begin{align}',
        'end{align}',
        'begin{align*}',
        'end{align*}',
        'begin{multline}',
        'end{multline}',
        'begin{multline*}',
        'end{multline*}',
        'begin{gather}',
        'end{gather}',
        'begin{gather*}',
        'end{gather*}',
        # some common abbreviations (newcommands):
        'beqan',
        'eeqan',
        'beqa',
        'eeqa',
        'balnn',
        'ealnn',
        'baln',
        'ealn',
        'balns',
        'ealns',
        'beq',
        'eeq',  # the simplest, contained in others, must come last...
        ]
    lines = filestr.splitlines()
    inside_bt = False
    inside_bt_i = 0
    inside_bc = False
    for i in range(len(lines)):
        if lines[i].startswith('!bt'):
            inside_bt = True
            inside_bt_i = i
        if lines[i].startswith('!et'):
            inside_bt = False
            inside_bt_i = 0
        if lines[i].startswith('!bc'):
            inside_bc = True
        if lines[i].startswith('!ec'):
            inside_bc = False
        for command in commands:
            if '\\' + command in lines[i] and not inside_bt:
                if '`' not in lines[i] and not inside_bc:  # not verbatim
                    print '\n*** error in math equation: command\n%s\nis not inside !bt - !et environment' % command
                    print '\n'.join(lines[i-3:i+3])
                    _abort()

    """
    # This is better done in sphinx.py, or should we provide warnings
    # to enforce writers to stay away from a range of latex
    # constructions even if sphinx.py can substitute them away?
    """
    not_for_sphinx = [
        '{eqnarray}',
        '{eqnarray*}',
        '{multline}',
        '{multline*}',
        '{gather}',
        '{gather*}',
        'beqan',
        'beqa',
        ]
    warning_given = False
    if format == 'sphinx':
        for command in not_for_sphinx:
            if command in filestr:
                if not warning_given:
                    print '\n*** warning:'
                print 'Not recommended for sphinx output: math environment %s' % command
                if not warning_given:
                    print '(use equation, equation*, \[ \], or align/align*)'
                    warning_given = True
    """
    """
    # Remove tex and code blocks
    filestr, code_blocks, code_block_types, tex_blocks = \
             remove_code_and_tex(filestr)

    begin_end_consistency_checks(filestr, doconce_envirs())

    # Check that headings have consistent use of = signs
    for line in filestr.splitlines():
        if line.strip().startswith('==='):
            w = line.split()
            if w[0] != w[-1]:
                print '\n*** error: inconsistent no of = in heading:\n', line
                print '      lengths: %d and %d, must be equal and odd' % \
                      (len(w[0]), len(w[-1]))
                _abort()

    # Check that references have parenthesis (equations) or
    # the right preceding keyword (Section, Chapter, Exercise, etc.)
    pattern = re.compile(r'\s+([A-Za-z]+?)\s+(ref\{.+?\})', re.MULTILINE)
    refs = pattern.findall(filestr)
    prefixes = ['chapter', 'ch.',
                'section', 'sec.',
                'appendix', 'app.', 'appendice',
                'figure', 'fig.',
                'movie',
                'exercise',
                'problem',
                'project',
                'example', 'ex.',
                'and', 'or']
    for prefix, ref in refs:
        orig_prefix = prefix
        if prefix[-1] == 's':
            prefix = prefix[:-1]  # skip plural
        if not prefix.lower() in prefixes:
            print '*** warning: found reference "%s %s" with unexpected word "%s" in front' % (orig_prefix, ref, orig_prefix),
            print '    (reference to equation, but missing parenthesis in (%s)?)' % (ref)

    # Code/tex blocks cannot have a comment, table, figure, etc.
    # right before them
    constructions = {'comment': r'^\s*#.*?$',
                     'table': r'-\|\s*$',
                     'figure': r'^\s*FIGURE:.+$',
                     'movie': r'^\s*MOVIE:.+$',
                     }
    for construction in constructions:
        pattern = re.compile(r'%s\s*^(!b[ct]\s*$|@@@CODE| +\* +| +o +)' % \
                             constructions[construction],
                             re.MULTILINE)
        m = pattern.search(filestr)
        if m and format in ('rst', 'sphinx'):
            print '\n*** error: line before list, !bc, !bt or @@@CODE block is a %s line\nwhich will "swallow" the block in reST format.\n    Insert some extra line (text) to separate the two elements.' % construction
            print filestr[m.start():m.start()+80]
            _abort()

    matches = re.findall(r'\\cite\{.+?\}', filestr)
    if matches:
        print '\n*** warning: found \\cite{...} with backslash'
        print '    (cite{...} has no backslash in Doconce syntax)'
        print '\n'.join(matches)

    matches = re.findall(r'\\idx\{.+?\}', filestr)
    if matches:
        print '\n*** warning: found \\idx{...} (idx{...} has no backslash)'
        print '\n'.join(matches)
        _abort()

    matches = re.findall(r'\\index\{.+?\}', filestr)
    if matches:
        print '\n*** warning: found \\index{...} (index is written idx{...})'
        print '\n'.join(matches)

    # There should only be ref and label *without* the latex-ish backslash
    matches = re.findall(r'\\label\{.+?\}', filestr)
    if matches:
        print '\n*** warning: found \\label{...} with backslash'
        print '    (label{...} has no backslash in Doconce syntax)'
        print '\n'.join(matches)

    matches = re.findall(r'\\ref\{.+?\}', filestr)
    if matches:
        print '\n*** warning: found \\ref{...} with backslash'
        print '    (ref{...} has no backslash in Doconce syntax)'
        print '\n'.join(matches)

    # consistency check between label{} and ref{}:
    # (does not work well without labels from the !bt environments)
    """
    labels = re.findall(r'label\{(.+?)\}', filestr)
    refs = re.findall(r'ref\{(.+?)\}', filestr)
    for ref in refs:
        if not ref in labels:
            print '...ref{%s} has no corresponding label{%s} (within this file)' % \
                (ref, ref)
    """


    # Cannot check on these since doconce documents about ptex2tex and
    # latex writings may contain these expressions in inline verbatim or
    # block verbatim
    """
    patterns = r'\\[be]cod', r'\\begin{[Vv]erbatim', r'\\end{[Vv]erbatim', r'\\[be]sys', r'\\[be]py',
    for pattern in patterns:
        matches = re.findall(pattern, filestr)
        if matches:
            print '\nSyntax error: Wrong syntax (latex!)'
            print '\n'.join(matches)
            sys.exit(1)
    """

    pattern = r'__[A-Z][A-Za-z0-9,:` ]+__\.'
    matches = re.findall(pattern, filestr)
    if matches:
        print '\n*** error: wrong paragraphs'
        print '\n'.join(matches)
        _abort()

    pattern = re.compile(r'^__.+?[^.:?]__', re.MULTILINE)
    matches = pattern.findall(filestr)
    if matches:
        print '*** warning: missing ., : or ? after paragraph heading:'
        print '\n'.join(matches)

    pattern = r'idx\{[^}]*?\\_[^}]*?\}'
    matches = re.findall(pattern, filestr)
    if matches:
        print '*** warning: Backslash before underscore(s) in idx (remove backslash)'
        print matches

    # Figure without comma between filename and options? Or initial spaces?
    pattern = r'^FIGURE:\s*\[[^,\]]+ +[^\]]*\]'
    cpattern = re.compile(pattern, re.MULTILINE)
    matches = cpattern.findall(filestr)
    if matches:
        print '*** error: missing comma after filename, before options in FIGURE'
        print '\n'.join(matches)
        _abort()

    # Movie without comma between filename and options? Or initial spaces?
    pattern = r'^MOVIE:\s*\[[^,\]]+ +[^\]]*\]'
    cpattern = re.compile(pattern, re.MULTILINE)
    matches = cpattern.findall(filestr)
    if matches:
        print '\n*** error: missing comma after filename, before options in MOVIE'
        print '\n'.join(matches)
        _abort()

    # Keywords at the beginning of the lines:
    keywords = 'AUTHOR', 'TITLE', 'DATE', 'FIGURE', 'BIBFILE', 'MOVIE', 'TOC',
    for kw in keywords:
        pattern = '^ +' + kw
        cpattern = re.compile(pattern, re.MULTILINE)
        matches = cpattern.findall(filestr)
        if matches:
            print '\n*** error: %s specification must be at the beginning of a line' % kw
            print '\n'.join(matches)
            _abort()

    # Keywords without colon:
    for kw in keywords:
        pattern = '(^' + kw + ' +)(.*)'
        cpattern = re.compile(pattern, re.MULTILINE)
        matches = [keyword + rest for keyword, rest in cpattern.findall(filestr)]
        if matches:
            print '\n*** error: missing colon after %s specification' % kw
            print '\n'.join(matches)
            _abort()

    if format in ('latex', 'pdflatex'):
        # if TITLE is given, AUTHOR and DATE must also be present
        #md = re.search(r'^DATE:', filestr, flags=re.MULTILINE)
        #mt = re.search(r'^TITLE:', filestr, flags=re.MULTILINE)
        #ma = re.search(r'^AUTHOR:', filestr, flags=re.MULTILINE)
        cdate   = re.compile(r'^DATE:', re.MULTILINE)  # v2.6 way of doing it
        ctitle  = re.compile(r'^TITLE:', re.MULTILINE)
        cauthor = re.compile(r'^AUTHOR:', re.MULTILINE)
        md = cdate.search(filestr)
        mt = ctitle.search(filestr)
        ma = cauthor.search(filestr)
        if md or mt or ma:
            if not (md and mt and ma):
                print """
*** error: latex format requires TITLE, AUTHOR and DATE to be
    specified if one of them is present."""
                if not md:
                    print '    DATE is missing'
                if not mt:
                    print '    TITLE is missing'
                if not ma:
                    print '    AUTHOR is missing '
                _abort()

    if format == "sphinx":
        # Check that local URLs are in _static directory
        links = []
        for link_tp in 'linkURL2', 'linkURL3', 'linkURL2v', 'linkURL3v', \
                'plainURL':
            links.extend(re.findall(INLINE_TAGS[link_tp], filestr))
        import sets
        links = list(sets.Set([link[1] for link in links]))
        links2local = []
        for link in links:
            if not (link.startswith('http') or link.startswith('file:/') or \
                    link.startswith('_static')):
                links2local.append(link)
        for link in links2local:
            print '*** warning: hyperlink to URL %s is to a local file,\n    recommended to be _static/%s for sphinx' % (link, os.path.basename(link))
        if links2local:
            print '    move linked file to _static and change URLs unless'
            print '    you really know that the links will be correct when the'
            print '    sphinx build directory is moved to its final destination'
            #_abort()  # no abort since some documentation has local URLs for illustration

    return None

def urlcheck(filestr):
    pattern = '"(https?://.+?)"'
    urls = re.findall(pattern, filestr)
    problematic = []
    for url in urls:
        if is_file_or_url(url) != 'url':
            problematic.append(url)
    if problematic:
        print '*** warning: found non-existing URLs'
        for problem in problematic:
            print '    ', problem

    """
    pieces = url.split('/')
    site = '/'.join(pieces[0:3])
    path = '/' + '/'join(pieces[3:])

    connection = httplib.HTTPConnection(site)
    connection.request('HEAD', path)
    response = connection.getresponse()
    connection.close()
    ok = False
    if response.status == 200:
        ok = True
    #if response.status in (200, 301, 301):  # incl. redirection
    if not ok:
        print '*** warning: URL "%s" does not exist!'
    return ok
    """

def make_one_line_paragraphs(filestr, format):
    # THIS FUNCTION DOES NOT WORK WELL - it's difficult to make
    # one-line paragraphs...
    print 'make_one_line_paragraphs: this function does not work well'
    print 'drop --oneline_paragraphs option on the command line...'
    # make double linebreaks to triple
    filestr = re.sub('\n *\n', '[[[[[DOUBLE_NEWLINE]]]]]', filestr)
    # save some single linebreaks
    # section headings
    filestr = re.sub('(===+)\n', r'\g<1>[[[[[SINGLE_NEWLINE]]]]]\n', filestr)
    # tables
    filestr = re.sub('(\\|\\s*)\n', r'\g<1>[[[[[SINGLE_NEWLINE]]]]]\n', filestr)
    # idx/label/ref{}
    filestr = re.sub('(\\}\\s*)\n', r'\g<1>[[[[[SINGLE_NEWLINE]]]]]\n', filestr)
    filestr = re.sub('\n(AUTHOR|TITLE|DATE|FIGURE)', r'\n[[[[[SINGLE_NEWLINE]]]]]\g<1>', filestr)
    debugpr('ONELINE1:', filestr)

    # then remove all single linebreaks + following indentation
    filestr = re.sub('\n *', ' ', filestr)
    debugpr('ONELINE2:', filestr)
    # finally insert single and double linebreaks
    filestr = filestr.replace('[[[[[SINGLE_NEWLINE]]]]] ', '\n')
    filestr = filestr.replace('[[[[[SINGLE_NEWLINE]]]]]', '\n')
    debugpr('ONELINE3:', filestr)
    filestr = filestr.replace('[[[[[DOUBLE_NEWLINE]]]]] ', '\n\n')
    filestr = filestr.replace('[[[[[DOUBLE_NEWLINE]]]]]', '\n\n')
    debugpr('ONELINE4:', filestr)
    return filestr

def bm2boldsymbol(filestr, format):
    if format in ("html", "sphinx", "pandoc", "ipynb"):
        if r'\bm{' in filestr:
            print r'*** replacing \bm{...} by \boldsymbol{...} (\bm is not supported by MathJax)'
            filestr = filestr.replace(r'\bm{', r'\boldsymbol{')
            # See http://www.wikidot.com/doc:math
    return filestr

def insert_code_from_file(filestr, format):
    if not '@@@CODE ' in filestr:
        return filestr

    # Create dummy file if specified file not found?
    CREATE_DUMMY_FILE = False

    # Filename prefix
    path_prefix = option('code_prefix=', '')
    if '~' in path_prefix:
        path_prefix = os.path.expanduser(path_prefix)

    lines = filestr.splitlines()
    inside_verbatim = False
    for i in range(len(lines)):
        line = lines[i]
        line = line.lstrip()

        # detect if we are inside verbatim blocks:
        if line.startswith('!bc'):
            inside_verbatim = True
        if line.startswith('!ec'):
            inside_verbatim = False
        if inside_verbatim:
            continue

        if line.startswith('@@@CODE '):
            debugpr('found verbatim copy (line %d):\n%s\n' % (i+1, line))
            words = line.split()
            try:
                filename = words[1]
            except IndexError:
                raise SyntaxError, \
                      'Syntax error: missing filename in line\n  %s' % line
            orig_filename = filename # keep a copy in case we have a prefix
            if path_prefix:
                filename = os.path.join(path_prefix, filename)

            try:
                codefile = open(filename, 'r')
            except IOError, e:
                print '*** error: could not open the file %s used in\n%s' % (filename, line)
                if CREATE_DUMMY_FILE and 'No such file or directory' in str(e):
                    print '    No such file or directory!'
                    print '    A dummy file %s is generated...' % filename
                    dummyfile = open(filename, 'w')
                    dummyfile.write(
                        'File %s missing - made this dummy file...\n'
                        % filename)
                    dummyfile.close()
                    codefile = open(filename, 'r')
                else:
                    print e
                    _abort()

            # Determine code environment from filename extension
            filetype = os.path.splitext(filename)[1][1:]  # drop dot

            if filetype == 'cxx' or filetype == 'C' or filetype == 'h' \
                   or filetype == 'i':
                filetype = 'cpp'
            elif filetype in ('f90', 'f95'):
                filetype = 'f'
            elif filetype == 'pyx':  # Cython code is called cy
                filetype = 'cy'
            elif filetype == 'ufl':  # UFL applies Python
                filetype = 'py'
            elif filetype == 'htm':
                filetype = 'html'
            elif filetype == 'text':
                filetype = 'txt'
            elif filetype == 'data':
                filetype = 'dat'
            elif filetype in ('csh', 'ksh', 'zsh', 'tcsh'):
                filetype = 'sh'

            if filetype in ('py', 'f', 'c', 'cpp', 'sh',
                            'm', 'pl', 'cy', 'rst',
                            'pyopt',  # Online Python Tutor
                            'pysc',   # Sage cell
                            'rb', 'html', 'xml', 'js',
                            'txt', 'csv', 'dat'):
                code_envir = filetype
            elif filetype == 'tex':
                code_envir = 'latex'
            else:
                code_envir = ''
            if code_envir in ('txt', 'csv', 'dat', ''):
                code_envir_tp = 'filedata'
            else:
                code_envir_tp = 'program'

            m = re.search(r'from-?to:', line)
            if m:
                index = m.start()
                fromto = m.group()
            else:
                index = -1  # no from-to or fromto
                fromto = 'fromto:'  # default

            #print index, words
            if index == -1 and len(words) < 3:
                # no from/to regex, read the whole file:
                print 'copy complete file %s' % filename,
                complete_file = True
                code = codefile.read().rstrip()
                debugpr('copy the whole file "%s" into a verbatim block\n' % filename)

            else:
                complete_file = False
                if index >= 0:
                    patterns = line[index+len(fromto):].strip()
                else:
                    # fromto: was not found, that is okay, use the
                    # remaining words as patterns
                    patterns = ' '.join(words[2:]).strip()
                try:
                    from_, to_ = patterns.split('@')
                except:
                    raise SyntaxError, \
                    'Syntax error: missing @ in regex in line\n  %s' % line

                print 'copying %s regex "%s" until %s\n     file: %s,' % \
                      ('after' if fromto == 'from-to:' else 'from',
                       from_,
                       ('"' + to_ + '"') if to_ != '' else 'end of file',
                       filename),
                # Note that from_ and to_ are regular expressions
                # and to_ might be empty
                cfrom = re.compile(from_)
                cto = re.compile(to_)

                # Task: copy from the line with from_ if fromto is 'fromto:',
                # or copy from the line after the with from_ if fromto
                # is 'from-to:', and copy all lines up to, but not including,
                # the line matching to_

                codefile_lines = codefile.readlines()
                from_found = False
                to_found = False
                from_line = -1
                to_line = len(codefile_lines)
                codelines = []
                copy = False
                for line_no, codeline in enumerate(codefile_lines):
                    mf = cfrom.search(codeline)
                    if mf and fromto == 'fromto:' and not from_found:
                        # The test on not to_found ensures that
                        # we cannot get a second match for from_
                        # (which copies to the end if there are no
                        # following matches for to_!)
                        copy = True
                        from_found = True
                        from_line = line_no+1
                        debugpr('hit (fromto:) start "%s" (as "%s") in line no. %d\n%s\ncode environment: %s' % (from_, codeline[mf.start():mf.end()], line_no+1, codeline, code_envir if code_envir else 'none'))

                    if to_:
                        mt = cto.search(codeline)
                        if mt:
                            copy = False
                            to_found = True
                            to_line = line_no+1
                            # now the to_ line is not included
                            debugpr('hit end "%s" (as "%s") in line no. %d\n%s' %  (to_, codeline[mt.start():mt.end()], line_no+1, codeline))
                    if copy:
                        debugpr('copy: %s' % codeline.rstrip())
                        if codeline[-2:] == '\\\n':
                            # Insert extra space to preserve
                            # continuation line
                            codeline = codeline[:-2] + '\\ \n'
                        codelines.append(codeline)

                    if mf and fromto == 'from-to:' and not from_found:
                        copy = True  # start copy from next codeline
                        from_found = True
                        from_line = line_no+2
                        debugpr('hit (from-to:) start "%s" (as "%s") in line no. %d\n%s\ncode environment: %s' % (from_, codeline[mf.start():mf.end()], line_no+1, codeline, code_envir if code_envir else 'none'))

                code = ''.join(codelines)
                code = code.rstrip() # remove trailing whitespace
                if code == '' or code.isspace():
                    if not from_found:
                        print 'but could not find regex "%s"!' % from_,
                    if not to_found and to_ != '':
                        print 'but could not find regex "%s"!' % to_,
                    if from_found and to_found:
                        print '"From" and "to" regex match at the same line - empty text.',
                    print
                    _abort()
                print ' lines %d-%d' % (from_line, to_line),
            codefile.close()

            #if format == 'latex' or format == 'pdflatex' or format == 'sphinx':
                # Insert a cod or pro directive for ptex2tex and sphinx.
            if code_envir_tp == 'program':
                if complete_file:
                    code = "!bc %spro\n%s\n!ec" % (code_envir, code)
                    print ' (format: %spro)' % code_envir
                else:
                    code = "!bc %scod\n%s\n!ec" % (code_envir, code)
                    print ' (format: %scod)' % code_envir
            else:
                # filedata (.txt, .csv, .dat, etc)
                if code_envir:
                    code = "!bc %s\n%s\n!ec" % (code_envir, code)
                    print ' (format: %s)' % code_envir
                else:
                    code = "!bc\n%s\n!ec" % code
                    print ' (format: plain !bc, not special type)'
            lines[i] = code

    filestr = '\n'.join(lines)
    return filestr


def insert_os_commands(filestr, format):
    if not '@@@OSCMD ' in filestr:
        return filestr

    # Filename prefix
    path_prefix = option('code_prefix=', '')
    if '~' in path_prefix:
        path_prefix = os.path.expanduser(path_prefix)
    os_prompt = option('os_prompt=', 'Terminal>')

    import subprocess
    def system(cmd):
        """Run system command cmd."""
        print '*** running OS command', cmd
        try:
            output = subprocess.check_output(cmd, shell=True,
                                             stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print '*** error: failure of @@@OSCMD %s' % cmd
            print e.output
            print 'Return code:', e.returncode
            _abort()
        print '-------- terminal output ----------'
        print output.rstrip()
        print '-----------------------------------'
        return output

    lines = filestr.splitlines()
    inside_verbatim = False
    for i in range(len(lines)):
        line = lines[i]
        line = line.lstrip()

        # detect if we are inside verbatim blocks:
        if line.startswith('!bc'):
            inside_verbatim = True
        if line.startswith('!ec'):
            inside_verbatim = False
        if inside_verbatim:
            continue

        if line.startswith('@@@OSCMD '):
            cmd = line[9:].strip()
            output = system(cmd)
            text = '!bc sys\n'
            if os_prompt in ('None', 'none', 'empty'):
                text += cmd + '\n'
            elif os_prompt == 'nocmd':
                pass  # drop showing cmd
            else:
                text += os_prompt + ' ' + cmd + '\n'
            text += output
            if text[-1] != '\n':
                text += '\n'
            text += '!ec\n'
            lines[i] = text
    filestr = '\n'.join(lines)
    return filestr

def exercises(filestr, format, code_blocks, tex_blocks):
    # Exercise:
    # ===== Exercise: title ===== (starts with at least 3 =, max 5)
    # label{some:label} file=thisfile.py solution=somefile.do.txt
    # __Hint 1.__ some paragraph...,
    # __Hint 2.__ ...

    all_exer = []   # collection of all exercises
    exer = {}       # data for one exercise, to be appended to all_exer
    inside_exer = False
    exer_end = False
    exer_counter = dict(Exercise=0, Problem=0, Project=0, Example=0)

    # Regex: no need for re.MULTILINE since we treat one line at a time
    if option('examples_as_exercises'):
        exer_heading_pattern = r'^\s*(=====)\s*\{?(Exercise|Problem|Project|Example)\}?:\s*(?P<title>[^ =-].+?)\s*====='
    else:
        exer_heading_pattern = r'^\s*(=====)\s*\{?(Exercise|Problem|Project)\}?:\s*(?P<title>[^ =-].+?)\s*====='
    if not re.search(exer_heading_pattern, filestr, flags=re.MULTILINE):
        return filestr

    label_pattern = re.compile(r'^\s*label\{(.+?)\}')
    # We accept file and solution to be comment lines
    #file_pattern = re.compile(r'^#?\s*file\s*=\s*([^\s]+)')
    file_pattern = re.compile(r'^#?\s*files?\s*=\s*([A-Za-z0-9\-._, ]+)')
    solution_pattern = re.compile(r'^#?\s*solutions?\s*=\s*([A-Za-z0-9\-._, ]+)')
    keywords_pattern = re.compile(r'^#?\s*(keywords|kw)\s*=\s*([A-Za-z0-9\-._;, ]+)')

    hint_pattern_begin = '!bhint'
    hint_pattern_end = '!ehint'
    answer_pattern_begin = '!bans'
    answer_pattern_end = '!eans'
    solution_pattern_begin = '!bsol'
    solution_pattern_end = '!esol'
    subex_pattern_begin = '!bsubex'
    subex_pattern_end = '!esubex'
    closing_remarks_pattern_begin = '!bremarks'
    closing_remarks_pattern_end = '!eremarks'

    lines = filestr.splitlines()
    newlines = []  # lines in resulting file
    # m_* variables: various match objects from regex searches

    for line_no in range(len(lines)):
        line = lines[line_no].lstrip()
        #print 'LINE %d:' % i, line
        #import pprint; pprint.pprint(exer)

        m_heading = re.search(exer_heading_pattern, line)
        if m_heading:
            inside_exer = True

            exer = {}  # data in the exercise
            exer['title'] = m_heading.group('title')
            exer['heading'] = m_heading.group(1)   # heading type

            exer_tp = m_heading.group(2)           # exercise type
            if '{' + exer_tp + '}' in line:
                exer['type_visible'] = False
            else:
                exer['type_visible'] = True
            exer['type'] = exer_tp

            # We count all Exercises, Problems, etc. with the
            # same counter (Exercise 4 and Problem 4 are likely
            # to be confusing...)
            exer_counter['Exercise'] += 1
            exer['no'] = exer_counter['Exercise']

            exer['label'] = None
            exer['solution_file'] = None
            exer['file'] = None
            exer['keywords'] = None
            exer.update(dict(text=[], hints=[], answer=[],
                             solution=[], subex=[], closing_remarks=[]))

            exer_end = False

            inside_hint = False
            inside_subex = False
            inside_answer = False
            inside_solution = False
            inside_closing_remarks = False
        elif inside_exer:
            instruction_line = True

            m_label = label_pattern.search(line)
            m_file = file_pattern.search(line)
            m_solution_file = solution_pattern.search(line)
            m_keywords = keywords_pattern.search(line)

            if m_label:
                if exer['label'] is None:
                    exer['label'] = m_label.group(1)
            elif m_keywords:
                exer['keywords'] = [name.strip() for name in
                                    m_keywords.group(2).split(';')]
            elif m_file and not inside_subex:
                if exer['file'] is None:  # only the first counts
                    exer['file'] = [name.strip() for name in
                                    m_file.group(1).split(',')]
            elif m_file and inside_subex:
                subex['file'] = [name.strip() for name in
                                 m_file.group(1).split(',')]
            elif m_solution_file:
                exer['solution_file'] = [name.strip() for name in
                                         m_solution_file.group(1).split(',')]

            elif line.startswith(subex_pattern_begin):
                inside_subex = True
                subex = dict(text=[], hints=[], answer=[],
                             solution=[], file=None)
            elif line.startswith(subex_pattern_end):
                inside_subex = False
                subex['text'] = '\n'.join(subex['text']).strip()
                subex['answer'] = '\n'.join(subex['answer']).strip()
                subex['solution'] = '\n'.join(subex['solution']).strip()
                for _i in range(len(subex['hints'])):
                    subex['hints'][_i] = '\n'.join(subex['hints'][_i]).strip()

                exer['subex'].append(subex)

            elif line.startswith(answer_pattern_begin):
                inside_answer = True
            elif line.startswith(answer_pattern_end):
                inside_answer = False

            elif line.startswith(solution_pattern_begin):
                inside_solution = True
            elif line.startswith(solution_pattern_end):
                inside_solution = False

            elif line.startswith(hint_pattern_begin):
                inside_hint = True
                if inside_subex:
                    subex['hints'].append([])
                else:
                    exer['hints'].append([])
            elif line.startswith(hint_pattern_end):
                inside_hint = False

            elif line.startswith(closing_remarks_pattern_begin):
                inside_closing_remarks = True
            elif line.startswith(closing_remarks_pattern_end):
                inside_closing_remarks = False

            else:
                instruction_line = False

            # [[[
            # Read the suggestions below. Multiple choice must be
            # a separate functionality so we can insert !bmchoice also
            # outside exercises. Just read the text into a data structure
            # and let formats have a new SURVEY[format] function to typeset
            # the questions. One can generate plain HTML or create full
            # surveys, see TODO/quiz.do.txt.

            # It should be possible to leave out questions from a doconce doc.
            #
            # How to do multiple choice in exer or subex (or inside admons
            # and elsewhere, e.g., survey questions):
            # !bmchoice, !emchoice (bchoices does not work since it starts with bc!)
            # inside_mchoice: store all that text in subex/exer['multiple_choice']
            # afterwards: interpret the text in multiple_choices
            # syntax:
            # Q: can be multiline whatever (up to C(f|r):)
            # Cr: right answer
            # E: corresponding explanation
            # Cf: another but wrong answer, can be multiline
            # regex (inside all the bmchoice text): (Cf|Cr):.+^(E|Cf|Cr|ENDMARKER), re.DOTALL, problem: if not E:, re.findall will not pick out all because the match goes up to and including the next Cf/Cr. Maybe look ahead at (E|Cf|Cr|$) can solve this? Try out first! (Must add ENDMARKER to the end of the text)
            # Could add a remarks section for lessons learned, etc.?
            # Add title or have it as part of !bmchoice

            # Example code: intro-programming, more modern tools
            # are jQuery.Survey: http://flesler.webs.com/jQuery.Survey/ (see source for use), see also https://github.com/jdarling/jQuery.Survey
            # Really simple, read this first about HTML and jquery!!: http://www.hungrypiranha.org/make-a-website/html-quiz (seems more straightforward than any other solution)
            # Some js theory for pop-up surveys: http://www.jensbits.com/2010/01/29/pop-up-survey-with-jquery-ui-dialog/
            # Simple js: https://www.inkling.com/read/javascript-jquery-david-sawyer-mcfarland-2nd/chapter-3/tutorial-a-simple-quiz

            # syntax: Cf/Cr: ..., required E: ... for explanation (can be empty)
            # Cf is a false choice, Cr is a right choice (or False:/True:)
            # Easy to use a regex to pick out the structure of the multiple
            # choice text (False|True):(.+?)(E|Explanation|$): (with $ explanations are optional - NO!!)
            # Better: do a split on True: and then a split on False,
            # for each True/False, extract E: if it exists (split?)
            # (E|Explanation):(.+?)($|False|True)
            # HTML can generate JavaScript a la INF1100 quiz (put all
            # js in the html file), latex can use fancy constructions,
            # others can use a plain list. --with_sol determines if
            # the solution is published (as for the answer/solution).
            # Should have possibility to have textarea as answer to
            # question for future smart regex checks of the answer, maybe
            # also upload files.
            if inside_subex and not instruction_line:
                if inside_answer:
                    subex['answer'].append(lines[line_no])
                elif inside_solution:
                    subex['solution'].append(lines[line_no])
                elif inside_hint:
                    subex['hints'][-1].append(lines[line_no])
                else:
                    # ordinary text line
                    subex['text'].append(lines[line_no])
            elif not inside_subex and not instruction_line:
                if inside_answer:
                    exer['answer'].append(lines[line_no])
                elif inside_solution:
                    exer['solution'].append(lines[line_no])
                elif inside_hint:
                    exer['hints'][-1].append(lines[line_no])
                elif inside_closing_remarks:
                    exer['closing_remarks'].append(lines[line_no])
                else:
                    # ordinary text line
                    exer['text'].append(lines[line_no])

        else:  # outside exercise
            newlines.append(lines[line_no])

        # End of exercise? Either 1) new (sub)section with at least ===,
        # 2) !split, or 3) end of file
        if line_no == len(lines) - 1:  # last line?
            exer_end = True
        elif inside_exer and lines[line_no+1].startswith('!split'):
            exer_end = True
        elif inside_exer and lines[line_no+1].startswith('====='):
            exer_end = True
        elif inside_exer and option('sections_down') and lines[line_no+1].startswith('==='):
            exer_end = True

        if exer and exer_end:
            exer['text'] = '\n'.join(exer['text']).strip()
            exer['answer'] = '\n'.join(exer['answer']).strip()
            exer['solution'] = '\n'.join(exer['solution']).strip()
            exer['closing_remarks'] = '\n'.join(exer['closing_remarks']).strip()
            for i_ in range(len(exer['hints'])):
                exer['hints'][i_] = '\n'.join(exer['hints'][i_]).strip()

            debugpr('Data structure from interpreting exercises:',
                    pprint.pformat(exer))
            formatted_exercise = EXERCISE[format](exer)
            newlines.append(formatted_exercise)
            all_exer.append(exer)
            inside_exer = False
            exer_end = False
            exer = {}

    filestr = '\n'.join(newlines)
    if all_exer:
        # Replace code and math blocks by actual code.
        # This must be done in the all_exer data structure,
        # if a pprint.pformat'ed string is used, quotes in
        # computer code and derivatives lead to errors
        # if we take an eval on the output.

        from common import _CODE_BLOCK, _MATH_BLOCK

        def replace_code_math(text):
            if not isinstance(text, basestring):
                return text

            pattern = r"(\d+) %s( +)([a-z]+)" % _CODE_BLOCK
            code = re.findall(pattern, text, flags=re.MULTILINE)
            for n, space, tp in code:
                block = code_blocks[int(n)]
                from_ = '%s %s%s%s' % (n, _CODE_BLOCK, space, tp)
                to_ = '!bc %s\n' % (tp) + block + '\n!ec'
                text = text.replace(from_, to_)
            # Remaining blocks without type
            pattern = r"(\d+) %s" % _CODE_BLOCK
            code = re.findall(pattern, text, flags=re.MULTILINE)
            for n in code:
                block = code_blocks[int(n)]
                from_ = '%s %s' % (n, _CODE_BLOCK)
                to_ = '!bc\n' + block + '\n!ec'
                text = text.replace(from_, to_)
            pattern = r"(\d+) %s" % _MATH_BLOCK
            math = re.findall(pattern, text, flags=re.MULTILINE)
            for n in math:
                block = tex_blocks[int(n)]
                from_ = '%s %s' % (n, _MATH_BLOCK)
                to_ = '!bt\n' + block + '\n!et'
                text = text.replace(from_, to_)
            return text

        for e in range(len(all_exer)):
            for key in all_exer[e]:
                if key == 'subex':
                    for es in range(len(all_exer[e][key])):
                       for keys in all_exer[e][key][es]:
                           all_exer[e][key][es][keys] = \
                               replace_code_math(all_exer[e][key][es][keys])
                else:
                     all_exer[e][key] = \
                               replace_code_math(all_exer[e][key])

        all_exer_str = pprint.pformat(all_exer)

        # (recall that we write to pprint-formatted string!)

        # Dump this data structure to file
        exer_filename = filename.replace('.do.txt', '')
        exer_filename = '.%s.exerinfo' % exer_filename
        f = open(exer_filename, 'w')
        f.write("""
# Information about all exercises in the file %s.
# The information can be loaded into a Python list of dicts by
#
# f = open('%s', 'r')
# exer = eval(f.read())
#
""" % (filename, exer_filename))
        f.write(all_exer_str)
        f.close()
        print 'found info about %d exercises, written to %s' % \
              (len(all_exer), exer_filename)
        debugpr('The file after interpreting exercises:', filestr)
    else:
        debugpr('No exercises found.')

    # Syntax check: must be no more exercise-specific environments left
    envirs = ['ans', 'sol', 'subex', 'hint', 'remarks']
    for envir in envirs:
        begin = '!b' + envir
        end = '!e' + envir
        found_pairs = False
        # Find pairs
        blocks = re.findall(r'^%s.+?^%s' % (begin, end), filestr,
                            flags=re.DOTALL|re.MULTILINE)
        if blocks:
            found_pairs = True
            print '*** error: %s-%s block is not legal outside an exercise' % \
                  (begin, end)
            print '    (or problem/project/example) section:'
            for block in blocks:
                print block
            _abort()
        # Find single occurences (syntax error)
        if not found_pairs:
            m = re.search(r'^![be]%s' % envir, filestr, flags=re.MULTILINE)
            if m:
                print '*** error: found !b%s or !e%s outside exercise section' % envir
                print repr(filestr[m.start():m.start()+120])
                _abort()

    return filestr


def parse_keyword(keyword, format):
    """
    Parse a keyword for a description list when the keyword may
    represent information about an argument to a function or a
    variable in a program::

      - argument x: x coordinate (float).
      - keyword argument tolerance: error tolerance (float).
      - return: corresponding y coordinate (float).
    """
    keyword = keyword.strip()
    if keyword[-1] == ':':      # strip off trailing colon
        keyword = keyword[:-1]

    typical_words = ('argument', 'keyword argument', 'return', 'variable')
    parse = False
    for w in typical_words:
        if w in keyword:    # part of function argument++ explanation?
            parse = True
            break
    if not parse:
        # no need to parse for variable type and name
        if format == 'epytext':
            # epytext does not have description lists, add a "bullet" -
            keyword = '- ' + keyword
        return keyword

    # parse:
    if 'return' in keyword:
        type = 'return'
        varname = None
        type = ARGLIST[format][type]  # formatting of keyword type
        return type
    else:
        words = keyword.split()
        varname = words[-1]
        type = ' '.join(words[:-1])
        if type == 'argument':
            type = 'parameter'
        elif type == 'keyword argument':
            type = 'keyword'
        elif type == 'instance variable':
            type = 'instance variable'
        elif type == 'class variable':
            type = 'class variable'
        elif type == 'module variable':
            type = 'module variable'
        else:
            return keyword # probably not a list of variable explanations
        # construct "type varname" string, where varname is typeset in
        # inline verbatim:
        pattern = r'(?P<begin>^)(?P<subst>%s)(?P<end>$)' % varname
        #varname = re.sub(pattern, INLINE_TAGS_SUBST[format]['verbatim'], varname)
        keyword = ARGLIST[format][type] + ' ' + varname
        return keyword


def space_in_tables(filestr):
    """
    Add spaces around | in tables such that substitutions $...$ and
    `...` get right.
    """
    pattern = r'^\s*\|.+\| *$'
    table_lines = re.findall(pattern, filestr, re.MULTILINE)
    horizontal_rule = r'^\s*\|[-lrc]+\|\s*$'
    for line in table_lines:
        if not re.search(horizontal_rule, line, flags=re.MULTILINE) \
           and re.search(r'[^ ]|[^ ]', line) and line.count('|') > 2:
            line_wspaces = ' | '.join(line.split('|'))
            filestr = filestr.replace(line, line_wspaces)
    return filestr

def typeset_tables(filestr, format):
    """
    Translate tables with pipes and dashes to a list of
    row-column values. Horizontal rules become a row
    ['horizontal rule'] in the list.
    The list is easily translated to various output formats
    by other modules.
    """

    from StringIO import StringIO
    result = StringIO()

    # table is a dict with keys rows, headings_align, columns_align
    table = {'rows': []}  # init new table
    inside_table = False

    tables2csv = option('tables2csv')
    import csv
    table_counter = 0
    # Add functionality:
    # doconce csv2table, which reads a .csv file and outputs
    # a doconce formatted table

    horizontal_rule_pattern = r'^\|[\-lrc]+\|'
    lines = filestr.splitlines()
    # Fix: add blank line if document ends with a table (otherwise we
    # cannot see the end of the table)
    if re.search(horizontal_rule_pattern, lines[-1]):
        lines.append('\n')

    for line in lines:
        lin = line.strip()
        # horisontal table rule?
        if re.search(horizontal_rule_pattern, lin):
            horizontal_rule = True
        else:
            horizontal_rule = False
        if horizontal_rule:
            table['rows'].append(['horizontal rule'])

            # See if there is c-l-r alignments:
            align = lin[1:-1].replace('-', '') # keep | in align spec.
            if align:
                # Non-empty string contains lrc letters for alignment
                # (can be alignmend of heading or of columns)
                if align == '|'*len(align):  # Just '|||'?
                    print 'Syntax error: horizontal rule in table '\
                          'contains | between columns - remove these.'
                    print line
                    _abort()
                for char in align:
                    if char not in ('|', 'r', 'l', 'c'):
                        print 'illegal alignment character in table:', char
                        _abort()
                if len(table['rows']) == 0:
                    # first horizontal rule, align spec concern headings
                    table['headings_align'] = align
                else:
                    # align spec concerns column alignment
                    table['columns_align'] = align
            continue  # continue with next line
        if lin.startswith('|') and not horizontal_rule:
            # row in table:
            if not inside_table:
                inside_table = True
                table_counter += 1
            # Check if | is used in math in this line
            math_exprs = re.findall(r'\$(.+?)\$', line)
            for math_expr in math_exprs:
                if '|' in math_expr:
                    print '*** error: use of | in math formulas in tables confuses'
                    print '    the interpretation of the table. Rewrite and remove |.'
                    print line
                    _abort()

            # Extract columns, but drop first and last since these
            # are always empty after .split('|')
            columns = line.strip().split('|')[1:-1]  # does not work with math2 syntax
            # remove empty columns and extra white space:
            #columns = [c.strip() for c in columns if c]
            #columns = [c.strip() for c in columns if c.strip()]
            # Remove extra white space in columns
            columns = [c.strip() for c in columns]
            table['rows'].append(columns)
        elif lin.startswith('#') and inside_table:
            continue  # just skip commented table lines
        else:
            if inside_table:
                # not a table line anymore, but we were just inside a table
                # so the table is ended
                inside_table = False
                #import pprint; pprint.pprint(table)

                # Check for consistency of the recorded table:
                try:
                    # We demand three horizontal rules
                    ok = table['rows'][0] == ['horizontal rule'] and \
                         table['rows'][2] == ['horizontal rule'] and \
                         table['rows'][-1] == ['horizontal rule']
                except IndexError:
                    ok = False
                if not ok:
                    print '*** error: syntax error in table!'
                    print '    missing three horizontal rules and heading'
                    for row in table['rows']:
                        if row != ['horizontal rule']:
                            # Check for common syntax error: |--l--|--r--|
                            if sum([bool(re.search('[lrc-]{%d}' % len(c), c)) for c in row]) > 0:
                                print 'NOTE: do not use pipes in horizontal rule of this type:'
                                print '(write instead |%s|)' % '-'.join(row)
                            print '| ' + ' | '.join(row) + ' |'
                        else:
                            print '|---------------------| (horizontal rule)'
                    print '(or maybe not a table, just an opening pipe symbol at the beginning of the line?)'
                    _abort()

                result.write(TABLE[format](table))   # typeset table
                # Write CSV file
                if tables2csv:
                    outfile = open('table_%d.csv' % table_counter, 'w')
                    writer = csv.writer(outfile)
                    for row in table['rows']:
                        if row == ['horizontal rule']:
                            continue
                        writer.writerow(row)
                    outfile.close()
                table = {'rows': []}  # init new table
            else:
                result.write(line + '\n')
    return result.getvalue()

def typeset_envirs(filestr, format):
    # Note: exercises are done (and translated to doconce syntax)
    # before this function is called
    envirs = doconce_envirs()[8:]

    for envir in envirs:
        if not '!b' + envir in filestr:
            # Drop re.sub below on envirs that are not used in the document
            continue

        if format in ENVIRS and envir in ENVIRS[format]:
            def subst(m):  # m: match object from re.sub, group(1) is the text
                title = m.group(1).strip()
                # Text size specified in parenthesis?
                m2 = re.search('^\s*\((.+?)\)', title)
                text_size = 'normal'
                if m2:
                    text_size = m2.group(1).lower()
                    title = title.replace('(%s)' % text_size, '').strip()
                    if text_size not in ('small', 'large'):
                        print '*** warning: wrong text size "%s" specified in %s environment!' % (text_size, envir)
                        print '    must be "large" or "small" - will be set to normal'
                if title == '':
                    # Rely on the format's default title
                    return ENVIRS[format][envir](m.group(2), format, text_size=text_size)
                else:
                    return ENVIRS[format][envir](m.group(2), format, title, text_size=text_size)
        else:
            # subst functions for default handling in primitive formats
            # that do not support the current environment
            if envir in ('quote', 'box'):
                # Just indent the block
                def subst(m):
                    return indent_lines(m.group(1), format, ' '*4) + '\n'
            elif envir in admons + ('hint', 'remarks'):
                # Just a plan paragraph with paragraph heading
                def subst(m):
                    title = m.group(1).strip()
                    # Text size specified in parenthesis?
                    m2 = re.search('^\s*\((.+?)\)', title)

                    if title == '' and envir != 'block':
                        title = envir.capitalize() + '.'
                    elif title.lower() == 'none':
                        title == ''
                    elif m2:
                        text_size = m2.group(1).lower()
                        title = title.replace('(%s)' % text_size, '').strip()
                    elif title and title[-1] not in ('.', ':', '!', '?'):
                        # Make sure the title ends with puncuation
                        title += '.'
                    # Recall that this formatting is called very late
                    # so native format must be used
                    if title:
                        title = INLINE_TAGS_SUBST[format]['paragraph'].replace(
                            r'\g<subst>', '%s') % title + '\n'
                        # Could also consider subsubsection formatting
                    text = title + m.group(2) + '\n\n'
                    return text

            # else: other envirs for slides are treated later with
            # the begin and end directives set in comments, see doconce2format

        #pattern = r'^!b%s([A-Za-z0-9,.!:? /()\-]*?)\n(.+?)\s*^!e%s\s*' % (envir, envir)
        pattern = r'^!b%s(.*?)\n(.+?)\s*^!e%s' % (envir, envir)
        filestr = re.sub(pattern, subst, filestr,
                         flags=re.DOTALL | re.MULTILINE)

        latexfigdir_all = latex.latexfigdir + '.all'
        if os.path.isdir(latexfigdir_all):
            shutil.rmtree(latexfigdir_all)
    return filestr


def typeset_lists(filestr, format, debug_info=[]):
    """
    Go through filestr and parse all lists and typeset them correctly.
    This function must be called after all (verbatim) code and tex blocks
    have been removed from the file.
    This function also treats comment lines and blank lines.
    """
    debugpr('*** List typesetting phase + comments and blank lines ***')
    from StringIO import StringIO
    result = StringIO()
    lastindent = 0
    lists = []
    inside_description_environment = False
    lines = filestr.splitlines()
    lastline = lines[0]
    # for debugging only:
    _code_block_no = 0; _tex_block_no = 0
    exercise_comment_line = r'--- (begin|end) .*?exercise ---'

    for i, line in enumerate(lines):
        debugpr('\n------------------------\nsource line=[%s]' % line)
        # do a syntax check:
        for tag in INLINE_TAGS_BUGS:
            bug = INLINE_TAGS_BUGS[tag]
            if bug:
                m = re.search(bug[0], line)
                if m:
                    print '*** syntax error: "%s"\n    %s' % \
                          (m.group(0), bug[1])
                    print '    in line\n[%s]' % line
                    print '    surrounding text is\n'
                    for l in lines[i-4:i+5]:
                        print l
                    _abort()

        if not line or line.isspace():  # blank line?
            if not lists:
                result.write(BLANKLINE[format])
            # else: drop writing out blank line inside lists
                debugpr('  > This is a blank line')
            lastline = line
            continue

        if line.startswith('#'):

            # first do some debug output:
            if line.startswith('#!!CODE') and len(debug_info) >= 1:
                result.write(line + '\n')
                debugpr('  > Here is a code block:\n%s\n--------' % \
                      debug_info[0][_code_block_no])
                _code_block_no += 1
            elif line.startswith('#!!TEX') and len(debug_info) >= 2:
                result.write(line + '\n')
                debugpr('  > Here is a latex block:\n%s\n--------' % \
                      debug_info[1][_tex_block_no])
                _tex_block_no += 1

            else:
                debugpr('  > This is just a comment line')
                # the comment can be propagated to some formats
                # (rst, latex, html):
                if 'comment' in INLINE_TAGS_SUBST[format]:
                    comment_action = INLINE_TAGS_SUBST[format]['comment']
                    if isinstance(comment_action, str):
                        new_comment = comment_action % line[1:].strip()
                    elif callable(comment_action):
                        new_comment = comment_action(line[1:].strip())

                    # Exercises has comment lines that make end of lists,
                    # let these be treated as ordinary new, nonindented
                    # lines
                    if not re.search(exercise_comment_line, line):
                        # Ordinary comment
                        result.write(new_comment + '\n')
                    else:
                        # Special exercise comment (ordinary line)
                        line = new_comment  # will be printed later

            lastline = line
            if not re.search(exercise_comment_line, line):
                # Ordinary comment
                continue
            # else: just proceed and use zero indent as indicator
            # for end of list

        # structure of a line:
        linescan = re.compile(
            r"(?P<indent> *(?P<listtype>[*o-] )? *)" +
            r"(?P<keyword>.+?:\s+)?(?P<text>.*)\s?")
            #r"(?P<keyword>[^:]+?:)?(?P<text>.*)\s?")

        m = linescan.match(line)
        indent = len(m.group('indent'))
        listtype = m.group('listtype')
        if listtype:
            listtype = listtype.strip()
            listtype = LIST_SYMBOL[listtype]
        keyword = m.group('keyword')
        text = m.group('text')
        debugpr('  > indent=%d (previous indent=%d), keyword=[%s], text=[%s]' % (indent, lastindent, keyword, text))

        # new (sub)section makes end of any indent (we could demand
        # (sub)sections to start in column 1, but we have later relaxed
        # such a requirement; it is easier to just test for ___ or === and
        # set indent=0 here):
        if line.lstrip().startswith('___') or line.lstrip().startswith('==='):
            indent = 0


        if indent > lastindent and listtype:
            debugpr('  > This is a new list of type "%s"' % listtype)
            # begin a new list or sublist:
            lists.append({'listtype': listtype, 'indent': indent})
            result.write(LIST[format][listtype]['begin'])
            if len(lists) > 1:
                result.write(LIST[format]['separator'])

            lastindent = indent
            if listtype == 'enumerate':
                enumerate_counter = 0
        elif listtype:
            # inside a list, but not in the beginning
            # (we don't write out blank lines inside lists anymore!)
            # write a possible blank line if the format wants that between items
            result.write(LIST[format]['separator'])

        if indent < lastindent:
            # end a list or sublist, nest back all list
            # environments on the lists stack:
            while lists and lists[-1]['indent'] > indent:
                 debugpr('  > This is the end of a %s list' % \
                       lists[-1]['listtype'])
                 result.write(LIST[format][lists[-1]['listtype']]['end'])
                 del lists[-1]
            lastindent = indent

        if indent == lastindent:
            debugpr('  > This line belongs to the previous block since it has '\
                  'the same indent (%d blanks)' % indent)

        if listtype:
            # (a separator (blank line) is written above because we need
            # to ensure that the separator is not written in the top of
            # an entire new list)

            # first write the list item identifier:
            itemformat = LIST[format][listtype]['item']
            if format == 'cwiki' or format == 'mwiki':
                itemformat = itemformat*len(lists)  # *, **, #, ## etc. for sublists
            item = itemformat
            if listtype == 'enumerate':
                debugpr('  > This is an item in an enumerate list')
                enumerate_counter += 1
                if '%d' in itemformat:
                    item = itemformat % enumerate_counter
                # indent here counts with '3. ':
                result.write(' '*(indent - 2 - enumerate_counter//10 - 1))
                result.write(item + ' ')
            elif listtype == 'description':
                if '%s' in itemformat:
                    if not keyword:
                        # empty keyword, the regex has a bad problem: when only
                        # keyword on the line, keyword is None and text
                        # is keyword - make a fix here
                        if text[-1] == ':':
                            keyword = text
                            text = ''
                    if keyword:
                        keyword = parse_keyword(keyword, format) + ':'
                        item = itemformat % keyword + ' '
                        debugpr('  > This is an item in a description list '\
                              'with parsed keyword=[%s]' % keyword)
                        keyword = '' # to avoid adding keyword up in
                        # below (ugly hack, but easy linescan parsing...)
                    else:
                        debugpr('  > This is an item in a description list, but empty keyword, serious error....')
                result.write(' '*(indent-2))  # indent here counts with '- '
                result.write(item)
                if not (text.isspace() or text == ''):
                    #result.write('\n' + ' '*(indent-1))
                    # Need special treatment if type specifications in
                    # descrption lists for sphinx API doc
                    if format == 'sphinx' and text.lstrip().startswith('type:'):
                        text = text.lstrip()[5:].lstrip()
                        # no newline for type info
                    else:
                        result.write('\n' + ' '*(indent))
            else:
                debugpr('  > This is an item in a bullet list')
                result.write(' '*(indent-2))  # indent here counts with '* '
                result.write(item + ' ')

        else:
            debugpr('  > This line is some ordinary line, no special list syntax involved')
            # should check emph, verbatim, etc., syntax check and common errors
            result.write(' '*indent)      # ordinary line

        # this is not a list definition line and therefore we must
        # add keyword + text because these two items make up the
        # line if a : present in an ordinary line
        if keyword:
            text = keyword + text
        debugpr('text=[%s]' % text)

        # hack to make wiki have all text in an item on a single line:
        newline = '' if lists and format in ('gwiki', 'cwiki') else '\n'
        #newline = '\n'
        result.write(text + newline)
        lastindent = indent
        lastline = line

    # end lists if any are left:
    while lists:
        debugpr('  > This is the end of a %s list' % lists[-1]['listtype'])
        result.write(LIST[format][lists[-1]['listtype']]['end'])
        del lists[-1]

    return result.getvalue()


def handle_figures(filestr, format):
    if not format in FIGURE_EXT:
        # no special handling of figures:
        return filestr

    pattern = INLINE_TAGS['figure']
    c = re.compile(pattern, re.MULTILINE)

    # Plan: first check if the figure files are of right type, then
    # call format-specific functions for how to format the figures.

    if type(FIGURE_EXT[format]) is str:
        extensions = [FIGURE_EXT[format]]  # wrap in list
    else:
        extensions = FIGURE_EXT[format]

    figfiles = [filename.strip()
             for filename, options, caption in c.findall(filestr)]
    import sets; figfiles = sets.Set(figfiles)   # remove multiple occurences

    # Prefix figure paths if user has requested it
    figure_prefix = option('figure_prefix=')
    if figure_prefix is not None:
        # substitute all figfile names in figfiles with figure_prefix + figfile
        if '~' in figure_prefix:
            figure_prefix = os.path.expanduser(figure_prefix)
        for figfile in figfiles:
            if not figfile.startswith('http'):
                newname = os.path.join(figure_prefix, figfile)
                filestr = re.sub(r'%s([,\]])' % figfile,
                                 '%s\g<1>' % newname, filestr)
    # Prefix movies also
    movie_pattern = INLINE_TAGS['movie']
    movie_files = [filename.strip()
                   for filename, options, caption in
                   re.findall(movie_pattern, filestr, flags=re.MULTILINE)]
    movie_prefix = option('movie_prefix=')
    if movie_prefix is not None:
        if '~' in movie_prefix:
            movie_prefix = os.path.expanduser(movie_prefix)
        for movfile in movie_files:
            if not movfile.startswith('http'):
                newname = os.path.join(movie_prefix, movfile)
                filestr = re.sub(r'%s([,\]])' % movfile,
                                 '%s\g<1>' % newname, filestr)

    # Find new filenames
    figfiles = [filename.strip()
             for filename, options, caption in c.findall(filestr)]
    import sets; figfiles = sets.Set(figfiles)   # remove multiple occurences

    for figfile in figfiles:
        if figfile.startswith('http'):
            # latex, pdflatex must download the file,
            # html, sphinx and web-based formats can use the URL directly
            basepath, ext = os.path.splitext(figfile)
            # Avoid ext = '.05' etc from numbers in the filename
            if not ext.lower() in ['.eps', '.pdf', '.png', '.jpg', 'jpeg',
                                   '.gif', '.tif', '.tiff']:
                ext = ''
            if ext:
                if is_file_or_url(figfile) != 'url':
                    print '*** error: figure URL "%s" could not reached' % figfile
                    _abort()
            else:
                # no extension, run through the allowed extensions
                # to see if figfile + ext exists:
                file_found = False
                for ext in extensions:
                    newname = figfile + ext
                    if is_file_or_url(newname) == 'url':
                        file_found = True
                        print 'figure file %s:\n    can use %s for format %s' \
                              % (figfile, newname, format)
                        filestr = re.sub(r'%s([,\]])' % figfile,
                                         '%s\g<1>' % newname, filestr)
                        break
                if not file_found:
                    print '*** error: figure %s:\n    could not find URL with legal extension %s' % (figfile, ', '.join(extensions))
                    _abort()
            continue
        # else: check out local figure file on the disk
        file_found = False
        if not os.path.isfile(figfile):
            basepath, ext = os.path.splitext(figfile)
            # Avoid ext = '.05' etc from numbers in the filename
            if not ext.lower() in ['.eps', '.pdf', '.png', '.jpg', 'jpeg',
                                   '.gif', '.tif', '.tiff']:
                ext = ''
            if not ext:  # no extension?
                # try to see if figfile + ext exists:
                for ext in extensions:
                    newname = figfile + ext
                    if os.path.isfile(newname):
                        print 'figure file %s:\n    can use %s for format %s' % \
                              (figfile, newname, format)
                        filestr = re.sub(r'%s([,\]])' % figfile,
                                         '%s\g<1>' % newname, filestr)
                        figfile = newname
                        file_found = True
                        break
                # couldn't find figfile with an acceptable extension,
                # try to see if other extensions exist and use the
                # first one to convert to right format:
                if not file_found:
                    candidate_files = glob.glob(figfile + '.*')
                    for newname in candidate_files:
                        if os.path.isfile(newname):
                            print 'found', newname
                            #dangerous: filestr = filestr.replace(figfile, newname)
                            filestr = re.sub(r'%s([,\]])' % figfile,
                                             '%s\g<1>' % newname, filestr)
                            figfile = newname
                            file_found = True
                            break
        if not os.path.isfile(figfile):
            #raise ValueError('file %s does not exist' % figfile)
            print '*** error: figure file "%s" does not exist!' % figfile
            _abort()
        basepath, ext = os.path.splitext(figfile)
        if not ext in extensions:
            # convert to proper format
            for e in extensions:
                converted_file = basepath + e
                if not os.path.isfile(converted_file):
                    # ext might be empty, in that case we cannot convert
                    # anything:
                    if ext:
                        print 'figure', figfile, 'must have extension(s)', \
                              extensions
                        # use ps2pdf and pdf2ps for vector graphics
                        # and only convert if to/from png/jpg/gif
                        if ext.endswith('ps') and e == '.pdf':
                            #cmd = 'epstopdf %s %s' % \
                            #      (figfile, converted_file)
                            cmd = 'ps2pdf -dEPSCrop %s %s' % \
                                  (figfile, converted_file)
                        elif ext == '.pdf' and ext.endswith('ps'):
                            cmd = 'pdf2ps %s %s' % \
                                  (figfile, converted_file)
                        else:
                            cmd = 'convert %s %s' % (figfile, converted_file)
                            if e in ('.ps', '.eps', '.pdf') and \
                               ext in ('.png', '.jpg', '.jpeg', '.gif'):
                                print """\
*** warning: need to convert from %s to %s
using ImageMagick's convert program, but the result will
be loss of quality. Generate a proper %s file.""" % \
                                (figfile, converted_file, converted_file)
                        failure = os.system(cmd)
                        if not failure:
                            print '....image conversion:', cmd
                            # dangerous: filestr = filestr.replace(figfile, converted_file)
                            filestr = re.sub(r'%s([,\]])' % figfile,
                                         '%s\g<1>' % converted_file, filestr)

                            break  # jump out of inner e loop
                else:  # right file exists:
                    #print '....ok, ', converted_file, 'exists'
                    #dangerous: filestr = filestr.replace(figfile, converted_file)
                    filestr = re.sub(r'%s([,\]])' % figfile,
                                     '%s\g<1>' % converted_file, filestr)

                    break

    # replace FIGURE... by format specific syntax:
    try:
        replacement = INLINE_TAGS_SUBST[format]['figure']
        filestr = c.sub(replacement, filestr)
    except KeyError:
        pass
    return filestr


def handle_cross_referencing(filestr, format):
    # 1. find all section/chapter titles and corresponding labels
    #section_pattern = r'(_+|=+)([A-Za-z !.,;0-9]+)(_+|=+)\s*label\{(.+?)\}'
    section_pattern = r'^\s*(_{3,9}|={3,9})(.+?)(_{3,9}|={3,9})\s*label\{(.+?)\}'
    m = re.findall(section_pattern, filestr, flags=re.MULTILINE)
    #pprint.pprint(m)
    # Make sure sections appear in the right order
    # (in case rst.ref_and_label_commoncode has to assign numbers
    # to section titles that are identical)
    section_label2title = OrderedDict()
    for dummy1, title, dummy2, label in m:
        section_label2title[label] = title.strip()
        if 'ref{' in title and format in ('rst', 'sphinx', 'html'):
            print '*** warning: reference in title\n  %s\nwill come out wrong in format %s' % (title, format)
    #pprint.pprint(section_label2title)


    # 2. Make table of contents
    # TOC: on|off
    #section_pattern = r'^\s*(_{3,9}|={3,9})(.+?)(_{3,9}|={3,9})'
    section_pattern = r'^\s*(_{3,9}|={3,9})(.+?)(_{3,9}|={3,9})(\s*label\{(.+?)\})?'
    m = re.findall(section_pattern, filestr, flags=re.MULTILINE)
    sections = []
    heading2section_type = {9: 0, 7: 1, 5: 2, 3: 3}
    for heading, title, dummy2, dummy3, label in m:
        if len(heading) % 2 == 0:
            print '*** error: headings must have 3, 5, 7, or 9 = signs,'
            print '    not %d as in %s %s' % (len(heading), heading, title)
            _abort()
        if label == '':
            label = None
        sections.append((title, heading2section_type[len(heading)], label))
    #print 'sections:'
    #import pprint; pprint.pprint(sections)

    toc = TOC[format](sections)  # Always call TOC[format] to make a toc
    # See if the toc string is to be inserted in filestr
    pattern = re.compile(r'^TOC:\s*(on|off).*$', re.MULTILINE)
    m = pattern.search(filestr)
    if m:
        value = m.group(1)
        if value == 'on':
            toc_fixed = toc.replace('\\', '\\\\') # re.sub swallows backslashes
            filestr = pattern.sub('\n%s\n\n' % toc_fixed, filestr)
        else:
            filestr = pattern.sub('', filestr)

    # 3. Handle references that can be internal or external
    #    ref[internal][cite][external-HTML]
    internal_labels = re.findall(r'label\{(.+?)\}', filestr)
    ref_pattern = r'ref(ch)?\[([^\]]*?)\]\[([^\]]*?)\]\[([^\]]*?)\]'
    general_refs = re.findall(ref_pattern, filestr)
    for chapref, internal, cite, external in general_refs:
        ref_text = 'ref%s[%s][%s][%s]' % (chapref, internal, cite, external)
        if not internal and not external:
            print '*** error:', ref_text, 'has empty fields'
            _abort()
        ref2labels = re.findall(r'ref\{(.+?)\}', internal)
        refs_to_this_doc = [label for label in ref2labels
                            if label in internal_labels]
        if len(refs_to_this_doc) == len(ref2labels):
            # All refs to labels in this doc
            filestr = filestr.replace(ref_text, internal)
        elif format in ('latex', 'pdflatex'):
            if cite:
                replacement = cite if chapref else internal + cite
            filestr = filestr.replace(ref_text, replacement)
        else:
            filestr = filestr.replace(ref_text, external)

    # 4. Perform format-specific editing of ref{...} and label{...}
    filestr = CROSS_REFS[format](section_label2title, format, filestr)

    return filestr


def handle_index_and_bib(filestr, format, has_title):
    """Process idx{...} and cite{...} instructions."""
    if not format in ('latex', 'pdflatex'):
        # Make cite[]{} to cite{} (...)
        def cite_subst(m):
            detailed_ref = m.group(1)
            citekey = m.group(2)
            if not detailed_ref:
                print '*** error: empty text inside parenthesis: %s' % m.group(0)
                _abort()
            return 'cite{%s} (%s)' % (citekey, detailed_ref)

        filestr = re.sub(r'cite\[(.+?)\]\{(.+?)\}', cite_subst, filestr)
    # else: latex can work with cite[]{}

    pubfile = None
    pubdata = None
    index = {}  # index[word] = lineno
    citations = OrderedDict()  # citations[label] = no_in_list (1,2,3,...)
    line_counter = 0
    cite_counter = 0
    for line in filestr.splitlines():
        line_counter += 1
        line = line.strip()
        if line.startswith('BIBFILE:'):
            pubfile = line.split()
            if len(pubfile) == 1:
                print line
                print '*** error: missing name of publish database'
                _abort()
            else:
                pubfile = pubfile[1]
            if not pubfile.endswith('.pub'):
                print line
                print '*** error: illegal publish database', pubfile, \
                      '(must have .pub extension)'
                _abort()
            if not os.path.isfile(pubfile):
                print '*** error: cannot find publish database', pubfile
                _abort()
            import publish
            # Note: we have to operate publish in the directory
            # where pubfile resides
            directory, basename = os.path.split(pubfile)
            if not directory:
                directory = os.curdir
            this_dir = os.getcwd()
            os.chdir(directory)

            pubdata = publish.database.read_database(basename)

            os.chdir(this_dir)
        else:
            index_words = re.findall(r'idx\{(.+?)\}', line)
            if index_words:
                for word in index_words:
                    if word in index:
                        index[word].append(line_counter)
                    else:
                        index[word] = [line_counter]
                # note: line numbers in the .do.txt file are of very limited
                # value for the end format file...anyway, we make them...

            cite_args = re.findall(r'cite\{(.+?)\}', line)
            if format in ('latex', 'pdflatex'):
                # latex keeps cite[]{} (other formats rewrites to cite{} ([]))
                cite_args += re.findall(r'cite\[.+?\]\{(.+?)\}', line)
            if cite_args:
                # multiple labels can be separated by comma:
                cite_labels = []
                for arg in cite_args:
                    for c in arg.split(','):
                        cite_labels.append(c.strip())
                for label in cite_labels:
                    if not label in citations:
                        cite_counter += 1  # new citation label
                        citations[label] = cite_counter
                # Replace cite{label1,label2,...} by individual cite{label1}
                # cite{label2}, etc. if not latex or pandoc format
                if format != 'latex' and format != 'pdflatex' and \
                       format != 'pandoc':
                    for arg in cite_args:
                        replacement = ' '.join(['cite{%s}' % label.strip() \
                                                 for label in arg.split(',')])
                        filestr = filestr.replace('cite{%s}' % arg,
                                                  replacement)
                elif format == 'pandoc':
                    # prefix labels with @ and substitute , by ;
                    for arg in cite_args:
                        replacement = ';'.join(
                            ['@' + label for label in arg.split(',')])
                        filestr = filestr.replace('cite{%s}' % arg,
                                                  replacement)

    if len(citations) > 0 and OrderedDict is dict:
        # version < 2.7 warning
        print '*** warning: citations may appear in random order unless you upgrade to Python version 2.7 or 3.1 or later'
    if len(citations) > 0 and 'BIBFILE:' not in filestr:
        print '*** warning: you have citations but no bibliography (BIBFILE: ...)'
        #_abort()
    if 'BIBFILE:' in filestr and len(citations) > 0 and \
           which('publish') is None:
        print '*** error: you have citations and specified a BIBFILE, but'
        print '    publish (needed to treat the BIBFILE) is not installed.'
        print '    Download publish from https://bitbucket.org/logg/publish,'
        print '    do cd publish; sudo python setup.py install'
        _abort()
    # Check that citations are correct
    if pubdata:
        pubdata_keys = [item['key'] for item in pubdata]
        for citation in citations:
            if not citation in pubdata_keys:
                print '*** error: citation "%s" is not in the BIBFILE' % citation
                _abort()

    filestr = INDEX_BIB[format](filestr, index, citations, pubfile, pubdata)

    if not citations and pubfile is not None:
        # No need for references, remove the section before BIBFILE
        filestr = re.sub(r'={5,9} .+? ={5,9}\s+^BIBFILE:.+', '',
                         filestr, flags=re.MULTILINE)
        # In case we have no heading and just BIBFILE
        filestr = re.sub(r'^BIBFILE:.+', '', filestr, flags=re.MULTILINE)
        return filestr

    return filestr

def interpret_authors(filestr, format):
    debugpr('\n*** Dealing with authors and institutions ***')
    # first deal with AUTHOR as there can be several such lines
    author_lines = re.findall(r'^AUTHOR:\s*(?P<author>.+)\s*$', filestr,
                              re.MULTILINE)
    #filestr = re.sub(r'^AUTHOR:.+$', 'XXXAUTHOR', filestr, flags=re.MULTILINE)
    cpattern = re.compile(r'^AUTHOR:.+$', re.MULTILINE)
    filestr = cpattern.sub('XXXAUTHOR', filestr)  # v2.6 way of doing it
    # contract multiple AUTHOR lines to one single:
    filestr = re.sub('(XXXAUTHOR\n)+', 'XXXAUTHOR', filestr)

    # (author, (inst1, inst2, ...) or (author, None)
    authors_and_institutions = []
    for line in author_lines:
        if ' at ' in line:
            # author and institution(s) given
            try:
                a, i = line.split(' at ')
            except ValueError:
                print 'Wrong syntax of author(s) and institution(s): too many "at":\n', line, '\nauthor at inst1, adr1 and inst2, adr2a, adr2b and inst3, adr3'
                _abort()
            a = a.strip()
            if ' & ' in i:
                i = [w.strip() for w in i.split(' & ')]
            #elif ' and ' in i:
            #    i = [w.strip() for w in i.split(' and ')]
            else:
                i = (i.strip(),)
        else:  # just author's name
            a = line.strip()
            i = None
        if 'mail:' in a:  # email?
            a, e = re.split(r'[Ee]?mail:\s*', a)
            a = a.strip()
            e = e.strip()
            if not '@' in e:
                print 'Syntax error: wrong email specification in AUTHOR line: "%s" (no @)' % e
        else:
            e = None
        authors_and_institutions.append((a, i, e))

    inst2index = OrderedDict()
    index2inst = {}
    auth2index = OrderedDict()
    auth2email = OrderedDict()
    # get unique institutions:
    for a, institutions, e in authors_and_institutions:
        if institutions is not None:
            for i in institutions:
                inst2index[i] = None
    for index, i in enumerate(inst2index):
        inst2index[i] = index+1
        index2inst[index+1] = i
    for a, institutions, e in authors_and_institutions:
        if institutions is not None:
            auth2index[a] = [inst2index[i] for i in institutions]
        else:
            auth2index[a] = ''  # leads to empty address
        auth2email[a] = e

    # version < 2.7 warning:
    if len(auth2index) > 1 and OrderedDict is dict:
        print '*** warning: multiple authors\n - correct order of authors requires Python version 2.7 or 3.1 (or higher)'
    return authors_and_institutions, auth2index, inst2index, index2inst, auth2email, filestr

def typeset_authors(filestr, format):
    authors_and_institutions, auth2index, inst2index, \
        index2inst, auth2email, filestr = interpret_authors(filestr, format)
    author_block = INLINE_TAGS_SUBST[format]['author']\
        (authors_and_institutions, auth2index, inst2index,
         index2inst, auth2email).rstrip() + '\n'  # ensure one newline
    filestr = filestr.replace('XXXAUTHOR', author_block)
    return filestr


def inline_tag_subst(filestr, format):
    """Deal with all inline tags by substitution."""
    # Note that all tags are *substituted* so that the sequence of
    # operations are not important for the contents of the document - we
    # choose a sequence that is appropriate from a substitution point
    # of view

    filestr = typeset_authors(filestr, format)

    # deal with DATE: today (i.e., find today's date)
    m = re.search(r'^(DATE:\s*[Tt]oday)', filestr, re.MULTILINE)
    if m:
        origstr = m.group(1)
        w = time.asctime().split()
        date = w[1] + ' ' + w[2] + ', ' + w[4]
        filestr = filestr.replace(origstr, 'DATE: ' + date)

    debugpr('\n*** Inline tags substitution phase ***')

    # Do tags that require almost format-independent treatment such
    # that everything is conveniently defined here
    # 1. Quotes around normal text in LaTeX style:
    pattern = "``([A-Za-z][A-Za-z0-9\s,.;?!/:'() -]*?)''"
    if format not in ('pdflatex', 'latex'):
        filestr = re.sub(pattern, '"\g<1>"', filestr)

    # Treat tags that have format-dependent typesetting

    ordered_tags = (
        'title',
        'date',
        'movie',
        #'figure',  # done separately
        'abstract',  # must become before sections since it tests on ===
        'emphasize', 'math2', 'math',
        # important to do section, subsection, etc. before paragraph and bold:
        'chapter', 'section', 'subsection', 'subsubsection',
        'bold',
        'inlinecomment',
        'colortext',
        'verbatim',
        'paragraph',  # after bold and emphasize
        'plainURL',   # must come before linkURL2 to avoid "URL" as link name
        'linkURL2v',
        'linkURL3v',
        'linkURL2',
        'linkURL3',
        'linkURL',
        'linebreak',
        )
    for tag in ordered_tags:
        debugpr('\n*************** Working with tag "%s"' % tag)
        tag_pattern = INLINE_TAGS[tag]
        #print 'working with tag "%s" = "%s"' % (tag, tag_pattern)
        if tag in ('abstract', 'inlinecomment'):
            c = re.compile(tag_pattern, re.MULTILINE|re.DOTALL)
        else:
            c = re.compile(tag_pattern, re.MULTILINE)
        try:
            replacement = INLINE_TAGS_SUBST[format][tag]
        except KeyError:
            continue  # just ignore missing tags in current format
        if replacement is None:
            continue  # no substitution

        findlist = c.findall(filestr)
        occurences = len(findlist)
        findlist = pprint.pformat(findlist)

        # first some info for debug output:
        if occurences > 0:
            debugpr('Found %d occurences of "%s":\nfindall list: %s' % (occurences, tag, findlist))
            debugpr('%s is to be replaced using %s' % (tag, replacement))
            m = c.search(filestr)
            if m:
                debugpr('First occurence: "%s"\ngroups: %s\nnamed groups: %s' % (m.group(0), m.groups(), m.groupdict()))

        if isinstance(replacement, basestring):
            filestr = c.sub(replacement, filestr)
        elif callable(replacement):
            filestr = c.sub(replacement, filestr)
        elif False:
            # treat line by line because replacement string depends
            # on the match object for each occurence
            # (this is mainly for headlines in rst format)
            lines = filestr.splitlines()
            occurences = 0
            for i in range(len(lines)):
                m = re.search(tag_pattern, lines[i])
                if m:
                    try:
                        replacement_str = replacement(m)
                    except Exception, e:
                        print 'Problem at line\n   ', lines[i], \
                              '\nException:\n', e
                        print 'occured while replacing inline tag "%s" (%s) with aid of function %s' % (tag, tag_pattern, replacement.__name__)
                        #raise Exception(e)
                        # Raising exception is misleading since the
                        # error occured in the replacement function
                        _abort()
                    lines[i] = re.sub(tag_pattern, replacement_str, lines[i])
                    occurences += 1
            filestr = '\n'.join(lines)

        else:
            raise ValueError, 'replacement is of type %s' % type(replacement)
        if occurences > 0:
            debugpr('\n**** The file after %d "%s" substitutions ***\n%s\n%s\n\n' % (occurences, tag, filestr, '-'*80))
    return filestr

def subst_away_inline_comments(filestr):
    # inline comments: [hpl: this is a comment]
    pattern = r'\[(?P<name>[A-Za-z0-9_ ,.@]+?): +(?P<comment>[^\]]*?)\]\s*'
    filestr = re.sub(pattern, '', filestr)
    return filestr

def subst_class_func_mod(filestr, format):
    if format == 'sphinx' or format == 'rst':
        return filestr

    # Replace :mod:`~my.pack.mod` by `my.pack.mod`
    tp = 'class', 'func', 'mod'
    for t in tp:
        filestr = re.sub(r':%s:`~?([A-Za-z0-9_.]+?)`' % t,
                         r'`\g<1>`', filestr)
    return filestr


def file2file(in_filename, format, basename):
    """
    Perform the transformation of a doconce file, stored in in_filename,
    to a given format (html, latex, etc.), written to out_filename (returned).
    This is the principal function in the module.
    """
    if in_filename.startswith('__'):
        print 'translating preprocessed doconce text in', in_filename, \
              'to', format
    else:
        print 'translating doconce text in', in_filename, 'to', format

    if format == 'html':
        html_output = option('html_output=', '')
        if html_output:
            basename = html_output
        # Initial the doc's file collection
        html.add_to_file_collection(basename + '.html',
                                    basename, mode='w')

    # if trouble with encoding:
    # Unix> doconce guess_encoding myfile.do.txt
    # Unix> doconce change_encoding latin1 utf-8 myfile.do.txt
    # or plain Unix:
    # Unix> file myfile.do.txt
    # myfile.do.txt: UTF-8 Unicode English text
    # Unix> # convert to latin-1:
    # Unix> iconv -f utf-8 -t LATIN1 myfile.do.txt --output newfile
    if encoding:  # global variable
        print 'open file with encoding', encoding
        f = codecs.open(in_filename, 'r', encoding)
    else:
        f = open(in_filename, 'r')
    filestr = f.read()
    f.close()

    if in_filename.endswith('.py') or in_filename.endswith('.py.do.txt'):
        filestr = doconce2format4docstrings(filestr, format)
    else:
        filestr = doconce2format(filestr, format)

    out_filename = basename + FILENAME_EXTENSION[format]

    if encoding:
        f = codecs.open(out_filename, 'w', encoding)
    else:
        f = open(out_filename, 'w')

    def error_message():
        m = str(e)
        if "codec can't encode character" in m:
            pos = m.split('position')[1].split(':')[0]
            print '*** error: problem with character when writing to file:'
            print '(text position %s)' % pos
            try:
                pos = int(pos)
            except:
                if '-' in pos:
                    pos = pos.split('-')[0]
                    pos = int(pos)
            print repr(filestr[pos-40:pos+40])
            print ' '*42 + '^'
            print '    remedies: fix character or try --encoding=utf-8'
            _abort()

    try:
        f.write(filestr)
    except UnicodeEncodeError, e:
        # Provide error message and abortion, because the code
        # below that tries UTF-8 will result in strange characters
        # in the output. It is better that the user specifies
        # correct encoding and gets correct results.
        error_message()
        # Try UTF-8 (not a good fallback as the output may be corrupt)
        """
        try:
            f.close()
            f = codecs.open(out_filename, 'w', encoding='utf-8')
            f.write(filestr)
        except UnicodeEncodeError, e:
            # Cannot write ASCII or UTF-8 - giving up...
            # (could have tested latin1 on older systems)
            error_message()
        """

    f.close()
    return out_filename


def doconce2format4docstrings(filestr, format):
    """Run doconce2format on all doc strings in a Python file."""

    c1 = re.compile(r'^\s*(class|def)\s+[A-Za-z0-9_,() =]+:\s+(""".+?""")',
                    re.DOTALL|re.MULTILINE)
    c2 = re.compile(r"^\s*(class|def)\s+[A-Za-z0-9_,() =]+:\s+('''.+?''')",
                    re.DOTALL|re.MULTILINE)
    doc_strings = [doc_string for dummy, doc_string in c1.findall(filestr)] + \
                  [doc_string for dummy, doc_string in c2.findall(filestr)]
    lines = filestr.splitlines()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith('#'):
            break
    filestr2 = '\n'.join(lines[i:])
    c3 = re.compile(r'^\s*""".+?"""', re.DOTALL) # ^ is the very start
    c4 = re.compile(r"^\s*'''.+?'''", re.DOTALL) # ^ is the very start
    doc_strings = c3.findall(filestr2) + c4.findall(filestr2) + doc_strings

    # Find and remove indentation
    all = []
    for doc_string in doc_strings:
        lines = doc_string.splitlines()
        if len(lines) > 1:
            indent = 0
            line1 = lines[1]
            while line1[indent] == ' ':
                indent += 1
            for i in range(1, len(lines)):
                lines[i] = lines[i][indent:]
            all.append(('\n'.join(lines), indent))
        else:
            all.append((doc_string, None))

    for doc_string, indent in all:
        new_doc_string = doconce2format(doc_string, format)
        if indent is not None:
            lines = new_doc_string.splitlines()
            for i in range(1, len(lines)):
                lines[i] = ' '*indent + lines[i]
            new_doc_string = '\n'.join(lines)
            lines = doc_string.splitlines()
            for i in range(1, len(lines)):
                if lines[i].isspace() or lines[i] == '':
                    pass  # don't indent blank lines
                else:
                    lines[i] = ' '*indent + lines[i]
            doc_string = '\n'.join(lines)

        filestr = filestr.replace(doc_string, new_doc_string)

    return filestr

def doconce2format(filestr, format):
    filestr = fix(filestr, format, verbose=1)
    syntax_check(filestr, format)

    global FILENAME_EXTENSION, BLANKLINE, INLINE_TAGS_SUBST, CODE, \
           LIST, ARGLIST,TABLE, EXERCISE, FIGURE_EXT, CROSS_REFS, INDEX_BIB, \
           TOC, ENVIRS, INTRO, OUTRO

    for module in html, latex, pdflatex, rst, sphinx, st, epytext, plaintext, gwiki, mwiki, cwiki, pandoc, ipynb:
        #print 'calling define function in', module.__name__
        module.define(FILENAME_EXTENSION,
                      BLANKLINE,
                      INLINE_TAGS_SUBST,
                      CODE,
                      LIST,
                      ARGLIST,
                      TABLE,
                      EXERCISE,
                      FIGURE_EXT,
                      CROSS_REFS,
                      INDEX_BIB,
                      TOC,
                      ENVIRS,
                      INTRO,
                      OUTRO,
                      filestr)

    # -----------------------------------------------------------------

    # Step: check if ^?TITLE: is present, and if so, header and footer
    # are to be included (later below):
    if re.search(r'^TITLE:', filestr, re.MULTILINE):
        has_title = True
    else:
        has_title = False

    # Next step: run operating system commands and insert output
    filestr = insert_os_commands(filestr, format)
    debugpr('The file after running @@@OSCMD (from file):', filestr)

    # Next step: insert verbatim code from other (source code) files:
    # (if the format is latex, we could let ptex2tex do this, but
    # the CODE start@stop specifications may contain uderscores and
    # asterix, which will be replaced later and hence destroyed)
    #if format != 'latex':
    filestr = insert_code_from_file(filestr, format)
    debugpr('The file after inserting @@@CODE (from file):', filestr)

    # Hack to fix a bug with !ec/!et at the end of files, which is not
    # correctly substituted by '' in rst, sphinx, st, epytext, plain, wikis
    # (the fix is to add "enough" blank lines - the reason can be
    # an effective strip of filestr, e.g., through '\n'.join(lines))
    if format in ('rst', 'sphinx', 'st', 'epytext', 'plain',
                  'mwiki', 'cwiki', 'gwiki'):
        filestr = filestr.rstrip()
        if filestr.endswith('!ec') or filestr.endswith('!et'):
            filestr += '\n'*10

    # Next step: change \bm{} to \boldsymbol{} for all MathJax-based formats
    # (must be done before math blocks are removed and again after
    # newcommands files are inserted)
    filestr = bm2boldsymbol(filestr, format)

    # Hack for transforming align envirs to separate equations
    if format in ("sphinx", "pandoc", "ipynb"):
        filestr = align2equations(filestr, format)
        debugpr('The file after {align} envirs are rewritten as separate equations:', filestr)

    # Next step: remove all verbatim and math blocks

    filestr, code_blocks, code_block_types, tex_blocks = \
             remove_code_and_tex(filestr)

    debugpr('The file after removal of code/tex blocks:', filestr)
    debugpr('The code blocks:', pprint.pformat(code_blocks))
    debugpr('The code block types:', pprint.pformat(code_block_types))
    debugpr('The tex blocks:', pprint.pformat(tex_blocks))

    # Check URLs to see if they are valid
    if option('urlcheck'):
        urlcheck(filestr)

    # Lift sections up or down?
    s2name = {9: 'chapter', 7: 'section',
              5: 'subsection', 3: 'subsubsection'}
    section_level_changed = False
    if option('sections_up'):
        for s in 7, 5, 3:
            header_old = '='*s
            header_new = '='*(s+2)
            print 'transforming sections: %s to %s...' % (s2name[s], s2name[s+2])
            pattern = r'%s(.+?)%s' % (header_old, header_old)
            replacement = r'%s\g<1>%s' % (header_new, header_new)
            filestr = re.sub(pattern, replacement, filestr)
        section_level_changed = True
    if option('sections_down'):
        for s in 5, 7, 9:
            header_old = '='*s
            header_new = '='*(s-2)
            print 'transforming sections: %s to %s...' % (s2name[s], s2name[s-2])
            pattern = r'%s(.+?)%s' % (header_old, header_old)
            replacement = r'%s\g<1>%s' % (header_new, header_new)
            filestr = re.sub(pattern, replacement, filestr)
        section_level_changed = True

    if section_level_changed:
        # Fix Exercise, Problem, Project, Example - they must be 5=
        filestr = re.sub(r'^\s*=======\s*(\{?(Exercise|Problem|Project|Example)\}?):\s*([^ =-].+?)\s*=======', '===== \g<1>: \g<3> =====', filestr, flags=re.MULTILINE)
        filestr = re.sub(r'^\s*===\s*(\{?(Exercise|Problem|Project|Example)\}?):\s*([^ =-].+?)\s*===', '===== \g<1>: \g<3> =====', filestr, flags=re.MULTILINE)

    # Remove linebreaks within paragraphs
    if option('oneline_paragraphs'):  # (does not yet work well)
        filestr = make_one_line_paragraphs(filestr, format)

    # Remove inline comments
    if option('skip_inline_comments'):
        filestr = subst_away_inline_comments(filestr)
    else:
        # Number inline comments
        inline_comments = re.findall(INLINE_TAGS['inlinecomment'], filestr,
                                     flags=re.DOTALL|re.MULTILINE)
        counter = 1
        for name, space, comment in inline_comments:
            filestr = filestr.replace(
                '[%s:%s%s]' % (name, space, comment),
                '[%s %d: %s]' % (name, counter, comment))
            counter += 1


    # Remove comments starting with ##
    pattern = r'^##.+$\n'
    filestr = re.sub(pattern, '', filestr, flags=re.MULTILINE)

    # Fix stand-alone http(s) URLs (after verbatim blocks are removed,
    # but before figure handling and inline_tag_subst)
    pattern = r' (https?://.+?)([ ,?:;!)\n])'
    filestr = re.sub(pattern, ' URL: "\g<1>"\g<2>', filestr)

    # Next step: deal with exercises
    filestr = exercises(filestr, format, code_blocks, tex_blocks)

    # Next step: deal with figures
    filestr = handle_figures(filestr, format)

    # Next step: deal with cross referencing (must occur before other format subst)
    filestr = handle_cross_referencing(filestr, format)

    debugpr('The file after handling ref and label cross referencing:', filestr)
    # Next step: deal with index and bibliography (must be done before lists):
    filestr = handle_index_and_bib(filestr, format, has_title)

    debugpr('The file after handling index and bibliography:', filestr)


    # Next step: deal with lists
    filestr = typeset_lists(filestr, format,
                            debug_info=[code_blocks, tex_blocks])
    debugpr('The file after typesetting of lists:', filestr)

    # Next step: add space around | in tables for substitutions to get right
    filestr = space_in_tables(filestr)
    debugpr('The file after adding space around | in tables:', filestr)

    # Next step: do substitutions
    filestr = inline_tag_subst(filestr, format)
    debugpr('The file after all inline substitutions:', filestr)

    # Next step: deal with tables
    filestr = typeset_tables(filestr, format)
    debugpr('The file after typesetting of tables:', filestr)

    # Next step: deal with various commands and envirs to be put as comments
    commands = ['!split', '!bpop', '!epop', '!bslidecell', '!eslidecell',
                '!bnotes', '!enotes',]
    for command in commands:
        comment_action = INLINE_TAGS_SUBST[format].get('comment', '# %s')
        if isinstance(comment_action, str):
            split_comment = comment_action % (command + r'\g<1>')
        elif callable(comment_action):
            split_comment = comment_action((command + r'\g<1>'))
        cpattern = re.compile('^%s( *| +.*)$' % command, re.MULTILINE)
        filestr = cpattern.sub(split_comment, filestr)
    debugpr('The file after commenting out %s:' % ', '.join(commands), filestr)


    # Next step: substitute latex-style newcommands in filestr and tex_blocks
    # (not in code_blocks)
    from expand_newcommands import expand_newcommands
    if format not in ('latex', 'pdflatex'):  # replace for 'pandoc', 'html'
        newcommand_files = glob.glob('newcommands*_replace.tex')
        if format == 'sphinx':  # replace all newcommands in sphinx
            newcommand_files = [name for name in glob.glob('newcommands*.tex')
                                if not name.endswith('.p.tex')]
            # note: could use substitutions (|newcommand|) in rst/sphinx,
            # but they don't allow arguments so expansion of \newcommand
            # is probably a better solution
        filestr = expand_newcommands(newcommand_files, filestr)
        for i in range(len(tex_blocks)):
            tex_blocks[i] = expand_newcommands(newcommand_files, tex_blocks[i])

    # Next step: subst :class:`ClassName` by `ClassName` for
    # non-rst/sphinx formats:
    filestr = subst_class_func_mod(filestr, format)

    # Next step: add header and footer, but first wrap main body
    # of text inside some recognizable delimiters such that we
    # can distinguish it later from header and footer (especially
    # if there is no title and header/footer is not added, but
    # the final fixes in CODE[format] adds another header/footer, e.g.,
    # puts the main body inside a user-given HTML template or LaTeX template).
    if format in ('latex', 'pdflatex', 'html'):
        comment_pattern = INLINE_TAGS_SUBST[format]['comment']
        delimiter = main_content_begin
        delimiter = '\n' + comment_pattern % delimiter + '\n'  # wrap as comment
        filestr = delimiter + '\n' + filestr
        delimiter = main_content_end
        delimiter = comment_pattern % delimiter + '\n'  # wrap as comment
        filestr = filestr + '\n' + delimiter
    if has_title and not option('no_header_footer') and \
           option('html_template=', default='') == '':
        if format in INTRO:
            filestr = INTRO[format] + filestr
        if format in OUTRO:
            filestr = filestr + OUTRO[format]


    # Next step: insert verbatim and math code blocks again and
    # substitute code and tex environments:
    # (this is the place to do package-specific fixes too!)
    filestr = CODE[format](filestr, code_blocks, code_block_types,
                           tex_blocks, format)
    filestr += '\n'

    debugpr('The file after inserting intro/outro and tex/code blocks, and fixing last format-specific issues:', filestr)

    # Next step: deal with !b... !e... environments
    # (done after code and text to ensure correct indentation
    # in the formats that applies indentation)
    filestr = typeset_envirs(filestr, format)

    debugpr('The file after typesetting of admons and the rest of the !b/!e environments:', filestr)

    # Next step: remove exercise solution/answers, notes, etc
    # (Note: must be done after code and tex blocks are inserted!
    # Otherwise there is a mismatch between all original blocks
    # and those present after solutions, answers, etc. are removed)
    envir2option = dict(sol='solutions', ans='answers', hint='hints')
    # Recall that the comment syntax is now dependent on the format
    comment_pattern = INLINE_TAGS_SUBST[format].get('comment', '# %s')
    for envir in 'sol', 'ans', 'hint':
        option_name = 'without_' + envir2option[envir]
        if option(option_name):
            pattern = comment_pattern % envir_delimiter_lines[envir][0] + \
                      '\n.+?' + comment_pattern % \
                      envir_delimiter_lines[envir][1] + '\n'
            replacement = comment_pattern % ('removed !b%s ... !e%s environment\n' % (envir, envir)) + comment_pattern % ('(because of the command-line option --%s)\n' % option_name)
            filestr = re.sub(pattern, replacement, filestr, flags=re.DOTALL)


    debugpr('The file after removal of solutions, answers, notes, hints, etc.:', filestr)

    # Check if we have wrong-spelled environments
    if not option('examples_as_exercises'):
        pattern = r'^(![be].+)'
        m = re.search(pattern, filestr, flags=re.MULTILINE)
        if m:
            # Found, but can be inside code block (should have |[be].+ then)
            # and hence not necessarily an error
            print '*** error: could not translate environment: %s' % m.group(1)
            print '    context:\n'
            print filestr[m.start()-50:m.end()+50]
            print '    possible reasons:'
            print '     * syntax error in environment name'
            print '     * environment inside code: use | instead of !'
            print '     * or bug in doconce'
            _abort()


    # Next step: change \bm{} to \boldsymbol{} for all MathJax-based formats
    # (must be done before math blocks are removed and again after
    # newcommands files are inserted)
    filestr = bm2boldsymbol(filestr, format)

    # Final step: replace environments starting with | (instead of !)
    # by ! (for illustration of doconce syntax inside !bc/!ec directives).
    # Enough to consider |bc, |ec, |bt, and |et since all other environments
    # are processed when code and tex blocks are removed from the document.
    for envir in doconce_envirs():
        filestr = filestr.replace('|b' + envir, '!b' + envir)
        filestr = filestr.replace('|e' + envir, '!e' + envir)

    debugpr('The file after replacing |bc and |bt environments by true !bt and !et (in code blocks):', filestr)

    return filestr


def preprocess(filename, format, preprocessor_options=[]):
    """
    Run the preprocess and mako programs on filename and return the name
    of the resulting file. The preprocessor_options list contains
    the preprocessor options given on the command line.
    In addition, the preprocessor option FORMAT (=format) is
    always defined.
    """
    orig_filename = filename

    device = None
    # Is DEVICE set as command-line option?
    for arg in sys.argv[1:]:
        if arg.startswith('-DDEVICE='):
            device = arg.split('-DDEVICE=')[1]
        elif arg.startswith('DEVICE='):
            device = arg.split('DEVICE=')[1]
    if device is None:
        device = 'paper' if option('device=', '') == 'paper' else 'screen'

    f = open(filename, 'r'); filestr = f.read(); f.close()
    if filestr.strip() == '':
        print '*** error: empty file', filename
        _abort()

    preprocessor = None

    # First guess if preprocess or mako is used

    # Collect first -Dvar=value options on the command line
    preprocess_options = [opt for opt in preprocessor_options
                          if opt[:2] == '-D']
    # Add -D to mako name=value options so that such variables
    # are set for preprocess too (but enclose value in quotes)
    for opt in preprocessor_options:
        if opt[0] != '-' and '=' in opt:
            var, value = opt.split('=')
            preprocess_options.append('-D%s="%s"' % (var, value))

    # Look for mako variables
    mako_kwargs = {'FORMAT': format, 'DEVICE': device}
    for opt in preprocessor_options:
        if opt.startswith('-D'):
            opt2 = opt[2:]
            if '=' in opt:
                key, value = opt2.split('=')
            else:
                key = opt2;  value = opt.startswith('-D')
        elif not opt.startswith('--'):
            try:
                key, value = opt.split('=')
            except ValueError:
                print 'command line argument "%s" not recognized' % opt
                _abort()
        else:
            key = None

        if key is not None:
            # Try eval(value), if it fails, assume string or bool
            try:
                mako_kwargs[key] = eval(value)
            except (NameError, TypeError, SyntaxError):
                mako_kwargs[key] = value

    resultfile = 'tmp_preprocess__' + filename
    resultfile2 = 'tmp_mako__' + filename

    filestr_without_code, code_blocks, code_block_types, tex_blocks = \
                          remove_code_and_tex(filestr)

    preprocess_commands = r'^#\s*#(if|define|include)'
    if re.search(preprocess_commands, filestr_without_code, re.MULTILINE):
        debugpr('Found use of %d preprocess directives # #if|define|include in file %s' % (len(re.findall(preprocess_commands, filestr_without_code, flags=re.MULTILINE)), filename))

        #print 'run preprocess on', filename, 'to make', resultfile
        preprocessor = 'preprocess'
        preprocess_options = ' '.join(preprocess_options)

        # Syntax check: preprocess directives without leading #?
        pattern1 = r'^#if.*'; pattern2 = r'^#else'
        pattern3 = r'^#elif'; pattern4 = r'^#endif'
        for pattern in pattern1, pattern2, pattern3, pattern4:
            cpattern = re.compile(pattern, re.MULTILINE)
            matches = cpattern.findall(filestr)
            if matches:
                print '\nSyntax error in preprocess directives: missing # '\
                      'before directive'
                print pattern
                _abort()
        try:
            import preprocess
        except ImportError:
            print """\
%s makes use of preprocess directives and therefore requires
the preprocess program to be installed (see code.google.com/p/preprocess).
On Debian systems, preprocess can be installed through the
preprocess package (sudo apt-get install preprocess).
""" % filename
            _abort()

        if option('no_preprocess'):
            print 'Found preprocess-like statements, but --no_preprocess prevents running preprocess'
            shutil.copy(filename, resultfile)  # just copy
        else:
            cmd = 'preprocess -DFORMAT=%s -DDEVICE=%s %s %s > %s' % \
                  (format, device, preprocess_options, filename, resultfile)
            print 'running', cmd
            failure, outtext = commands.getstatusoutput(cmd)
            if failure:
                print 'Could not run preprocessor:\n%s' % cmd
                print outtext
                _abort()
            # Make filestr the result of preprocess in case mako shall be run
            f = open(resultfile, 'r'); filestr = f.read(); f.close()
            filestr_without_code, code_blocks, code_block_types, tex_blocks = \
                                  remove_code_and_tex(filestr)


    mako_commands = r'^ *<?%[^%]'
    # Problem: mako_commands match Matlab comments and SWIG directives,
    # so we need to remove code blocks for testing if we really use
    # mako. Also issue warnings if code blocks contain mako instructions
    # matching the mako_commands pattern
    match_percentage = re.search(mako_commands, filestr_without_code,
                                 re.MULTILINE)  # match %
    if match_percentage:
        debugpr('Found use of %% sign(s) for mako code in %s:\n%s' % (resultfile, ', '.join(re.findall(mako_commands, filestr_without_code))))

    match_mako_variable = False
    for name in mako_kwargs:
        pattern = r'\$\{%s\}' % name  # ${name}
        if re.search(pattern, filestr_without_code):
            match_mako_variable = True
            debugpr('Found use of mako variable(s) in %s: %s' % (resultfile, ', '.join(re.findall(pattern, filestr_without_code))))
            break
        pattern = r'\b%s\b' % name    # e.g. % if name == 'a' (or Python code)
        if re.search(pattern, filestr_without_code):
            match_mako_variable = True
            debugpr('Found use mako variable(s) in mako code in %s: %s' % (resultfile, ', '.join(re.findall(pattern, filestr_without_code))))
            break

    if (match_percentage or match_mako_variable) and option('no_mako'):
        # Found mako-like statements, but --no_mako is forced, give a message
        print '*** warning: mako is not run because of the option --no-mako'

    if (not option('no_mako')) and (match_percentage or match_mako_variable):
        # Found use of mako

        # Check if there is SWIG or Matlab code that can fool mako with a %
        mako_problems = False
        for code_block in code_blocks:
            m = re.search(mako_commands, code_block, re.MULTILINE)
            if m:
                print '\n\n*** warning: detected problem with the code block\n---------------------------'
                print code_block
                print '''---------------------------
The above code block contains "%s" on the beginning of a line.
Such lines cause problems for the mako preprocessor
since it thinks this is a mako statement.
''' % (m.group(0))
                print
                mako_problems = True
        if mako_problems:
            print '''\
Use %% in the code block(s) above to fix the problem with % at the
beginning of lines, or put the code in a file that is included
with @@@CODE filename, or drop mako instructions or variables and
rely on preprocess only in the preprocessing step.
Including --no_mako on the command line avoids running mako.
If you have % in code, see if it is possible to move the % char
away from the beginning of the line.
'''
            print 'mako is not run because of lines starting with %,'
            print 'fix the lines as described or remove all mako statements.'
            _abort()
            return filename if preprocessor is None else resultfile

        # Check if LaTeX math has ${...} constructions that cause problems
        # for mako
        inline_math = re.findall(INLINE_TAGS['math'], filestr_without_code)
        for groups in inline_math:
            formula = groups[2]
            suggestion = ''
            if formula[0] == '{':
                if formula[1] == '}':
                    suggestion = 'as $\,{}...$'
                if formula[1:7] == r'\cal O}':
                    suggestion = r'as \newcommand{\Oof}[1]{{\cal O}{#1}}'
                else:
                    suggestion = 'or make a newcommand'
                print """\
*** error: potential problem with formula $%s$'
    since ${ can confuse Mako - rewrite %s""" % (formula, suggestion)
                _abort()

        if preprocessor is not None:  # already found preprocess commands?
            # The output is in resultfile, mako is run on that
            filename = resultfile
        preprocessor = 'mako'

        try:
            import mako
        except ImportError:
            print """\
%s makes use of mako directives and therefore requires mako
to be installed (www.makotemplates.org).
On Debian systems, mako can easily be installed through the
python-mako package (sudo apt-get install python-mako).
""" % filename
            _abort()

        print 'running mako on', filename, 'to make', resultfile2
        # add a space after \\ at the end of lines (otherwise mako
        # eats one of the backslashes in tex blocks)
        # same for a single \ before newline
        f = open(filename, 'r')
        filestr = f.read()
        f.close()
        filestr = filestr.replace('\\\\\n', '\\\\ \n')
        filestr = filestr.replace('\\\n', '\\ \n')
        f = open(resultfile2, 'w')
        f.write(filestr)
        f.close()

        strict_undefined = True if option('mako_strict_undefined') else False
        from mako.template import Template
        from mako.lookup import TemplateLookup
        lookup = TemplateLookup(directories=[os.curdir])
        #temp = Template(filename=resultfile2, lookup=lookup,
        #                strict_undefined=strict_undefined)
        if encoding:
            filestr = unicode(filestr, encoding)
        try:
            temp = Template(text=filestr, lookup=lookup,
                            strict_undefined=strict_undefined)
        except Exception as e:
            print '*** mako error:', str(type(e)).split("'")[1]
            print '   ', e
            if "'ascii'" in str(e):
                print '    reason: doconce file contains non-ascii characters'
                print '    rerun with --encoding=utf-8 (or similar):'
                print '    doconce format %s %s %s --encoding=utf-8' \
                      % (format, orig_filename, ' '.join(sys.argv[1:]))
            _abort()

        debugpr('Keyword arguments to be sent to mako: %s' % \
                pprint.pformat(mako_kwargs))
        if preprocessor_options:
            print 'mako variables:', mako_kwargs

        try:
            filestr = temp.render(**mako_kwargs)
        except TypeError, e:
            if "'Undefined' object is not callable" in str(e):
                calls = '\n'.join(re.findall(r'(\$\{[A-Za-z0-9_ ]+?\()[^}]+?\}', filestr))
                print '*** mako error: ${func(...)} calls undefined function "func",\ncheck all ${...} calls in the file(s) for possible typos and lack of includes!\n%s' % calls
                _abort()
            else:
                # Just dump everything mako has
                print '*** mako error:'
                filestr = temp.render(**mako_kwargs)


        except NameError, e:
            if "Undefined" in str(e):
                print '*** mako error: NameError Undefined variable,'
                print '    one or more ${var} variables are undefined.\n'
                print '    Rerun doconce format with --mako_strict_undefined to see where the problem is.'
                _abort()
            elif "is not defined" in str(e):
                print '*** mako error: NameError', e
                _abort()
            else:
                # Just dump everything mako has
                print '*** mako error:'
                filestr = temp.render(**mako_kwargs)

        if encoding:
            f = codecs.open(resultfile2, 'w', encoding)
        else:
            f = open(resultfile2, 'w')
        f.write(filestr)
        f.close()
        resultfile = resultfile2

    if preprocessor is None:
        # no preprocessor syntax detected
        resultfile = filename
    else:
        debugpr('The file after running preprocess and/or mako:', filestr)

    return resultfile

def format_driver():
    # doconce format accepts special command-line arguments:
    #   - debug (for debugging in file _doconce_debugging.log) or
    #   - skip_inline_comments
    #   - oneline (for removal of newlines/linebreaks within paragraphs)
    #   - encoding utf-8 (e.g.)
    #   - preprocessor options (-DVAR etc. for preprocess)

    # oneline is inactive (doesn't work well yet)

    global _log, encoding, filename, dofile_basename

    if '--options' in sys.argv:
        from misc import help_format
        help_format()
        sys.exit(1)

    from misc import check_command_line_options
    check_command_line_options(4)

    try:
        format = sys.argv[1]
        filename = sys.argv[2]
        del sys.argv[1:3]
    except IndexError:
        from misc import get_legal_command_line_options
        options = ' '.join(get_legal_command_line_options())
        print 'Usage: %s format filename [preprocessor options] [%s]\n' \
              % (sys.argv[0], options)
        print 'Run "doconce format --options" to see explanation of all options'
        if len(sys.argv) == 1:
            print 'Missing format specification!'
        print 'formats:', ', '.join(supported_format_names())
        print '\n-DFORMAT=format is always defined when running preprocess'
        print 'Other -Dvar or -Dvar=value options can be added'
        sys.exit(1)

    names = supported_format_names()
    if format not in names:
        print '%s is not among the supported formats:\n%s' % (format, names)
        _abort()

    encoding = option('encoding=', default='')

    if option('debug'):
        _log_filename = '_doconce_debugging.log'
        _log = open(_log_filename,'w')
        _log.write("""
    This is a log file for the doconce script.
    Debugging is turned on by the command-line argument '--debug'
    to doconce format. Without that command-line argument,
    this file is not produced.

    """)
        print '*** debug output in', _log_filename


    debugpr('\n\n******* output format: %s *******\n\n' % format)

    if not os.path.isfile(filename):
        basename = filename
        filename = filename + '.do.txt'
        if not os.path.isfile(filename):
            print 'no such doconce file: %s' % (filename[:-7])
            _abort()
    else:
        basename = filename[:-7]

    dofile_basename = basename  # global variable

    #print '\n----- doconce format %s %s' % (format, filename)
    preprocessor_options = [arg for arg in sys.argv[1:]
                            if not arg.startswith('--')]
    filename_preprocessed = preprocess(filename, format,
                                       preprocessor_options)
    out_filename = file2file(filename_preprocessed, format, basename)

    if filename_preprocessed.startswith('__') and not option('debug'):
        os.remove(filename_preprocessed)  # clean up
    #print '----- successful run: %s filtered to %s\n' % (filename, out_filename)
    print 'output in', out_filename


class DoconceSyntaxError(Exception):
    pass

def doconce_format(format, dotext, compile=False,
                   filename_stem='_tmp', cleanup=False, **options):
    """
    Library interface to the doconce format command and
    possibly subsequent formats for compiling the output
    format to a final document, which is returned as
    string.

    Method: system calls to basic doconce functionality,
    but input is text (`dotext`) and output is the
    resulting file as string, or filename(s) and associated
    files if `compile` is true.

    Generated doconce files are removed if `cleanup` is True.
    """
    options_string = ' '.join(['--%s=%s' % (key, options[key])
                               for key in options])
    dofile = open(filename_stem + '.do.txt', 'w')
    dofile.write(dotext)
    dofile.close()
    cmd = 'doconce format %(format)s %(filename_stem)s %(options_string)s' % vars()
    import commands
    failure, output = commands.getstatusoutput(cmd)

    if failure:
        raise DoconceSyntaxError('Could not run %s.\nOutput:\n%s' %
                                 (cmd, output))
    # Grab filename
    for line in output.splitlines():
        if line.startswith('output in '):
            outfile = line.split()[-1]
    f = open(outfile, 'r')
    text = f.read()
    f.close()
    if compile:
        raise NotImplementedError('compiling not implemented')
        if outfile.endswith('.p.tex'):
            pass
        if outfile.endswith('.rst') and format == 'sphinx':
            pass
        if outfile.endswith('.rst') and format == 'rst':
            pass
    if cleanup:
        for filename in glob.glob(filename_stem + '.*'):
            os.remove(filename)
    return text


if __name__ == '__main__':
    format_driver()
