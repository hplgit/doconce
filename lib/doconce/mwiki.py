"""
MediaWiki translator, aimed at Wikipedia/WikiBooks type of web pages.
Syntax defined by http://en.wikipedia.org/wiki/Help:Wiki_markup
and http://en.wikipedia.org/wiki/Help:Displaying_a_formula.
The prefix m in the name mwiki distinguishes this translator from
gwiki (googlecode wiki).

Not yet implemented:
mwiki_ref_and_label (just using code from gwiki)

Just using plan ASCII solutions for index_bib (requires some work to
port to MediaWiki, but is straightforward - use rst as template) and
exercise (probably ok with the plain solution).

GitHub wiki pages understand MediaWiki, see
https://github.com/github/gollum

The page http://en.wikibooks.org/wiki/Wikibooks:Sandbox is fine for
short-lived experiments.

http://shoutwiki.com can host MediaWiki pages.
http://jumpwiki.com/wiki/Main_Page can also host MediaWiki pages, but
there are troubles with align envirs and math (ugly typesetting and
some strange indents).

Create a user account, choose *Create a Wiki* in the menu on the left,
fill out the form, wait until you get a Main Page, click on edit, make
references to a new page, say [[First demo|demo]], save, click on
demo and fill out that page with the content of a mydoconcefile.wiki,
sometimes it is necessary to create a new account, just do that and
go back.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from builtins import *
from future import standard_library
standard_library.install_aliases()
from builtins import range


import re, os, subprocess, sys
from .common import default_movie, plain_exercise, insert_code_and_tex
from .plaintext import plain_quiz
from .misc import _abort

def align2equations(math_text):
    """
    Transform an align environment to a set of equation environments.
    Used to handle multiple equations if align does not work well.

    Note: This version is outdated. common.align2equations is the
    newest attempt to implement align in terms of single equations.
    """
    if not '{align' in math_text:
        return
    math_text = math_text.replace('&', '')
    math_text = math_text.replace('\\\\', r"""
</math>

:<math>""")
    pattern = r'\\(begin|end)\{align\*?\}\s*'
    math_text = re.sub(pattern, '', math_text)
    # :<math> and </math> surroundings appear when !bt and !et are translated
    return math_text

def equation2nothing(math_text):
    pattern = r'\\(begin|end)\{equation\*?\}\s*'
    math_text = re.sub(pattern, '', math_text)
    math_text = math_text.replace(r'\[', '')
    math_text = math_text.replace(r'\]', '')
    return math_text

def remove_labels(math_text):
    pattern = 'label\{(.+?)\}\s*'
    labels = re.findall(pattern, math_text)
    if labels:
        math_text = re.sub(pattern, '', math_text)
    return math_text, labels


def mwiki_code(filestr, code_blocks, code_block_types,
               tex_blocks, format):
    # http://en.wikipedia.org/wiki/Help:Displaying_a_formula
    # MediaWiki math does not support labels in equations.
    # The enviros equation and \[ \] must be removed (not supported).

    for i in range(len(tex_blocks)):
        # Standard align works in Wikipedia and Wikibooks.
        # Standard align gives somewhat ugly output on wiiki.com services,
        # but a set of separate equations is not much better.
        # We therefore stick to align instead.
        #tex_blocks[i] = align2equations(tex_blocks[i])
        tex_blocks[i] = equation2nothing(tex_blocks[i])
        tex_blocks[i], labels = remove_labels(tex_blocks[i])
        for label in labels:
            if label in filestr:
                print('*** warning: reference to label "%s" in an equation does not work in MediaWiki' % label)

    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, format)

    # Supported programming languages:
    # http://www.mediawiki.org/wiki/Extension:SyntaxHighlight_GeSHi#Supported_languages
    envir2lang = dict(cod='python', pycod='python', cycod='python',
                      fcod='fortran', ccod='c', cppcod='cpp',
                      mcod='matlab', plcod='perl', shcod='bash',
                      pro='python', pypro='python', cypro='python',
                      fpro='fortran', cpro='c', cpppro='cpp',
                      mpro='matlab', plpro='perl', shpro='bash',
                      rbpro='ruby', rbcod='ruby',
                      javacod='java', javapro='java',
                      htmlcod='html5', xmlcod='xml',
                      htmlpro='html5', xmlpro='xml',
                      html='html5', xml='xml',
                      sys='bash', dat='text', csv='text', txt='text',
                      pyoptpro='python', pyscpro='python',
                      ipy='python', pyshell='python',
                      )

    for key in envir2lang:
        language = envir2lang[key]
        cpattern = re.compile(r'^!bc\s+%s\s*\n' % key, flags=re.MULTILINE)
        filestr = cpattern.sub('<syntaxhighlight lang="%s">\n' % \
                               envir2lang[key], filestr)
    c = re.compile(r'^!bc.*$\n', re.MULTILINE)
    filestr = c.sub('<syntaxhighlight lang="text">\n', filestr)
    filestr = re.sub(r'!ec\n', '</syntaxhighlight>\n', filestr)
    c = re.compile(r'^!bt\n', re.MULTILINE)
    filestr = c.sub(':<math>\n', filestr)
    filestr = re.sub(r'!et\n', '</math>\n', filestr)

    # Final fix of MediaWiki file

    # __TOC__ syntax is misinterpretated as paragraph heading, so we
    # use <<<TOC>>> instead and replace to right syntax here at the end.
    filestr = filestr.replace('<<<TOC>>>', '__TOC__')

    return filestr


def mwiki_figure(m):
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
            failure, output = subprocess.getstatusoutput(cmd)
            if failure:
                print('\n**** warning: could not run ', cmd)
                print('       convert %s to PNG format manually' % filename)
                _abort()
            filename = root + '.png'

    caption = m.group('caption').strip()
    if caption != '':
        caption = '|' + caption  # add | for non-empty caption
    else:
        # Avoid filename as caption when caption is empty
        # see http://www.mediawiki.org/wiki/Help:Images
        caption = '|<span title=""></span>'
    # keep label if it's there:
    caption = re.sub(r'label\{(.+?)\}', '(\g<1>)', caption)

    size = ''
    opts = m.group('options').strip()
    if opts:
        info = dict([s.split('=') for s in opts.split()])
        if 'width' in info and 'height' in info:
            size = '|%sx%spx' % (info['width'], info['height'])
        elif 'width' in info:
            size = '|%spx' % info['width']
        elif 'height' in info:
            size = '|x%spx' % info['height']

    if link:
        # We link to some image on the web
        filename = os.path.basename(filename)
        link = os.path.dirname(link)
        result = r"""
