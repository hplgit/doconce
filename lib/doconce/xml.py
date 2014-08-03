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
     cite_with_multiple_args2multiple_cites, _abort, is_file_or_url
from misc import option


def html_code(filestr, code_blocks, code_block_types,
              tex_blocks, format):
    """Replace code and LaTeX blocks by html environments."""


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

    filestr = re.sub(r'^!bc(.*?)', subst, filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!ec', r'</code>', filestr, flags=re.MULTILINE)

    math_tp = []
    if text_blocks:
        math_tp.append('tex-blocks')
    if re.search(r'<math>.+?</math>'):
        math_tp.append('inline-math')
    filestr = '<mathemathics type="%s">' % \
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

def html_figure(m):
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

def html_table(table):
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

def html_movie(m):
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

def html_author(authors_and_institutions, auth2index,
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


def html_ref_and_label(section_label2title, format, filestr):
    # NOTE: drop this html version, just replace ref{} by <ref ..
    # can of course find the prefix and if it is start of line etc...
    # .... see section ref{my:sec} is replaced by
    # see the section "...section heading..."
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

    # Need special adjustment to handle start of sentence (capital) or not.
    pattern = r'([.?!]\s+|^)<ref prefix="'
    replacement = r'\g<1><ref sentencestart="True" prefix="'
    filestr = re.sub(pattern, replacement, filestr, flags=re.MULTILINE)

    # Did xml to this point. References of this type are hard...
    # 2DO: the rest FIXME: the rest [[[[[[

    # Remove Exercise, Project, Problem in references since those words
    # are used in the title of the section too
    pattern = r'(the\s*)?([Ee]xercises?|[Pp]rojects?|[Pp]roblems?)\s+ref\{'
    replacement = r'ref{'
    filestr = re.sub(pattern, replacement, filestr)

    # extract the labels in the text (filestr is now without
    # mathematics and those labels)
    running_text_labels = re.findall(r'label\{(.+?)\}', filestr)

    # XML: can have label as attribute for section/subsection/etc?
    # or always <label>..</label>? Think what is best, probably
    # the first one.

    # make special anchors for all the section titles with labels:
    for label in section_label2title:
        # make new anchor for this label (put in title):
        title = section_label2title[label]
        title_pattern = r'(_{3,9}|={3,9})\s*%s\s*(_{3,9}|={3,9})\s*label\{%s\}' % (re.escape(title), label)
        title_new = '\g<1> %s <a name="%s"></a> \g<2>' % (title.replace('\\', '\\\\'), label)
        filestr, n = re.subn(title_pattern, title_new, filestr)
        # (a little odd with mix of doconce title syntax and html NAME tag...)
        if n == 0:
            #raise Exception('problem with substituting "%s"' % title)
            pass

    # turn label{myname} to anchors <a name="myname"></a>
    filestr = re.sub(r'label\{(.+?)\}', r'<a name="\g<1>"></a>', filestr)

    # replace all references to sections by section titles:
    for label in section_label2title:
        title = section_label2title[label]
        filestr = filestr.replace('ref{%s}' % label,
                                  '<a href="#%s">%s</a>' % (label, title))

    # This special character transformation is easier done
    # with encoding="utf-8" in the first line in the html file:
    # (but we do it explicitly to make it robust)
    filestr = latin2html(filestr)
    # (wise to do latin2html before filestr = '\n'.join(lines) below)

    # Number all figures, find all figure labels and replace their
    # references by the figure numbers
    # (note: figures are already handled!)
    caption_start = '<p class="caption">'
    caption_pattern = r'%s(.+?)</p>' % caption_start
    label_pattern = r'%s.+?<a name="(.+?)">' % caption_start
    lines = filestr.splitlines()
    label2no = {}
    fig_no = 0
    for i in range(len(lines)):
        if caption_start in lines[i]:
            m = re.search(caption_pattern, lines[i])
            if m:
                fig_no += 1
                caption = m.group(1)
                from_ = caption_start + caption
                to_ = caption_start + 'Figure %d: ' % fig_no + caption
                lines[i] = lines[i].replace(from_, to_)

            m = re.search(label_pattern, lines[i])
            if m:
                label2no[m.group(1)] = fig_no
    filestr = '\n'.join(lines)

    for label in label2no:
        filestr = filestr.replace('ref{%s}' % label,
                                  '<a href="#%s">%d</a>' %
                                  (label, label2no[label]))

    # replace all other references ref{myname} by <a href="#myname">myname</a>:
    for label in running_text_labels:
        filestr = filestr.replace('ref{%s}' % label,
                                  '<a href="#%s">%s</a>' % (label, label))

    # insert enumerated anchors in all section headings without label
    # anchors, in case we want a table of contents with links to each section
    section_pattern = re.compile(r'^\s*(_{3,9}|={3,9})(.+?)(_{3,9}|={3,9})\s*$',
                                 re.MULTILINE)
    m = section_pattern.findall(filestr)
    for i in range(len(m)):
        heading1, title, heading2 = m[i]
        if not '<a name="' in title:
            newtitle = title + ' <a name="___sec%d"></a>' % i
            filestr = filestr.replace(heading1 + title + heading2,
                                      heading1 + newtitle + heading2,
                                      1) # count=1: only the first!

    return filestr


def html_index_bib(filestr, index, citations, pubfile, pubdata):
    if citations:
        filestr = cite_with_multiple_args2multiple_cites(filestr)
    for label in citations:
        filestr = filestr.replace('cite{%s}' % label,
                                  '<a href="#%s">[%d]</a>' % \
                                  (label, citations[label]))
    if pubfile is not None:
        bibtext = bibliography(pubdata, citations, format='doconce')
        for label in citations:
            try:
                bibtext = bibtext.replace('label{%s}' % label,
                                          '<a name="%s"></a>' % label)
            except UnicodeDecodeError, e:
                print e
                print '*** error: problems in %s' % pubfile
                print '    with key', label
                _abort()

        bibtext = """
<!-- begin bibliography -->
%s
<!-- end bibliography -->
""" % bibtext

        filestr = re.sub(r'^BIBFILE:.+$', bibtext, filestr, flags=re.MULTILINE)

    # could use anchors for idx{...}, but multiple entries of an index
    # would lead to multiple anchors, so remove them all:
    filestr = re.sub(r'idx\{.+?\}\n?', '', filestr)

    return filestr

# Module variable holding info about section titles etc.
# To be used in navitation panels.
global tocinfo
tocinfo = None

def html_toc(sections):
    # Find minimum section level
    level_min = 4
    for title, level, label in sections:
        if level < level_min:
            level_min = level


    extended_sections = []  # extended list for toc in HTML file
    #hr = '<hr>'
    hr = ''
    s = '<h2>Table of contents</h2>\n\n%s\n' % hr
    for i in range(len(sections)):
        title, level, label = sections[i]
        href = label if label is not None else '___sec%d' % i
        indent = '&nbsp; '*(3*(level - level_min))
        s += indent + '<a href="#%s">%s</a>' % (href, title ) + '<br>\n'
        extended_sections.append((title, level, label, href))
    s += '%s\n<p>\n' % hr

    # Store for later use in navgation panels etc.
    global tocinfo
    tocinfo = {'sections': extended_sections, 'highest level': level_min}

    return s

def html_box(block, format, text_size='normal'):
    """Add a HTML box with text, code, equations inside. Can have shadow."""
    # box_shadow is a global variable set in the top of the file
    shadow = ' ' + box_shadow if option('html_box_shadow') else ''
    return """
<!-- begin box -->
<div style="width: 95%%; padding: 10px; border: 1px solid #000; border-radius: 4px;%s">
%s
</div>
<!-- end box -->
""" % (shadow, block)

def html_quote(block, format, text_size='normal'):
    return """\
<blockquote>
%s
</blockquote>
""" % (indent_lines(block, format, ' '*4, trailing_newline=False))

admons = 'notice', 'summary', 'warning', 'question', 'block'
global admon_css_vars        # set in define
global html_admon_style      # set below

html_admon_style = option('html_admon=', None)
if html_admon_style is None:
    # Set sensible default value
    if option('html_style=') == 'solarized':
        html_admon_style = 'apricot'
    elif option('html_style=') == 'blueish2':
        html_admon_style = 'yellow'
    else:
        html_admon_style = 'gray'

for _admon in admons:
    _Admon = _admon.capitalize()  # upper first char
    # Below we could use
    # <img src="data:image/png;base64,iVBORw0KGgoAAAANSUh..."/>
    _text = '''
def html_%(_admon)s(block, format, title='%(_Admon)s', text_size='normal'):
    # No title?
    if title.lower().strip() == 'none':
        title = ''
    # Blocks without explicit title should have empty title
    if title == 'Block':  # block admon has no default title
        title = ''

    if title and title[-1] not in ('.', ':', '!', '?'):
        # Make sure the title ends with puncuation
        title += '.'

    # Make pygments background equal to admon background for colored admons?
    keep_pygm_bg = option('keep_pygments_html_bg')
    pygments_pattern = r'"background: .+?">'

    # html_admon_style is global variable
    if html_admon_style == 'colors':
        if not keep_pygm_bg:
            block = re.sub(pygments_pattern, r'"background: %%s">' %%
                           admon_css_vars['colors']['background_%(_admon)s'], block)
        janko = """<div class="%(_admon)s alert-text-%%s"><b>%%s</b>
%%s
</div>
""" %% (text_size, title, block)
        return janko

    elif html_admon_style in ('gray', 'yellow', 'apricot'):
        if not keep_pygm_bg:
            block = re.sub(pygments_pattern, r'"background: %%s">' %%
                           admon_css_vars[html_admon_style]['background'], block)
        code = """<div class="alert alert-block alert-%(_admon)s alert-text-%%s"><b>%%s</b>
%%s
</div>
""" %% (text_size, title, block)
        return code

    elif html_admon_style == 'lyx':
        block = '<div class="alert-text-%%s">%%s</div>' %% (text_size, block)
        if '%(_admon)s' != 'block':
            lyx = """
<table width="95%%%%" border="0">
<tr>
<td width="25" align="center" valign="top">
<img src="https://raw.github.com/hplgit/doconce/master/bundled/html_images/lyx_%(_admon)s.png" hspace="5" alt="%(_admon)s"></td>
<th align="left" valign="middle"><b>%%s</b></th>
</tr>
<tr><td>&nbsp;</td> <td align="left" valign="top"><p>
%%s
</p></td></tr>
</table>
""" %% (title, block)
        else:
            lyx = """
<table width="95%%%%" border="0">
<tr><th align="left" valign="middle"><b>%%s</b></th>
</tr>
<tr><td>&nbsp;&nbsp;&nbsp;&nbsp;</td> <td align="left" valign="top"><p>
%%s
</p></td></tr>
</table>
""" %% (title, block)
        return lyx

    else:
        # Plain paragraph
        paragraph = """

<!-- admonition: %(_admon)s, typeset as paragraph -->
<div class="alert-text-%%s"><b>%%s</b>
%%s
</div>
""" %% (text_size, title, block)
        return paragraph
''' % vars()
    exec(_text)

def html_quiz(quiz):
    return ''

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

    FILENAME_EXTENSION['xml'] = '.html'  # output file extension
    BLANKLINE['xml'] = '\n<blankline>\n' # blank input line => new paragraph

    INLINE_TAGS_SUBST['xml'] = {         # from inline tags to HTML tags
        # keep math as is:
        'math':          r'\g<begin>\( \g<subst> \)\g<end>',
        'math2':         r'\g<begin>\( \g<latexmath> \)\g<end>',
        'emphasize':     r'\g<begin><em>\g<subst></em>\g<end>',
        'bold':          r'\g<begin><b>\g<subst></b>\g<end>',
        'verbatim':      r'\g<begin><code>\g<subst></code>\g<end>',
        'colortext':     r'<font color="\g<color>">\g<text></font>',
        #'linkURL':       r'\g<begin><a href="\g<url>">\g<link></a>\g<end>',
        'linkURL2':      r'<a href="\g<url>" target="_self">\g<link></a>',
        'linkURL3':      r'<a href="\g<url>" target="_self">\g<link></a>',
        'linkURL2v':     r'<a href="\g<url>" target="_self"><tt>\g<link></tt></a>',
        'linkURL3v':     r'<a href="\g<url>" target="_self"><tt>\g<link></tt></a>',
        'plainURL':      r'<a href="\g<url>" target="_self"><tt>\g<url></tt></a>',
        'inlinecomment': r'\n<!-- begin inline comment -->\n<font color="red">[<b>\g<name></b>: <em>\g<comment></em>]</font>\n<!-- end inline comment -->\n',
        'chapter':       r'\n<h1>\g<subst></h1>',
        'section':       r'\n<h2>\g<subst></h2>',
        'subsection':    r'\n<h3>\g<subst></h3>',
        'subsubsection': r'\n<h4>\g<subst></h4>\n',
        'paragraph':     r'<b>\g<subst></b>\g<space>',
        'abstract':      r'<abstract type="\g<type>">\n\g<text>\n</abstract>\n\g<rest>',
        'title':         r'\n<title>\g<subst></title>\n\n<center><h1>\g<subst></h1></center>',
        'date':          r'<date>\n\g<subst>\n</date>',
        'author':        html_author,
        'figure':        html_figure,
        'movie':         html_movie,
        'comment':       '<comment>%s</comment>',
        'linebreak':     r'\g<text><br />',
        'ampersand2':    r' \g<1><ampersand>\g<2>',
        'ampersand1':    r'\g<1> <ampersand> \g<2>',
        }

    if option('wordpress'):
        INLINE_TAGS_SUBST['xml'].update({
            'math':          r'\g<begin>$latex \g<subst>$\g<end>',
            'math2':         r'\g<begin>$latex \g<latexmath>$\g<end>'
            })

    ENVIRS['xml'] = {
        'quote':         html_quote,
        'warning':       html_warning,
        'question':      html_question,
        'notice':        html_notice,
        'summary':       html_summary,
        'block':         html_block,
        'box':           html_box,
    }

    CODE['xml'] = html_code

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
    CROSS_REFS['xml'] = html_ref_and_label
    TABLE['xml'] = html_table
    INDEX_BIB['xml'] = html_index_bib
    EXERCISE['xml'] = plain_exercise
    TOC['xml'] = html_toc
    QUIZ['xml'] = html_quiz

    # Embedded style sheets
    style = option('html_style=')
    if  style == 'solarized':
        css = css_solarized
    elif style == 'blueish':
        css = css_blueish
    elif style == 'blueish2':
        css = css_blueish2
    elif style == 'bloodish':
        css = css_bloodish
    else:
        css = css_blueish # default

    if not option('no_pygments_html') and \
           option('html_style=', 'blueish') != 'solarized':
        # Remove pre style as it destroys the background for pygments
        css = re.sub(r'pre .*?\{.+?\}', '', css, flags=re.DOTALL)

    # Fonts
    body_font_family = option('html_body_font=', None)
    heading_font_family = option('html_heading_font=', None)
    google_fonts = ('Patrick+Hand+SC', 'Molle:400italic', 'Happy+Monkey',
                    'Roboto+Condensed', 'Fenix', 'Yesteryear',
                    'Clicker+Script', 'Stalemate',
                    'Herr+Von+Muellerhoff', 'Sacramento',
                    'Architects+Daughter', 'Kotta+One',)
    if body_font_family == '?' or body_font_family == 'help' or \
       heading_font_family == '?' or heading_font_family == 'help':
        print ' '.join(google_fonts)
        _abort()
    link = "@import url(http://fonts.googleapis.com/css?family=%s);"
    import_body_font = ''
    if body_font_family is not None:
        if body_font_family in google_fonts:
            import_body_font = link % body_font_family
        else:
            print '*** warning: --html_body_font=%s is not valid' % body_font_family
    import_heading_font = ''
    if heading_font_family is not None:
        if heading_font_family in google_fonts:
            import_heading_font = link % heading_font_family
        else:
            print '*** warning: --html_heading_font=%s is not valid' % heading_font_family
    if import_body_font or import_heading_font:
        css = '    ' + '\n    '.join([import_body_font, import_heading_font]) \
              + '\n' + css
    if body_font_family is not None:
        css = re.sub(r'font-family:.+;',
                     "font-family: '%s';" % body_font_family.replace('+', ' '),
                     css)
    if heading_font_family is not None:
        css += "\n    h1, h2, h3 { font-family: '%s'; }\n" % heading_font_family.replace('+', ' ')

    global admon_css_vars
    admon_styles = 'gray', 'yellow', 'apricot', 'colors', 'lyx', 'paragraph'
    admon_css_vars = {style: {} for style in admon_styles}
    admon_css_vars['yellow']  = dict(boundary='#fbeed5', background='#fcf8e3')
    admon_css_vars['apricot'] = dict(boundary='#FFBF00', background='#fbeed5')
    #admon_css_vars['gray']    = dict(boundary='#bababa', background='whiteSmoke')
    admon_css_vars['gray']    = dict(boundary='#bababa', background='#f8f8f8') # same color as in pygments light gray background
    # Override with user's values
    html_admon_bg_color = option('html_admon_bg_color=', None)
    html_admon_bd_color = option('html_admon_bd_color=', None)
    if html_admon_bg_color is not None:
        for tp in ('yellow', 'apricot', 'gray'):
            admon_css_vars[tp]['background'] = html_admon_bg_color
    if html_admon_bd_color is not None:
        for tp in ('yellow', 'apricot', 'gray'):
            admon_css_vars[tp]['boundary'] = html_admon_bd_color

    for a in admons:
        if a != 'block':
            admon_css_vars['yellow']['icon_' + a]  = 'small_yellow_%s.png' % a
            admon_css_vars['apricot']['icon_' + a] = 'small_yellow_%s.png' % a
            admon_css_vars['gray']['icon_' + a]    = 'small_gray_%s.png' % a
        else:
            admon_css_vars['yellow']['icon_' + a]  = ''
            admon_css_vars['apricot']['icon_' + a] = ''
            admon_css_vars['gray']['icon_' + a]    = ''
    admon_css_vars['colors'] = dict(
        background_notice='#BDE5F8',
        background_block='#BDE5F8',
        background_summary='#DFF2BF',
        background_warning='#FEEFB3',
        background_question='#DFF2BF',
        icon_notice='Knob_Info.png',
        icon_summary='Knob_Valid_Green.png',
        icon_warning='Knob_Attention.png',
        icon_question='Knob_Forward.png',
        icon_block='',
        )
    if option('html_admon_shadow'):
        # Add a shadow effect to the admon_styles2 boxes
        global admon_styles2
        admon_styles2 = re.sub(
            r'(-webkit-|-moz-|)(border-radius: \d+px;)',
            '\g<1>\g<2> \g<1>%s' % box_shadow,
            admon_styles2)

    # Need to add admon_styles? (html_admon_style is global)
    for admon in admons:
        if '!b'+admon in filestr and '!e'+admon in filestr:
            if html_admon_style == 'colors':
                css += (admon_styles1 % admon_css_vars[html_admon_style])
            elif html_admon_style in ('gray', 'yellow', 'apricot'):
                css += (admon_styles2 % admon_css_vars[html_admon_style])
            elif html_admon_style in ('lyx', 'paragraph'):
                css += admon_styles_text
            break

    style = """
<style type="text/css">
%s
</style>
""" % css
    css_filename = option('css=')
    if css_filename:
        style = ''
        if ',' in css_filename:
            css_filenames = css_filename.split(',')
        else:
            css_filenames = [css_filename]
        for css_filename in css_filenames:
            if css_filename:
                if not os.path.isfile(css_filename):
                    # Put the style in the file when the file does not exist
                    f = open(css_filename, 'w')
                    f.write(css)
                    f.close()
                style += '<link rel="stylesheet" href="%s">\n' % css_filename
                add_to_file_collection(filename)

    meta_tags = """\
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="generator" content="Doconce: https://github.com/hplgit/doconce/" />
"""
    m = re.search(r'^TITLE: *(.+)$', filestr, flags=re.MULTILINE)
    if m:
        meta_tags += '<meta name="description" content="%s">\n' % \
                     m.group(1).strip()
    keywords = re.findall(r'idx\{(.+?)\}', filestr)
    # idx with verbatim is usually too specialized - remove them
    keywords = [keyword for keyword in keywords
                if not '`' in keyword]
    # keyword!subkeyword -> keyword subkeyword
    keywords = ','.join(keywords).replace('!', ' ')

    if keywords:
        meta_tags += '<meta name="keywords" content="%s">\n' % keywords


    INTRO['xml'] = """\
<!DOCTYPE html>
<!--
Automatically generated HTML file from Doconce source
(https://github.com/hplgit/doconce/)
-->
<html>
<head>
%s

%s
</head>
<body>

    """ % (meta_tags, style)

    # document ending:
    OUTRO['xml'] = """

</body>
</html>
    """
