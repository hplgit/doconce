"""
See http://johnmacfarlane.net/pandoc/README.html
for syntax.
"""

import re, sys
from common import default_movie, plain_exercise, table_analysis, \
     insert_code_and_tex, bibliography
from html import html_movie, html_table
from misc import option

def pandoc_title(m):
    title = m.group('subst')
    if option('strapdown'):
        # title is in <title> tag in INTRO for the header of the HTML output
        return ''
    elif option('strict_markdown_output'):
        return '# ' + title
    elif option('multimarkdown_output'):
        return 'Title: ' + title
    else:
        return '% ' + title

def pandoc_author(authors_and_institutions, auth2index,
                 inst2index, index2inst, auth2email):
    # List authors on multiple lines
    authors = []
    for author, i, e in authors_and_institutions:
        author = '**%s**' % author  # set in boldface
        if i is None:
            authors.append(author)
        else:
            authors.append(author + ' at ' + ' and '.join(i))

    plain_text = '### Author'
    if len(authors) > 1:
        plain_text += 's'
    plain_text += '\n\n' + '\n\n'.join(authors) + '\n\n'

    if option('strapdown'):
        return plain_text
    elif option('strict_markdown_output'):
        return plain_text
    elif option('multimarkdown_output'):
        return 'Author: ' + ', '.join(authors) + '\n'
    else:
        return '% ' + ';  '.join(authors) + '\n'


