import re
from common import remove_code_and_tex, insert_code_and_tex, indent_lines, \
     default_movie, plain_exercise

def old_epytext_code(filestr):
    # In rst syntax, code blocks are typeset with :: (verbatim)
    # followed by intended blocks. This function indents everything
    # inside code (or TeX) blocks. The code here is similar to
    # rst.rst_code, but a special epytext version was
    # necessary since epytext is fooled by \n in code/tex blocks.

    # first indent all code/tex blocks:
    filestr, code_blocks, tex_blocks = remove_code_and_tex(filestr)
    for i in range(len(code_blocks)):
        code_blocks[i] = indent_lines(code_blocks[i], True)
    for i in range(len(tex_blocks)):
        tex_blocks[i] = indent_lines(tex_blocks[i], True)
    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, 'rst')

    # substitute !bc and !ec appropriately:
    # (see rst.rst_code for comments if problems)
    from rst import bc_regex_pattern, bt_regex_pattern
    c = re.compile(bc_regex_pattern, re.DOTALL)
    filestr = c.sub(r'\g<1>::\n\n', filestr)
    filestr = re.sub(r'!ec\n', '\n\n', filestr)
    c = re.compile(bt_regex_pattern, re.DOTALL)
    filestr = c.sub(r'\g<1>::\n\n', filestr)
    filestr = re.sub(r'!et\n', '\n\n', filestr)
    return filestr

def epytext_author(authors_and_institutions, auth2index,
                   inst2index, index2inst, auth2email):
    text = 'BY: '
    ai = []
    for author, institutions, email in authors_and_institutions:
        if institutions is not None:
            ai.append('%s (%s)' % (author, ', and '.join(institutions)))
        else:
            ai.append(author)
    text += '; '.join(ai)
    return text


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

    FILENAME_EXTENSION['epytext'] = '.epytext'
    BLANKLINE['epytext'] = '\n'
    # replacement patterns for substitutions of inline tags
    INLINE_TAGS_SUBST['epytext'] = {
        'math':      r'\g<begin>M{\g<subst>}\g<end>',
        #'math2':     r'\g<begin>M{\g<latexmath>}\g<end>', # has \ in \sin e.g. so we rather use the puretext version
        'math2':    r'\g<begin>M{\g<puretext>}\g<end>',
        'emphasize': r'\g<begin>I{\g<subst>}\g<end>',
        'bold':      r'\g<begin>B{\g<subst>}\g<end>',
        'verbatim':  r'\g<begin>C{\g<subst>}\g<end>',
        #'linkURL':   r'\g<begin>U{\g<link><\g<url>>}\g<end>',
        'linkURL2':  r'U{\g<link><\g<url>>}',
        'linkURL3':  r'U{\g<link><\g<url>>}',
        'linkURL2v': r'U{C{\g<link>}<\g<url>>}',
        'linkURL3v': r'U{C{\g<link>}<\g<url>>}',
        'plainURL':  r'U{\g<url><\g<url>>}',
        'colortext': '\g<text>',
        # the replacement string differs, depending on the match object m:
        'chapter':       lambda m: '%s\n%s' % (m.group('subst'), '%'*len(m.group('subst'))),
        'section':       lambda m: '%s\n%s' % (m.group('subst'), '='*len(m.group('subst'))),
        'subsection':    lambda m: '%s\n%s' % (m.group('subst'), '-'*len(m.group('subst'))),
        'subsubsection': lambda m: '%s\n%s\n' % (m.group('subst'), '~'*len(m.group('subst'))),
        'paragraph':     r'I{\g<subst>} ',
        'abstract':      r'\nI{\g<type>.} \g<text>\n\g<rest>',
        'title':         r'TITLE: \g<subst>',
        'date':          r'DATE: \g<subst>',
        'author':        epytext_author,
        'movie':         default_movie,
        'linebreak':     r'\g<text>',
        'non-breaking-space': ' ',
        }

    from rst import rst_code, rst_table
    CODE['epytext'] = rst_code
    TABLE['epytext'] = rst_table
    from plaintext import plain_ref_and_label, plain_index_bib
    CROSS_REFS['epytext'] = plain_ref_and_label
    INDEX_BIB['epytext'] = plain_index_bib
    EXERCISE['epytext'] = plain_exercise

    LIST['epytext'] = {
        'itemize':
        {'begin': '', 'item': '-', 'end': '\n'},

        'enumerate':
        {'begin': '', 'item': '%d.', 'end': '\n'},

        'description':
        {'begin': '', 'item': '%s', 'end': '\n'},

        'separator': '',
        }
    ARGLIST['epytext'] = {
        'parameter': '@param',
        'keyword': '@keyword',
        'return': '@return',
        'instance variable': '@ivar',
        'class variable': '@cvar',
        'module variable': '@var',
        }
    TOC['epytext'] = lambda x: '\n'  # no toc for epydoc
    QUIZ['epytext'] = lambda quiz: '\nB{Cannot typeset quiz} %s\n' % quiz.get('heading', '')

    #FORTSETT: insert QUIZ in various .py files, plaintext can do something simple, problem: cannot insert headline and exercise because then the exercise is not interpreted! problem2: quiz will just be a part of an exercises, unrendered
    #solution problem1: typeset_quizzes1 inserts the headline if the first headline prior to the quiz is not Exercise: heading, if heading is missing see if it can be obtained from the last Exercise|Project|Problem heading (if last heading is of this type)
    #solution problem2: the exercise data struct is not written to file before a similar interpretation as in extract_quizzes, then we can drop substituting in the data structure too!