[[File:%s|frame%s|link=%s|alt=%s%s]]
""" % (filename, size, link, filename, caption)
    else:
        # We try to link to a file at wikimedia.org.
        found_wikimedia = False
        orig_filename = filename
        # Check if the file exists and find the appropriate wikimedia name.
        # http://en.wikipedia.org/w/api.php?action=query&titles=Image:filename&prop=imageinfo&format=xml

        # Skip directories - get the basename
        filename = os.path.basename(filename)
        import urllib.request, urllib.parse, urllib.error
        prms = urllib.parse.urlencode({
            'action': 'query', 'titles': 'Image:' + filename,
            'prop': 'imageinfo', 'format': 'xml'})
        url = 'http://en.wikipedia.org/w/api.php?' + prms
        try:
            print(' ...checking if %s is stored at en.wikipedia.org/w/api.php...' % filename)
            f = urllib.request.urlopen(url)

            imageinfo = f.read()
            f.close()
            def get_data(name, text):
                pattern = '%s="(.*?)"' % name
                m = re.search(pattern, text)
                if m:
                    match = m.group(1)
                    if 'Image:' in match:
                        return match.split('Image:')[1]
                    if 'File:' in match:
                        return match.split('File:')[1]
                    else:
                        return match
                else:
                    return None

            data = ['from', 'to', 'title', 'missing', 'imagerepository',
                    'timestamp', 'user']
            orig_filename = filename
            filename = get_data('title', imageinfo)
            user = get_data('user', imageinfo)
            timestamp = get_data('timestamp', imageinfo)
            if user:
                found_wikimedia = True
                print(' ...found %s at wikimedia' % filename)
                result = r"""
    [[File:%s|frame%s|alt=%s%s]] <!-- user: %s, filename: %s, timestamp: %s -->
    """ % (filename, size, filename, caption, user, orig_filename, timestamp)
        except IOError:
            print(' ...no Internet connection...')

        if not found_wikimedia:
            print(' ...for wikipedia/wikibooks you must upload image file %s to\n    common.wikimedia.org' % orig_filename)
            # see http://commons.wikimedia.org/wiki/Commons:Upload
            # and http://commons.wikimedia.org/wiki/Special:UploadWizard
            print(' ...for now we use local file %s' % filename)
            # This is fine if we use github wiki

            result = r"""
[[File:%s|frame%s|alt=%s%s]] <!-- not yet uploaded to common.wikimedia.org -->
""" % (filename, size, filename, caption)

    return result

from .common import table_analysis


def mwiki_author(authors_and_institutions, auth2index,
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
    # we skip institutions in mwiki
    return text

from .gwiki import wiki_ref_and_label_common

def mwiki_ref_and_label(section_label2title, format, filestr):
    return wiki_ref_and_label_common(section_label2title, format, filestr)

def mwiki_admon(block, format, title='Warning', text_size='normal',
                admon_type='warning'):
    if title.lower().strip() == 'none':
        title = ''
    # Blocks without explicit title should have empty title
    if title == 'Block':
        title = ''

    if title and title[-1] not in ('.', ':', '!', '?'):
        # Make sure the title ends with puncuation
        title += '.'

    admon_type2mwiki = dict(notice='notice',
                            warning='warning',  # or critical or important
                            hint='notice',
                            quote='quote')
    if admon_type in admon_type2mwiki:
        admon_type = admon_type2mwiki[admon_type]  # use mwiki admon
    else:
        admon_type = title # Just use the title

    text = "'''%s''' " % title + block

    if text_size == 'normal':
        text_size = '90%'
    elif text_size == 'large':
        text_size = '130%'
    elif text_size == 'small':
        text_size = '80%'

    if admon_type == 'quote':
        s = """
{{quote box
| quote = %s
| textstyle = font-size: %s;
}}