def pandoc_code(filestr, code_blocks, code_block_types,
                tex_blocks, format):
    # Note: the tex code require the MathJax fix of doconce md2html
    # to insert right MathJax extensions to interpret align and labels
    # correctly.
    # (Also, doconce.py runs align2equations so there are no align/align*
    # environments in tex blocks.)
    for i in range(len(tex_blocks)):
        # Remove latex envir in single equations
        tex_blocks[i] = tex_blocks[i].replace(r'\[', '')
        tex_blocks[i] = tex_blocks[i].replace(r'\]', '')
        tex_blocks[i] = tex_blocks[i].replace(r'\begin{equation*}', '')
        tex_blocks[i] = tex_blocks[i].replace(r'\end{equation*}', '')
        #tex_blocks[i] = tex_blocks[i].replace(r'\[', '$$')
        #tex_blocks[i] = tex_blocks[i].replace(r'\]', '$$')
        # Check for illegal environments
        m = re.search(r'\\begin\{(.+?)\}', tex_blocks[i])
        if m:
            envir = m.group(1)
            if envir not in ('equation', 'equation*', 'align*', 'align'):
                print """\
*** warning: latex envir \\begin{%s} does not work well.
""" % envir
        # Add $$ on each side of the equation
        tex_blocks[i] = '$$\n' + tex_blocks[i] + '$$\n'
    # Note: HTML output from pandoc requires $$ while latex cannot have
    # them if begin-end inside ($$\begin{...} \end{...}$$)

    if option('strict_markdown_output'):
        # Code blocks are just indented
        for i in range(len(code_blocks)):
            code_blocks[i] = indent_lines(code_blocks[i], format)

    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, format)

    if not option('strict_markdown_output'):
        # Mapping of envirs to correct Pandoc verbatim environment
        defs = dict(cod='Python', pycod='Python', cppcod='Cpp',
                    fcod='Fortran', ccod='C',
                    pro='Python', pypro='Python', cpppro='Cpp',
                    fpro='Fortran', cpro='C',
                    rbcod='Ruby', rbpro='Ruby',
                    plcod='Perl', plpro='Perl',
                    # sys, dat, csv, txt: no support for pure text,
                    # just use a plain text block
                    #sys='Bash',
                    pyoptpro='Python', pyscpro='Python')
            # (the "python" typesetting is neutral if the text
            # does not parse as python)

        github_md = option('github_md')

        # Code blocks apply the ~~~~~ delimiter, with blank lines before
        # and after
        for key in defs:
            language = defs[key]
            if github_md:
                replacement = '\n```%s\n' % defs[key]
            else:
                # pandoc-extended Markdown
                replacement = '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.%s}\n' % defs[key]
                #replacement = '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.%s ,numberLines}\n' % defs[key]  # enable line numbering
            filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                             replacement, filestr, flags=re.MULTILINE)

        # any !bc with/without argument becomes an unspecified block
        if github_md:
            replacement = '\n```'
        else:
            replacement = '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        filestr = re.sub(r'^!bc.*$', replacement, filestr, flags=re.MULTILINE)

        if github_md:
            replacement = '\n```\n'
        else:
            replacement = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        filestr = re.sub(r'^!ec\s*$', replacement, filestr, flags=re.MULTILINE)

    filestr = re.sub(r'^!bt *\n', '', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!et *\n', '', filestr, flags=re.MULTILINE)

    # \eqref and labels will not work, but labels do no harm
    filestr = filestr.replace(' label{', ' \\label{')
    pattern = r'^label\{'
    filestr = re.sub(pattern, '\\label{', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'\(ref\{(.+?)\}\)', r'\eqref{\g<1>}', filestr)

    # Final fixes

    # Seems that title and author must appear on the very first lines
    filestr = filestr.lstrip()

    # Enable tasks lists:
    #   - [x] task 1 done
    #   - [ ] task 2 not yet done
    if github_md:
        pattern = '^(\s+)\*\s+(\[[x ]\])\s+'
        filestr = re.sub(pattern, '\g<1>- \g<2> ', filestr, flags=re.MULTILINE)

    return filestr

def pandoc_table(table):
    if option('github_md'):
        text = html_table(table)
        # Fix the problem that `verbatim` inside the table is not
        # typeset as verbatim in the GitHub Issue Tracker
        text = re.sub(r'`([^`]+?)`', '<code>\g<1></code>', text)
        return text

    # else: Pandoc-extended Markdown syntax

        """

    Simple markdown tables look like this::

        Left         Right   Center     Default
        -------     ------ ----------   -------
        12              12     12            12
        123            123     123          123
        1                1      1             1

    """
    # Slight modification of rst_table

    column_width = table_analysis(table['rows'])
    ncolumns = len(column_width)
    column_spec = table.get('columns_align', 'c'*ncolumns).replace('|', '')
    heading_spec = table.get('headings_align', 'c'*ncolumns).replace('|', '')
    a2py = {'r': 'rjust', 'l': 'ljust', 'c': 'center'}
    s = ''  # '\n'
    for i, row in enumerate(table['rows']):
        #s += '    '  # indentation of tables
        if row == ['horizontal rule'] and i > 0 and i < len(table['rows'])-1:
            # No horizontal rule at the top and bottom, just after heading
            for w in column_width:
                s += '-'*w + '  '
        else:
            # check if this is a headline between two horizontal rules:
            if i == 1 and \
               table['rows'][i-1] == ['horizontal rule'] and \
               table['rows'][i+1] == ['horizontal rule']:
                headline = True
            else:
                headline = False

            for w, c, ha, ca in \
                    zip(column_width, row, heading_spec, column_spec):
                if headline:
                    s += getattr(c, a2py[ha])(w) + '  '
                elif row != ['horizontal rule']:
                    s += getattr(c, a2py[ca])(w) + '  '
        s += '\n'
    s += '\n'
    return s

def pandoc_figure(m):
    filename = m.group('filename')
    caption = m.group('caption').strip()
    text = '![%s](%s)' % (caption, filename)
    #print 'pandoc_figure:', text
    return text

def pandoc_ref_and_label(section_label2title, format, filestr):
    # .... see section ref{my:sec} is replaced by
    # see the section "...section heading..."
    pattern = r'[Ss]ection(s?)\s+ref\{'
    replacement = r'the section\g<1> ref{'
    filestr = re.sub(pattern, replacement, filestr)
    pattern = r'[Cc]hapter(s?)\s+ref\{'
    replacement = r'the chapter\g<1> ref{'
    filestr = re.sub(pattern, replacement, filestr)
    # Need special adjustment to handle start of sentence (capital) or not.
    pattern = r'([.?!])\s+the (sections?|captions?)\s+ref'
    replacement = r'\g<1> The \g<2> ref'
    filestr = re.sub(pattern, replacement, filestr)

    # Remove Exercise, Project, Problem in references since those words
    # are used in the title of the section too
    pattern = r'(the\s*)?([Ee]xercises?|[Pp]rojects?|[Pp]roblems?)\s+ref\{'
    replacement = r' ref{'
    filestr = re.sub(pattern, replacement, filestr)

    # Remove label{...} from output (when only label{} on a line, remove
    # the newline too, leave label in figure captions, and remove all the rest)
    #filestr = re.sub(r'^label\{.+?\}\s*$', '', filestr, flags=re.MULTILINE)
    cpattern = re.compile(r'^label\{.+?\}\s*$', flags=re.MULTILINE)
    filestr = cpattern.sub('', filestr)
    #filestr = re.sub(r'^(FIGURE:.+)label\{(.+?)\}', '\g<1>{\g<2>}', filestr, flags=re.MULTILINE)
    cpattern = re.compile(r'^(FIGURE:.+)label\{(.+?)\}', flags=re.MULTILINE)
    filestr = cpattern.sub('\g<1>{\g<2>}', filestr)
    filestr = re.sub(r'label\{.+?\}', '', filestr)  # all the remaining

    # Replace all references to sections. Pandoc needs a coding of
    # the section header as link.
    def title2pandoc(title):
        # http://johnmacfarlane.net/pandoc/README.html
        for c in ('?', ';', ':'):
            title = title.replace(c, '')
        title = title.replace(' ', '-').strip()
        start = 0
        for i in range(len(title)):
            if title[i].isalpha():
                start = i
        title = title[start:]
        title = title.lower()
        if not title:
            title = 'section'
        return title

    for label in section_label2title:
        filestr = filestr.replace('ref{%s}' % label,
                  '[%s](#%s)' % (section_label2title[label],
                                 title2pandoc(section_label2title[label])))

    return filestr


def pandoc_index_bib(filestr, index, citations, pubfile, pubdata):
    # pandoc citations are of the form
    # bla-bla, see [@Smith04, ch. 1; @Langtangen_2008]
    # Method: cite{..} -> [...], doconce.py has already fixed @ and ;
    filestr = re.sub(r'cite\{(.+?)\}', r'[\g<1>]', filestr)

    if pubfile is not None:
        bibtext = bibliography(pubdata, citations, format='doconce')
        filestr = re.sub(r'^BIBFILE:.+$', bibtext, filestr, flags=re.MULTILINE)

    # pandoc does not support index entries,
    # remove all index entries (could also place them
    # in special comments to keep the information)

    filestr = re.sub(r'idx\{.+?\}' + '\n?', '', filestr)
    return filestr

def pandoc_quote(block, format, text_size='normal'):
    # block quotes in pandoc start with "> "
    lines = []
    for line in block.splitlines():
        lines.append('> ' + line)
    return '\n'.join(lines) + '\n\n'

def define(FILENAME_EXTENSION,
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
           filestr):
    # all arguments are dicts and accept in-place modifications (extensions)

    FILENAME_EXTENSION['pandoc'] = '.md'
    BLANKLINE['pandoc'] = '\n'
    # replacement patterns for substitutions of inline tags
    INLINE_TAGS_SUBST['pandoc'] = {
        'math':      None,  # indicates no substitution, leave as is
        'math2':     r'\g<begin>$\g<latexmath>$\g<end>',
        'emphasize': None,
        'bold':      None,
        'figure':    pandoc_figure,
        #'movie':     default_movie,
        'movie':     html_movie,
        'verbatim':  None,
        #'linkURL':   r'\g<begin>\g<link> (\g<url>)\g<end>',
        'linkURL2':  r'[\g<link>](\g<url>)',
        'linkURL3':  r'[\g<link>](\g<url>)',
        'linkURL2v': r'[`\g<link>`](\g<url>)',
        'linkURL3v': r'[`\g<link>`](\g<url>)',
        'plainURL':  r'<\g<url>>',
        'colortext':     r'<font color="\g<color>">\g<text></font>',  # HTML
        # "Reference links" in pandoc are not yet supported
        'title':     pandoc_title,
        'author':    pandoc_author,
        'date':      '% \g<subst>\n',
        'chapter':       lambda m: '# '    + m.group('subst'),
        'section':       lambda m: '## '   + m.group('subst'),
        'subsection':    lambda m: '### '  + m.group('subst'),
        'subsubsection': lambda m: '#### ' + m.group('subst') + '\n',
        'paragraph':     r'*\g<subst>* ',  # extra blank
        'abstract':      r'*\g<type>.* \g<text>\n\n\g<rest>',
        'comment':       '<!-- %s -->',
        'linebreak':     r'\g<text>\\n',
        'non-breaking-space': '\\ ',
        }

    CODE['pandoc'] = pandoc_code
    ENVIRS['pandoc'] = {
        'quote':        pandoc_quote,
        }

    from common import DEFAULT_ARGLIST
    ARGLIST['pandoc'] = DEFAULT_ARGLIST
    LIST['pandoc'] = {
        'itemize':
        {'begin': '', 'item': '*', 'end': '\n'},

        'enumerate':
        {'begin': '', 'item': '%d.', 'end': '\n'},

        'description':
        {'begin': '', 'item': '%s\n  :   ', 'end': '\n'},

        'separator': '\n',
        }
    CROSS_REFS['pandoc'] = pandoc_ref_and_label

    TABLE['pandoc'] = pandoc_table
    INDEX_BIB['pandoc'] = pandoc_index_bib
    EXERCISE['pandoc'] = plain_exercise
    TOC['pandoc'] = lambda s: '# Table of contents: Run pandoc with --toc option'
    FIGURE_EXT['pandoc'] = ('.png', '.gif', '.jpg', '.jpeg', '.tif', '.tiff', '.pdf')

    # Wrap markdown output in strapdown HTML code for quick auto rendering
    # with Bootstrap themes?
    if option('strapdown'):
        # Themes
        boostrap_bootwatch_theme = option('bootwatch_theme=', 'spacelab')
        # Grab title
        title = ''
        if 'TITLE:' in filestr:
            for line in filestr.splitlines():
                if line.startswith('TITLE:'):
                    title = line.split('TITLE:')[-1].strip()
                    break
        INTRO['pandoc'] = """<!DOCTYPE html>
<html>
<title>%(title)s</title>

<xmp theme="%(boostrap_bootwatch_theme)s" style="display:none;">
# Markdown text goes in here
""" % vars()
        OUTRO['pandoc'] = """
</xmp>

<script src="http://strapdownjs.com/v/0.2/strapdown.js"></script>
</html>
"""

