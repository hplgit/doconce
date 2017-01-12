"""
Remaining problems:

1. _testdoc.do.txt:
!bc
|bc pycod
def f(x):
    return x+1
|ec
!ec

does not work properly.

2.
"""
from __future__ import absolute_import
from builtins import str
from builtins import range
from past.builtins import basestring
import re, sys
from .common import default_movie, plain_exercise, bibliography, \
     cite_with_multiple_args2multiple_cites, insert_code_and_tex, \
     fix_ref_section_chapter
from .misc import option
from .doconce import errwarn

def matlabnb_author(authors_and_institutions, auth2index,
                 inst2index, index2inst, auth2email):
    text = '\n'
    for author in auth2index:
        email = auth2email[author]
        email_text = '' if email is None else '(%s)' % email
        text += ' '.join(['Author: ' + author, str(auth2index[author]), email_text]) + '\n'
    text += '\n'
    for index in index2inst:
        text += '[%d] %s\n' % (index, index2inst[index])
    text += '\n'
    return text

def matlabnb_code(filestr, code_blocks, code_block_types,
                  tex_blocks, format):
    # Remove all begin-end and \[ \] in tex blocks, join to one line,
    # embed in $$. Write error message if anything else than a single equation.
    pattern = 'begin\{(.+?)\}'
    for i in range(len(tex_blocks)):
        m = re.search(pattern, tex_blocks[i])
        if m:
            envir = m.group(1)
            if envir not in ('equation', 'equation*'):
                errwarn('*** warning: \\begin{%s}-\\end{%s} does not work in Matlab notebooks' % (envir, envir))
            tex_blocks[i] = re.sub(r'\\begin{%s}\s+' % envir, '', tex_blocks[i])
            tex_blocks[i] = re.sub(r'\\end{%s}\s+' % envir, '', tex_blocks[i])
        tex_blocks[i] = re.sub(r'\\\[', '', tex_blocks[i])
        tex_blocks[i] = re.sub(r'\\\]', '', tex_blocks[i])
        tex_blocks[i] = re.sub(r'label\{(.+?)\}', '', tex_blocks[i])
        tex_blocks[i] = '$$' + ' '.join(tex_blocks[i].strip().splitlines()).strip() + '$$'
        # Note: now the tex block ends with $$!et

    # Insert % in code if envir with -t name or if not Matlab code
    for i in range(len(code_blocks)):
        executable_matlab = code_block_types[i] in ('mcod', 'mpro')
        if not executable_matlab:
            # Note that monospace font requires two blanks after %
            code_blocks[i] = '\n'.join([
                '%  ' + line for line in code_blocks[i].splitlines()
                if not (line.startswith('!bc') or line.startswith('!ec'))]) + '\n'

    # Insert % at the beginning of each line
    from .common import _CODE_BLOCK, _MATH_BLOCK
    code_line = r'^\d+ ' + _CODE_BLOCK
    code_line_problem = r' (\d+ ' + _CODE_BLOCK + ')'
    math_line = r'^\d+ ' + _MATH_BLOCK
    math_line_problem = r' (\d+ ' + _MATH_BLOCK + ')'
    heading_no = 0
    lines = filestr.splitlines()
    for i in range(len(lines)):
        if re.search(code_line, lines[i], flags=re.MULTILINE):
            if heading_no < 2:
                # Add %% (empty heading) before code block because
                # code cannot come after the first heading, only
                # after the second and onwards
                lines[i] = '%%\n' + lines[i]
                continue
        elif re.search(math_line, lines[i], flags=re.MULTILINE):
            continue
        elif re.search(code_line_problem, lines[i], flags=re.MULTILINE):
            # Paragraphs can move a block indicator after its heading, insert \n
            lines[i] = re.sub(code_line_problem, '\n\g<1>', lines[i])
        elif re.search(math_line_problem, lines[i], flags=re.MULTILINE):
            # Paragraphs can move a block indicator after its heading, insert \n
            lines[i] = re.sub(math_line_problem, '\n\g<1>', lines[i])
        elif lines[i].startswith('>>>H'):
            # Heading
            lines[i] = '%%' + lines[i].replace('>>>H', '')
            heading_no += 1
        else:
            lines[i] = '% ' + lines[i]

    filestr = '\n'.join(lines)
    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, 'matlabnb')
    filestr = re.sub(r'\$\$!et', '$$', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!bt\s+\$\$', '% $$', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!bc.+', '', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!ec', '', filestr, flags=re.MULTILINE)
    # Remove all blank lines
    filestr = re.sub(r'^\s+', '', filestr, flags=re.MULTILINE)
    # Fix emphasize markup (conflicts with boldface so we do a hack)
    filestr = re.sub(r'\^\^\^X(.+?)X\^\^\^', '_\g<1>_', filestr,
                     flags=re.DOTALL)  # emph
    filestr = re.sub(r'\{\{\{X(.+?)X\}\}\}', '*\g<1>*', filestr,
                     flags=re.DOTALL)  # bold
    filestr = re.sub(r'<<<X(.+?)X>>>',       '|\g<1>|', filestr,
                     flags=re.DOTALL)  # verb

    return filestr

def matlabnb_ref_and_label(section_label2title, format, filestr):
    filestr = fix_ref_section_chapter(filestr, format)

    # remove label{...} from output (when only label{} on a line, remove
    # the newline too, leave label in figure captions, and remove all the rest)
    #filestr = re.sub(r'^label\{.+?\}\s*$', '', filestr, flags=re.MULTILINE)
    cpattern = re.compile(r'^label\{.+?\}\s*$', flags=re.MULTILINE)
    filestr = cpattern.sub('', filestr)
    #filestr = re.sub(r'^(FIGURE:.+)label\{(.+?)\}', '\g<1>{\g<2>}', filestr, flags=re.MULTILINE)
    cpattern = re.compile(r'^(FIGURE:.+)label\{(.+?)\}', flags=re.MULTILINE)
    filestr = cpattern.sub('\g<1>{\g<2>}', filestr)
    filestr = re.sub(r'label\{.+?\}', '', filestr)  # all the remaining

    # replace all references to sections:
    for label in section_label2title:
        filestr = filestr.replace('ref{%s}' % label,
                                  '"%s"' % section_label2title[label])

    from .common import ref2equations
    filestr = ref2equations(filestr)

    return filestr


def matlabnb_index_bib(filestr, index, citations, pubfile, pubdata):
    if citations:
        filestr = cite_with_multiple_args2multiple_cites(filestr)
    for label in citations:
        filestr = filestr.replace('cite{%s}' % label,
                                  '[%d]' % citations[label])
    if pubfile is not None:
        bibtext = bibliography(pubdata, citations, format='doconce')
        bibtext = re.sub(r'label\{.+?\} ', '', bibtext)
        # Remove boldface _author_ (typically 12. _John Doe and Jane Doe_.)
        bibtext = re.sub(r'(\d+)\. _(.+)_\.', '\g<2>', bibtext)
        filestr = re.sub(r'^BIBFILE:.+$', bibtext, filestr, flags=re.MULTILINE)

    # remove all index entries:
    filestr = re.sub(r'idx\{.+?\}\n?', '', filestr)
    # no index since line numbers from the .do.txt (in index dict)
    # never correspond to the output format file
    #filestr += '\n\n======= Index =======\n\n'
    #for word in index:
    #    filestr + = '%s, line %s\n' % (word, ', '.join(index[word]))

    return filestr

def matlabnb_toc(sections, filestr):
    # Find minimum section level
    tp_min = 4
    for title, tp, label in sections:
        if tp < tp_min:
            tp_min = tp

    s = 'Table of contents:\n\n'
    for title, tp, label in sections:
        s += ' '*(2*(tp-tp_min)) + title + '\n'
    return s

def matlabnb_box(text, title=''):
    """Wrap a box around the text, with a title on the upper box border."""
    lines = text.splitlines()
    maxlen = max([len(line) for line in lines])
    newlines = []
    # title can be :: since equations and code must be preceeded by ::
    # and plaintext inserts a double colon
    if title == '' or title.lower() == 'none' or title == '::':
        newlines.append('|-' + '-'*maxlen + '-|')
    else:
        newlines.append(title + ' ' + '-'*(maxlen-len(title)) + '--|')
    for line in lines:
        newlines.append('| ' + line + ' '*(maxlen-len(line)) + ' |')
    newlines.append('|-' + '-'*maxlen + '-|')
    # Drop blank lines at the beginning
    drop = 0
    for line in newlines[1:]:
        if re.search(r'[^\-| ]', line):
            break
        else:
            drop += 1
    for i in range(drop):
        del newlines[1]
    if re.search(r'^\w', newlines[0]):
        # Insert a blank line
        newlines.insert(1, '| ' + ' '*maxlen + ' |')
    # Drop blank lines at the end
    drop = 0
    for line in reversed(newlines[:-1]):
        if re.search(r'[^\-| ]', line):
            break
        else:
            drop += 1
    for i in range(1, drop+1, 1):
        del newlines[-2]

    return '\n' + '\n'.join(newlines) + '\n'

def matlabnb_quiz(quiz):
    # Simple typesetting of a quiz
    import string
    question_prefix = quiz.get('question prefix',
                               option('quiz_question_prefix=', 'Question:'))
    common_choice_prefix = option('quiz_choice_prefix=', 'Choice')
    quiz_expl = option('quiz_explanations=', 'on')

    text = '\n\n'
    if 'new page' in quiz:
        text += '======= %s =======\n\n' % (quiz['new page'])

    # Don't write Question: ... if inside an exercise section
    if quiz.get('embedding', 'None') in ['exercise',]:
        pass
    else:
        text += '\n'
        if question_prefix:
            text += '%s ' % (question_prefix)

    text += quiz['question'] + '\n\n'

    # List choices as paragraphs
    for i, choice in enumerate(quiz['choices']):
        #choice_no = i+1
        choice_no = string.ascii_uppercase[i]
        answer = choice[0].capitalize() + '!'
        choice_prefix = common_choice_prefix
        if 'choice prefix' in quiz:
            if isinstance(quiz['choice prefix'][i], basestring):
                choice_prefix = quiz['choice prefix'][i]
        if choice_prefix == '' or choice_prefix[-1] in ['.', ':', '?']:
            pass  # don't add choice number/letter
        else:
            choice_prefix += ' %s:' % choice_no
        # Let choice start with a newline if pure code starts the choice
        # (test for different code block types so this function can work
        # for other formats too...)
        choice = choice[1].lstrip()
        code_starters = 'Code::', '~~~', '```', '{{{'
        for code_starter in code_starters:
            if choice.startswith(code_starter):
                choice = '\n' + choice

        # Cannot treat explanations
        text += '%s %s\n\n' % (choice_prefix, choice)
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

    FILENAME_EXTENSION['matlabnb'] = '.m'
    BLANKLINE['matlabnb'] = '\n'
    # replacement patterns for substitutions of inline tags
    encoding = 'utf-8'
    INLINE_TAGS_SUBST['matlabnb'] = {
        'math':      None,
        'math2':     r'\g<begin>$\g<latexmath>$\g<end>',
        # emphasize goes to _..._ and bold subst afterwards takes it to *...*
        # make a different syntax and fix it in matlabnb_code
        'emphasize': r'\g<begin>^^^X\g<subst>X^^^\g<end>',
        'bold':      r'\g<begin>*\g<subst>*\g<end>',
        # Need a hack to avoid |...| for verbatim to avoid conflict in tables
        'verbatim':  r'\g<begin><<<X\g<subst>X>>>\g<end>',
        'figure':    lambda m: '<<%s>>' % m.group('filename'),
        'movie':     default_movie,
        'linkURL2':  r'\g<link> <\g<url>>',
        'linkURL3':  r'\g<link> <\g<url>>',
        'linkURL2v': r'\g<link> <\g<url>>',
        'linkURL3v': r'\g<link> <\g<url>>',
        'plainURL':  r'<\g<url>>',
        'comment':   r'%% %s',
        'inlinecomment': None,
        'colortext': '\g<text>',
        'title':     r'>>>H \g<subst>\n',
        'author':    matlabnb_author,
        'date':      r'\nDate: \g<subst>\n',
        'chapter':       r'>>>H \g<subst>',
        'section':       r'>>>H \g<subst>',
        'subsection':    r'>>>H \g<subst>',
        'subsubsection': r'>>>H \g<subst>',
        # Same problem with abstract/paragraph as with emphasize, use same trick
        'abstract':      r'\n{{{X\g<type>.X}}} \g<text>\g<rest>',
        'paragraph':     r'{{{X\g<subst>X}}} ',  # extra blank
        'linebreak':     r'\g<text>',
        'footnote':      None,
        'non-breaking-space': ' ',
        'ampersand2':    r' \g<1>&\g<2>',
        }

    CODE['matlabnb'] = matlabnb_code
    from .common import DEFAULT_ARGLIST
    ARGLIST['matlabnb'] = DEFAULT_ARGLIST
    FIGURE_EXT['matlabnb'] = {
        'search': ('.png', '.gif', '.jpg', '.jpeg', '.pdf'),  #.pdf?
        'convert': ('.png', '.gif', '.jpg')}
    LIST['matlabnb'] = {
        'itemize':
        {'begin': '', 'item': '*', 'end': '\n'},

        'enumerate':
        {'begin': '', 'item': '#', 'end': '\n'},

        'description':
        {'begin': '', 'item': '%s', 'end': '\n'},

        'separator': '\n',
        }
    CROSS_REFS['matlabnb'] = matlabnb_ref_and_label
    from .html import html_table
    TABLE['matlabnb'] = html_table
    #TABLE['matlabnb'] = matlabnb_table
    EXERCISE['matlabnb'] = plain_exercise
    INDEX_BIB['matlabnb'] = matlabnb_index_bib
    TOC['matlabnb'] = matlabnb_toc

    from .common import indent_lines
    ENVIRS['matlabnb'] = {
        'warning':   lambda block, format, title='Warning', text_size='normal':
           matlabnb_box(block, title),
        'notice':    lambda block, format, title='Notice', text_size='normal':
           matlabnb_box(block, title),
        'question':  lambda block, format, title='Question', text_size='normal':
           matlabnb_box(block, title),
        'hint':      lambda block, format, title='Hint', text_size='normal':
           matlabnb_box(block, title),
        'summary':   lambda block, format, title='Summary', text_size='normal':
           matlabnb_box(block, title),
        'block':     lambda block, format, title='Block', text_size='normal':
           matlabnb_box(block, title),
        'box':       lambda block, format, title='none', text_size='normal':
           matlabnb_box(block, title),
        'quote':     lambda block, format, title='none', text_size='normal':
           indent_lines(block, 'matlabnb'),
        }
    QUIZ['matlabnb'] = matlabnb_quiz
