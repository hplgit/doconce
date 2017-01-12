from __future__ import absolute_import
from builtins import str
from builtins import range
from past.builtins import basestring
import re, sys
from .common import default_movie, plain_exercise, bibliography, \
     cite_with_multiple_args2multiple_cites, fix_ref_section_chapter
from .misc import option


def plain_author(authors_and_institutions, auth2index,
                 inst2index, index2inst, auth2email):
    text = '\n'
    for author in auth2index:
        email = auth2email[author]
        email_text = '' if email is None else '(%s)' % email
        text += ' '.join([author, str(auth2index[author]), email_text]) + '\n'
    text += '\n'
    for index in index2inst:
        text += '[%d] %s\n' % (index, index2inst[index])
    text += '\n'
    return text

def plain_ref_and_label(section_label2title, format, filestr):
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


def plain_index_bib(filestr, index, citations, pubfile, pubdata):
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

def plain_toc(sections, filestr):
    # Find minimum section level
    tp_min = 4
    for title, tp, label in sections:
        if tp < tp_min:
            tp_min = tp

    s = 'Table of contents:\n\n'
    for title, tp, label in sections:
        s += ' '*(2*(tp-tp_min)) + title + '\n'
    return s

def plain_box(text, title=''):
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

def plain_quiz(quiz):
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

    FILENAME_EXTENSION['plain'] = '.txt'
    BLANKLINE['plain'] = '\n'
    # replacement patterns for substitutions of inline tags
    encoding = 'utf-8'
    INLINE_TAGS_SUBST['plain'] = {
        'math':      r'\g<begin>\g<subst>\g<end>',  # drop $ signs
        'math2':     r'\g<begin>\g<puretext>\g<end>',
        'emphasize': None,
        'bold':      None,
        'figure':    None,
        'movie':     default_movie,
        'verbatim':  r'\g<begin>\g<subst>\g<end>',  # no ` chars
        #'linkURL':   r'\g<begin>\g<link> (\g<url>)\g<end>',
        'linkURL2':  r'\g<link> (\g<url>)',
        'linkURL3':  r'\g<link> (\g<url>)',
        'linkURL2v': r'\g<link> (\g<url>)',
        'linkURL3v': r'\g<link> (\g<url>)',
        'plainURL':  r'\g<url>',
        'colortext': '\g<text>',
        'title':     r'======= \g<subst> =======\n',  # doconce top section, to be substituted later
        'author':    plain_author,
        'date':      r'\nDate: \g<subst>\n',
        'chapter':       lambda m: '%s\n%s' % (m.group('subst'), '%'*len(m.group('subst'))),
        'section':       lambda m: '%s\n%s' % (m.group('subst'), '='*len(m.group('subst'))),
        'subsection':    lambda m: '%s\n%s' % (m.group('subst'), '-'*len(m.group('subst'))),
        'subsubsection': lambda m: '%s\n%s\n' % (m.group('subst'), '~'*len(m.group('subst'))),
        'paragraph':     r'*\g<subst>*\g<space>',  # extra blank
        'abstract':      r'\n*\g<type>.* \g<text>\g<rest>',
        'linebreak':     r'\g<text>',
        'footnote':      None,
        'non-breaking-space': ' ',
        'ampersand2':    r' \g<1>&\g<2>',
        }

    from .rst import rst_code
    CODE['plain'] = rst_code
    from .common import DEFAULT_ARGLIST
    ARGLIST['plain'] = DEFAULT_ARGLIST
    LIST['plain'] = {
        'itemize':
        {'begin': '', 'item': '*', 'end': '\n'},

        'enumerate':
        {'begin': '', 'item': '%d.', 'end': '\n'},

        'description':
        {'begin': '', 'item': '%s', 'end': '\n'},

        'separator': '\n',
        }
    CROSS_REFS['plain'] = plain_ref_and_label
    from .rst import rst_table
    TABLE['plain'] = rst_table
    #TABLE['plain'] = plain_table
    EXERCISE['plain'] = plain_exercise
    INDEX_BIB['plain'] = plain_index_bib
    TOC['plain'] = plain_toc

    from .common import indent_lines
    ENVIRS['plain'] = {
        'warning':   lambda block, format, title='Warning', text_size='normal':
           plain_box(block, title),
        'notice':    lambda block, format, title='Notice', text_size='normal':
           plain_box(block, title),
        'question':  lambda block, format, title='Question', text_size='normal':
           plain_box(block, title),
        'hint':      lambda block, format, title='Hint', text_size='normal':
           plain_box(block, title),
        'summary':   lambda block, format, title='Summary', text_size='normal':
           plain_box(block, title),
        'block':     lambda block, format, title='Block', text_size='normal':
           plain_box(block, title),
        'box':       lambda block, format, title='none', text_size='normal':
           plain_box(block, title),
        'quote':     lambda block, format, title='none', text_size='normal':
           indent_lines(block, 'plain'),
        }
    QUIZ['plain'] = plain_quiz
