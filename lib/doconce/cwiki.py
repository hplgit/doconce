"""
Creole Wiki (as used on bitbucket.org).
See http://www.wikicreole.org/wiki/Creole1.0 for syntax.
"""
from __future__ import absolute_import
from builtins import zip
# Simple edit of gwiki.py

import re, os, sys, subprocess
from .common import default_movie, plain_exercise, insert_code_and_tex
from .plaintext import plain_quiz
from .misc import _abort
from .doconce import errwarn

def cwiki_code(filestr, code_blocks, code_block_types,
               tex_blocks, format):
    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, format)
    c = re.compile(r'^!bc(.*?)\n', re.MULTILINE)
    filestr = c.sub(r'{{{\n', filestr)
    filestr = re.sub(r'!ec\n', r'}}}\n', filestr)
    c = re.compile(r'^!bt\n', re.MULTILINE)
    filestr = c.sub(r'{{{\n', filestr)
    filestr = re.sub(r'!et\n', r'}}}\n', filestr)
    return filestr

def cwiki_figure(m):
    filename = m.group('filename')
    link = filename if filename.startswith('http') else None
    if not link and not os.path.isfile(filename):
        raise IOError('no figure file %s' % filename)

    basename  = os.path.basename(filename)
    stem, ext = os.path.splitext(basename)
    root, ext = os.path.splitext(filename)

    if link is None:
        if not ext in '.png .gif .jpg .jpeg'.split():
            # try to convert image file to PNG, using
            # convert from ImageMagick:
            cmd = 'convert %s png:%s' % (filename, root+'.png')
            try:
                output = subprocess.check_output(cmd, shell=True,
                                                 stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                errwarn('\n**** Warning: could not run ' + cmd)
                errwarn('Convert %s to PNG format manually' % filename)
                _abort()
            filename = root + '.png'
    caption = m.group('caption')
    # keep label if it's there:
    caption = re.sub(r'label\{(.+?)\}', '(\g<1>)', caption)

    result = r"""{{%s|%s}}""" % (filename, caption)
    return result

from .common import table_analysis

def cwiki_table(table):
    """Native Creole wiki table."""
    # add 2 chars for column width since we add boldface _..._
    # in headlines:
    column_width = [c+2 for c in table_analysis(table['rows'])]

    s = '\n'
    for i, row in enumerate(table['rows']):
        if row == ['horizontal rule']:
            continue
        if i == 1 and \
           table['rows'][i-1] == ['horizontal rule'] and \
           table['rows'][i+1] == ['horizontal rule']:
            headline = True
        else:
            headline = False

        for column, w in zip(row, column_width):
            if headline:
                c = '=%s ' % ((column).ljust(w))
            else:
                c = ' %s ' % column.ljust(w)
            s += ' | %s ' % c
        s += ' |\n'
    s += '\n\n'
    return s

def cwiki_author(authors_and_institutions, auth2index,
                 inst2index, index2inst, auth2email):

    authors = []
    for author, i, email in authors_and_institutions:
        if email is None:
            email_text = ''
        else:
            name, adr = email.split('@')
            email_text = ' (%s at %s)' % (name, adr)
        authors.append('_%s_%s' % (author, email_text))

    if len(authors) ==  1:
        authors = authors[0]
    elif len(authors) == 2:
        authors = authors[0] + ' and ' + authors[1]
    elif len(authors) > 2:
        authors[-1] = 'and ' + authors[-1]
        authors = ', '.join(authors)
    else:
        # no authors:
        return ''
    text = '\n\nBy ' + authors + '\n\n'
    # we skip institutions in Creole wiki
    return text

from .gwiki import wiki_ref_and_label_common

def cwiki_ref_and_label(section_label2title, format, filestr):
    return wiki_ref_and_label_common(section_label2title, format, filestr)


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
           QUIZ,
           INTRO,
           OUTRO,
           filestr):
    # all arguments are dicts and accept in-place modifications (extensions)

    FILENAME_EXTENSION['cwiki'] = '.cwiki'  # output file extension
    BLANKLINE['cwiki'] = '\n'

    # replacement patterns for substitutions of inline tags
    INLINE_TAGS_SUBST['cwiki'] = {
        # use verbatim mode for math:
        'math':          r'\g<begin>{{{\g<subst>}}}\g<end>',
        'math2':         r'\g<begin>\g<puretext>\g<end>',
        'emphasize':     r'\g<begin>//\g<subst>//\g<end>',
        'bold':          r'\g<begin>**\g<subst>**\g<end>',
        'verbatim':      r'\g<begin>{{{\g<subst>}}}\g<end>',
        #'linkURL':       r'\g<begin>[[\g<url>|\g<link>]]\g<end>',
        'linkURL2':      r'[[\g<url>|\g<link>]]',
        'linkURL3':      r'[[\g<url>|\g<link>]]',
        'linkURL2v':     r'[[\g<url>|{{{\g<link>}}}]]',
        'linkURL3v':     r'[[\g<url>|{{{\g<link>}}}]]',
        'plainURL':      r'[[\g<url>]]',
        'colortext':     r'<font color="\g<color>">\g<text></font>',
        'chapter':       r'= \g<subst> =',
        'section':       r'= \g<subst> =',
        'subsection':    r'== \g<subst> ==',
        'subsubsection': r'=== \g<subst> ===\n',
#        'section':       r'++++ \g<subst> ++++',
#        'subsection':    r'++++++ \g<subst> ++++++',
#        'subsubsection': r'++++++++ \g<subst> ++++++++',
        'paragraph':     r'//\g<subst>//\g<space>',
        'title':         r'#summary \g<subst>\n<wiki:toc max_depth="2" />',
        'date':          r'=== \g<subst> ===',
        'author':        cwiki_author, #r'===== \g<name>, \g<institution> =====',
#        'figure':        r'<\g<filename>>',
        'figure':        cwiki_figure,
        'movie':         default_movie,  # will not work for HTML movie player
        'comment':       '<wiki:comment> %s </wiki:comment>',
        'abstract':      r'\n//\g<type>.// \g<text>\g<rest>',
        'linebreak':     r'\g<text><br />',
        'horizontal-rule': '----',
        'non-breaking-space': ' ',
        'ampersand2':    r' \g<1>&\g<2>',
        }

    CODE['cwiki'] = cwiki_code
    #from html import html_table
    #TABLE['cwiki'] = html_table
    TABLE['cwiki'] = cwiki_table

    # native list:
    LIST['cwiki'] = {
        'itemize':     {'begin': '\n', 'item': '*', 'end': '\n\n'},
        'enumerate':   {'begin': '\n', 'item': '#', 'end': '\n\n'},
        'description': {'begin': '\n', 'item': '* %s ', 'end': '\n\n'},
        'separator': '\n'}
    # (the \n\n for end is a hack because doconce.py avoids writing
    # newline at the end of lists until the next paragraph is hit)
    #LIST['cwiki'] = LIST['HTML']  # does not work well


    # how to typeset description lists for function arguments, return
    # values, and module/class variables:
    ARGLIST['cwiki'] = {
        'parameter': '*argument*',
        'keyword': '*keyword argument*',
        'return': '*return value(s)*',
        'instance variable': '*instance variable*',
        'class variable': '*class variable*',
        'module variable': '*module variable*',
        }

    FIGURE_EXT['cwiki'] = {
        'search': ('.png', '.gif', '.jpg', '.jpeg'),
        'convert': ('.png', '.gif', '.jpg')}
    CROSS_REFS['cwiki'] = cwiki_ref_and_label
    from .plaintext import plain_index_bib
    EXERCISE['cwiki'] = plain_exercise
    INDEX_BIB['cwiki'] = plain_index_bib
    TOC['cwiki'] = lambda s, f: '<<TableOfContents>>'
    QUIZ['cwiki'] = plain_quiz
    # document start:
    INTRO['cwiki'] = ''
    #INTRO['cwiki'] = '#summary YourOneLineSummary\n<wiki:toc max_depth="1" />\n'
