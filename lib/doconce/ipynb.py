import re, sys, shutil, os
from common import default_movie, plain_exercise, table_analysis, \
     insert_code_and_tex, indent_lines
from html import html_movie
from pandoc import pandoc_table, pandoc_ref_and_label, \
     pandoc_index_bib, pandoc_quote, pandoc_figure
from misc import option

"""
TODO:

1. Only pycod, pypro and later other languages should go to code tp,
otherwise use plain markdown verbatim block and mark cell as "markdown"
        for i in range(len(code_blocks)):
            code_blocks[i] = indent_lines(code_blocks[i], format)

sys with running a .py program, find full path, run "fullpath"
"""

def ipynb_author(authors_and_institutions, auth2index,
                 inst2index, index2inst, auth2email):
    authors = []
    for author, i, e in authors_and_institutions:
        author_str = "new_author(name=u'%s'" % author
        if i is not None:
            author_str += ", affiliation=u'%s'" % ' and '.join(i)
        if e is not None:
            author_str += ", email=u'%s'" % e
        author_str += ')'
        authors.append(author_str)
    s ='authors = [%s]' % (', '.join(authors))
    return s

def ipynb_figure(m):
    filename = m.group('filename')
    caption = m.group('caption').strip()
    if not filename.startswith('http'):
        text = '![%s](files/%s)' % (caption, filename)  # hack for plain file
    else:
        text = '![%s](%s)' % (caption, filename)
    return text

