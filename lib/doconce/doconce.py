
#!/usr/bin/env python
global dofile_basename

import re, os, sys, shutil, subprocess, pprint, time, glob, codecs
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
from misc import option, which, _abort
import html, latex, pdflatex, rst, sphinx, st, epytext, plaintext, gwiki, mwiki, cwiki, pandoc, ipynb, xml, matlabnb

def supported_format_names():
    return 'html', 'latex', 'pdflatex', 'rst', 'sphinx', 'st', 'epytext', 'plain', 'gwiki', 'mwiki', 'cwiki', 'pandoc', 'ipynb', 'xml', 'matlabnb'

def doconce_envirs():                     # begin-end environments
    return ['c', 't',                     # verbatim and tex blocks
            'ans', 'sol', 'subex',        # exercises
            'pop', 'slidecell', 'notes',  # slides
            'hint', 'remarks',            # exercises
            'quote', 'box',
            'notice', 'summary', 'warning', 'question', 'block', # admon
            'quiz', 'u-',
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

def encode_error_message(exception, text, print_length=40):
    m = str(exception)
    if "codec can't encode character" in m:
        pos = m.split('position')[1].split(':')[0]
        print '*** error: problem with character when writing to file:'
        print str(exception)
        try:
            pos = int(pos)
        except:
            if '-' in pos:
                pos = pos.split('-')[0]
                pos = int(pos)
        print 'ordinal of this character is', ord(text[pos])
        print repr(text[pos-print_length:pos+print_length])
        print ' '*(print_length+2) + '^'
        #print repr(text[pos-print_length:pos]), '<strange char>', repr(text[pos:+1:pos+print_length])
        print '    remedies: fix character or try --encoding=utf-8'
        #raise Exception
        _abort()

def markdown2doconce(filestr, format=None, ipynb_mode=False):
    """
    Look for Markdown (and Extended Markdown) syntax in the file (filestr)
    and transform the text to valid DocOnce format.
    """
    #md2doconce "preprocessor" --markdown --write_doconce_from_markdown=myfile.do.txt (for debugging the translation from markdown-inspired doconce)
    #check https://stackedit.io/

    # Not treated:
    """
    * Tables without opening and closing | (simplest tables)
    * Definition lists
    * SmartyPants
    * Headlines with underline instead of #
    * labels (?) a la {#label}
    """
    lines = filestr.splitlines()
    # Headings: must have # at the beginning of the line and blank before
    # and after
    inside_code = False
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
        if lines[i].startswith('```') and inside_code:
            inside_code = False
            continue
        if lines[i].startswith('```') and not inside_code:
            inside_code = True
            continue
        if not inside_code:
            if re.search(r'^#{1,3} ', lines[i]):
                # Potential heading
                heading = False
                if i > 0 and lines[i-1].strip() == '':
                    # Blank line before (after might be a label)
                    heading = True
                elif i == 0:
                    heading = True
                if heading:
                    # H1: can be confused with comments,
                    # write comments as #Comment without initial blank after #
                    lines[i] = re.sub(
                        r'^# +([^#]+?)$', r"======= \g<1> =======", lines[i])
                    # H2
                    lines[i] = re.sub(
                        r'^## +([^#]+?)$', r"===== \g<1> =====", lines[i])
                    # H3
                    lines[i] = re.sub(
                        r'^### +([^#]+?)$', r"=== \g<1> ===", lines[i])

    # tables:
    inside_table = False
    # line starting and ending with pipe symbol is the start of a table
    pattern = r'^ *\| .+ \| *$'
    for i in range(len(lines)):
        if (not inside_table) and re.search(pattern, lines[i]):
            inside_table = True
            # Add table header
            header = '|%s|' % ('-'*(len(lines[i])-2))
            lines[i] = header + '\n' + lines[i]
        if inside_table and (':-' in lines[i] or '-:' in lines[i]):
            # Align specifications
            aligns = lines[i].split('|')[1:-1]
            specs = []
            for align in aligns:
                a = align.strip()
                if a.startswith(':') and a.endswith('-'):
                    specs.append('l')
                elif a.startswith(':') and a.endswith(':'):
                    specs.append('c')
                if a.startswith('-') and a.endswith(':'):
                    specs.append('r')
            lines[i] = '|' + '-'.join(['---%s---' % spec for spec in specs]) + '|'
        if inside_table and not lines[i].lstrip().startswith('|'):
            inside_table = False
            lines[i] += header
    filestr = '\n'.join(lines)

    # Still missing: figures and videos

    quote_envir = 'notice'
    quote_title = ' None'
    quote_title = ''
    quote_envir = 'quote'
    quote_envir = 'block'

    from common import inline_tag_begin, inline_tag_end
    extended_markdown_language2dolang = dict(
        Python='py', Ruby='rb', Fortran='f', Cpp='cpp', C='c',
        Perl='pl', Bash='sh', HTML='html')

    bc_postfix = '-t' if ipynb_mode else ''
    from common import unindent_lines
    regex = [
        # Computer code with language specification
        (r"\n?```([A-Za-z]+)(.*?)\n```", lambda m: "\n\n!bc %scod%s%s\n!ec\n" % (extended_markdown_language2dolang[m.group(1)], bc_postfix, unindent_lines(m.group(2).rstrip(), trailing_newline=False)), re.DOTALL), # language given
        # Computer code without (or the same) language specification
        (r"\n?```\n(.+?)\n```", lambda m: "\n\n!bc\n%s\n!ec\n" % unindent_lines(m.group(1).rstrip(), trailing_newline=False), re.DOTALL),
        # Paragraph heading written in boldface
        (r"\n\n\*\*(?P<subst>[^*]+?)([.?!:])\*\* ", r"\n\n__\g<subst>\g<2>__ "),
        # Boldface **word** to _word_
        (r"%(inline_tag_begin)s\*\*(?P<subst>[^*]+?)\*\*%(inline_tag_end)s" % vars(),
         r"\g<begin>_\g<subst>_\g<end>"),
        # Figure/movie references [Figure](#label)
        (r'\[Figure\]\(#(.+?)\)', 'Figure ref{\g<1>}'),
        # equation references from doconce-translatex ipynb files (do this before links! - same syntax...)
        (r'\[\(\d+?\)\]\(#(.+?)\)', r'(ref{\g<1>})'),
        # Link with link text
        (r"\[(?P<text>[^\]]+?)\]\((?P<url>.+?)\)", r'"\g<text>": "(\g<url>)"'),
        # Equation
        (r"\n?\$\$\n *(\\begin\{.+?\}.+?\\end\{.+?\})\s+\$\$", r"\n!bt\n\g<1>\n!et", re.DOTALL),
        (r"\n?\$\$\n(.+?)\n\$\$", r"\n!bt\n\\[ \g<1> \]\n!et", re.DOTALL),
        # Figure/movie (the figure/movie syntax is in a dom: comment)
        (r'<!-- begin figure -->.+?<!-- end figure -->\n', '', re.DOTALL),
        (r'<!-- begin movie -->.+?<!-- end movie -->\n', '', re.DOTALL),
        (r'!\[(.+?)\]\((.+?)\)', 'FIGURE: [\g<2>, width=600 frac=0.8] \g<1>\n'),
        # TOC
        (r"^\[TOC\]", r"TOC: on", re.MULTILINE),
        # doconce metadata comments in .ipynb files
        (r'<!-- dom:TITLE: (.+?) -->\n# .+', r'TITLE: \g<1>'),
        (r'<!-- dom:(.+?) --><div id=".+?"></div>', r'\g<1>'), # label
        (r'<!-- dom:(.+?) -->', r'\g<1>'), # idx, AUTHOR typically
        (r'Date: _(.+?)_', r'DATE: \g<1>'),
        (r'<!-- Author: --> .+\s+', ''),  # author lines
        (r'<!-- Equation labels as ordinary links -->\n<div id=".+?"></div>\n', ''),
        (r' \\tag\{\d+\}', ''),
        # Smart StackEdit comments (must appear before normal comments)
        # First treat DocOnce-inspired syntax with [name: comment]
        (r"<!--- ([A-Za-z]+?): (.+?)-->", r'[\g<1>: \g<2>]', re.DOTALL),
        # Second treat any such comment as inline DocOnce comment
        (r"<!---(.+?)-->", r'[comment: \g<1>]', re.DOTALL),
        # Plain comments starting on the beginning of a line, avoid blank
        # to not confuse with headings
        (r"^<!--(.+?)-->", lambda m: '#' + '\n# '.join(m.group(1).splitlines()), re.DOTALL|re.MULTILINE),
        # Plain comments inside the text must be inline comments in DocOnce
        # or dropped...
        (r"<!--(.+)-->", r'[comment: \g<1>]', re.DOTALL),
        #(r"<!--(.+)-->", r'', re.DOTALL)
        # Quoted paragraph
        #(r"\n\n> +(.+?)\n\n", r"\n\n!bquote\n\g<1>\n!equote\n\n", re.DOTALL),
        (r"\n\n> +(.+?)\n\n", r"\n\n!b%(quote_envir)s%(quote_title)s\n\g<1>\n!e%(quote_envir)s\n\n" % vars(), re.DOTALL),
        # lists with - should be bullets
        (r"^( +)-( +)", r"\g<1>*\g<2>", re.MULTILINE),
        # enumerated lists should be o
        (r"^( +)\d+\.( +)", r"\g<1>o\g<2>", re.MULTILINE),
        (r"<br>", r" <linebreak>"), # before next line which inserts <br>
        # doconce-translated ipynb files, treat remaining div tags as labels
        (r'<div id="(.+)?"></div>\n', r'label{\g<1>}\n'),
    ]
    for r in regex:
        if len(r) == 2:
            filestr = re.sub(r[0], r[1], filestr)
        elif len(r) == 3:
            filestr = re.sub(r[0], r[1], filestr, flags=r[2])

    # links that are written in Markdown as footnotes:
    links = {}
    lines = filestr.splitlines()
    newlines = []
    for line in lines:
        pattern = r'^ *\[([^\^]+?)\]:(.+)$'
        m = re.search(pattern, line, flags=re.MULTILINE)
        if m:
            links[m.group(1).strip()] = m.group(2).strip()
        else:
            # Skip all lines that contain link definitions and save the rest
            newlines.append(line.rstrip())
    filestr = '\n'.join(newlines)
    for link in links:
        filestr = re.sub(r'\[(.+?)\]\[%s\]' % link, '"\g<1>": "%s"' % links[link], filestr)
    # Fix quote blocks with opening > in lines
    pattern = '^!b%(quote_envir)s%(quote_title)s\n(.+?)^!e%(quote_envir)s' % vars()
    quotes = re.findall(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
    for quote in quotes:
        if '>' not in quote:
            continue
        lines = quote.splitlines()
        for i in range(len(lines)):
            if lines[i].startswith('>'):
                lines[i] = lines[i][1:].lstrip()
                try:
                    # list?
                    if lines[i].startswith('- '):
                        lines[i] = '  *' + lines[i][1:]
                    elif lines[i].startswith('* '):
                        lines[i] = '  *' + lines[i][1:]
                    elif re.search(r'^\d+\. ', lines[i]):
                        lines[i] = re.sub(r'^\d+\. ', '  o ', lines[i])
                except Exception, e:
                    raise e
        new_quote = '\n'.join(lines)
        # Cannot use re.sub since there are many strange chars (for regex)
        # in quote; only exact subst works
        from_ = '!b%(quote_envir)s%(quote_title)s%%s!e%(quote_envir)s' % vars() % ('\n'+ quote)
        to_ = '!b%(quote_envir)s%(quote_title)s%%s!e%(quote_envir)s' % vars() % ('\n' + new_quote + '\n')
        filestr = filestr.replace(from_, to_)
    # Fixes
    # Remove extensions in figure filenames
    filestr = re.sub(r'^FIGURE: +\[(.+?)\.(pdf|png|jpe?g|e?ps|gif)',
                     'FIGURE: [\g<1>', filestr, flags=re.MULTILINE)
    # No \ in labels
    filestr = filestr.replace('\\label{', 'label{')
    # Too many blanks before !bt and !bc
    filestr = re.sub(r'\n\n\n+!b([ct])', r'\n\n!b\g<1>', filestr)
    return filestr

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

    # Known issue: idex{some _boldface at the end_!_boldface at the beginning}
    pattern = r'idx\{(.+?)_!_(.+?)\}'
    m = re.search(pattern, filestr)
    if m:
        filestr, n = re.subn(pattern, r'idx{\g<1>_! _\g<2>}', filestr)
        # do not count this: num_fixes += n

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

    # edit markup: add space after add: and del: for .,;?
    # (should consider using https://github.com/CriticMarkup/CriticMarkup-toolkit instead!)
    pattern = r'\[(add|del):([.,;])\]'
    filestr, n = re.subn(pattern, r'[\g<1>: \g<2>]', filestr)
    num_fixes += n
    if n > 0:
        print '*** warning: found %d [add:...] or [del:...] edits without space after colon' % n

    """
    Drop this and report error instead:
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
    """

    if verbose and num_fixes:
        print '\n*** warning: the total of %d fixes above should be manually edited in the file!\n    (also note: some of these automatic fixes may not be what you want)\n' % num_fixes
    return filestr



def syntax_check(filestr, format):
    """Check for common errors in the doconce syntax."""

    # Check that we don't have multiple labels
    # (gives error if we have an example in !bc and then rendered label
    # afterwards...)
    labels = re.findall('label\{(.+?)\}', filestr)
    multiple_labels = list(set([label for label in labels if labels.count(label) > 1]))
    if multiple_labels:
        print '*** error: found multiple labels:'
        print '   ', ' '.join(multiple_labels)
        _abort()
    # Consistency of implemented environments
    user_defined_envirs = list(set(re.findall(r'^!b(u-[^ ]+)', filestr, flags=re.MULTILINE)))
    envirs = doconce_envirs() + user_defined_envirs
    envirs.remove('u-')
    for envir1 in envirs:
        for envir2 in envirs:
            if envir1 != envir2 and envir1.startswith(envir2):
                print '*** BUG in doconce: environment ![be]%s cannot start with the text of environment ![be]%s' % (envir1, envir2)
                _abort()
    # Could add users !bu-X environments too

    # Check that we don't have ~ref
    m = re.findall(r'~ref\{', filestr)
    if m:
        print '*** syntax error: ~ref (%d problems)' % len(m)
        print '    non-breaking space character not needed/allowed before'
        print '    figure, section, etc. (or other non-equation) references'
        _abort()

    # URLs with just one /
    m = re.findall(r'https?:/[A-Za-z].+', filestr)
    if m:
        print '*** error: missing double // in URLs'
        print '   ', '\n'.join(m)
        _abort()

    # Initial spaces in verbatim, bold, emphasize cannot be tested
    # (one may get matches between last ` and next beginning `, for instance).

    for envir in doconce_envirs():
        # Check that environments !bc, !ec, !bans, !eans, etc.
        # appear at the very beginning of the line
        # (allow e.g. `!benvir argument` and comment lines)
        pattern = re.compile(r'^([^#\n].+?[^`(\n]| +)(![eb]%s)' % envir, re.MULTILINE)
        m = pattern.search(filestr)
        if m:
            print '\n*** error: %s is not at the beginning of a line' % \
                  (m.group(2))
            print '    surrounding text:'
            print filestr[m.start()-100:m.end()+100], '\n'
            if m.group(1).strip() == '':
                print 'set %s at the beginning of the line' % m.group(2)
            else:
                print 'did you mean to write `%s` in some sentence?' % m.group(2)
            _abort()

        # Check that envirs have b and e before their name
        # (!subex is a frequent error...)
        pattern = '^!' + envir + r'\s'
        m = re.search(pattern, filestr, flags=re.MULTILINE)
        if m:
            print '\n*** error: found !%s at the beginning of a line' % envir
            print '    must be !b%s or !e%s' % (envir, envir)
            print '    surrounding text:'
            print filestr[m.start()-100:m.start()+len(m.group())+100]
            _abort()

    # Generalized references with whitespace between ] and [
    pattern = r'(ref(ch)?\[[^\]]*?\]\s+\[[^\]]*?\]\s+\[[^\]]*?\])'
    refgens = [refgen for refgen, dummy in re.findall(pattern, filestr)]
    if refgens:
        print '*** error: found generalized references ref[][][] with whitespaces'
        print '    between closing (]) and opening ([) brackets, and that'
        print '    is not legal syntax.\n'
        print '\n\n'.join(refgens)
        _abort()
    # Linebreaks must have space before them if verbatim
    pattern = r'`<linebreak>[^`]'
    m = re.search(pattern, filestr)
    if m:
        print '*** error: need space between inline verbatim code and <linebreak>'
        print filestr[m.start()-50:m.end()]
        _abort()

    # Footnotes cannot be at the beginning of the line
    pattern = r'^\[\^[A-Za-z].+?\][^:]'
    m = re.search(pattern, filestr, flags=re.MULTILINE)
    if m:
        print '*** error: footnote cannot appear at the beginning of a line:'
        print filestr[m.start()-50:m.start()+60]
        _abort()

    # edit markup
    section_pattern = r'^={3,9}(.+?)={3,9}'
    headings = re.findall(section_pattern, filestr, flags=re.MULTILINE)
    edit_patterns = r'\[(add|del):.+?\]', r' -> '
    for heading in headings:
        for pattern in edit_patterns:
            m = re.search(pattern, heading)
            if m:
                print '*** error: cannot use edit markup %s in section heading' % m.group()
                print '   ', heading
                print '    use inline comment below the heading instead where you explain the problem'
                _abort()

    pattern = r'^[A-Za-z0_9`"].+\n *- +.+\n^[A-Za-z0_9`"]'
    m = re.search(pattern, filestr, flags=re.MULTILINE)
    if m:
        print '*** error: hyphen in front of text at a line'
        print '    indicates description list, but this is not'
        print '    indended here: (move the hypen to previous line)'
        print filestr[m.start()-50:m.start()+150]
        _abort()

    # Need extra blank lines around tables
    pattern = r'!b.+?\n\|----'
    m = re.search(pattern, filestr)
    if m:
        print '*** syntax error: need blank line before table'
        print filestr[m.start()-100:m.start()+100]
        _abort()
    pattern = r'----\|\n!e.+'
    m = re.search(pattern, filestr)
    if m:
        print '*** syntax error: need blank line after table'
        print filestr[m.start()-100:m.start()+100]
        _abort()
    # Verbatim words must be the whole link, otherwise issue
    # warnings for the formats where this may look strange
    if format not in ('pandoc',):
        links  = re.findall(INLINE_TAGS['linkURL2'], filestr)
        links += re.findall(INLINE_TAGS['linkURL3'], filestr)
        for link, url1, url2 in links:
            if '``' in link[1:-1]:
                pass # quotes are ok
            elif '`' in link[1:-1]:
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
            print '\n*** error: must in format "%s" have a plain sentence before\na code block like !bc/!bt/@@@CODE, not a section/paragraph heading,\ntable, or comment:\n\n---------------------------------' % format
            print filestr2[m.start()-40:m.start()+80]
            print '---------------------------------'
            _abort()

    # If latex format and native latex code for tables are inserted,
    # ampersands cannot be quoted and --no_ampersand_quote is needed.
    if format in ('latex', 'pdflatex'):
        if 'begin{tabular}' in filestr:
            if not option('no_ampersand_quote'):
                print """*** error: the document has a native latex table
    (search for begin{tabular}) with ampersands (&). To prevent these
    from being quoted, add the --no_ampersand_quote option."""
                _abort()

    # Syntax error `try`-`except`, should be `try-except`,
    # similarly `tuple`/`list` or `int` `N` must be rewritten
    pattern = r'(([`A-Za-z0-9._]+)`(-|/| +)`([`A-Za-z0-9._]+))'
    m = re.search(pattern, filestr)
    if m:
        print '*** error: %s is syntax error' % (m.group(1))
        print '    rewrite to e.g. %s%s%s' % (m.group(2), m.group(3), m.group(4))
        print '    surrounding text:'
        print filestr[m.start()-100:m.start()+100]
        _abort()
    # Backticks for inline verbatim without space (in the middle of text)
    #pattern = r'[A-Za-z-]`[A-Za-z]'  # orig test with - (why?)
    pattern = r'[A-Za-z]`[A-Za-z]'
    m = re.search(pattern, filestr)
    if m:
        print '*** error: backtick ` in the middle of text is probably syntax error'
        print '    surrounding text:'
        print filestr[m.start()-50:m.start()+50]
        _abort()

    begin_end_consistency_checks(filestr, doconce_envirs())

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
             remove_code_and_tex(filestr, format)

    # Check that all references to equations have parenthesis
    eq_labels = []
    pattern = r'label\{(.+?)\}'
    for tex_block in tex_blocks:
        if 'label{' in tex_block:
            eq_labels += re.findall(pattern, tex_block)
    pattern = r'[^(]ref\{%s\}[^)]'
    found_problem = False
    for eq_label in eq_labels:
        m = re.search(pattern % eq_label, filestr)
        if m:
            print '*** error: reference to equation label "%s" is without parentheses' % eq_label
            print '    the equation reference should be type set as (ref{%s})' % eq_label
            print '...', filestr[m.start()-10:m.start()], filestr[m.start():m.end()+20], '...'
            found_problem = True
    if found_problem:
        _abort()

    # Check that all references have corresponding labels, except in
    # generalized references (ref[][][])
    ref_pattern = r'ref(ch)?\[([^\]]*?)\]\[([^\]]*?)\]\[([^\]]*?)\]'
    filestr2 = re.sub(ref_pattern, '', filestr)
    bu_labels = re.findall(r' label=([^\s]+)', filestr)
    labels = re.findall(r'label\{(.+?)\}', filestr2) + eq_labels + bu_labels
    refs = re.findall(r'ref\{(.+?)\}', filestr2)
    found_problem = False
    for ref in refs:
        if ref not in labels:
            print '*** error: reference ref{%s} to non-defined label' % ref
            found_problem = True
    if found_problem and not option('allow_refs_to_external_docs'):
        print """
Causes of missing labels:
1: label is defined in another document. Use generalized references
   ref[][][], or use --allow_refs_to_external_docs (to ignore this error)
2: preprocessor if-else has left the label out
3: forgotten to define the label
"""
        _abort()

    # Quotes or inline verbatim is not allowed inside emphasize and bold:
    # (force non-blank in the beginning and end to avoid interfering with lists)
    from common import inline_tag_begin, inline_tag_end
    pattern = r'%s\*(?P<subst>[^ ][^*]+?[^ ])\*%s' % (inline_tag_begin, inline_tag_end)
    for dummy1, dummy2, phrase, dummy3, dummy4 in \
            re.findall(pattern, filestr, flags=re.MULTILINE):
        if '`' in phrase:
            print '*** warning: found ` (backtick) inside something that looks like emphasize:'
            print '   ', '*%s*' % phrase
            print '    (backtick inside *...* emphasize is not allowed)'

    # Check underscores in latex
    if format in ('latex', 'pdflatex'):
        filestr2 = re.sub(r'\$.+?\$', '', filestr, flags=re.DOTALL) # strip math
        # Filer out @@@CODE, verbatim, boldface, paragraph, idx, and comments
        filestr2 = re.sub(r'idx\{(.+?)\}', '', filestr2, flags=re.MULTILINE)
        filestr2 = re.sub(INLINE_TAGS['paragraph'], '', filestr2,
                          flags=re.MULTILINE)
        filestr2 = re.sub(r'^@@@CODE .+', '', filestr2,
                          flags=re.MULTILINE)
        filestr2 = re.sub(INLINE_TAGS['verbatim'], ' ', filestr2,
                          flags=re.MULTILINE)
        filestr2 = re.sub(INLINE_TAGS['bold'], ' ', filestr2,
                          flags=re.MULTILINE)
        filestr2 = re.sub(r'^#.*\n', '', filestr2, flags=re.MULTILINE)
        underscore_words = [word.strip() for word in
                            re.findall(r'\s[A-Za-z0-9_]*_[A-Za-z0-9_]*\s',
                                       filestr2)]
        if underscore_words:
            print '*** warning: latex format will have problem with words'
            print '    containing underscores:\n'
            print '\n'.join(underscore_words)
            print '\n    typeset these words with `inline verbatim` or escape with backslash'

    # Check that headings have consistent use of = signs
    for line in filestr.splitlines():
        if line.strip().startswith('==='):
            w = line.split()
            if w[0] != w[-1]:
                print '\n*** error: inconsistent no of = in heading:\n', line
                print '      lengths: %d and %d, must be equal and odd' % \
                      (len(w[0]), len(w[-1]))
                _abort()

    # Check that ref{} and label{} have closing }
    pattern = r'(ref|label)\{([^}]+?)\}'
    refs_labels = re.findall(pattern, filestr)
    for tp, label in refs_labels:
        if ' ' in label:
            print '*** error: space in label is not allowed!'
            print '    %s{%s}\n' % (tp, label)
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
            print '*** warning: found reference "%s %s" with unexpected word "%s" in front\n' % (orig_prefix, ref, orig_prefix),
            print '    (expected Section/Chapter/Figure %s, or could it be a reference to an equation, but missing parenthesis in (%s)?)' % (ref, ref)

    # Code/tex blocks cannot have a comment, table, figure, etc.
    # right before them in rst/sphinx
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
        print '    (cite{...} has no backslash in DocOnce syntax)'
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
        print '    (label{...} has no backslash in DocOnce syntax)'
        print '\n'.join(matches)

    matches = re.findall(r'\\ref\{.+?\}', filestr)
    if matches:
        print '\n*** warning: found \\ref{...} with backslash'
        print '    (ref{...} has no backslash in DocOnce syntax)'
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

    pattern = r'__[A-Z][A-Za-z0-9,:` ]+__[.?]'
    matches = re.findall(pattern, filestr)
    if matches:
        print '\n*** error: wrong paragraph heading syntax: period outside __'
        print '\n'.join(matches)
        _abort()

    pattern = re.compile(r'^__[^_]+?[^.:?)]__', re.MULTILINE)
    matches = pattern.findall(filestr)
    if matches:
        print '*** warning: missing . , : ) or ? after paragraph heading:'
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
    pattern = r'^MOVIE: *\[[^,\]]+ +[^\]]*\]'
    cpattern = re.compile(pattern, re.MULTILINE)
    matches = cpattern.findall(filestr)
    if matches:
        print '\n*** error: missing comma after filename, before options in MOVIE'
        print '\n'.join(matches)
        _abort()

    # Movie or figure with initial space in filename:
    pattern = r'^((MOVIE|FIGURE): *\[ +[A-Za-z_0-9/.]+)'
    matches = re.findall(pattern, filestr, flags=re.MULTILINE)
    if matches:
        print '\n*** error: wrong initial space in filename'
        print '\n'.join([match for match, tp in matches])
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
        links = list(set([link[1] for link in links]))
        links2local = []
        for link in links:
            if not (link.startswith('http') or link.startswith('file:/') or \
                    link.startswith('_static')):
                links2local.append(link)
        ok = True
        for link in links2local:
            if link.startswith('mov') and os.path.isdir(os.path.dirname(link)):
                pass  # automake_sphinx.py will move mov* dirs to static
            else:
                print '*** warning: hyperlink to URL %s is to a local file,\n    recommended to be _static/%s for sphinx' % (link, link)
                ok = False
        if not ok:
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
        return filestr, 0

    # Create dummy file if specified file not found?
    CREATE_DUMMY_FILE = False

    # Get filename prefix to be added to the found path
    path_prefix = option('code_prefix=', '')
    if '~' in path_prefix:
        path_prefix = os.path.expanduser(path_prefix)

    lines = filestr.splitlines()
    inside_verbatim = False
    num_files = 0
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
            num_files += 1
            debugpr('found verbatim copy (line %d):\n%s\n' % (i+1, line))
            code_envir = None
            words = line.split()
            try:
                filename = words[1]
            except IndexError:
                print '\n'.join(lines[i-3:i+4])
                print '*** error: missing filename in line\n  %s' % line
                _abort()
            orig_filename = filename # keep a copy in case we have a prefix
            if path_prefix:
                filename = os.path.join(path_prefix, filename)

            try:
                if 'http' in filename:
                    import urllib
                    codefile = urllib.urlopen(filename)
                    print '... fetching source code from', path_prefix
                else:
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

            # Check if the code environment is explicitly specified
            if 'envir=' in line:
                m = re.search(r'envir=([a-zN0-9_]+)', line)
                if m:
                    code_envir = m.group(1).strip()
                    line = line.replace('envir=%s' % code_envir, '').strip()
                    # Need a new split since we removed words from line
                    words = line.split()
            else:
                # Determine code environment from filename extension
                filetype = os.path.splitext(filename)[1][1:]  # drop dot

                # Adjustments to some names
                if filetype in ('f', 'c', 'java', 'cpp', 'py', 'pyopt', 'cy', 'm', 'sh', 'html', 'txt', 'dat'):
                    pass # standard filetypes
                elif filetype == 'cxx' or filetype == 'C' or filetype == 'h' \
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
                elif filetype == 'tex':  # TeX/LaTeX files are called latex
                    filetype = 'latex'
                elif filetype == 'text':
                    filetype = 'txt'
                elif filetype in ('data', 'cvs'):
                    filetype = 'dat'
                elif filetype in ('csh', 'ksh', 'zsh', 'tcsh'):
                    filetype = 'sh'
                else:
                    # Not a registered, supported filetype, use plain text
                    filetype = 'txt'
                if '.do.txt' in filename:
                    filetype = 'do'

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

                # Skip header?
                skipline = option('code_skip_until=', None)
                if skipline is not None and skipline in code:
                    codelines = code.splitlines()
                    for i in range(len(codelines)):
                        if skipline in codelines[i]:
                            code = '\n'.join(codelines[i+1:])
                            break

                debugpr('copy the whole file "%s" into a verbatim block\n' % filename)

            else:
                # use regex to read a part of the code file
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
                        print 'error: could not find regex "%s"!' % from_,
                    if not to_found and to_ != '':
                        print 'error: could not find regex "%s"!' % to_,
                    if from_found and to_found:
                        print '"From" and "to" regex match at the same line - empty text.',
                    print
                    _abort()
                print ' lines %d-%d' % (from_line, to_line),
            codefile.close()

            #if format == 'latex' or format == 'pdflatex' or format == 'sphinx':
            # Insert a cod or pro directive for ptex2tex and sphinx.
            if code_envir in ('None', 'off', 'none'):
                # no need to embed code in anything
                print ' (no format, just include)'
            elif code_envir is not None:
                code = "!bc %s\n%s\n!ec" % (code_envir, code)
                print ' (format: %s)' % code_envir
            else:
                if filetype == 'unknown':
                    code = "!bc\n%s\n!ec" % (code)
                    print ' (format: !bc)'
                elif filetype in ('txt', 'do', 'dat'):
                    # No cod or pro, just text files
                    code = "!bc %s\n%s\n!ec" % (filetype, code)
                    print ' (format: !bc)'
                elif complete_file:
                    code = "!bc %spro\n%s\n!ec" % (filetype, code)
                    print ' (format: %spro)' % filetype
                else:
                    code = "!bc %scod\n%s\n!ec" % (filetype, code)
                    print ' (format: %scod)' % filetype
            lines[i] = code

    filestr = '\n'.join(lines)
    return filestr, num_files


def insert_os_commands(filestr, format):
    if not '@@@OSCMD ' in filestr:
        return filestr, 0

    # Filename prefix
    path_prefix = option('code_prefix=', '')
    if '~' in path_prefix:
        path_prefix = os.path.expanduser(path_prefix)
    os_prompt = option('os_prompt=', 'Terminal>')

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
    num_commands = 0
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
            num_commands += 1
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
    return filestr, num_commands

def exercises(filestr, format, code_blocks, tex_blocks):
    # Exercise:
    # ===== Exercise: title ===== (starts with at least 3 =, max 5)
    # label{some:label} file=thisfile.py solution=somefile.do.txt
    # __Hint 1.__ some paragraph...,
    # __Hint 2.__ ...

    from common import _CODE_BLOCK, _MATH_BLOCK

    all_exer = []   # collection of all exercises
    exer = {}       # data for one exercise, to be appended to all_exer
    inside_exer = False
    exer_end = False
    exer_counter = dict(Exercise=0, Problem=0, Project=0, Example=0)

    # Regexes: no need for re.MULTILINE since we treat one line at a time
    if option('examples_as_exercises'):
        exer_heading_pattern = r'^(=====) *\{?(Exercise|Problem|Project|Example)\}?: *(?P<title>[^ =-].+?) *====='
    else:
        exer_heading_pattern = r'^(=====) *\{?(Exercise|Problem|Project)\}?:\s*(?P<title>[^ =-].+?) *====='
    if not re.search(exer_heading_pattern, filestr, flags=re.MULTILINE):
        return filestr

    label_pattern = re.compile(r'^\s*label\{(.+?)\}')
    # We accept file and solution to be comment lines
    #file_pattern = re.compile(r'^#? *file *= *([^\s]+)')
    file_pattern = re.compile(r'^#? *files? *= *([A-Za-z0-9\-._, *]+)')
    solution_pattern = re.compile(r'^#? *solutions? *= *([A-Za-z0-9\-._, ]+)')
    keywords_pattern = re.compile(r'^#? *(keywords|kw) *= *([A-Za-z0-9\-._;, ]+)')

    # Keep track of chapters
    chapter_pattern = re.compile(r'^ *========= *(Appendix:)?(.+?) *=========')
    chapter_counter = 0
    chapter_info = (None, None, None)  # (prefix Ch/App, no/char, title)
    chapter = True  # False means appendix
    chapter_exer_no = None
    preface = False

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
    newlines = []     # lines in resulting file
    solutions = []    # lines in an optional solution part
    standalones = []  # lines in standalone document for an exercise

    # m_* variables: various match objects from regex searches

    for line_no in range(len(lines)):
        line = lines[line_no].lstrip()
        #print 'LINE %d:' % line_no, line
        #pprint.pprint(exer)

        m_chapter = re.search(chapter_pattern, line)
        if m_chapter:
            if m_chapter.group(1):
                # Appendix
                if chapter:
                    chapter = False  # Start of appendices
                    chapter_counter = 65  # ord('A')
                else:
                    chapter_counter += 1
                title = m_chapter.group(2)
                chapter_info = ('Appendix', chr(chapter_counter), title)
            else:
                # Ordinary chapter
                title = m_chapter.group(2)
                if 'Preface' in title:
                    preface = True
                else:
                    # Add chapter counter only outside Preface
                    chapter_counter += 1
                chapter_info = ('Chapter', chapter_counter, title)
            chapter_exer_no = 0

        m_heading = re.search(exer_heading_pattern, line)
        if m_heading:
            inside_exer = True

            exer = {}  # data in the exercise
            subex = {} # data in a subexercise
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
            if chapter_exer_no is not None:  # do we have chapters?
                chapter_exer_no += 1

            exer['chapter_type'] = chapter_info[0]
            exer['chapter_no'] = chapter_info[1]
            exer['chapter_title'] = chapter_info[2]
            exer['chapter_exercise'] = chapter_exer_no

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
                             solution=[], file=None, aftertext=[])
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
                    if subex:
                        #if lines[line_no].strip() != '':
                        subex['aftertext'].append(lines[line_no])
                    else:
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
            for k_ in range(len(exer['subex'])):
                if 'aftertext' in exer['subex'][k_]:
                    exer['subex'][k_]['aftertext'] = '\n'.join(exer['subex'][k_]['aftertext'])
                    if exer['subex'][k_]['aftertext'] == '':
                        del exer['subex'][k_]['aftertext']

            debugpr('Data structure from interpreting exercises:',
                    pprint.pformat(exer))
            formatted_exercise, formatted_solution = EXERCISE[format](exer)
            newlines.append(formatted_exercise)
            solutions.append(formatted_solution)
            all_exer.append(exer)

            # Check if we have headings in solution (links to these
            # will appear in TOC) - recommend no headings
            solutions_wheadings = []
            if re.search(r'^===', exer['solution'], flags=re.MULTILINE):
                solutions_wheadings.append(exer['solution'])
            for s in exer['subex']:
                if re.search(r'^===', s['solution'], flags=re.MULTILINE):
                    solutions_wheadings.append(s['solution'])
            if solutions_wheadings:
                print '*** warning: heading in solution to exercise is not recommended!'
                print '    (will cause problems in table of contents if solutions'
                print '    are left out of the document). Just use paragraph headings!\n'
                print exer['title']
                print '\n\n'.join(solutions_wheadings)
                if format == 'html':
                    if not option('allow_refs_to_external_docs'):
                        _abort()  # will cause abort for split_html anyway

            # Check if Exercise could be Problem: no refs to labels
            # outside the Exercise
            if 1:
                _label_pattern = r'label\{(.+?)\}'
                _ref_pattern = r'ref\{(.+?)\}'
                _texblock_pattern = r'(\d+) ' + _MATH_BLOCK
                labels = re.findall(_label_pattern, formatted_exercise)
                refs   = re.findall(_ref_pattern, formatted_exercise)
                texblocks_no = re.findall(_texblock_pattern, formatted_exercise)
                for texblock in texblocks_no:
                    texblock = int(texblock)
                    labels += re.findall(_label_pattern, tex_blocks[texblock])
                external_refs = []
                for ref in refs:
                    if ref not in labels:
                        external_refs.append(ref)
                if not external_refs and exer['type'] == 'Exercise':
                    msg = '\n*** %s: %s' % (exer['type'], exer['title'])
                    if 'label' in exer:
                        msg += '\n    label{%s}' % exer['label']
                    msg += '\n    could be Problem (no refs beyond the exercise itself)'
                    print msg
                if external_refs and exer['type'] in ('Problem', 'Project'):
                    msg = '\n*** %s: %s' % (exer['type'], exer['title'])
                    if 'label' in exer:
                        msg += '\n    label{%s}' % exer['label']
                    msg += '\n    should be Exercise since it has refs to other parts of the document:\n    ' + ', '.join(external_refs)
                    print msg

            # Be ready for next iteration
            inside_exer = False
            exer_end = False
            exer = {}

    filestr = '\n'.join(newlines)
    solutions = '\n'.join(solutions)

    if option('without_solutions') and option('solutions_at_end'):
        from common import chapter_pattern
        if re.search(chapter_pattern, filestr, flags=re.MULTILINE):
            has_chapters = True
        else:
            has_chapters = False

        # Is writing to file a good idea? <<<!!CODE_BLOCK will not be
        # substituted. Better to grab the solution chapter/section
        # at the end of substitutions and write this to file!
        solfilename = dofile_basename + '_exersol.do.txt'
        f = open(solfilename, 'w')
        if has_chapters:
            sol_heading = '========= Solutions =========\nlabel{ch:solutions}\n\n'
        else:
            sol_heading = '======= Solutions =======\nlabel{sec:solutions}\n\n'
        f.write(sol_heading)
        f.write(solutions)
        f.close()
        #print 'solutions to exercises in', dofile_basename

        pattern = '(^={5,7} +(References|Bibliography) +={5,7})'
        sol_sec = sol_heading + solutions
        if re.search(pattern, filestr, flags=re.MULTILINE):
            filestr = re.sub(pattern,
                             sol_sec + '\n\n\\g<1>',
                             filestr, flags=re.MULTILINE)
        else:
            # Just add solutions at the end
            filestr += '\n\n\n' + sol_sec

    if option('exercises_in_zip'):
        extract_individual_standalone_exercises(
            filestr, format, all_exer, code_blocks, tex_blocks)

    if all_exer:
        # Replace code and math blocks by actual code.
        # This must be done in the all_exer data structure,
        # if a pprint.pformat'ed string is used, quotes in
        # computer code and derivatives lead to errors
        # if we take an eval on the output.

        def replace_code_math(text):
            if not isinstance(text, basestring):
                return text

            # Why not use insert_code_and_tex here? Should be safer
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

        # Should have sol here too, but this solution of substituting in
        # the data structure is not good, it's better to extract exercises
        # via comment lines as we do with quizzes and make them
        # separate.
        for e in range(len(all_exer)):
            for key in all_exer[e]:
                if key == 'subex':
                    for es in range(len(all_exer[e][key])):
                       for keys in all_exer[e][key][es]:
                           if isinstance(all_exer[e][key][es][keys], (list,tuple)):
                               for i in range(len(all_exer[e][key][es][keys])):
                                   all_exer[e][key][es][keys][i] = \
                               replace_code_math(all_exer[e][key][es][keys][i])
                           else: # str
                               all_exer[e][key][es][keys] = \
                               replace_code_math(all_exer[e][key][es][keys])
                else:
                     all_exer[e][key] = \
                               replace_code_math(all_exer[e][key])

        all_exer_str = pprint.pformat(all_exer)

        # (recall that we write to pprint-formatted string!)

        # Dump this all_exer data structure to file
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
        print 'found info about %d exercises' % (len(all_exer))
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
            if not option('examples_as_exercises'):
                print '    If the block is inside an Example, use --examples_as_exercises'
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


def process_envir(filestr, envir, format, action='remove', reason=''):
    """
    Find or replace an environment (envir) in filestr.
    action='remove' means replace with a comment
    'removed !b... ... !e... environment + reason. Return filestr.
    action='grep' means return all matching environments between
    the comment lines.
    """
    comment_pattern = INLINE_TAGS_SUBST[format].get('comment', '# %s')
    if callable(comment_pattern):
        pattern = comment_pattern(envir_delimiter_lines[envir][0]) + \
             '\n(.+?)' + comment_pattern(envir_delimiter_lines[envir][1])\
             + '\n'
    else:
        pattern = comment_pattern % envir_delimiter_lines[envir][0] + \
                  '\n(.+?)' + comment_pattern % \
                  envir_delimiter_lines[envir][1] + '\n'
    if action == 'remove':
        if callable(comment_pattern):
            replacement = comment_pattern('removed !b%s ... !e%s environment ' % (envir, envir) + reason)
        else:
            replacement = comment_pattern % ('removed !b%s ... !e%s environment %s' % (envir, envir, reason))
        filestr = re.sub(pattern, replacement, filestr, flags=re.DOTALL)
        return filestr
    elif action == 'grep':
        return re.findall(pattern, filestr, flags=re.DOTALL)
    else:
        raise ValueError(action)

def extract_individual_standalone_exercises(
    filestr, format, all_exer, code_blocks, tex_blocks):

    text = filestr

    # Grab all exercises
    exers = process_envir(text, 'exercise', 'plain', action='grep')
    if len(exers) != len(all_exer):
        print '*** error: doconce bug, no of exercises in all_exer',
        print 'differs from no of grabbed exercises'
        _abort()

    import zipfile
    filename = dofile_basename + '_exercises.zip'
    archive = zipfile.ZipFile(filename, mode='w')
    exer_filename = option('exercises_in_zip_filename=', 'logical')

    # Text for index file with list of exercise files
    index_text = """TITLE: List of stand-alone files with exercises

# Edit FILE_EXTENSIONS to the type of documents that will
# be listed in the this index
<%
FILE_EXTENSIONS = ['.tex', '.ipynb']
#FILE_EXTENSIONS = ['.tex', '.ipynb', '.do.txt', '.html']
%>

"""
    chapter_prev = None

    for i, sa in enumerate(exers):
        labels = re.findall(r'label\{(.+?)\}', sa)
        refs = re.findall(r'ref\{(.+?)\}', sa)
        external_references = False
        for ref in refs:
            if ref not in labels:
                external_references = True
                break

        pattern = r'^Filenames?: `(.+?)`.*$'
        m = re.search(pattern, sa, flags=re.MULTILINE)
        if m:
            logical_name = os.path.splitext(m.group(1).strip())[0]
        else:
            logical_name = None
        sa = re.sub(pattern + '.*', '', sa, flags=re.MULTILINE)

        # Replace section by title, author, date, filename comment
        replacement = r'TITLE: \g<1>\g<2>\nAUTHOR: Jane Doe Email:jane.doe@cyberspace.net\nDATE: Due Jan 32, 2150\n'
        if logical_name is not None:
            replacement += '\n# Logical name of exercise: %s\n' % logical_name
        if external_references:
            replacement += """
# This document contains references to a parent document (../%s).
# These references will work for latex (using the xr package and
# a compiled parent document (with ../%s.aux file), but other formats
# will have missing references.
# Externaldocuments: ../%s
""" % (dofile_basename, dofile_basename, dofile_basename)

        # At this stage {Exercise}: has the {} removed
        sa = re.sub(
            r'===== (Exercise|Problem|Project|Example):(.+?) =====',
            replacement, sa)
        # If we have {Exercise}, the exercise has just one subsec heading,
        # apply the previous subst for this
        sa = re.sub(r'===== (.+?) =====', replacement.replace(r'\g<2>', ''), sa)
        # Remove main label of exercise
        sa = sa.replace('label{%s}' % all_exer[i]['label'], '')

        sa = sa.strip() + '\n'

        sa = insert_code_and_tex(sa, code_blocks, tex_blocks, format,
                                 complete_doc=False)

        # Remove solutions after inserting all code/tex blocks
        sa = process_envir(sa, 'sol', 'plain', action='remove')
        sa = process_envir(sa, 'ans', 'plain', action='remove')
        # Note: ans and sol will not be removed from Examples, but that
        # is the correct behavior
        sa = re.sub('^# removed .+environment.*$', '', sa, flags=re.MULTILINE)
        # Remove comments around various constructions
        sa = re.sub('^# --- .+?\n', '', sa, flags=re.MULTILINE)

        # Use all_exer to find data
        if option('exercise_numbering=', 'absolute') == 'chapter' and \
               all_exer[i]['chapter_type'] is not None:
            no = '%s_%s.%s' % \
                 (all_exer[i]['chapter_type'],
                  all_exer[i]['chapter_no'],
                  all_exer[i]['chapter_exercise'])

        else: # 'absolute'
             no = 'exercise_' + str(all_exer[i]['no'])

        if exer_filename == 'logical' and logical_name is not None:
            name = logical_name + '.do.txt'
            path = os.path.join('standalone_exercises', name)
            archive.writestr(path, sa)
        else: # 'number':
            name = no + '.do.txt'
            path = os.path.join('standalone_exercises', name)
            archive.writestr(path, sa)

        if all_exer[i]['chapter_type'] is not None and \
           all_exer[i]['chapter_title'] != chapter_prev:
            index_text += '========= Chapter: %s =========\n\n' % all_exer[i]['chapter_title']
            chapter_prev = all_exer[i]['chapter_title']

        name = name.replace('.do.txt', '')
        index_text += """%% for EXT in FILE_EXTENSIONS:
"`%s${EXT}`": "%s${EXT}"
%% endfor
 <linebreak>

""" % (name, name)

    name = 'index.do.txt'
    path = os.path.join('standalone_exercises', name)
    archive.writestr(path, index_text)

    make_text = """
#!/usr/bin/env python
# Compile all stand-alone exercises to latex and ipynb
# (Must first unzip archive)

import glob, os

dofiles = glob.glob('*.do.txt')
dofiles.remove('index.do.txt')   # compile to html only

for dofile in dofiles:
    cmd = 'doconce format pdflatex %s --latex_code_style=vrb --figure_prefix=../ --movie_prefix=../' % dofile
    os.system(cmd)
    # Edit .tex file and remove doconce-specific things
    cmd = 'doconce subst "%% #.+" "" %s.tex' % dofile[:-7]  # preprocess
    os.system(cmd)
    cmd = 'doconce subst "%%.*" "" %s.tex' % dofile[:-7]

    cmd = 'doconce format ipynb %s --figure_prefix=../  --movie_prefix=../' % dofile
    os.system(cmd)

# Edit FILE_EXTENSIONS to adjust what kind of files that is listed in index.html
cmd = 'doconce format html index --html_style=bootstrap'
os.system(cmd)
"""
    name = 'make.py'
    path = os.path.join('standalone_exercises', name)
    archive.writestr(path, make_text)
    archive.close()
    print 'standalone exercises in', filename


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
    pattern = r'^\s*\|.+\| *$'  # table lines
    table_lines = re.findall(pattern, filestr, re.MULTILINE)
    horizontal_rule = r'^\s*\|[-lrc]+\|\s*$'
    inserted_space_around_pipe = False
    for line in table_lines:
        if not re.search(horizontal_rule, line, flags=re.MULTILINE) \
           and (re.search(r'[$`]\|', line) or re.search(r'\|[$`]', line)) \
           and line.count('|') > 2:
            # Found $|, |$, `|, or |` in table line, insert space
            line_wspaces = re.sub(r'([$`])\|', r'\g<1> |', line)
            line_wspaces = re.sub(r'\|([$`])', r'| \g<1>', line_wspaces)
            filestr = filestr.replace(line, line_wspaces)
            inserted_space_around_pipe = True
    return filestr, inserted_space_around_pipe

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

    # Fix: make sure there is a blank line after the table
    # (blank line can be swallowed if a table is at the end of a
    #  user-def envir.)
    filestr = re.sub(r'--\|\n([^|\n ]+)', r'--|\n\n\g<1>', filestr)

    # table is a dict with keys rows, headings_align, columns_align
    table = {'rows': []}  # init new table
    inside_table = False

    tables2csv = option('tables2csv')
    import csv
    table_counter = 0
    # Add functionality:
    # doconce csv2table, which reads a .csv file and outputs
    # a doconce formatted table

    horizontal_rule_pattern = r'^\|[\-lrcX]+\|'
    lines = filestr.splitlines()
    # Fix: add blank line if document ends with a table (otherwise we
    # cannot see the end of the table)
    if re.search(horizontal_rule_pattern, lines[-1]):
        lines.append('\n')

    for line_no, line in enumerate(lines):
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
                # Non-empty string contains lrcX| letters for alignment
                # (can be alignmend of heading or of columns)
                if align == '|'*len(align):  # Just '|||'?
                    print 'Syntax error: horizontal rule in table '\
                          'contains | between columns - remove these.'
                    print line
                    _abort()
                for char in align:
                    if char not in ('|', 'r', 'l', 'c', 'X'):
                        print 'illegal alignment character in table:', char
                        _abort()
                # The X align char is for tabularx environment in latex,
                # for other formats it must be treated as an l
                if 'X' in align and format not in ('latex', 'pdflatex'):
                    align = align.replace('X', 'l')
                if len(table['rows']) <= 1:
                    # first horizontal rule, align spec concern headings
                    table['headings_align'] = align
                else:
                    # align spec concerns column alignment
                    table['columns_align'] = align
            continue  # continue with next line
        if lin.startswith('|') and not horizontal_rule:
            if lin.startswith('|b') or lin.startswith('|e'):
                print '*** syntax error: ordinary line (outside code environments)'
                print '    starts with |b... or |e..., should be ! instead of |'
                print lin
                _abort()

            # row in table:
            if not inside_table:
                inside_table = True
                table_counter += 1
            # Check if | is used in math or code in this line.
            # If so, replace | by a marker text and substitute back
            # (this does not work with the plain text format because
            # we cannot at this stage recognize inline verbatim)
            marker_text = 'zzYYYpipeYYYzz?'
            # Note that inline substitutions are done before interpreting tables
            patterns = [r'\$.+?\$',  # math
                        r'\{.+?\}',  # latex verbatim (\code{})
                        r'<code>.+?</code>',  # html verbatim
                        r'``.+?``',  # rst verbatim
                        r'[^`]`.+?`[^`]',  # markdown verbatim
                        ]
            math_code_exprs = [re.findall(pattern, line)
                               for pattern in patterns]
            for math_code_expr in math_code_exprs:
                for expr in math_code_expr:
                    if '|' in expr:
                        marked_expr = expr.replace('|', marker_text)
                        line = line.replace(expr, marked_expr)
                    # (Caveat: split wrt | does not work with math2 syntax.
                    # Any $a=1$|$b=2$ syntax for two columns is already
                    # transformed to $a=1$ | $b=2$ in space_in_tables
                    # prior to inline substitutions.)

            # Extract columns by splitting wrt | (safe now since | in
            # math and code is taken care of). Drop first and last
            # since these are always empty after .split('|').
            columns = line.strip().split('|')[1:-1]
            # Restore any |
            columns = [c.replace(marker_text, '|') for c in columns]
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
                #pprint.pprint(table)

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
                    print '    in the right places'
                    print '\n    lines surrounding the table:'
                    for _line in lines[line_no-10:line_no+5]:
                        print _line
                    print '\n    here are the recorded table rows:'
                    for row in table['rows']:
                        if row != ['horizontal rule']:
                            # Check for common syntax error: |--l--|--r--|
                            if sum([bool(re.search('[lrc-]{%d}' % len(c), c)) for c in row]) > 0:
                                print 'NOTE: do not use pipes in horizontal rule of this type:'
                                print '(write instead |%s|)' % '-'.join(row)
                            print '| ' + ' | '.join(row) + ' |'
                        else:
                            print '|---------------------| (horizontal rule)'
                    print '\npossible trouble:'
                    print '1. Not a table, just an opening pipe symbol at the beginning of the line?'
                    print '2. Something wrong with the syntax in a preceding table?'
                    if format not in ('latex', 'pdflatex', 'html', 'sphinx', 'mwiki'):
                        print '3. In simple formats without math support, like %s, a formula like $|x|$ at the beginning of the line will have stripped off $ and hence line starts with |, which indicates a table. Move the formula so that it is not at the beginning of a line.' % format
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

def typeset_userdef_envirs(filestr, format):
    userdef_envirs = re.findall(r'^!bu-([^ ]+)', filestr, flags=re.MULTILINE)
    if not userdef_envirs:
        return filestr
    userfile = 'userdef_environments.py'
    if os.path.isfile(userfile):
        # This should be unnecessary, should find files in the current dir
        sys_path_original = list(sys.path)
        sys.path.append(os.path.dirname(os.path.realpath(userfile)))
        try:
            import userdef_environments as ue
        except Exception as e:
            print "*** error on import userdef_environments"
            print "*** when trying to import %s " % os.path.abspath(userfile)
            print "*** error:"
            print e
            _abort()
        sys.path = list(sys_path_original)
        if not hasattr(ue, 'envir2format'):
            print '*** error: envir2format not defined in', userfile
            _abort()
    else:
        print '*** error: found user-defined environments'
        print '   ', ', '.join(list(set(userdef_envirs)))
        print '    but no file', userfile, 'for defining the environments!'
        _abort()

    pattern = r'^(!bu-([^\s]+)(.*?)\n(.+?)\s*^!eu-([^\s]+))'
    userdef_envirs = re.findall(pattern, filestr, flags=re.MULTILINE|re.DOTALL)
    if 'intro' in ue.envir2format:
        if format == 'pdflatex' and 'latex' in ue.envir2format['intro']:
            intro = ue.envir2format['intro']['latex']
        elif format == 'latex' and 'pdflatex' in ue.envir2format['intro']:
            intro = ue.envir2format['intro']['pdflatex']
        else:
            intro = ue.envir2format['intro'].get(format, '')
    else:
        intro = ''
    # html and latex can have intros
    global INTRO
    if format == 'html':
        INTRO[format] = INTRO[format].replace('<!-- USER-DEFINED ENVIRONMENTS -->', intro)
    elif format in ('latex', 'pdflatex'):
        INTRO[format] = INTRO[format].replace('%%% USER-DEFINED ENVIRONMENTS', intro)

    counter = {}
    for all, user_envir, titleline, text, user_envir_end in userdef_envirs:
        if user_envir in counter:
            counter[user_envir] += 1
        else:
            counter[user_envir] = 1

        if not ue.envir2format[user_envir]:
            print '*** error: user-defined environment "%s" is not defined in' % user_envir, userfile
            _abort()
        instructions = ''
        if format in ue.envir2format[user_envir]:
            instructions = ue.envir2format[user_envir][format]
        elif format == 'pdflatex' and 'latex' in ue.envir2format[user_envir]:
            instructions = ue.envir2format[user_envir]['latex']
        elif format == 'latex' and 'pdflatex' in ue.envir2format[user_envir]:
            instructions = ue.envir2format[user_envir]['pdflatex']
        elif 'do' in ue.envir2format[user_envir]:
            instructions = ue.envir2format[user_envir]['do']
        if instructions == '':
            replacement = text  # just strip off begin/end
        elif callable(instructions):
            titleline = titleline.strip()
            replacement = instructions(text, titleline,
                                       counter[user_envir], format)
        else:
            print '*** error: envir2format["%s"]["%s"] is not string or function' % (user_envir, format)
            _abort()
        filestr = filestr.replace(all, replacement)
    return filestr

def typeset_envirs(filestr, format):
    # Note: exercises are done (and translated to doconce syntax)
    # before this function is called. bt/bc are taken elsewhere.
    # quiz is taken later.
    envirs = doconce_envirs()[8:-2]

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
                        title = INLINE_TAGS_SUBST[format]['paragraph'].\
                                replace(r'\g<space>', ' ').\
                                replace(r'\g<subst>', '%s') % title + '\n'
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
    import string
    from StringIO import StringIO
    result = StringIO()
    lastindent = 0
    lists = []
    inside_description_environment = False
    lines = filestr.splitlines()
    lastline = lines[0]
    special_comment = r'--- (begin|end) [A-Za-z0-9,();\- ]*? ---'
    #exercise_comment_line = r'--- (begin|end) .*?exercise ---'
    # for debugging only:
    _code_block_no = 0; _tex_block_no = 0

    for i, line in enumerate(lines):
        db_line = '[%s]' % line
        #debugpr('\n------------------------\nsource line=[%s]' % line)

        if not line or line.isspace():  # blank line?
            if not lists:
                result.write(BLANKLINE[format])
            # else: drop writing out blank line inside lists
                db_line_tp = 'blank line'
                #debugpr('  > This is a blank line')
            lastline = line
            continue

        if line.startswith('#'):

            # first do some debug output:
            if line.startswith('#!!CODE') and len(debug_info) >= 1:
                result.write(line + '\n')
                db_line_tp = 'code block:\n%s\n-----------' % debug_info[0][_code_block_no]
                #debugpr('  > Here is a code block:\n%s\n--------' % debug_info[0][_code_block_no])
                _code_block_no += 1
            elif line.startswith('#!!TEX') and len(debug_info) >= 2:
                result.write(line + '\n')
                db_line_tp = 'latex block:\n%s\n-----------' % debug_info[0][_code_block_no]
                #debugpr('  > Here is a latex block:\n%s\n--------' % debug_info[1][_tex_block_no])
                _tex_block_no += 1

            else:
                #debugpr('  > This is just a comment line')
                db_line= 'comment: %s' % line[1:]
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
                    # lines, same for special comments in quiz
                    if not re.search(special_comment, line):
                        # Ordinary comment
                        result.write(new_comment + '\n')
                        db_line_tp = 'comment'
                    else:
                        # Special comment (keep it as ordinary line)
                        line = new_comment  # will be printed later
                        db_line_tp = 'special comment'

            lastline = line
            if not re.search(special_comment, line):
                # Ordinary comment
                continue
            # else: just proceed and use zero indent as indicator
            # for end of list

        # structure of a line:
        linescan = re.compile(
            r"\n*(?P<indent> *(?P<listtype>[*o-] )? *)" +
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
        db_indent = '  > indent=%d (from %d)' % (indent, lastindent)
        #debugpr('  > indent=%d (previous indent=%d), keyword=[%s], text=[%s]' % (indent, lastindent, keyword, text))

        # new (sub)section makes end of any indent
        if line.startswith('==='):
            indent = 0


        if indent > lastindent and listtype:
            #debugpr('  > This is a new list of type "%s"' % listtype)
            db_line_tp = 'new list %s' % listtype
            # begin a new list or sublist:
            lists.append({'listtype': listtype, 'indent': indent})
            begin_list = LIST[format][listtype]['begin']
            if '<ol>' in begin_list and len(lists) % 2 == 0:
                begin_list = begin_list.replace('ol', 'ol type="a"')
            result.write(begin_list)
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
                #debugpr('  > This is the end of a %s list' % lists[-1]['listtype'])
                db_line_tp = 'end of a %s list' % lists[-1]['listtype']
                result.write(LIST[format][lists[-1]['listtype']]['end'])
                del lists[-1]
            lastindent = indent

        #if indent == lastindent:
        #    debugpr('  > This line belongs to the previous block since it has '\
        #          'the same indent (%d blanks)' % indent)

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
                #debugpr('  > This is an item in an enumerate list')
                db_line_tp = 'item enumerate list'
                enumerate_counter += 1
                if '%d' in itemformat:
                    # Switch between 1,2,3 and a,b,c
                    if len(lists) % 2 == 0:
                        item = itemformat.replace('%d', '%s') % \
                               string.lowercase[enumerate_counter-1]
                    else:
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
                        #debugpr('  > This is an item in a description list with parsed keyword=[%s]' % keyword)
                        db_line_tp = 'description list'
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
                #debugpr('  > This is an item in a bullet list')
                db_line_tp = 'bullet list'
                result.write(' '*(indent-2))  # indent here counts with '* '
                result.write(item + ' ')

        else:
            #debugpr('  > This line is some ordinary line, no special list syntax involved')
            db_line_tp = 'ordinary line'
            # should check emph, verbatim, etc., syntax check and common errors
            result.write(' '*indent)      # ordinary line

        # this is not a list definition line and therefore we must
        # add keyword + text because these two items make up the
        # line if a : present in an ordinary line
        if keyword:
            text = keyword + text
        #debugpr('text=[%s]' % text)
        db_result = '[%s]' % text

        # hack to make wiki have all text in an item on a single line:
        newline = '' if lists and format in ('gwiki', 'cwiki') else '\n'
        #newline = '\n'
        result.write(text + newline)
        lastindent = indent
        lastline = line
        if db_line_tp != 'ordinary line':
            debugpr('%s (%s)\n--> %s' % (db_line, db_line_tp, db_result.rstrip()))
        else:
            debugpr('%s (%s)' % (db_line, db_line_tp))
            """
            # Cannot do this test here because some formats have already
            # made indentation as part of their syntax
            if lines[i][0] == ' ':  # indented line?
                print '*** error: found indented line (syntax error):\n'
                print '>>> illegal indented line: "%s"\n' % lines[i]
                print 'surrounding text:\n'
                for _l in lines[i-3:i+4]:
                    print _l
                print '\nNote: all ordinary text and commands must start at the beginning of the line'
                print '(only lists can be indented)'
                _abort()
            """

    # end lists if any are left:
    while lists:
        debugpr('closing list: end of a %s list' % lists[-1]['listtype'])
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

    if not isinstance(FIGURE_EXT[format], dict):
        print '*** BUG: FIGURE_EXT["%s"] is %s, not dict' % (format, type(FIGURE_EXT[format]))
        _abort()
    search_extensions = FIGURE_EXT[format]['search']
    convert_extensions = FIGURE_EXT[format]['convert']

    figfiles = [filename.strip()
                for filename, options, caption in c.findall(filestr)]
    figfiles = set(figfiles)   # remove multiple occurences

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
    figfiles = set(figfiles)   # remove multiple occurences

    for figfile in figfiles:
        if figfile.startswith('http'):
            # latex, pdflatex must download the file,
            # html, sphinx and web-based formats can use the URL directly
            basepath, ext = os.path.splitext(figfile)
            # Avoid ext = '.05' etc from numbers in the filename
            if not ext.lower() in ['.eps', '.pdf', '.png', '.jpg', 'jpeg',
                                   '.gif', '.tif', '.tiff', '.svg']:
                ext = ''
            if ext:
                if is_file_or_url(figfile) != 'url':
                    print '*** error: figure URL "%s" could not be reached' % figfile
                    _abort()
            else:
                # no extension, run through the allowed extensions
                # to see if figfile + ext exists:
                file_found = False
                for ext in search_extensions:
                    newname = figfile + ext
                    if is_file_or_url(newname) == 'url':
                        file_found = True
                        print 'figure file %s:\n    can use %s for format %s' \
                              % (figfile, newname, format)
                        filestr = re.sub(r'%s([,\]])' % figfile,
                                         '%s\g<1>' % newname, filestr)
                        break
                if not file_found:
                    print '*** error: figure %s:\n    could not find URL with legal extension %s' % (figfile, ', '.join(search_extensions))
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
                for ext in search_extensions:
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
        if not ext in search_extensions:
            # convert to proper format
            for e in convert_extensions:
                converted_file = basepath + e
                if not os.path.isfile(converted_file):
                    # ext might be empty, in that case we cannot convert
                    # anything:
                    if ext:
                        print 'figure', figfile, 'must have extension(s)', \
                              ', '.join(search_extensions)
                        # use ps2pdf and pdf2ps for vector graphics
                        # and only convert if to/from png/jpg/gif
                        if ext.endswith('ps') and e == '.pdf':
                            #cmd = 'epstopdf %s %s' % \
                            #      (figfile, converted_file)
                            cmd = 'ps2pdf -dEPSCrop %s %s' % \
                                  (figfile, converted_file)
                        elif ext == '.pdf' and e.endswith('ps'):
                            cmd = 'pdf2ps %s %s' % \
                                  (figfile, converted_file)
                        else:
                            if not os.path.isfile(converted_file):
                                cmd = 'convert %s %s' % (figfile, converted_file)
                            else:
                                cmd = 'echo'  # do nothing, file exists

                            if e in ('.ps', '.eps', '.pdf') and \
                               ext in ('.png', '.jpg', '.jpeg', '.gif'):
                                print """\
*** warning: need to convert from %s to %s
using ImageMagick's convert program, but the result will
be loss of quality. Generate a proper %s file (if possible).""" % \
                                (figfile, converted_file, converted_file)
                        failure = os.system(cmd)
                        if not failure:
                            if not cmd == 'echo':
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
    section_pattern = r'^\s*(={3,9})(.+?)(={3,9})\s*label\{(.+?)\}'
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
    #pprint.pprint(sections)

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

    # 3. Replace ref by hardcoded numbers from a latex .aux file
    refaux = 'refaux{' in filestr
    from latex import aux_label2number
    label2number = aux_label2number()
    if refaux and not label2number:
        print '*** error: used refaux{} reference(s), but no option --replace_ref_by_latex_auxno='
        _abort()
    # If there is one refaux{...} in the document, only refaux{...}
    # references get replaced by label2number info
    if label2number:
        for label in label2number:
            no = label2number[label]
            if refaux:
                filestr = re.sub(r'refaux\{%s\}' % label, no, filestr)
            else:
                filestr = re.sub(r'ref\{%s\}' % label, no, filestr)

    # 4. Handle references that can be internal or external
    #    (generalized references) ref[internal][cite][external-HTML]
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


def handle_index_and_bib(filestr, format):
    """Process idx{...} and cite{...} and footnote instructions."""
    # Footnote definitions: start of line, spaces, [^name]: explanation
    # goes up to next footnote [^name] or a double newline or the end of the str
    pattern_def = '^ *\[\^(?P<name>.+?)\]:(?P<text>.+?)(?=(\n\n|\[\^|\Z))'
    #footnotes = {name: footnote for name, footnote, lookahead in
    #             re.findall(pattern_def, filestr, flags=re.MULTILINE|re.DOTALL)}
    #pattern_footnote = r'(?P<footnote> *\[\^(?P<name>.+?)\](?=([^:]))'
    # Footnote pattern has a word prior to the footnote [^name]
    # or math, inline code, link
    pattern_footnote = r'(?<=(\w|[$`").,;?!]))(?P<footnote>(?P<space> *)\[\^(?P<name>.+?)\])(?=[.,:;?)\s])'
    # (Note: cannot have footnote at beginning of line, because look behind
    # does not tolerate ^ in (\w|[$`")]|^)
    # Keep footnotes for pandoc, plain text
    # Make a simple transformation for rst, sphinx
    # Transform for latex: remove definition, insert \footnote{...}
    if format in INLINE_TAGS_SUBST and 'footnote' in INLINE_TAGS_SUBST[format]:
        if callable(INLINE_TAGS_SUBST[format]['footnote']):
            filestr = INLINE_TAGS_SUBST[format]['footnote'](
                filestr, format, pattern_def, pattern_footnote)
        elif INLINE_TAGS_SUBST[format]['footnote'] is not None:
            filestr = re.sub(pattern_def, INLINE_TAGS_SUBST[format]['footnote'], filestr)
    else:
        if re.search(pattern_footnote, filestr):
            print '*** warning: footnotes are not supported for format %s' % format
            print '    footnotes will be left in the doconce syntax'

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
            if pubfile is not None:
                print '*** error: more than one BIBFILE specification is illegal'
                _abort()
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
                cite_formatting = 'standard'
                if format in ('latex', 'pdflatex'):
                    cite_formatting = 'latex'
                elif format in ('pandoc', 'ipynb'):
                    if option('ipynb_cite=', 'plain') == 'latex':
                        cite_formatting = 'standard'
                    else:
                        cite_formatting = 'pandoc'
                if cite_formatting == 'standard':
                    for arg in cite_args:
                        replacement = ' '.join(['cite{%s}' % label.strip() \
                                                 for label in arg.split(',')])
                        filestr = filestr.replace('cite{%s}' % arg,
                                                  replacement)
                elif cite_formatting == 'pandoc':
                    # prefix labels with @ and substitute , by ;
                    for arg in cite_args:
                        replacement = '[' + ';'.join(
                            ['@' + label for label in arg.split(',')]) + ']'
                        filestr = filestr.replace('cite{%s}' % arg,
                                                  replacement)

    if len(citations) > 0 and OrderedDict is dict:
        # version < 2.7 warning
        print '*** warning: citations may appear in random order unless you upgrade to Python version 2.7 or 3.1 or later'
    if len(citations) > 0 and 'BIBFILE:' not in filestr:
        print '*** warning: you have citations but no bibliography (BIBFILE: ...)'
        print ', '.join(list(citations.keys()))
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
                              flags=re.MULTILINE)
    filestr = re.sub(r'^AUTHOR:.+$', 'XXXAUTHOR', filestr, flags=re.MULTILINE)
    # contract multiple AUTHOR lines to one single:
    filestr = re.sub('(XXXAUTHOR\n)+', 'XXXAUTHOR', filestr)

    from collections import OrderedDict
    copyright_ = OrderedDict()

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
                i = [i.strip(),]
        else:  # just author's name
            a = line.strip()
            i = None

        # Copyright: {copyright} {copyright,2006} {copyright,2006-2015}

        def interpret_copyright(s):
            """
            Interpret copyright syntax in the string s and
            remove the copyright.
            {copyright} {copyright,2005} {copyright,2005-2010}
            {copyright,2005-present} {copyright,present|CC BY}
            """
            license_ = None
            cc_license_wording = option('CC_license=',
                                        'Released under CC %s 4.0 license')
            cr_pattern = r'\{ *(copyright[^}]*)\}'
            m = re.search(cr_pattern, s)
            if m:
                cr = m.group(1)
                s = re.sub(cr_pattern, '', s).strip()  # remove {copyright...}
                if '|' in cr:
                    cr, license_ = cr.split('|')
                    if license_.startswith('CC'):
                        try:
                            license_ = license_.split()[1]
                        except IndexError:
                            print '*** error: wrong syntax for license in copyright:', license_
                            _abort()
                        # https://creativecommons.org/licenses/
                        # CC BY-ND
                        cctps = {
                            'BY': 'Attribution',
                            'ND': 'NoDerivs',
                            'NC': 'NonCommercial',
                            'SA': 'ShareAlike',
                            }
                        license_ = [cctps[cctp] for cctp in license_.split('-')]
                        license_ = cc_license_wording % '-'.join(license_)
                if ',' in cr:  # year?
                    year = cr.split(',')[1].strip()
                    this_year = time.asctime().split()[4] # current year
                    if year == 'present':
                        year = this_year
                    elif year == 'None':
                        year = None
                    elif year == 'date':
                        year = None
                        pattern = r'^DATE:(.+)'
                        m1 = re.search(pattern, filestr, flags=re.MULTILINE)
                        if m1:
                            pattern = r'\d\d\d\d'
                            date = m1.group(1)
                            m2 = research(pattern, date)
                            if m2:
                                year = m2.group()
                        if year is None:
                            year = this_year
                    elif '-' in year:
                        year = [y.strip() for y in year.split('-')]
                        if year[1] == 'present':
                            year[1] = this_year
                        if int(year[1]) > int(this_year):
                            print '*** warning: copyright year %s-%s is adjusted to %s-present (%s)' % (year[0], year[1], year[0], this_year)
                            year[1] = this_year
                        # Concatenate as interval
                        year = year[0] + '-' + year[1]
                else:
                    year = time.asctime().split()[4] # current year
                return s, year, license_
            else:
                return s, None, license_

        # Remove {copyright...} info from a and i
        a, year, license_ = interpret_copyright(a)
        if year is not None:
            # Remove email from a
            a_ = re.sub(r'[Ee]mail:.+', '', a).strip()
            copyright_[a_] = (year, license_)
        if i is not None:
            for k in range(len(i)):
                i[k], year, license_ = interpret_copyright(i[k])
                if year is not None:
                    copyright_[i[k]] = (year, license_)

        if 'mail:' in a:  # email?
            a, e = re.split(r'[Ee]?mail:\s*', a)
            a = a.strip()
            e = e.strip()
            if not '@' in e:
                print 'Syntax error: wrong email specification in AUTHOR line: "%s" (no @)' % e
        else:
            e = None

        authors_and_institutions.append((a, i, e))

    if copyright_:
        # Avoid multiple versions of the same institution in copyright_
        #keys = list(set(list(copyright_.keys()))) # does not preserve seq.
        keys = []
        for key in copyright_.keys():
            if not key in keys:
                keys.append(key)
        copy_copyright_ = copyright_.copy()
        copyright_ = OrderedDict()
        for key in keys:
            copyright_[key] = copy_copyright_[key]

        year0 = copyright_[keys[0]][0]
        license0 = copyright_[keys[0]][1]
        # Test that year and license are the same
        for key in keys[1:]:
            if copyright_[key][0] != year0:
                print '*** error: copyright year for %s is %s, different from %s for %s' % (key, copyright_[key], copyright_[keys[0]], keys[0])
                print '    make sure all copyrights have the same info!'
                _abort()
            if copyright_[key][1] != license0:
                print '*** error: copyright license for %s is "%s", different from "%s" for %s' % (key, copyright_[key], copyright_[keys[0]], keys[0])
                print '    make sure all copyrights have the same info!'
                _abort()
        copyright_ = {'holder': keys, 'year': year0, 'license': license0,
                      'cite doconce': option('cite_doconce', False)}
    elif option('cite_doconce', False):
        # Include copyright footer also if there is no copyright with
        # authors, but a --cite_doconce option
        copyright_ = {'cite doconce': True}
    if copyright_:
        # Store in file for use elsewhere (will only work for doconce format)
        try:
            with open('.' + dofile_basename + '.copyright', 'w') as f:
                f.write(repr(copyright_))
        except NameError:
            pass # file is already written

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

def typeset_section_numbering(filestr, format):
    chapter = section = subsection = subsubsection = 0
    # Do we have chapters?
    from common import chapter_pattern
    if re.search(chapter_pattern, filestr, flags=re.MULTILINE):
        has_chapters = True
    else:
        has_chapters = False

    def counter(*args):
        # Make 1.3.2 type of section number
        # args: chapter, section, subsection,
        if has_chapters:
            return '.'.join([str(s) for s in args])
        else:
            return '.'.join([str(s) for s in args[1:]])

    lines = filestr.splitlines()
    for i in range(len(lines)):
        if lines[i].startswith('========= '):
            chapter += 1
            section = subsection = subsubsection = 0
            lines[i] = re.sub(r'^========= ', '========= %s: ' %
                              counter(chapter), lines[i])
        elif lines[i].startswith('======= '):
            section += 1
            subsection = subsubsection = 0
            lines[i] = re.sub(r'^======= ', '======= %s: ' %
                              counter(chapter, section), lines[i])
        elif lines[i].startswith('===== '):
            subsection += 1
            subsubsection = 0
            lines[i] = re.sub(r'^===== ', '===== %s: ' %
                              counter(chapter, section, subsection),
                              lines[i])
        elif lines[i].startswith('=== '):
            subsubsection += 1
            lines[i] = re.sub(r'^=== ', '=== %s: ' %
                              counter(chapter, section, subsection, subsubsection),
                              lines[i])
    return '\n'.join(lines)

def typeset_quizzes1(filestr, insert_missing_quiz_header=True):
    """
    Find all multiple choice questions in the string (file) filestr.
    Return filestr with comment indications for various parts of
    the quizzes.

    Method: extract all quizzes, replace each quiz by a new format
    consisting of digested text between begin-end comments, run
    doconce text transformations, interpret the begin-end comments
    and store quiz info in a data structure, send data structure
    to a format-specific function for final rendering (the text is
    already in the right format).
    """
    # Should have possibility to have textarea as answer to
    # question for future smart regex checks of the answer, maybe
    # also upload files.
    # Should also have the possibility to include sound files
    # for applause etc. from Dropbox/collected../ideas/doconce/sound

    pattern = '^!bquiz.+?^!equiz'
    quiztexts = re.findall(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
    headings = [('', None)]*(len(quiztexts))
    # Find the heading before each quiz (can be compared with H: ...)
    pieces = filestr.split('!bquiz')
    # Can only do this when there are no extra inline !bquiz words
    # inside the text (because of the above split), just !bquiz in quiz envirs
    if len(pieces) == len(quiztexts) + 1:
        for i, piece in enumerate(pieces[:-1]):
            for line in reversed(piece.splitlines()):
                if line.startswith('===== '):
                    if re.search(r'=====\s+\{?(Exercise|Project|Problem|Example)', line):
                        headings[i] = line, 'exercise'
                    else:
                        headings[i] = line, 'subsection'
                    break
                elif line.startswith('======='):
                    headings[i] = line, 'section'
                    break
                """
                elif line.startswith('!bquestion') or line.startswith('!bnotice') or line.startswith('!bsummary'):
                    # Can have quiz in admons too
                    words = line.split()
                    if len(words) > 1:
                        headings[i] = (' '.join(words[1:]), words[2:] + '-admon')
                        break
                """
    quizzes = []
    for text, heading in zip(quiztexts, headings):
        new_text = interpret_quiz_text(text, insert_missing_quiz_header,
                                       heading[0], heading[1])
        quizzes.append(new_text)
        filestr = filestr.replace(text, new_text)
    return filestr, len(quiztexts)

def interpret_quiz_text(text, insert_missing_heading= False,
                        previous_heading=None, previous_heading_tp=None):
    """
    Replace quiz (in string text) with begin-end groups typeset as
    comments. The optional new page and heading lines are replaced
    by one-line comments.
    The function extract_quizzes can recognize the output of the
    present function, and create a data structure with the quiz
    content..
    """
    ct = comment_tag
    bct = begin_comment_tag
    ect = end_comment_tag

    data = {}
    # New page? NP
    pattern = r'^NP:(.+)'
    m = re.search(pattern, text, flags=re.MULTILINE)
    if m:
        header = m.group(1).strip()
        text = re.sub(pattern, ct('--- new quiz page: ' + header), text,
                      flags=re.MULTILINE)
    # Heading?
    pattern = r'^H:(.+)'
    m = re.search(pattern, text, flags=re.MULTILINE)
    if m:
        heading = m.group(1).strip()
        if insert_missing_heading and isinstance(previous_heading, str):
            if heading.lower() not in previous_heading.lower():
                # Quiz heading is missing and wanted
                text = '===== Exercise: %s =====\n\n' % heading + text
                # no label, file=, solution= are needed for quizes
                previous_heading_tp = 'exercise'
        heading_comment = ct('--- quiz heading: ' + heading) + '\n' + ct('--- previous heading type: ' + str(previous_heading_tp))
        text = re.sub(pattern, heading_comment, text, flags=re.MULTILINE)
    else:
        # Give info about previous heading type
        if previous_heading_tp is not None:
            text = ct('--- previous heading type: ' + str(previous_heading_tp)) + '\n' + text


    def begin_end_tags(tag, content):
        return """
%s
%s
%s
""" % (bct(tag), content, ect(tag))

    # Question
    pattern = r'(^Q:(.+?))(?=^(C[rw]|K|L):)'
    m = re.search(pattern, text, flags=re.MULTILINE|re.DOTALL)
    if m:
        question = m.group(2).strip()
        text = text.replace(m.group(1), begin_end_tags('quiz question', question))
    else:
        print '*** error: found quiz without question!'
        print text
        _abort()

    # Keywords
    pattern = r'^(K:(.+))$'
    m = re.search(pattern, text, flags=re.MULTILINE)
    if m:
        keywords = [s.strip() for s in m.group(2).split(';')]
        text = text.replace(m.group(1), ct('--- keywords: ' + str(keywords)))

    # Label
    pattern = r'^(L:(.+))$'
    m = re.search(pattern, text, flags=re.MULTILINE)
    if m:
        text = text.replace(m.group(1), ct('--- label: ' + str(m.group(2).strip())))

    # Choices: grab choices + optional explanations first,
    # then extract explanations.
    # Need end-of-string marker, cannot use $ since we want ^ and
    # re.MULTILINE ($ is then end of line)
    text += '_EOS_'
    pattern = r'^(C[rw]:(.+?))(?=(^C[rw]:|L:|K:|_EOS_|^!equiz))'
    choices = re.findall(pattern, text, flags=re.MULTILINE|re.DOTALL)
    text = text[:-5]  # remove _EOS_ marker
    counter = 1
    if choices:
        for choice_text, choice, _lookahead in choices:
            if re.search(r'^[KL]:', choice, flags=re.MULTILINE):
                print '*** error: keyword or label cannot appear between a'
                print '    choice and explanation in a quiz:'
                print choice
                _abort()
            right = choice_text.startswith('Cr')  # right or wrong choice?
            explanation = ''
            if re.search(r'^E:', choice, flags=re.MULTILINE):
                choice, explanation = re.split(r'^E:\s*',
                                               choice, flags=re.MULTILINE)
                text = text.replace(choice_text, begin_end_tags('quiz choice %d (%s)' % (counter, 'right' if right else 'wrong'), choice.strip()) + begin_end_tags('explanation of choice %d' % counter, explanation.strip()))
            else:
                text = text.replace(choice_text, begin_end_tags('quiz choice %d (%s)' % (counter, 'right' if right else 'wrong'), choice.strip()))
            counter += 1
    else:
        print '*** error: found quiz without choices!'
        print text
        _abort()
    text = re.sub('^!bquiz', bct('quiz'), text,
                  flags=re.MULTILINE)
    text = re.sub('^!equiz', ect('quiz'), text,
                  flags=re.MULTILINE)
    return text

_QUIZ_BLOCK = '<<<!!QUIZ_BLOCK'

def extract_quizzes(filestr, format):
    """
    Replace quizzes, formatted as output from function interpret_quiz_text,
    by a Python data structure and a special instruction where formatting
    of this data structure is to be inserted.
    """
    from collections import OrderedDict
    ct = comment_tag
    bct = begin_comment_tag
    ect = end_comment_tag
    cp = INLINE_TAGS_SUBST[format].get('comment', '# %s') # comment pattern
    if format in ("rst", "sphinx"):
        #cp = '.. %s\n'  # \n gives error if text follows right after !equiz
        cp = '.. %s'
    if not isinstance(cp, str):
        raise TypeError
    # line start: must allow spaces first in rst/sphinx, but quiz inside
    # indented admons do not work anyway in rst/sphix
    line_start = '^ *'  # could be rst/sphinx fix, but does not work
    line_start = '^'  # comments start in 1st column
    pattern = line_start + bct('quiz', cp) + '.+?' + ect('quiz', cp)
    quizzes = re.findall(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
    data = []
    for i, quiz in enumerate(quizzes):
        data.append(OrderedDict())
        data[-1]['no'] = i+1
        filestr = filestr.replace(quiz, '%d %s' % (i, _QUIZ_BLOCK))
        # Extract data in quiz
        pattern = line_start + ct('--- new quiz page: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            data[-1]['new page'] = m.group(1).strip()
        pattern = line_start + ct('--- quiz heading: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            data[-1]['heading'] = m.group(1).strip()
        pattern = line_start + ct('--- previous heading type: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            data[-1]['embedding'] = m.group(1).strip()

        pattern = line_start + bct('quiz question', cp) + '(.+?)' + ect('quiz question', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE|re.DOTALL)
        if m:
            question = m.group(1).strip()
            # Check if question prefix is specified
            # Q: [] Here goes the question...
            prefix_pattern = r'^\[(.*?)\]'
            m = re.search(prefix_pattern, question)
            if m:
                prefix = m.group(1)
                question = re.sub(prefix_pattern, '', question).strip()
                data[-1]['question prefix'] = prefix
            data[-1]['question'] = question
        else:
            print '*** error: malformed quiz, no question'
            print quiz
            print '\n     Examine the corresponding doconce source code for syntax errors.'
            _abort()

        pattern = line_start + ct('--- keywords: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            try:
                keywords = eval(m.group(1))  # should have list format
            except Exception as e:
                print '*** keywords in quiz have wrong syntax (should be semi-colon separated list):'
                print m.group(1)
                print '    Quiz question:', question
                _abort()
            data[-1]['keywords'] = keywords

        pattern = line_start + ct('--- label: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            data[-1]['label'] = m.group(1).strip()

        pattern = line_start + bct('quiz choice (\d+) \((right|wrong)\)', cp) + '(.+?)' + ect('quiz choice .+?', cp)
        choices = re.findall(pattern, quiz, flags=re.MULTILINE|re.DOTALL)
        data[-1]['choices'] = []
        data[-1]['choice prefix'] = [None]*len(choices)
        for i, right, choice in choices:
            choice = choice.strip()
            # choice can be of the form [Solution:] Here goes the text...
            m = re.search(prefix_pattern, choice)
            if m:
                prefix = m.group(1).strip()
                choice = re.sub(prefix_pattern, '', choice).strip()
                data[-1]['choice prefix'][int(i)-1] = prefix
            data[-1]['choices'].append([right, choice])
        # Include choice prefix only if it is needed
        if data[-1]['choice prefix'] == [None]*len(choices):
            del data[-1]['choice prefix']
        pattern = line_start + bct('explanation of choice (\d+)', cp) + '(.+?)' + ect('explanation of choice \d+', cp)
        explanations = re.findall(pattern, quiz, flags=re.MULTILINE|re.DOTALL)
        for i_str, explanation in explanations:
            i = int(i_str)
            try:
                data[-1]['choices'][i-1].append(explanation.strip())
            except IndexError:
                print """
*** error: quiz question
"%s"
has choices
%s
Something is wrong with the matching of choices and explanations
(compare the list above with the source code of the quiz).
This is a bug or wrong quiz syntax.

The raw code of this quiz at this stage of processing reads

%s
""" % (data[-1]['question'], data[-1]['choices'], quiz)
                _abort()

    return data, quizzes, filestr

def typeset_quizzes2(filestr, format):
    quizzes, html_quizzes, filestr = extract_quizzes(filestr, format)
    debugpr('The file after extracting quizzes, before inserting finally rendered quizzes', filestr)
    lines = filestr.splitlines()
    for i in range(len(lines)):
        m = re.search(r'^(\d+) ' + _QUIZ_BLOCK, lines[i])
        if m:
            n = int(m.group(1))
            quiz = quizzes[n]
            text = QUIZ[format](quiz)
            debugpr('Quiz no. %d data structure' % n, pprint.pformat(quiz))
            lines[i] = text
    filestr = '\n'.join(lines)
    # This alternative method with re.sub has side effects since
    # \f, \b in text are interpreted as special symbols.
    # That is why we use the method above of exact replacement.
    #filestr = re.sub(r'^%d ' % i , text, filestr,
    #                 flags=re.MULTILINE)
    if encoding:
        f = codecs.open('.%s.quiz' % dofile_basename, 'w', encoding)
    else:
        f = open('.%s.quiz' % dofile_basename, 'w')
    try:
        text = pprint.pformat([dict(quiz) for quiz in quizzes])
        f.write(text)
    except UnicodeEncodeError as e:
        encode_error_message(e, text)
    f.close()
    if encoding:
        f = codecs.open('.%s.quiz.html' % dofile_basename, 'w', encoding)
    else:
        f = open('.%s.quiz.html' % dofile_basename, 'w')
    for quiz in html_quizzes:
        try:
            f.write(quiz + '\n\n')
        except UnicodeEncodeError as e:
            encode_error_message(e, quiz)
    f.close()

    # quiz inside admon does not work in rst/sphinx - check that
    if format in ('rst', 'sphinx'):
        pattern = r'^ +\.\. --- begin quiz question ---(.+)^ +\.\. --- end quiz question ---'
        questions = [q.strip() for q in
                     re.findall(pattern, filestr, flags=re.MULTILINE|re.DOTALL)]
        if questions:
            print '*** error: quiz inside admon is not possible with rst/sphinx'
            print '    edit these quizzes:'
            for q in questions:
                if encoding:
                    print 'Quiz:', q.encode(encoding)
                else:
                    print 'Quiz:', q
            _abort()
    return filestr

def inline_tag_subst(filestr, format):
    """Deal with all inline tags by substitution."""

    # Author syntax contains ampersands so all this must be processed
    # before ampersand1 and ampersand2 substitutions (and the pre/post hack
    # for ampersands in inline verbatim expressions)
    filestr = typeset_authors(filestr, format)

    # deal with DATE: today (i.e., find today's date)
    m = re.search(r'^(DATE:\s*[Tt]oday)', filestr, re.MULTILINE)
    if m:
        origstr = m.group(1)
        w = time.asctime().split()
        date = w[1] + ' ' + w[2] + ', ' + w[4]
        # Add copyright right under the date if present
        if format not in ('html', 'latex', 'pdflatex', 'sphinx'):
            from common import get_copyfile_info
            cr_text = get_copyfile_info(filestr, format=format)
            if cr_text is not None:
                if cr_text == 'Made with DocOnce':
                    date += '\n\nMade with DocOnce\n\n'
                else:
                    date += '\n\nCopyright ' + cr_text + '\n\n'
        filestr = filestr.replace(origstr, 'DATE: ' + date)

    # Hack for not typesetting ampersands inside inline verbatim text
    groups = re.findall(INLINE_TAGS['verbatim'], filestr, flags=re.MULTILINE)
    verbatims = ['`' + subst + '`'
                 for begin, dummy1, subst, end, dummy2 in groups]
    # Protect & inside `...` by transforming it to some marker text.
    # This change will be substituted back after ampersands1 and ampersands2
    # are substituted.
    marker_text = 'zzYYYampYYYzz?'
    verbatims_to_be_fixed = []
    for verbatim in verbatims:
        if '&' in verbatim:
            from_ = verbatim
            to_ = verbatim.replace('&', marker_text)
            filestr = filestr.replace(from_, to_)
    # Assumption: no ampersands in inline math (of ampersand1/2 type)

    debugpr('\n*** Inline tags substitution phase ***')

    # Do tags that require almost format-independent treatment such
    # that everything is conveniently defined here
    # 1. Quotes around normal text in LaTeX style:
    pattern = "``([^']+?)''"  # here we had [A-Za-z][lots of chars]*?, but ^' is much smarter and mathces locale chars too
    if format in ('html',):
        filestr = re.sub(pattern, '&quot;\g<1>&quot;', filestr)
    elif format not in ('pdflatex', 'latex'):
        filestr = re.sub(pattern, '"\g<1>"', filestr)

    # Treat tags that have format-dependent typesetting

    ordered_tags = [
        'horizontal-rule',  # must be done before sections (they can give ---- in some formats)
        'title',
        'date',
        'movie',
        #'figure',  # done separately
        'inlinecomment',
        'abstract',  # must become before sections since it tests on ===
        'keywords',  # must become after abstract since abstract tests on KEYWORdS
        'emphasize', 'math2', 'math',
        'bold',
        'ampersand2',  # must come before ampersand1 (otherwise ampersand1 recognizes ampersand2 regex)
        'ampersand1',
        'colortext',
        'verbatim',
        'emoji',
        'paragraph',  # after bold and emphasize
        'plainURL',   # must come before linkURL2 to avoid "URL" as link name
        'linkURL2v',
        'linkURL3v',
        'linkURL2',
        'linkURL3',
        'linkURL',
        'chapter', 'section', 'subsection', 'subsubsection',
        'linebreak',
        'non-breaking-space',  # must become after math, colortext, links, etc
        ]
    if option('no_ampersand_quote'):
        ordered_tags.remove('ampersand1')
        ordered_tags.remove('ampersand2')

    for tag in ordered_tags:
        debugpr('\n*************** Working with tag "%s"' % tag)
        tag_pattern = INLINE_TAGS[tag]
        #print 'working with tag "%s" = "%s"' % (tag, tag_pattern)
        if tag in ('abstract',):
            c = re.compile(tag_pattern, re.MULTILINE|re.DOTALL)
        elif tag in ('inlinecomment',):
            c = re.compile(tag_pattern, re.DOTALL)
        else:
            c = re.compile(tag_pattern, re.MULTILINE)
        try:
            replacement = INLINE_TAGS_SUBST[format][tag]
        except KeyError:
            continue  # just ignore missing tags in current format
        if replacement is None:
            continue  # no substitution

        if tag == 'emoji' and option('no_emoji'):
            replacement = ''

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

    # Hack: substitute marker text for ampersand back
    filestr = filestr.replace(marker_text, '&')

    return filestr

def subst_away_inline_comments(filestr):
    # inline comments: [hpl: this is a comment]
    pattern = INLINE_TAGS['inlinecomment']
    filestr = re.sub(pattern, '', filestr, flags=re.DOTALL|re.MULTILINE)
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
            if '/' in html_output:
                print '*** error: --html_output=%s cannot specify another directory\n    %s' % (html_output, os.path.dirname(html_output))
                _abort()
            basename = html_output
        # Initialize the doc's file collection
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
    try:
        filestr = f.read()
    except UnicodeDecodeError as e:
        print 'Cannot read file:', in_filename, str(e)
        _abort()
    f.close()

    if not filestr:
        print '*** error: empty file', in_filename
        print '    something went wrong with Preprocess/Mako'
        _abort()

    if in_filename.endswith('.py') or in_filename.endswith('.py.do.txt'):
        filestr = doconce2format4docstrings(filestr, format)
    else:
        filestr = doconce2format(filestr, format)

    out_filename = basename + FILENAME_EXTENSION[format]

    if encoding:
        f = codecs.open(out_filename, 'w', encoding)
    else:
        f = open(out_filename, 'w')


    try:
        f.write(filestr)
    except UnicodeEncodeError, e:
        # Provide error message and abortion, because the code
        # below that tries UTF-8 will result in strange characters
        # in the output. It is better that the user specifies
        # correct encoding and gets correct results.
        encode_error_message(e, filestr)
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

global _t0, _t1

def doconce2format(filestr, format):
    global _t0, _t1
    _t0 = _t1 = time.time()
    verbose = int(option('verbose=', 0))
    if verbose == 0:
        report_cpu_time = 15
    elif verbose == 1:
        report_cpu_time = 5
    elif verbose == 2:
        report_cpu_time = 0
    else:
        report_cpu_time = 15

    def report_progress(msg):
        """Write a message about the progress if CPU time of a task takes time."""
        global _t1
        cpu_accumulated = time.time() - _t0
        cpu_last_task = time.time() - _t1
        _t1 = time.time()
        if cpu_last_task > report_cpu_time:
            print '\n...doconce translation:', msg, '%.1f s' % cpu_last_task, '(accumulated time: %.1f)' % cpu_accumulated
            time.sleep(1)

    report_progress('finished preprocessors')

    if option('syntax_check=', 'on') == 'on':
        filestr = fix(filestr, format, verbose=1)
        syntax_check(filestr, format)
        report_progress('handled syntax checks')

    global FILENAME_EXTENSION, BLANKLINE, INLINE_TAGS_SUBST, CODE, \
           LIST, ARGLIST,TABLE, EXERCISE, FIGURE_EXT, CROSS_REFS, INDEX_BIB, \
           TOC, ENVIRS, INTRO, OUTRO

    for module in html, latex, pdflatex, rst, sphinx, st, epytext, plaintext, gwiki, mwiki, cwiki, pandoc, ipynb, xml, matlabnb:
        #print 'calling define function in', module.__name__
        module.define(
            FILENAME_EXTENSION,
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
            QUIZ,
            INTRO,
            OUTRO,
            filestr)

    # -----------------------------------------------------------------

    # Translate from Markdown syntax if that is requested
    if option('markdown'):
        filestr = markdown2doconce(filestr, format)
        fname = option('md2do_output=', None)
        if fname is not None:
            f = open(fname, 'w')
            f.write(filestr)

    # Next step: standardize newlines
    filestr = re.sub(r'(\r\n|\r|\n)', '\n', filestr)

    # Check that all eqrefs have labels in tex blocks (\label{})
    if option('labelcheck=', 'off') == 'on':
        num_problems = 0
        labels = re.findall(r'label\{(.+?)\}', filestr)
        refs = re.findall(r'ref\{(.+?)\}', filestr)
        missing_labels = []
        for ref in refs:
            if not ref in labels:
                if ref not in missing_labels:
                    missing_labels.append(ref)
        if missing_labels:
            print '*** error: ref{} has no corresponding label{}:'
            print '\n'.join(missing_labels)
            print '    reasons:'
            print '1.  maybe ref{} is already inside a generalized reference ref[][][]'
            print '2.  maybe ref{} is needed in a generalized reference ref[][][]'
            print '3.  this compatibility test is not useful - turn off by --labelcheck=off'
            _abort()

    # Next step: first reformatting of quizzes
    filestr, num_quizzes = typeset_quizzes1(
        filestr, insert_missing_quiz_header=False)
    if num_quizzes:
        debugpr('The file after first reformatting of quizzes:', filestr)
        report_progress('handled first reformatting of quizzes')

    # Next step: run operating system commands and insert output
    filestr, num_commands = insert_os_commands(filestr, format)
    debugpr('The file after running @@@OSCMD (from file):', filestr)
    if num_commands:
        report_progress('handled @@@OSCMD executions')

    # Next step: insert verbatim code from other (source code) files:
    # (if the format is latex, we could let ptex2tex do this, but
    # the CODE start@stop specifications may contain uderscores and
    # asterix, which will be replaced later and hence destroyed)
    #if format != 'latex':
    filestr, num_files = insert_code_from_file(filestr, format)
    debugpr('The file after inserting @@@CODE (from file):', filestr)

    if num_files:
        report_progress('handled @@@CODE copying')

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

    # If ipynb is to make use of Image or movie objects, this results in
    # a living cell and hence a verbatim block, and figures/movies must be
    # interpreted before such blocks are removed.
    call_handle_figures = False  # indicates if handle_figures has been called here or not
    if format == 'ipynb':
        if 'FIGURE:' in filestr and option('ipynb_figure=', 'md') == 'Image':
            call_handle_figures = True
        if option('figure_prefix=') is not None or \
           option ('movie_prefix=') is not None:
            call_handle_figures = True
        if call_handle_figures:
            filestr = handle_figures(filestr, format)
        if 'MOVIE:' in filestr:
            filestr = re.sub(INLINE_TAGS['movie'],
                             INLINE_TAGS_SUBST[format]['movie'],
                             filestr, flags=re.MULTILINE)


    # Next step: deal with user-defined environments
    if '!bu-' in filestr:
        filestr = typeset_userdef_envirs(filestr, format)
        debugpr('The file after inserting user-defined environments:', filestr)

    # Next step: remove all verbatim and math blocks

    filestr, code_blocks, code_block_types, tex_blocks = \
             remove_code_and_tex(filestr, format)

    if format in ('html', 'sphinx', 'ipynb', 'matlabnb'):
        tex_blocks = add_labels_to_all_numbered_equations(tex_blocks)
        # needed for the split functionality when all user-defined labels are
        # given tags, then we need labels in all environments that will
        # create equation numbers


    debugpr('The file after removal of code/tex blocks:', filestr)
    def print_blocks(blocks, delimiter=True):
        s = ''
        for i in range(len(blocks)):
            s += str(i)
            if delimiter:
                s+= ':\n'
            s += blocks[i]
            if delimiter:
                s+= '\n------------'
            s+= '\n'
        return s

    debugpr('The code blocks:', print_blocks(code_blocks))
    debugpr('The code block types:', print_blocks(code_block_types, False))
    debugpr('The tex blocks:', print_blocks(tex_blocks))

    report_progress('removed all verbatim and latex blocks')

    # Next step: substitute latex-style newcommands in filestr and tex_blocks
    # (not in code_blocks)
    from expand_newcommands import expand_newcommands
    if format not in ('latex', 'pdflatex'):
        newcommand_files = glob.glob('newcommands*_replace.tex')
        if format in ('sphinx', 'pandoc', 'ipynb'):
            # replace all newcommands in these formats
            # (none of them likes a bulk of newcommands, only latex and html)
            newcommand_files = [name for name in glob.glob('newcommands*.tex')
                                if not name.endswith('.p.tex')]
            # (note: could use substitutions (|newcommand|) in rst/sphinx,
            # but they don't allow arguments so expansion of \newcommand
            # is probably a better solution)
        filestr = expand_newcommands(newcommand_files, filestr) # inline math
        for i in range(len(tex_blocks)):
            tex_blocks[i] = expand_newcommands(newcommand_files, tex_blocks[i])

    # Check URLs to see if they are valid
    if option('urlcheck'):
        urlcheck(filestr)

    # Comment out title, author, date?
    if option('no_title'):
        for tag in 'TITLE', 'AUTHOR', 'DATE':
            filestr = re.sub(r'^%s:' % tag, '#%s:' % tag,
                             filestr, flags=re.MULTILINE)

    # Lift sections up or down?
    s2name = {9: 'chapter', 7: 'section',
              5: 'subsection', 3: 'subsubsection'}
    section_level_changed = False
    if option('sections_up'):
        for s in 7, 5, 3:
            header_old = '='*s
            header_new = '='*(s+2)
            print 'transforming sections: %s to %s...' % (s2name[s], s2name[s+2])
            pattern = r'^ *%s +(.+?) +%s' % (header_old, header_old)
            replacement = r'%s \g<1> %s' % (header_new, header_new)
            filestr = re.sub(pattern, replacement, filestr, flags=re.MULTILINE)
        section_level_changed = True
    if option('sections_down'):
        for s in 5, 7, 9:
            header_old = '='*s
            header_new = '='*(s-2)
            print 'transforming sections: %s to %s...' % (s2name[s], s2name[s-2])
            pattern = r'^ *%s +(.+?) +%s' % (header_old, header_old)
            replacement = r'%s \g<1> %s' % (header_new, header_new)
            filestr = re.sub(pattern, replacement, filestr, flags=re.MULTILINE)
        section_level_changed = True

    if section_level_changed:
        # Fix Exercise, Problem, Project, Example - they must be 5=
        for s in 7, 3:
            filestr = re.sub(r'^ *%s +(\{?(Exercise|Problem|Project|Example)\}?):\s*(.+?) +%s' % ('='*s, '='*s), '===== \g<1>: \g<3> =====', filestr, flags=re.MULTILINE)
        debugpr('The file after changing the level of section headings:', filestr)

    # Next step: section numbering?
    if format not in ('latex', 'pdflatex'):
        if option('section_numbering=', 'off') == 'on':
            filestr = typeset_section_numbering(filestr, format)

    # Remove linebreaks within paragraphs
    if option('oneline_paragraphs'):  # (does not yet work well)
        filestr = make_one_line_paragraphs(filestr, format)

    # Remove inline comments
    if option('skip_inline_comments'):
        filestr = subst_away_inline_comments(filestr)
    else:
        # Number inline comments
        inline_comments = re.findall(INLINE_TAGS['inlinecomment'], filestr,
                                     flags=re.DOTALL)
        counter = 1
        for name, space, comment in inline_comments:
            filestr = filestr.replace(
                '[%s:%s%s]' % (name, space, comment),
                '[%s %d: %s]' % (name, counter, comment))
            counter += 1


    # Remove comments starting with ##
    pattern = r'^##.+$\n'
    filestr = re.sub(pattern, '', filestr, flags=re.MULTILINE)
    # (This is already done by Mako, if the document has Mako markup)

    # Fix stand-alone http(s) URLs (after verbatim blocks are removed,
    # but before figure handling and inline_tag_subst)
    pattern = r' (https?://.+?)([ ,?:;!)\n])'
    filestr = re.sub(pattern, ' URL: "\g<1>"\g<2>', filestr)

    # Next step: deal with exercises
    filestr = exercises(filestr, format, code_blocks, tex_blocks)

    debugpr('The file after handling exercises:', filestr)

    # Next step: deal with figures
    if format != 'ipynb' or not call_handle_figures:
        filestr = handle_figures(filestr, format)
    # else: ipynb figures/movies must be handled early above

    report_progress('figures')
    debugpr('The file after handling figures:', filestr)

    # Next step: deal with cross referencing (must occur before other format subst)
    filestr = handle_cross_referencing(filestr, format)

    debugpr('The file after handling ref and label cross referencing:', filestr)
    # Next step: deal with index and bibliography (must be done before lists):
    filestr = handle_index_and_bib(filestr, format)

    debugpr('The file after handling index and bibliography:', filestr)


    # Next step: deal with lists
    filestr = typeset_lists(filestr, format,
                            debug_info=[code_blocks, tex_blocks])
    debugpr('The file after typesetting of lists:', filestr)

    report_progress('handled lists')

    # Next step: add space around | in tables for substitutions to get right
    filestr, inserted_space_around_pipe = space_in_tables(filestr)
    if inserted_space_around_pipe:
        debugpr('The file after adding space around | in tables:', filestr)

    # Next step: do substitutions
    filestr = inline_tag_subst(filestr, format)
    debugpr('The file after all inline substitutions:', filestr)

    report_progress('inline substitutions')

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

    # Add header and footer if not an HTML template is specified or if
    # header and footer is turned off by --no_header_footer
    if not option('no_header_footer') and \
           option('html_template=', default='') == '':
        if format in INTRO:
            try:
                filestr = INTRO[format] + filestr
            except UnicodeDecodeError:
                # Title etc may contain non-ascii characters
                if not option('encoding=', '').lower() == 'utf-8':
                    print '*** error: found non-ascii character(s). Try --encoding=utf-8'
                    _abort()
        if format in OUTRO:
            filestr = filestr + OUTRO[format]


    # Need to treat quizzes for ipynb before code and text blocks are inserted
    if num_quizzes and format == 'ipynb':
        filestr = typeset_quizzes2(filestr, format)
        debugpr('The file after second reformatting of quizzes:', filestr)
        report_progress('handled second reformatting of quizzes')

    # Fix for amounts in dollars: latex requires \$, but the backslash
    # must be removed for all other formats
    if format not in ('latex', 'pdflatex'):
        filestr = re.sub(r'\\\$([\d.,]+\s)', r'$\g<1>', filestr)

    # Next step: insert verbatim and math code blocks again and
    # substitute code and tex environments:
    # (this is the place to do package-specific fixes too!)
    filestr = CODE[format](filestr, code_blocks, code_block_types,
                           tex_blocks, format)
    filestr += '\n'

    report_progress('insertion of verbatim and latex blocks')

    debugpr('The file after inserting intro/outro and tex/code blocks, and fixing last format-specific issues:', filestr)

    # Next step: deal with !b... !e... environments
    # (done after code and text to ensure correct indentation
    # in the formats that applies indentation)
    filestr = typeset_envirs(filestr, format)

    report_progress('!benvir/!eenvir constructions')

    debugpr('The file after typesetting of admons and the rest of the !b/!e environments:', filestr)

    # Check if we have wrong-spelled environments
    if not option('examples_as_exercises'):
        pattern = r'^(![be].+)'
        m = re.search(pattern, filestr, flags=re.MULTILINE)
        if m:
            # Found, but can be inside code block (should have |[be].+ then)
            # and hence not necessarily an error
            envir = m.group(1)
            print '*** error: could not translate environment: %s' % envir
            if m.group(1)[2:] in ('sol', 'ans', 'hint', 'subex'):
                print '    This is an environment in an exercise. Check if the'
                print '    heading is correct so the subsection was recognized'
                print '    as Exercise, Problem, or Project (Exercise: title).'
            else:
                print '    possible reasons:'
                print '     * syntax error in environment name'
                print '     * environment inside code: use | instead of !'
                print '     * or bug in doconce'

            print '    context:\n'
            print filestr[m.start()-50:m.end()+50]
            _abort()


    # Next step: change \bm{} to \boldsymbol{} for all MathJax-based formats
    # (must be done before math blocks are removed and again after
    # newcommands files are inserted)
    filestr = bm2boldsymbol(filestr, format)

    # Next step: replace environments starting with | (instead of !)
    # by ! (for illustration of doconce syntax inside !bc/!ec directives).
    # Enough to consider |bc, |ec, |bt, and |et since all other environments
    # are processed when code and tex blocks are removed from the document.
    if '|b' in filestr or '|e' in filestr:
        for envir in doconce_envirs():
            filestr = filestr.replace('|b' + envir, '!b' + envir)
            filestr = filestr.replace('|e' + envir, '!e' + envir)

        debugpr('The file after replacing |bc and |bt environments by true !bt and !et (in code blocks):', filestr)

    # Second reformatting of quizzes
    if num_quizzes and format != 'ipynb':
        filestr = typeset_quizzes2(filestr, format)
        debugpr('The file after second reformatting of quizzes:', filestr)
        report_progress('handled second reformatting of quizzes')

    if format == 'html':
        # Set value for URL to raw github (doconce) files
        # (must be done at this late stage)
        rawgit = option('html_raw_github_url=', 'safe')
        if rawgit in ('safe', 'cdn.rawgit'):
            raw_github_url = 'https://cdn.rawgit.com'
        elif rawgit in ('test', 'rawgit'):
            raw_github_url = 'https://rawgit.com'
        elif rawgit in ('github', 'raw.github'):
            raw_github_url = 'https://raw.github.com'
        elif rawgit in ('githubusercontent', 'raw.githubusercontent'):
            raw_github_url = 'https://raw.githubusercontent.com'
        filestr = filestr.replace('RAW_GITHUB_URL', raw_github_url)
        if option('html_DOCTYPE'):
            filestr = '<!DOCTYPE HTML>\n' + filestr
        if option('xhtml'):
            try:
                from bs4 import BeautifulSoup as BS
            except ImportError:
                print '*** error: for --xhtml the bs4 BeautifulSoup package must be installed'
                print '    pip install beautifulsoup4'
                _abort()
            soup = BS(filestr, 'lxml')
            # soup can be used to rewrite the entire doc
            filestr = soup.prettify()


    # Next step: remove exercise solution/answers, notes, etc
    # (Note: must be done after code and tex blocks are inserted!
    # Otherwise there is a mismatch between all original blocks
    # and those present after solutions, answers, etc. are removed)
    envir2option = dict(sol='solutions', ans='answers', hint='hints')
    # Recall that the comment syntax is now dependent on the format
    for envir in 'sol', 'ans', 'hint':
        option_name = 'without_' + envir2option[envir]
        if option(option_name):
            filestr = process_envir(
                filestr, envir, format, action='remove',
                reason='(because of the command-line option --%s)\n' % option_name)

    debugpr('The file after potential removal of solutions, answers, hints, etc.:', filestr)

    cpu = time.time() - _t0
    if cpu > 15:
        print '\n\n...doconce format used %.1f s to translate the document (%d lines)\n' % (cpu, filestr.count('\n'))
        time.sleep(1)

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

    # Standardize newlines
    filestr = re.sub(r'(\r\n|\r|\n)', '\n', filestr)

    preprocessor = None

    # First guess if preprocess or mako is used

    # Collect first -Dvar=value options on the command line
    preprocess_options = [opt for opt in preprocessor_options
                          if opt[:2] == '-D']
    if option('preprocess_include_subst'):
        # Substitute -DVAR=value: VAR -> value in the text
        # (same as doconce replace VAR value)
        preprocess_options.append('-i')

    # Add quotes to -DVAR=value options: -DVAR="value"
    for i in range(len(preprocess_options)):
        opt = preprocess_options[i]
        if opt.startswith('-D'):
            if '=' in opt and not '="' in opt:  # no quotes seemingly
                parts = opt.split('=')
                opt = '%s="%s"' % (parts[0], parts[1])
                preprocess_options[i] = opt

    # Add -D to mako name=value options so that such variables
    # are set for preprocess too (but enclose value in quotes)
    for opt in preprocessor_options:
        if opt[0] != '-' and '=' in opt:
            try:
                words = opt.split('=')
                var = words[0]
                value = '='.join(words[1:])
            except ValueError:
                print '*** error: illegal command-line argument:'
                print opt
                _abort()
            if value == 'False':
                pass # do not add any -Uvar since -U is not used by preprocess
                #preprocess_options.append('-U%s' % var)
            elif value == "True":
                preprocess_options.append('-D%s' % var)
            else:  # add explicit value
                preprocess_options.append('-D%s="%s"' % (var, value))

    # Look for mako variables
    mako_kwargs = {'FORMAT': format, 'DEVICE': device}
    for opt in preprocessor_options:
        if opt.startswith('-D'):
            opt2 = opt[2:]
            if '=' in opt:
                key, value = opt2.split('=')
                if value in ('True', 'False'):
                    value = eval(value)  # make it bool
            else:
                key = opt2;  value = True
        elif not opt.startswith('--'):
            # This is assumed to be key=value
            # Treat value as string except if it is True or False
            # or consists solely of digits
            try:
                words = opt.split('=')
                key = words[0]
                value = '='.join(words[1:])
                if value in ('True', 'False'):
                    value = eval(value)  # make it bool
                elif value.isdigit():
                    value = int(value)
            except ValueError:
                print 'command line argument "%s" not recognized' % opt
                _abort()
        else:
            key = None

        if key is not None:
            # evaluate value if it has the form eval('something')
            if isinstance(value, str) and value.startswith('eval('):
                try:
                    mako_kwargs[key] = eval(value[5:-1])
                except (NameError, TypeError, SyntaxError) as e:
                    print '*** error: %s=%s imples running eval, but this failed' % (key, value)
                    print '    ', str(e)
                    _abort()
            else:
                mako_kwargs[key] = value

            # No, this fails if value=input or something defined in python
            # Work with just strings and use key='eval(something)' instead

    resultfile = 'tmp_preprocess__' + filename
    resultfile2 = 'tmp_mako__' + filename

    filestr_without_code, code_blocks, code_block_types, tex_blocks = \
                          remove_code_and_tex(filestr, format)

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
            try:
                output = subprocess.check_output(cmd, shell=True,
                                                 stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print 'Could not run preprocessor:\n%s' % cmd
                print e.output
                print 'return code from preprocess:', e.returncode
                _abort()
            # Make filestr the result of preprocess in case mako shall be run
            f = open(resultfile, 'r'); filestr = f.read(); f.close()
            # Standardize newlines
            filestr = re.sub(r'(\r\n|\r|\n)', '\n', filestr)
            filestr_without_code, code_blocks, code_block_types, tex_blocks = \
                                  remove_code_and_tex(filestr, format)

    mako_commands = r'^ *<?%[^%]'
    # Problem: mako_commands match Matlab comments and SWIG directives,
    # so we need to remove code blocks for testing if we really use
    # mako. Also issue warnings if code blocks contain mako instructions
    # matching the mako_commands pattern
    match_percentage = re.search(mako_commands, filestr_without_code,
                                 re.MULTILINE)  # match %
    if match_percentage:
        debugpr('Found use of %% sign(s) for mako code in %s:\n%s' % (resultfile, ', '.join(re.findall(mako_commands, filestr_without_code))))

    match_mako_variable = False  # See if we use a mako variable
    for name in mako_kwargs:
        pattern = r'\$\{%s\}' % name  # ${name}
        if re.search(pattern, filestr_without_code):
            match_mako_variable = True  # command-line variable is used
            debugpr('Found use of mako variable(s) in %s: %s' % (resultfile, ', '.join(re.findall(pattern, filestr_without_code))))
            break
        pattern = r'\b%s\b' % name    # e.g. % if name == 'a' (or Python code)
        if re.search(pattern, filestr_without_code):
            match_mako_variable = True
            debugpr('Found use of mako variable(s) in mako code in %s: %s' % (resultfile, ', '.join(re.findall(pattern, filestr_without_code))))
            break
    if not match_mako_variable and not match_percentage:
        # See if we use a mako function/variable construction
        # when there is no <%...%> block
        if re.search(r'\$\{', filestr):
            m = re.search(r'(\$\{.+?\})', filestr, flags=re.DOTALL)
            if m:
                print '*** error: file has a mako construction %s' % m.group(1)
                print '    but seemingly no definition in <%...%>'
                print '    (it is not a command-line given mako variable either)'
                print '''    (however: if this is a variable in a Makefile or Bash script,
    run with --no_mako - and you cannot use mako and Makefile or Bash variables
    in the same document!)'''
                if not option('no_mako'):
                    _abort()

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
The above code block contains "%s" on the *beginning of a line*.
Such lines cause problems for the mako preprocessor
since it thinks this is a mako statement.
''' % (m.group(0))
                print
                mako_problems = True
        if mako_problems:
            print '''\
Use %% in the code block(s) above to fix the problem with % at the
*very* beginning of lines (column 1), otherwise (in case of blanks
first on the line) use the construction ${'%'}, or put the code in
a file that is included with @@@CODE filename, or drop mako instructions
or variables and rely on preprocess only in the preprocessing step.
Including --no_mako on the command line avoids running mako.
(If you have % in code, you can also see if it is possible to move
the % char away from the beginning of the line.)
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
                elif formula[1:7] == r'\cal O}':
                    suggestion = r'as \newcommand{\Oof}[1]{{\cal O}{#1}}'
                elif re.search(r'^\{[A-Za-z0-9_]+\}', formula):  # Mako variable?
                    break
                elif re.search(r'^\{[A-Za-z0-9_]+\(', formula):  # Mako func?
                    break
                else:
                    suggestion = 'or make a newcommand'
                print """\
*** error: potential problem with the math formula
           $%s$
    since ${ can confuse Mako - rewrite %s""" % (formula, suggestion)
                if formula.startswith('${\cal'):
                    print r'Here: use \mathcal{...} instead of {\cal ...}'
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

If you have pip installed, do

   sudo pip install mako

On Debian (incl. Ubuntu) systems, you can alternatively do

   sudo apt-get install python-mako
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
            try:
                filestr = unicode(filestr, encoding)
            except UnicodeDecodeError as e:
                if "unicode codec can't decode" in str(e):
                    print e
                    index = int(str(e).split('in position')[1].split(':')[0])
                    print filestr[index-50:index] + '  (problematic char)  ' + filestr[index+1:index+50]
                _abort()
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
                print '    doconce find_nonascii_chars can be used to identify non-ascii characters (use it on %s or tmp_mako__%s' % (orig_filename, orig_filename)
            elif "line:" in str(e):
                print '    Note: the line number refers to the file', resultfile2
            _abort()

        debugpr('Keyword arguments to be sent to mako: %s' % \
                pprint.pformat(mako_kwargs))
        if preprocessor_options:
            print 'mako variables:', mako_kwargs

        try:
            filestr = temp.render(**mako_kwargs)
        except TypeError as e:
            if "'Undefined' object is not callable" in str(e):
                calls = '\n'.join(re.findall(r'(\$\{[A-Za-z0-9_ ]+?\()[^}]+?\}', filestr))
                print '*** mako error: ${func(...)} calls undefined function "func",\ncheck all ${...} calls in the file(s) for possible typos and lack of includes!\n%s' % calls
                _abort()
            else:
                # Just dump everything mako has
                print '*** mako error:'
                filestr = temp.render(**mako_kwargs)


        except NameError as e:
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

        except UnicodeDecodeError as e:
            if "can't decode byte" in str(e):
                print '*** error when running mako: UnicodeDecodeError'
                print e
                index = int(str(e).split('position')[1].split(':')[0])
                # index==0 is often a misleading info
                if index > 0:
                    print filestr[index-50:index], ' -- problematic char -- ', filestr[index+1:index+50]
                    print 'ord(problematic char)=%d' % ord(filestr[0])
                _abort()
            else:
                # Just dump everything mako has
                print '*** mako error:'
                filestr = temp.render(**mako_kwargs)
        except SystemExit as e:
            # Just dump everything mako has
            print '*** mako SystemExit exception:', e
            filestr = temp.render(**mako_kwargs)
        except:
            print '*** mako error: mako terminated with exception', sys.exc_info()[0]
            # Just dump everything mako has
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
        import common
        common.format = format
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

    # Treat some synonyms of format
    if format == 'markdown':
        format = 'pandoc'

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

    dirname, basename = os.path.split(filename)
    if dirname:
        os.chdir(dirname)
        print '*** doconce format now works in directory %s' % dirname
    basename, ext = os.path.splitext(basename)
    # Can allow no extension, .do, or .do.txt
    legal_extensions = ['.do', '.do.txt']
    if ext == '':
        found = False
        for ext in legal_extensions:
            filename = basename + ext
            if os.path.isfile(filename):
                found = True
                break
        if not found:
            print '*** error: given doconce file "%s", but no' % basename
            print '    files with extensions %s exist' % ' or '.join(legal_extensions)
            _abort()
    else:
        # Given extension
        if not os.path.isfile(filename):
            print '*** error: file %s does not exist' % filename
            _abort()
        if ext == '.txt':
            if filename.endswith('.do.txt'):
                basename = filename[:-7]
            else: # just .txt
                basename = filename[:-4]
        elif ext == '.do':
            basename = filename[:-3]
        else:
            print '*** error: illegal file extension %s' % ext
            print '    must be %s' % ' or '.join(legal_extensions)
            _abort()

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
    print 'output in', os.path.join(dirname, out_filename)


class DocOnceSyntaxError(Exception):
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
    try:
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print 'Execution of "%s" failed!\n' % cmd
        raise DocOnceSyntaxError('Could not run %s.\nOutput:\n%s' %
                                 (cmd, e.output))
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
