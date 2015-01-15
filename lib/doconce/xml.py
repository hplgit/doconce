"""
************************************************************************
WARNING: This file is just a preliminary sketch. Most of the file
is still html.py copied here for modifications.
************************************************************************

Start with html.py, let output be begin and end tags surrounding
all constructs. Lists, environments, math, code, exercises can
easily be wrapped in tags.
Paragraphs ends are more challenging but can be treated at the
end: if there is an ordinary text without a closing tag and then
space until <p>, the previous text must be an ordinary paragraph
that should have an </p> at the end.

Sections can be done at the beginning (first native format function
called): just push the occurence of ===+ on to a stack ('chapter',
'section', ...) and empty the stack down the current heading level
when encountering a new heading.

With a doconce to XML translator it is possible to use XML
tools to translate to any desired output since all constructs
are wrapped in tags.

Drop begin-end of paragraphs, just mark newlines (<newline/>) and
let paragraphs be running text inside the parent element.
"""

import re, os, glob, sys, glob
from common import table_analysis, plain_exercise, insert_code_and_tex, \
     indent_lines, online_python_tutor, bibliography, \
     cite_with_multiple_args2multiple_cites, is_file_or_url
from misc import option, _abort


def xml_code(filestr, code_blocks, code_block_types,
              tex_blocks, format):
    """Replace code and LaTeX blocks by html environments."""

    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, format)

    for i in range(len(tex_blocks)):
        if 'label' in tex_blocks[i]:
            # Fix label -> \label in tex_blocks
            tex_blocks[i] = tex_blocks[i].replace(' label{', ' \\label{')
            tex_blocks[i] = re.sub(r'^label\{', '\\label{',
                                   tex_blocks[i], flags=re.MULTILINE)


    def subst(m):
        tp = m.group(1).strip()
        if tp:
            return '<code type="%s">' % tp
        else:
            return '<code>'

    filestr = re.sub(r'^!bc(.*)', subst, filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!ec', r'</code>', filestr, flags=re.MULTILINE)

    math_tp = []
    if tex_blocks:
        math_tp.append('tex-blocks')
    if re.search(r'<inlinemath>.+?</inlinemath>', filestr):
        math_tp.append('inline-math')
    filestr = '<mathematics type="%s">' % \
              (','.join(math_tp) if math_tp else 'None') + '\n' + filestr

    filestr = re.sub(r'^!bt', '<latex>',  filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!et', '</latex>', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'\(ref\{(.+?)\}\)', r'<eqref>\g<1></eqref>', filestr)


    # Add </li> in lists
    cpattern = re.compile('<li>(.+?)(\s+)<li>', re.DOTALL)
    def find_list_items(match):
        """Return replacement from match of <li> tags."""
        # Does the match run out of the list?
        if re.search(r'</?(ul|ol)>', match.group(1)):
            return '<li>' + match.group(1) + match.group(2)
        else:
            return '<li>' + match.group(1) + '</li>' + match.group(2)

    # cpattern can only detect every two list item because it cannot work
    # with overlapping patterns. Remedy: have two <li> to avoid overlap,
    # fix that after all replacements are done.
    filestr = filestr.replace('<li>', '<li><li>')
    filestr = cpattern.sub(find_list_items, filestr)
    # Fix things that go wrong with cpattern: list items that go
    # through end of lists over to next list item.
    cpattern = re.compile('<li>(.+?)(\s+)(</?ol>|</?ul>)', re.DOTALL)
    filestr = cpattern.sub('<li>\g<1></li>\g<2>\g<3>', filestr)
    filestr = filestr.replace('<li><li>', '<li>')  # fix

    # Reduce redunant newlines and <p> (easy with lookahead pattern)
    # Eliminate any <p> that goes with blanks up to <p> or a section
    # heading
    pattern = r'<newline/>\s+(?=<newline/>|<[hH]\d>)'
    filestr = re.sub(pattern, '', filestr)
    # Extra blank before section heading
    pattern = r'\s+(?=^<[hH]\d>)'
    filestr = re.sub(pattern, '\n\n', filestr, flags=re.MULTILINE)
    # Elimate <newline/> before equations and before lists
    filestr = re.sub(r'<newline/>\s+(<math|<ul>|<ol>)', r'\g<1>', filestr)
    filestr = re.sub(r'<newline/>\s+<title>', '<title>', filestr)
    # Eliminate <newline/> after </h1>, </h2>, etc.
    filestr = re.sub(r'(</h\d>)\s+<newline/>', '\g<1>\n', filestr)

    return filestr

def xml_figure(m):
    caption = m.group('caption').strip()
    filename = m.group('filename').strip()
    opts = m.group('options').strip()

    if opts:
        opts = [s.split('=') for s in opts.split()]
        opts = ['%s="%s"' % (key, value) for key, value in opts]
        opts = ' ' + ' '.join(opts)
    else:
        opts = ''

    text = '<figure filename="%s%s>' % (filename, opts)
    if caption:
        text += '\n<caption>\n%s\n</caption>' % caption
    text += '\n</figure>\n'
    return text

def xml_toc(sections):
    return 'XML TOC not implemented yet'

def xml_table(table):
    # COPY NEW from html.py
    column_width = table_analysis(table['rows'])
    ncolumns = len(column_width)
    column_spec = table.get('columns_align', 'c'*ncolumns).replace('|', '')
    heading_spec = table.get('headings_align', 'c'*ncolumns).replace('|', '')
    a2html = {'r': 'right', 'l': 'left', 'c': 'center'}

    s = '<tabl>\n'
    for i, row in enumerate(table['rows']):
        if row == ['horizontal rule']:
            continue
        if i == 1 and \
           table['rows'][i-1] == ['horizontal rule'] and \
           table['rows'][i+1] == ['horizontal rule']:
            headline = True
            # Empty column headings?
            skip_headline = max([len(column.strip())
                                 for column in row]) == 0
        else:
            headline = False

        s += '<tr>'
        for column, w, ha, ca in \
                zip(row, column_width, heading_spec, column_spec):
            if headline:
                if not skip_headline:
                    s += '<td align="%s"><b> %s </b></td> ' % \
                         (a2html[ha], column.center(w))
            else:
                s += '<td align="%s">   %s    </td> ' % \
                     (a2html[ca], column.ljust(w))
        s += '</tr>\n'
    s += '</table>\n'
    return s

def xml_movie(m):
    filename = m.group('filename').srip()
    opts = m.group('options').strip()
    caption = m.group('caption').strip()

    if opts:
        opts = [s.split('=') for s in opts.split()]
        opts = ['%s="%s"' % (key, value) for key, value in opts]
        opts = ' ' + ' '.join(opts)
    else:
        opts = ''

    autoplay = option('html_video_autoplay=', 'False')
    if autoplay in ('on', 'off', 'True', 'true'):
        autoplay = True
    else:
        autoplay = False
    if opts:
        opts.append('autoplay="%s"' % str(autoplay))

    text = '<figure filename="%s%s>' % (filename, opts)
    if caption:
        text += '\n<caption>\n%s\n</caption>' % caption
    text += '\n</figure>\n'
    return text

def xml_author(authors_and_institutions, auth2index,
                inst2index, index2inst, auth2email):
    # Make a short list of author names - can be extracted elsewhere
    # from the HTML code and used in, e.g., footers.
    authors = [author for author in auth2index]
    if len(authors) > 1:
        authors[-1] = 'and ' + authors[-1]
    authors = ', '.join(authors)
    text = '<authors>\n'

    def email(author):
        return address if address else ''

    email = auth2email[author]
    one_author_at_one_institution = False
    if len(auth2index) == 1:
        author = list(auth2index.keys())[0]
        if len(auth2index[author]) == 1:
            one_author_at_one_institution = True
    if one_author_at_one_institution:
        # drop index
        author = list(auth2index.keys())[0]
        text += """
<author>
<name>%s</name>
""" % author
        if email:
            text += '<email>%s</email>\n' % email
        text += '<institution>%s</institution>\n' %index2inst[1]
    else:
        for author in auth2index:
            text += """
<author>
<name>%s</name>
""" % author
        if email:
            text += '<email>%s</email>\n' % email
        for index in index2inst:
            text += '<institution index="%s">%s</institution>\n' % \
                    (index, index2inst[index])
    text += '</authors>\n'
    return text


def xml_find_paragraphs(filestr):
    lines = filestr.splitlines()
    print 'XML: need to locate end of paragraphs'
    #print filestr
    # Note: figures are already handled
    # Or can we just wait until all tags are written and then
    # recognize where to put </p>
    filestr = '\n'.join(lines)
    return filestr

def xml_ref_and_label(section_label2title, format, filestr):
    # This is the first format-specific function to be called.
    # Go through the file and mark end of paragraphs.
    filestr = xml_find_paragraphs(filestr)

    pattern = r'([Ss]ections?)\s+ref\{(.+?)\}'
    replacement = r'<ref prefix="\g<1>" type="section">\g<2></ref>'
    filestr = re.sub(pattern, replacement, filestr)
    pattern = r'([Cc]apters?)\s+ref\{(.+?)\}'
    replacement = r'<ref prefix="\g<1>" type="chapter">\g<2></ref>'
    filestr = re.sub(pattern, replacement, filestr)
    pattern = r'([Aa]ppendix)\s+ref\{(.+?)\}'
    replacement = r'<ref prefix="\g<1>" type="appendix">\g<2></ref>'
    filestr = re.sub(pattern, replacement, filestr)
    pattern = r'([Aa]ppendices)\s+ref\{(.+?)\}'
    replacement = r'<ref prefix="\g<1>" type="appendix">\g<2></ref>'
    filestr = re.sub(pattern, replacement, filestr)
    pattern = r'([Ff]igures?)\s+ref\{(.+?)\}'
    replacement = r'<ref prefix="\g<1>" type="chapter">\g<2></ref>'
    filestr = re.sub(pattern, replacement, filestr)
    pattern = r'(the\s*)?([Ee]xercises?|[Pp]rojects?|[Pp]roblems?)\s+ref\{(.+?)\}'
    replacement = r'<ref prefix="\g<2>" type="exercise">\g<3></ref>'
    filestr = re.sub(pattern, replacement, filestr)

    # Need special adjustment to handle start of sentence (capital) or not.
    pattern = r'([.?!]\s+|^)<ref prefix="'
    replacement = r'\g<1><ref sentencestart="True" prefix="'
    filestr = re.sub(pattern, replacement, filestr, flags=re.MULTILINE)

    # Did xml to this point. References of this type are hard...
    # 2DO: the rest FIXME: the rest [[[[[[


    # extract the labels in the text (filestr is now without
    # mathematics and those labels)
    running_text_labels = re.findall(r'label\{(.+?)\}', filestr)

    # XML: can have label as attribute for section/subsection/etc?
    # or always <label>..</label>? Think what is best, probably
    # the first one.

    # make special anchors for all the section titles with labels:
    def subst_heading(m):
        heading_tp = (11 - len(m.group(1)))/2
        s = '<section type="%s" label="%s">%s</section>' % (heading_tp, label, title.replace('\\', '\\\\'))
        return s

    for label in section_label2title:
        # make new anchor for this label (put in title):
        title = section_label2title[label]
        title_pattern = r'(={3,9})\s*%s\s*(={3,9})\s*label\{%s\}' % (re.escape(title), label)
        filestr = re.sub(title_pattern, subst_heading, filestr)

    # Deal with all sections without proceding labels
    def subst_heading2(m):
        heading_tp = (11 - len(m.group(1)))/2
        s = '<section type="%s" label="None">%s</section>' % \
            (heading_tp, m.group(2).strip())
        return s
    filestr = re.sub(r'^(={3,9})(.+?)(={3,9})', subst_heading2,
                     filestr, flags=re.MULTILINE)

    filestr = re.sub(r'label\{(.+?)\}', r'<label>\g<1></label>', filestr)

    # Number all figures, find all figure labels and replace their
    # references by the figure numbers
    # (note: figures are already handled!)
    # Can process this by findall and sub, since we assume all
    # captions with label are unique because the label should be unique.
    pattern = '<caption>(.+?)</caption>'
    captions = re.findall(pattern, filestr, flags=re.DOTALL)
    fig_no = 0
    for caption in captions:
        m = re.search(r'<label>(.+?)</label>', filestr)
        if m:
            label = m.group(1)
            filestr = re.sub(pattern,
                             r'<caption no="%s">\g<1></caption>' % fig_no,
                             filestr,
                             flags=re.DOTALL)
            fig_no += 1

    # Replace all admon and many other envirs here (then xml_quote etc
    # will not be called later by doconce.py)
    from doconce import doconce_envirs
    for envir in doconce_envirs()[5:-1]:
        filestr = re.sub(r'^!b%s +(.+)' % envir, r'<%s heading="\g<1>">' % envir,
                         filestr, flags=re.MULTILINE)
        filestr = re.sub(r'^!b%s *' % envir, r'<%s>' % envir,
                         filestr, flags=re.MULTILINE)
        filestr = re.sub(r'^!e%s *' % envir, r'</%s>' % envir,
                         filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!split', '\n<split />', filestr, flags=re.MULTILINE)

    # [[[ Could replace label=None in <section> tags by a unique section id
    return filestr


def xml_index_bib(filestr, index, citations, pubfile, pubdata):
    if citations:
        filestr = cite_with_multiple_args2multiple_cites(filestr)
    for label in citations:
        filestr = filestr.replace('cite{%s}' % label,
                                  '<cite label="%s">%s</cite>' % \
                                  (label, citations[label]))

    if pubfile is not None:
        bibtext = bibliography(pubdata, citations, format='xml')
        bibtext = """

<!-- begin bibliography -->
%s
<!-- end bibliography -->
""" % bibtext

        filestr = re.sub(r'^BIBFILE:.+$', bibtext, filestr, flags=re.MULTILINE)

    filestr = re.sub(r'idx\{(.+?)\}\n?', r'<index>\g<1></index>', filestr)

    return filestr



def xml_quiz(quiz):
    return ''


def xml_footnotes(filestr, format, pattern_def, pattern_footnote):

    footnotes = re.findall(pattern_def, filestr, flags=re.MULTILINE|re.DOTALL)
    names = [name for name, footnote, dummy in footnotes]
    footnotes = {name: text for name, text, dummy in footnotes}

    name2index = {names[i]: i+1 for i in range(len(names))}

    def subst_def(m):
        name = m.group('name').strip()
        text = m.group('text').strip()
        xml = '<footnote:definition id="%s">%s</footnote:definitiaon>' % \
              (name2index[name], text)
        return xml

    filestr = re.sub(pattern_def, subst_def, filestr,
                     flags=re.MULTILINE|re.DOTALL)

    def subst_footnote(m):
        name = m.group('name').strip()
        if name in name2index:
            i = name2index[m.group('name')]
        else:
            print '*** error: found footnote with name "%s", but this one is not defined' % name
            _abort()
        xml = r'<footnote id="%s">%s<footnote>' % (i, name)
        return xml

    filestr = re.sub(pattern_footnote, subst_footnote, filestr)
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

    FILENAME_EXTENSION['xml'] = '.xml'  # output file extension
    BLANKLINE['xml'] = '\n<blankline />\n' # blank input line => new paragraph
    BLANKLINE['xml'] = '\n'

    INLINE_TAGS_SUBST['xml'] = {         # from inline tags to HTML tags
        # keep math as is:
        'math':          r'\g<begin><inlinemath>\g<subst></inlinemath>\g<end>',
        'math2':         r'\g<begin><inlinemath>\g<latexmath></inlinemath>\g<end>',
        'emphasize':     r'\g<begin><em>\g<subst></em>\g<end>',
        'bold':          r'\g<begin><b>\g<subst></b>\g<end>',
        'verbatim':      r'\g<begin><inlinecode>\g<subst></inlinecode>\g<end>',
        'colortext':     r'<color type="\g<color>">\g<text></color>',
        #'linkURL':       r'\g<begin><a href="\g<url>">\g<link></a>\g<end>',
        'linkURL2':      r'<link url="\g<url>">\g<link></link>',
        'linkURL3':      r'<link url="\g<url>">\g<link></link>',
        'linkURL2v':     r'<link url="\g<url>"><inlinecode>\g<link></inlinecode></link>',
        'linkURL3v':     r'<link url="\g<url>"><inlinecode>\g<link></inlinecode></link>',
        'plainURL':      r'<link url="\g<url>"><inlinecode>\g<url></inlinecode></link>',
        'inlinecomment': r'<inlinecomment name="\g<name>">\g<comment></inlinecomment>',
        'chapter':       r'\n<h1>\g<subst></h1>',
        'section':       r'\n<h2>\g<subst></h2>',
        'subsection':    r'\n<h3>\g<subst></h3>',
        'subsubsection': r'\n<h4>\g<subst></h4>\n',
        'paragraph':     r'<b>\g<subst></b>\g<space>',
        'abstract':      r'<abstract type="\g<type>">\n\g<text>\n</abstract>\n\g<rest>',
        'title':         r'\n<title>\g<subst></title>',
        'date':          r'<date>\n\g<subst>\n</date>',
        'author':        xml_author,
        'figure':        xml_figure,
        'movie':         xml_movie,
        'comment':       '<comment>%s</comment>',
        'footnote':      xml_footnotes,
        'non-breaking-space': '<nonbreakingspace />',
        'horizontal-rule': '<horizontalrule />',
        'linebreak':     r'\g<text><linebreak />',
        'ampersand2':    r' \g<1><ampersand />\g<2>',
        'ampersand1':    r'\g<1> <ampersand /> \g<2>',
        }

    if option('wordpress'):
        INLINE_TAGS_SUBST['xml'].update({
            'math':          r'\g<begin>$latex \g<subst>$\g<end>',
            'math2':         r'\g<begin>$latex \g<latexmath>$\g<end>'
            })

    ENVIRS['xml'] = {}

    CODE['xml'] = xml_code

    # how to typeset lists and their items in html:
    LIST['xml'] = {
        'itemize':
        {'begin': '\n<ul>\n', 'item': '<li>', 'end': '</ul>\n\n'},

        'enumerate':
        {'begin': '\n<ol>\n', 'item': '<li>', 'end': '</ol>\n\n'},

        'description':
        {'begin': '\n<dl>\n', 'item': '<dt>%s<dd>', 'end': '</dl>\n\n'},

        'separator': '<newline/>',
        }

    # how to typeset description lists for function arguments, return
    # values, and module/class variables:
    ARGLIST['xml'] = {
        'parameter': '<b>argument</b>',
        'keyword': '<b>keyword argument</b>',
        'return': '<b>return value(s)</b>',
        'instance variable': '<b>instance variable</b>',
        'class variable': '<b>class variable</b>',
        'module variable': '<b>module variable</b>',
        }

    FIGURE_EXT['xml'] = ('.png', '.gif', '.jpg', '.jpeg')
    CROSS_REFS['xml'] = xml_ref_and_label
    TABLE['xml'] = xml_table
    INDEX_BIB['xml'] = xml_index_bib
    EXERCISE['xml'] = plain_exercise
    TOC['xml'] = xml_toc
    QUIZ['xml'] = xml_quiz

    INTRO['xml'] = """\
<?xml version="1.0" encoding="utf-8"?>
"""

    keywords = re.findall(r'idx\{(.+?)\}', filestr)
    # idx with verbatim is usually too specialized - remove them
    keywords = [keyword for keyword in keywords
                if not '`' in keyword]
    # keyword!subkeyword -> keyword subkeyword
    keywords = ','.join(keywords).replace('!', ' ')

    if keywords:
        meta_tags = '<meta name="keywords" content="%s">\n' % keywords
        INTRO['xml'] += """\
<keywords>%s</keywords>
""" % (meta_tags)

    # document ending:
    OUTRO['xml'] = ""