def ipynb_code(filestr, code_blocks, code_block_types,
               tex_blocks, format):
    # newcommands (code taken from html.py)
    import glob
    newcommands_files = list(
        sorted([name
                for name in glob.glob('newcommands*.tex')
                if not name.endswith('.p.tex')]))
    newcommands = ''
    for filename in newcommands_files:
        f = open(filename, 'r')
        text = ''
        for line in f.readlines():
            if not line.startswith('%'):
                text += line
        text = text.strip()
        if text:
            newcommands += '\n<!-- %s -->\n' % filename + '$$\n' + text \
                           + '\n$$\n\n'
    if newcommands:
        filestr = newcommands + filestr

    # filestr becomes json list after this function so we must typeset
    # envirs here. All envirs are typeset as pandoc_quote.
    from common import _CODE_BLOCK, _MATH_BLOCK
    envir_format = option('ipynb_admon=', 'paragraph')
    # Remove all !bpop-!epop environments (they cause only problens and
    # have no use)
    for envir in 'pop', 'slidecell', 'notes':
        filestr = re.sub('^!b%s.*\n' % envir, '', filestr, flags=re.MULTILINE)
        filestr = re.sub('^!e%s\s+' % envir, '', filestr, flags=re.MULTILINE)
    from doconce import doconce_envirs
    envirs = doconce_envirs()[8:-1]
    for envir in envirs:
        pattern = r'^!b%s(.*?)\n(.+?)\s*^!e%s' % (envir, envir)
        if envir_format in ('quote', 'paragraph'):
            def subst(m):
                title = m.group(1).strip()
                # Text size specified in parenthesis?
                m2 = re.search('^\s*\((.+?)\)', title)

                if title == '' and envir not in ('block', 'quote'):
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
                    title = '**' + title + '**\n'
                    # Could also consider subsubsection formatting
                block = m.group(2)
                if envir_format == 'quote':
                    # Make Markdown quote of the block: lines start with >
                    lines = []
                    for line in block.splitlines():
                        # Just quote plain text
                        if not (_MATH_BLOCK in line or
                                _CODE_BLOCK in line or
                                line.startswith('FIGURE:') or
                                line.startswith('MOVIE:') or
                                line.startswith('|')):
                            lines.append('> ' + line)
                        else:
                            lines.append('\n' + line + '\n')
                    block = '\n'.join(lines) + '\n\n'

                    # Add quote and a blank line after title
                    if title:
                        title = '> ' + title + '>\n'
                else:
                    # Add a blank line after title
                    if title:
                        title += '\n'

                text = title + block + '\n\n'
                return text
        else:
            print '*** error: --ipynb_admon=%s is not supported'  % envir_format
        filestr = re.sub(pattern, subst, filestr,
                         flags=re.DOTALL | re.MULTILINE)

    # Fix pyshell and ipy interactive sessions: remove prompt and output.
    # Fix sys and use run prog.py.
    # Only typeset Python code as blocks, otherwise plain indented Markdown.
    from doconce import dofile_basename
    from sets import Set
    ipynb_tarfile = 'ipynb-%s-src.tar.gz' % dofile_basename
    src_dirs = Set()

    ipynb_code_tp = [None]*len(code_blocks)
    for i in range(len(code_blocks)):
        tp = code_block_types[i]
        if tp in ('pyshell', 'ipy'):
            # Remove prompt and output lines; leave code executable in cell
            lines = code_blocks[i].splitlines()
            for j in range(len(lines)):
                if lines[j].startswith('>>> ') or lines[j].startswith('... '):
                    lines[j] = lines[j][4:]
                elif lines[j].startswith('In ['):
                    lines[j] = ':'.join(lines[j].split(':')[1:]).strip()
                else:
                    # output
                    lines[j] = ''

            for j in range(lines.count('')):
                lines.remove('')
            code_blocks[i] = '\n'.join(lines)
            ipynb_code_tp[i] = 'cell'
        elif tp == 'sys':
            # Do we find execution of python file? If so, copy the file
            # to separate subdir and make a run file command in a cell.
            # Otherwise, it is just a plain verbatim Markdown block.
            found_unix_lines = False
            lines = code_blocks[i].splitlines()
            for j in range(len(lines)):
                m = re.search(r'(.+?>|\$) *python +([A-Za-z_0-9]+?\.py)',
                              lines[j])
                if m:
                    name = m.group(2).strip()
                    if os.path.isfile(name):
                        src_dirs.add(os.path.dirname(name))
                        lines[j] = '%%run "%s"' % fullpath
                else:
                    found_unix_lines = True
            src_dirs = list(src_dirs)
            if src_dirs and not found_unix_lines:
                # This is a sys block with run commands only
                code_blocks[i] = '\n'.join(lines)
                ipynb_code_tp[i] = 'cell'
            else:
                # Standard Markdown code
                code_blocks[i] = '\n'.join(lines)
                code_blocks[i] = indent_lines(code_blocks[i], format)
                ipynb_code_tp[i] = 'markdown'
        elif tp.startswith('py'):
            ipynb_code_tp[i] = 'cell'
        else:
            # Should support other languages as well, but not for now
            code_blocks[i] = indent_lines(code_blocks[i], format)
            ipynb_code_tp[i] = 'markdown'
    if src_dirs:
        # Make tar file with all the source dirs with files
        # that need to be executed
        os.system('tar cfz %s %s' % (ipynb_tarfile, ' '.join(src_dirs)))
        print 'collected all required .py files in', ipynb_tarfile, 'which must be distributed with the notebook'


    # Parse document into markdown text, code blocks, and tex blocks.
    # Store in nested list notebook_blocks.
    notebook_blocks = [[]]
    authors = ''
    for line in filestr.splitlines():
        if line.startswith('authors = [new_author(name='):
            authors = line[10:]
        elif _CODE_BLOCK in line:
            notebook_blocks[-1] = '\n'.join(notebook_blocks[-1]).strip()
            notebook_blocks.append(line)
        elif _MATH_BLOCK in line:
            notebook_blocks[-1] = '\n'.join(notebook_blocks[-1]).strip()
            notebook_blocks.append(line)
        else:
            if not isinstance(notebook_blocks[-1], list):
                notebook_blocks.append([])
            notebook_blocks[-1].append(line)
    if isinstance(notebook_blocks[-1], list):
        notebook_blocks[-1] = '\n'.join(notebook_blocks[-1]).strip()


    # Add block type info
    pattern = r'(\d+) +%s'
    for i in range(len(notebook_blocks)):
        if re.match(pattern % _CODE_BLOCK, notebook_blocks[i]):
            m = re.match(pattern % _CODE_BLOCK, notebook_blocks[i])
            idx = int(m.group(1))
            if ipynb_code_tp[idx] == 'cell':
                notebook_blocks[i] = ['cell', notebook_blocks[i]]
            else:
                notebook_blocks[i] = ['text', notebook_blocks[i]]
        elif re.match(pattern % _MATH_BLOCK, notebook_blocks[i]):
            notebook_blocks[i] = ['math', notebook_blocks[i]]
        else:
            notebook_blocks[i] = ['text', notebook_blocks[i]]

    # Go through tex_blocks and wrap in $$
    # (doconce.py runs align2equations so there are no align/align*
    # environments in tex blocks)
    for i in range(len(tex_blocks)):
        # Remove \[ and \] or \begin/end{equation*} in single equations
        tex_blocks[i] = tex_blocks[i].replace(r'\[', '')
        tex_blocks[i] = tex_blocks[i].replace(r'\]', '')
        tex_blocks[i] = tex_blocks[i].replace(r'\begin{equation*}', '')
        tex_blocks[i] = tex_blocks[i].replace(r'\end{equation*}', '')
        # Check for illegal environments
        m = re.search(r'\\begin\{(.+?)\}', tex_blocks[i])
        if m:
            envir = m.group(1)
            if envir not in ('equation', 'equation*', 'align*', 'align'):
                print """\
*** warning: latex envir \\begin{%s} does not work well in Markdown.
    Stick to \\[ ... \\], equation, equation*, align, or align*
    environments in math environments.
""" % envir
        eq_type = 'heading'  # or '$$'
        eq_type = '$$'
        # Markdown: add $$ on each side of the equation
        if eq_type == '$$':
            # Make sure there are no newline after equation
            tex_blocks[i] = '$$\n' + tex_blocks[i].strip() + '\n$$'
        # Here: use heading (###) and simple formula (remove newline
        # in math expressions to keep everything within a heading) as
        # the equation then looks bigger
        elif eq_type == 'heading':
            tex_blocks[i] = '### $ ' + '  '.join(tex_blocks[i].splitlines()) + ' $'

    # blocks is now a list of text chunks in markdown and math/code line
    # instructions. Insert code and tex blocks
    for i in range(len(notebook_blocks)):
        if _CODE_BLOCK in notebook_blocks[i][1] or _MATH_BLOCK in notebook_blocks[i][1]:
            words = notebook_blocks[i][1].split()
            # start of notebook_blocks[i]: number block-indicator code-type
            n = int(words[0])
            if _CODE_BLOCK in notebook_blocks[i][1]:
                notebook_blocks[i][1] = code_blocks[n]
            if _MATH_BLOCK in notebook_blocks[i][1]:
                notebook_blocks[i][1] = tex_blocks[n]

    # Make IPython structures
    from IPython.nbformat.v3 import (
         NotebookNode,
         new_code_cell, new_text_cell, new_worksheet, new_notebook, new_output,
         new_metadata, new_author)
    import IPython.nbformat.v3.nbjson
    ws = new_worksheet()
    prompt_number = 1
    for block_tp, block in notebook_blocks:
        if (block_tp == 'text' or block_tp == 'math') and block != '':
            ws.cells.append(new_text_cell(u'markdown', source=block))
        elif block_tp == 'cell' and block != '':
            ws.cells.append(new_code_cell(input=block,
                                          prompt_number=prompt_number,
                                          collapsed=False))
    # Catch the title as the first heading
    m = re.search(r'^#+\s*(.+)$', filestr, flags=re.MULTILINE)
    title = m.group(1).strip() if m else ''
    if authors:
        authors = eval(authors)
        md = new_metadata(name=title, authors=authors)
    else:
        md = new_metadata(name=title)
    nb = new_notebook(worksheets=[ws], metadata=new_metadata())

    # Convert nb to json format
    filestr = IPython.nbformat.v3.nbjson.writes(nb)

    # must do the replacements here at the very end when json is written out
    # \eqref and labels will not work, but labels do no harm
    filestr = re.sub(r'([^\\])label\{', r'\g<1>\\\\label{', filestr,
                     flags=re.MULTILINE)
    # \eqref crashes the notebook, may be better with full MathJax support?
    #filestr = re.sub(r'\(ref\{(.+?)\}\)', r'\eqref{\g<1>}', filestr)
    filestr = re.sub(r'\(ref\{(.+?)\}\)', r'Eq (\g<1>)', filestr)

    '''
    # Final fixes: replace all text between cells by markdown code cells
    # Note: the patterns are overlapping so a plain re.sub will not work,
    # here we run through all blocks found and subsitute the first remaining
    # one, one by one.
    pattern = r'   \},\n(.+?)\{\n    "cell_type":'
    begin_pattern = r'^(.+?)\{\n    "cell_type":'
    remaining_block_begin = re.findall(begin_pattern, filestr, flags=re.DOTALL)
    remaining_blocks = re.findall(pattern, filestr, flags=re.DOTALL)
    import string
    for block in remaining_block_begin + remaining_blocks:
        filestr = string.replace(filestr, block, json_markdown(block) + '   ',
                                 maxreplace=1)
    filestr_end = re.sub(r'   \{\n    "cell_type": .+?\n   \},\n', '', filestr,
                         flags=re.DOTALL)
    filestr = filestr.replace(filestr_end, json_markdown(filestr_end))
    filestr = """{
 "metadata": {
  "name": "SOME NAME"
 },
 "nbformat": 3,
 "nbformat_minor": 0,
 "worksheets": [
  {
   "cells": [
""" + filestr.rstrip() + '\n'+ \
    json_pycode('', final_prompt_no+1, 'python').rstrip()[:-1] + """
   ],
   "metadata": {}
  }
 ]
}"""
    '''
    return filestr


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

    FILENAME_EXTENSION['ipynb'] = '.ipynb'
    BLANKLINE['ipynb'] = '\n'
    # replacement patterns for substitutions of inline tags
    INLINE_TAGS_SUBST['ipynb'] = {
        'math':      None,  # indicates no substitution, leave as is
        'math2':     r'\g<begin>$\g<latexmath>$\g<end>',
        'emphasize': None,
        'bold':      r'\g<begin>**\g<subst>**\g<end>',
        'figure':    ipynb_figure,
        #'movie':     default_movie,
        'movie':     html_movie,
        'verbatim':  None,
        #'linkURL':   r'\g<begin>\g<link> (\g<url>)\g<end>',
        'linkURL2':  r'[\g<link>](\g<url>)',
        'linkURL3':  r'[\g<link>](\g<url>)',
        'linkURL2v': r'[`\g<link>`](\g<url>)',
        'linkURL3v': r'[`\g<link>`](\g<url>)',
        'plainURL':  r'<\g<url>>',
        'colortext': r'<font color="\g<color>">\g<text></font>',
        'title':     r'# \g<subst>',
        'author':    ipynb_author,
        'date':      '_\g<subst>_\n',
        'chapter':       lambda m: '# '    + m.group('subst'),
        'section':       lambda m: '## '   + m.group('subst'),
        'subsection':    lambda m: '### '  + m.group('subst'),
        'subsubsection': lambda m: '#### ' + m.group('subst') + '\n',
        'paragraph':     r'*\g<subst>*\g<space>',
        'abstract':      r'\n*\g<type>.* \g<text>\n\n\g<rest>',
        'comment':       '<!-- %s -->',
        'linebreak':     r'\g<text>',  # Not sure how this is supported; Markdown applies <br> but that cannot be used for latex output with ipynb...
        'non-breaking-space': ' ',
        'ampersand2':    r' \g<1>&\g<2>',
        }

    CODE['ipynb'] = ipynb_code
    # Envirs are in doconce.py treated after code is inserted, which
    # means that the ipynb format is json. Therefore, we need special
    # treatment of envirs in ipynb_code and ENVIRS can be empty.
    ENVIRS['ipynb'] = {}

    from common import DEFAULT_ARGLIST
    ARGLIST['ipynb'] = DEFAULT_ARGLIST
    LIST['ipynb'] = {
        'itemize':
        {'begin': '', 'item': '*', 'end': '\n'},

        'enumerate':
        {'begin': '', 'item': '%d.', 'end': '\n'},

        'description':
        {'begin': '', 'item': '%s\n  :   ', 'end': '\n'},

        'separator': '\n',
        }
    CROSS_REFS['ipynb'] = pandoc_ref_and_label

    TABLE['ipynb'] = pandoc_table
    INDEX_BIB['ipynb'] = pandoc_index_bib
    EXERCISE['ipynb'] = plain_exercise
    TOC['ipynb'] = lambda s: ''
    FIGURE_EXT['ipynb'] = ('.png', '.gif', '.jpg', '.jpeg', '.tif', '.tiff', '.pdf')
    QUIZ['ipynb'] = lambda quiz: '**Cannot typeset quiz**: "%s"' % quiz.get('heading', '')