""" % (block, text_size)
        # quote has also | source = ... but other formats like
        # latex and html have no specific source tag, so it must
        # be typeset manually
    else:
        s = """
{{mbox
| type = %s
| textstyle = font-size: %s;
| text = %s
}}

""" % (admon_type, text_size, text)
    return s

# mbox: notice

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

    FILENAME_EXTENSION['mwiki'] = '.mwiki'  # output file extension
    BLANKLINE['mwiki'] = '\n'

    # replacement patterns for substitutions of inline tags
    INLINE_TAGS_SUBST['mwiki'] = {
        'math':          r'\g<begin><math>\g<subst></math>\g<end>',
        'math2':         r'\g<begin><math>\g<latexmath></math>\g<end>',
        'emphasize':     r"\g<begin>''\g<subst>''\g<end>",
        'bold':          r"\g<begin>'''\g<subst>'''\g<end>",
        'verbatim':      r'\g<begin><code>\g<subst></code>\g<end>',
        #'linkURL':       r'\g<begin>[\g<url> \g<link>]\g<end>',
        'linkURL2':      r'[\g<url> \g<link>]',
        'linkURL3':      r'[\g<url> \g<link>]',
        'linkURL2v':     r'[\g<url> <code>\g<link></code>]',
        'linkURL3v':     r'[\g<url> <code>\g<link></code>]',
        'plainURL':      r'\g<url>',
        'colortext':     r'<font color="\g<color>">\g<text></font>',
        'chapter':       r"""== '''\g<subst>''' ==""",
        'section':       r'== \g<subst> ==',
        'subsection':    r'=== \g<subst> ===',
        'subsubsection': r'==== \g<subst> ====\n',
        'paragraph':     r"''\g<subst>''\n",
        'title':         r'#TITLE (actually governed by the filename): \g<subst>\n',
        'date':          r'===== \g<subst> =====',
        'author':        mwiki_author, #r'===== \g<name>, \g<institution> =====',
#        'figure':        r'<\g<filename>>',
        'figure':        mwiki_figure,
        'movie':         default_movie,  # will not work for HTML movie player
        'comment':       '<!-- %s -->',
        'abstract':      r'\n*\g<type>.* \g<text>\g<rest>',
        'linebreak':     r'\g<text><br />',
        'non-breaking-space': '&nbsp;',
        'ampersand2':    r' \g<1>&\g<2>',
        }

    CODE['mwiki'] = mwiki_code
    from .html import html_table
    TABLE['mwiki'] = html_table
    ENVIRS['mwiki'] = {
        'warning':   lambda block, format, title='Warning', text_size='normal':
           mwiki_admon(block, format, title, text_size, 'warning'),
        'notice':    lambda block, format, title='Notice', text_size='normal':
           mwiki_admon(block, format, title, text_size, 'notice'),
        'question':  lambda block, format, title='Question', text_size='normal':
           mwiki_admon(block, format, title, text_size, 'question'),
        'hint':      lambda block, format, title='Hint', text_size='normal':
           mwiki_admon(block, format, title, text_size, 'hint'),
        'summary':   lambda block, format, title='Summary', text_size='normal':
           mwiki_admon(block, format, title, text_size, 'summary'),
        'block':     lambda block, format, title='Block', text_size='normal':
        mwiki_admon(block, format, title, text_size, 'block'),
        'box':       lambda block, format, title='none', text_size='normal':
           mwiki_admon(block, format, title, text_size, 'box'),
        'quote':     lambda block, format, title='none', text_size='normal':
           mwiki_admon(block, format, title, text_size, 'quote'),
        }

    # native list:
    LIST['mwiki'] = {
        'itemize':     {'begin': '\n', 'item': '*', 'end': '\n\n'},
        'enumerate':   {'begin': '\n', 'item': '#', 'end': '\n\n'},
        'description': {'begin': '\n', 'item': '* %s ', 'end': '\n\n'},
        'separator': '\n'}
    # Try this:
    LIST['mwiki'] = LIST['html']


    # how to typeset description lists for function arguments, return
    # values, and module/class variables:
    ARGLIST['mwiki'] = {
        'parameter': '*argument*',
        'keyword': '*keyword argument*',
        'return': '*return value(s)*',
        'instance variable': '*instance variable*',
        'class variable': '*class variable*',
        'module variable': '*module variable*',
        }

    FIGURE_EXT['mwiki'] = ('.png', '.gif', '.jpg', '.jpeg')
    CROSS_REFS['mwiki'] = mwiki_ref_and_label
    from .plaintext import plain_index_bib
    EXERCISE['mwiki'] = plain_exercise
    INDEX_BIB['mwiki'] = plain_index_bib
    TOC['mwiki'] = lambda s: '<<<TOC>>>'  # __TOC__ will be wrongly translated to paragraph headline and needs a fix
    QUIZ['mwiki'] = plain_quiz

    # document start:
    INTRO['mwiki'] = ''
