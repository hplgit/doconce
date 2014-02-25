# http://sphinx.pocoo.org/ext/math.html#

# can reuse most of rst module:
from rst import *
from common import align2equations, online_python_tutor, bibliography
from misc import option

legal_pygments_languages = [
    'Cucumber', 'cucumber', 'Gherkin', 'gherkin',
    'abap', 'ada', 'ada95ada2005',
    'antlr-as', 'antlr-actionscript', 'antlr-cpp', 'antlr-csharp',
    'antlr-c#', 'antlr-java', 'antlr-objc', 'antlr-perl',
    'antlr-python', 'antlr-ruby', 'antlr-rb', 'antlr',
    'apacheconf', 'aconf', 'apache', 'applescript', 'as',
    'actionscript', 'as3', 'actionscript3', 'aspx-cs', 'aspx-vb',
    'asy', 'asymptote', 'basemake', 'bash', 'sh', 'ksh', 'bat',
    'bbcode', 'befunge', 'boo', 'brainfuck', 'bf', 'c-objdump',
    'c', 'cfm', 'cfs', 'cheetah', 'spitfire', 'clojure', 'clj',
    'cmake', 'coffee-script', 'coffeescript', 'common-lisp',
    'cl', 'console', 'control',
    'cpp', 'c++', 'cpp-objdump', 'c++-objdumb', 'cxx-objdump',
    'csharp', 'c#',
    'css+django', 'css+jinja', 'css+erb', 'css+ruby',
    'css+genshitext', 'css+genshi', 'css+mako', 'css+myghty',
    'css+php', 'css+smarty', 'css',
    'cython', 'pyx', 'd-objdump', 'd', 'delphi', 'pas',
    'pascal', 'objectpascal', 'diff', 'udiff',
    'django', 'jinja', 'dpatch', 'dylan', 'erb',
    'erl', 'erlang', 'evoque', 'felix', 'flx',
    'fortran', 'gas', 'genshi', 'kid',
    'xml+genshi', 'xml+kid', 'genshitext', 'glsl',
    'gnuplot', 'go', 'groff', 'nroff', 'man', 'haml',
    'HAML', 'haskell', 'hs',
    'html+cheetah', 'html+spitfire', 'html+django', 'html+jinja',
    'html+evoque', 'html+genshi', 'html+kid', 'html+mako',
    'html+myghty', 'html+php', 'html+smarty', 'html',
    'hx', 'haXe', 'ini', 'cfg', 'io', 'irc',
    'java', 'js+cheetah', 'javascript+cheetah', 'js+spitfire',
    'javascript+spitfire', 'js+django', 'javascript+django',
    'js+jinja', 'javascript+jinja', 'js+erb', 'javascript+erb',
    'js+ruby', 'javascript+ruby', 'js+genshitext', 'js+genshi',
    'javascript+genshitext', 'javascript+genshi', 'js+mako',
    'javascript+mako', 'js+myghty', 'javascript+myghty',
    'js+php', 'javascript+php', 'js+smarty', 'javascript+smarty',
    'js', 'javascript', 'jsp',
    'lhs', 'literate-haskell', 'lighty', 'lighttpd', 'llvm',
    'logtalk', 'lua', 'make', 'makefile', 'mf', 'bsdmake',
    'mako', 'matlab', 'octave', 'matlabsession', 'minid',
    'modelica', 'modula2', 'm2', 'moocode', 'mupad', 'mxml',
    'myghty', 'mysql', 'nasm', 'newspeak', 'nginx', 'numpy',
    'objdump', 'objective-c', 'objectivec', 'obj-c', 'objc',
    'objective-j', 'objectivej', 'obj-j', 'objj', 'ocaml',
    'ooc', 'perl', 'pl', 'php', 'php3', 'php4', 'php5',
    'pot', 'po', 'pov', 'prolog', 'py3tb', 'pycon', 'pytb',
    'python', 'py', 'python3', 'py3', 'ragel-c', 'ragel-cpp',
    'ragel-d', 'ragel-em', 'ragel-java', 'ragel-objc',
    'ragel-ruby', 'ragel-rb', 'ragel', 'raw', 'rb', 'ruby',
    'rbcon', 'irb', 'rconsole', 'rout', 'rebol', 'redcode',
    'rhtml', 'html+erb', 'html+ruby', 'rst', 'rest',
    'restructuredtext', 'sass', 'SASS', 'scala', 'scheme',
    'scm', 'smalltalk', 'squeak', 'smarty', 'sourceslist',
    'sources.list', 'splus', 's', 'r', 'sql', 'sqlite3',
    'squidconf', 'squid.conf', 'squid', 'tcl', 'tcsh',
    'csh', 'tex', 'latex', 'text', 'trac-wiki', 'moin',
    'vala', 'vapi', 'vb.net', 'vbnet', 'vim',
    'xml+cheetah', 'xml+spitfire', 'xml+django', 'xml+jinja',
    'xml+erb', 'xml+ruby', 'xml+evoque', 'xml+mako',
    'xml+myghty', 'xml+php', 'xml+smarty', 'xml', 'xslt', 'yaml']


def sphinx_figure(m):
    result = ''
    # m is a MatchObject

    filename = m.group('filename')
    caption = m.group('caption').strip()

    # Stubstitute Doconce label by rst label in caption
    # (also, remove final period in caption since caption is used as hyperlink
    # text to figures).

    m_label = re.search(r'label\{(.+?)\}', caption)
    if m_label:
        label = m_label.group(1)
        result += '\n.. _%s:\n' % label
        # remove . at the end of the caption text
        parts = caption.split('label')
        parts[0] = parts[0].rstrip()
        if parts[0] and parts[0][-1] == '.':
            parts[0] = parts[0][:-1]
        parts[0] = parts[0].strip()
        # insert emphasize marks if not latex $ at the
        # beginning or end (math subst does not work for *$I=1$*)
        if parts[0] and not parts[0].startswith('$') and \
           not parts[0].endswith('$'):
            parts[0] = '*' + parts[0] + '*'
        #caption = '  label'.join(parts)
        caption = parts[0]
        # contrary to rst_figure, we do not write label into caption
        # since we just want to remove the whole label as part of
        # the caption (otherwise done when handling ref and label)

    else:
        if caption and caption[-1] == '.':
            caption = caption[:-1]

    # math is ignored in references to figures, test for math only
    if caption.startswith('$') and caption.endswith('$'):
        print '*** warning: math only in sphinx figure caption\n  %s\n    FIGURE: [%s' % (caption, filename)

    #stem = os.path.splitext(filename)[0]
    #result += '\n.. figure:: ' + stem + '.*\n'  # utilize flexibility  # does not work yet
    result += '\n.. figure:: ' + filename + '\n'
    opts = m.group('options')
    if opts:
        # opts: width=600 frac=0.5 align=center
        # opts: width=600, frac=0.5, align=center
        info = [s.split('=') for s in opts.split()]
        fig_info = ['   :%s: %s' % (option, value.replace(',', ''))
                    for option, value in info if option not in ['frac']]
        result += '\n'.join(fig_info)
    if caption:
        result += '\n\n   ' + caption + '\n'
    else:
        result += '\n\n'
    #print 'sphinx figure: caption=\n', caption, '\nresult:\n', result
    return result

from latex import fix_latex_command_regex as fix_latex

def sphinx_code(filestr, code_blocks, code_block_types,
                tex_blocks, format):
    # In rst syntax, code blocks are typeset with :: (verbatim)
    # followed by intended blocks. This function indents everything
    # inside code (or TeX) blocks.

    # default mappings of !bc environments and pygments languages:
    envir2lang = dict(
        cod='python', pro='python',
        pycod='python', cycod='cython',
        pypro='python', cypro='cython',
        fcod='fortran', fpro='fortran',
        ccod='c', cppcod='c++',
        cpro='c', cpppro='c++',
        mcod='matlab', mpro='matlab',
        plcod='perl', plpro='perl',
        shcod='bash', shpro='bash',
        rbcod='ruby', rbpro='ruby',
        sys='console',
        rst='rst',
        dat='text', csv='text', txt='text',
        cc='text', ccq='text',  # not possible with extra indent for ccq
        ipy='python',
        xmlcod='xml', xmlpro='xml', xml='xml',
        htmlcod='html', htmlpro='html', html='html',
        texcod='latex', texpro='latex', tex='latex',
        pyoptpro='python', pyscpro='python',
        )

    # grab line with: # Sphinx code-blocks: cod=python cpp=c++ etc
    # (do this before code is inserted in case verbatim blocks contain
    # such specifications for illustration)
    m = re.search(r'.. *[Ss]phinx +code-blocks?:(.+)', filestr)
    if m:
        defs_line = m.group(1)
        # turn specifications into a dictionary:
        for definition in defs_line.split():
            key, value = definition.split('=')
            envir2lang[key] = value

    # First indent all code blocks

    for i in range(len(code_blocks)):
        if code_block_types[i].startswith('pyoptpro'):
            code_blocks[i] = online_python_tutor(code_blocks[i],
                                                 return_tp='iframe')
        code_blocks[i] = indent_lines(code_blocks[i], format)

    # Treat math labels. Drop labels in environments with multiple
    # equations since these do not work in Sphinx. Method: keep
    # label if there is one and only one. Otherwise use old
    # method of removing labels. Do not use :nowrap: since this will
    # generate other labels that we cannot refer to.
    #
    # After transforming align environments to separate equations
    # the problem with multiple math labels has disappeared.
    # (doconce.py applies align2equations, which takes all align
    # envirs and translates them to separate equations, but align*
    # environments are allowed.
    # Any output of labels in align means an error in the
    # align -> equation transformation...)
    math_labels = []
    multiple_math_labels = []  # sphinx has problems with multiple math labels
    for i in range(len(tex_blocks)):
        tex_blocks[i] = indent_lines(tex_blocks[i], format)
        # extract all \label{}s inside tex blocks and typeset them
        # with :label: tags
        label_regex = fix_latex( r'label\{(.+?)\}', application='match')
        labels = re.findall(label_regex, tex_blocks[i])
        if len(labels) == 1:
            tex_blocks[i] = '   :label: %s\n' % labels[0] + tex_blocks[i]
        elif len(labels) > 1:
            multiple_math_labels.append(labels)
        if len(labels) > 0:
            math_labels.extend(labels)
        tex_blocks[i] = re.sub(label_regex, '', tex_blocks[i])

        # fix latex constructions that do not work with sphinx math
        commands = [r'\begin{equation}',
                    r'\end{equation}',
                    r'\begin{equation*}',
                    r'\end{equation*}',
                    r'\begin{eqnarray}',
                    r'\end{eqnarray}',
                    r'\begin{eqnarray*}',
                    r'\end{eqnarray*}',
                    r'\begin{align}',
                    r'\end{align}',
                    r'\begin{align*}',
                    r'\end{align*}',
                    r'\begin{multline}',
                    r'\end{multline}',
                    r'\begin{multline*}',
                    r'\end{multline*}',
                    r'\begin{split}',
                    r'\end{split}',
                    r'\begin{gather}',
                    r'\end{gather}',
                    r'\begin{gather*}',
                    r'\end{gather*}',
                    r'\[',
                    r'\]',
                    # some common abbreviations (newcommands):
                    r'\beqan',
                    r'\eeqan',
                    r'\beqa',
                    r'\eeqa',
                    r'\balnn',
                    r'\ealnn',
                    r'\baln',
                    r'\ealn',
                    r'\beq',
                    r'\eeq',  # the simplest, contained in others, must come last!
                    ]
        for command in commands:
            tex_blocks[i] = tex_blocks[i].replace(command, '')
        tex_blocks[i] = re.sub('&\s*=\s*&', ' &= ', tex_blocks[i])
        # provide warnings for problematic environments
        if '{alignat' in tex_blocks[i]:
            print '*** warning: the "alignat" environment will give errors in Sphinx:\n\n', tex_blocks[i], '\n'

    # Replace all references to equations that have labels in math environments:
    for label in math_labels:
        filestr = filestr.replace('(:ref:`%s`)' % label, ':eq:`%s`' % label)

    multiple_math_labels_with_refs = [] # collect the labels with references
    for labels in multiple_math_labels:
        for label in labels:
            ref = ':eq:`%s`' % label  # ref{} is translated to eq:``
            if ref in filestr:
                multiple_math_labels_with_refs.append(label)

    if multiple_math_labels_with_refs:
        print """
*** warning: detected non-align math environment with multiple labels
    (Sphinx cannot handle this equation system - labels will be removed
    and references to them will be empty):"""
        for label in multiple_math_labels_with_refs:
            print '    label{%s}' % label
        print

    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, 'rst')

    # Remove all !bc ipy and !bc pyshell since interactive sessions
    # are automatically handled by sphinx without indentation
    # (just a blank line before and after)
    filestr = re.sub(r'^!bc +ipy *\n(.*?)^!ec *\n',
                     '\n\g<1>\n', filestr, re.DOTALL|re.MULTILINE)
    filestr = re.sub(r'^!bc +pyshell *\n(.*?)^!ec *\n',
                     '\n\g<1>\n', filestr, re.DOTALL|re.MULTILINE)

    # Make correct code-block:: language constructions
    for key in envir2lang:
        language = envir2lang[key]
        if not language in legal_pygments_languages:
            raise TypeError('%s is not a legal Pygments language '\
                            '(lexer) in line with:\n  %s' % \
                                (language, defs_line))
        #filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
        #                 '\n.. code-block:: %s\n\n' % envir2lang[key], filestr,
        #                 flags=re.MULTILINE)
        # Check that we have code installed to handle pyscpro
        if key == 'pyscpro':
            try:
                import icsecontrib.sagecellserver
            except ImportError:
                print """
*** warning: pyscpro for computer code (sage cells) is requested, but'
    icsecontrib.sagecellserver from https://github.com/kriskda/sphinx-sagecell
    is not installed. Using plain Python typesetting instead."""
                key = 'pypro'

        if key == 'pyoptpro':
            filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                             '\n.. raw:: html\n\n',
                             filestr, flags=re.MULTILINE)
        elif key == 'pyscpro':
            filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                             '\n.. sagecellserver::\n\n',
                             filestr, flags=re.MULTILINE)
        else:
            filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                             '\n.. code-block:: %s\n\n' % \
                             envir2lang[key], filestr, flags=re.MULTILINE)

    # any !bc with/without argument becomes a text block:
    #filestr = re.sub(r'^!bc.+\n', '\n.. code-block:: text\n\n', filestr,
    #                 flags=re.MULTILINE)
    filestr = re.sub(r'^!bc.*$', '\n.. code-block:: text\n\n', filestr,
                     flags=re.MULTILINE)

    filestr = re.sub(r'^!ec *\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!bt *\n', '\n.. math::\n', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!et *\n', '\n', filestr, flags=re.MULTILINE)

    # Final fixes

    filestr = fix_underlines_in_headings(filestr)
    # Ensure blank line before and after comments
    filestr = re.sub(r'([.:;?!])\n^\.\. ', r'\g<1>\n\n.. ',
                     filestr, flags=re.MULTILINE)
    filestr = re.sub(r'(^\.\. .+)\n([^ \n]+)', r'\g<1>\n\n\g<2>',
                     filestr, flags=re.MULTILINE)
    # Line breaks interfer with tables and needs a final blank line too
    lines = filestr.splitlines()
    inside_block = False
    for i in range(len(lines)):
        if lines[i].startswith('<linebreakpipe>') and not inside_block:
            inside_block = True
            lines[i] = lines[i].replace('<linebreakpipe> ', '') + '\n'
            continue
        if lines[i].startswith('<linebreakpipe>') and inside_block:
            lines[i] = '|' + lines[i].replace('<linebreakpipe>', '')
            continue
        if inside_block and not lines[i].startswith('<linebreakpipe>'):
            inside_block = False
            lines[i] = '| ' + lines[i] + '\n'
    filestr = '\n'.join(lines)

    if option('html_links_in_new_window'):
        filestr = '\n\n.. Open external links in new windows.\n\n' + filestr

    return filestr

def sphinx_ref_and_label(section_label2title, format, filestr):
    filestr = ref_and_label_commoncode(section_label2title, format, filestr)

    # replace all references to sections:
    for label in section_label2title:
        filestr = filestr.replace('ref{%s}' % label, ':ref:`%s`' % label)

    # not of interest after sphinx got equation references:
    #from common import ref2equations
    #filestr = ref2equations(filestr)

    # replace remaining ref{x} as :ref:`x`
    filestr = re.sub(r'ref\{(.+?)\}', ':ref:`\g<1>`', filestr)

    return filestr

def sphinx_index_bib(filestr, index, citations, pubfile, pubdata):
    filestr = rst_bib(filestr, citations, pubfile, pubdata)

    for word in index:
        # Drop verbatim and math in index
        word2 = word.replace('`', '')
        word2 = word2.replace('$', '').replace('\\', '')
        if '!' not in word and ',' not in word:
            # .. index:: keyword
            filestr = filestr.replace(
                'idx{%s}' % word,
                '\n.. index:: ' + word2 + '\n')
        elif '!' not in word:
            # .. index::
            #    single: keyword with comma
            filestr = filestr.replace(
                'idx{%s}' % word,
                '\n.. index::\n   single: ' + word2 + '\n')
        else:
            # .. index::
            #    single: keyword; subentry
            word3 = word2.replace('!', '; ')
            filestr = filestr.replace(
                'idx{%s}' % word,
                '\n.. index::\n   single: ' + word3 + '\n')

            # Symmetric keyword; subentry and subentry; keyword
            #filestr = filestr.replace(
            #    'idx{%s}' % word,
            #    '\n.. index::\n   pair: ' + word3 + '\n')
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
           INTRO,
           OUTRO,
           filestr):
    if not 'rst' in BLANKLINE:
        # rst.define is not yet ran on these dictionaries, do it:
        import rst
        rst.define(FILENAME_EXTENSION,
                   BLANKLINE,
                   INLINE_TAGS_SUBST,
                   CODE,
                   LIST,
                   ARGLIST,
                   TABLE,
                   FIGURE_EXT,
                   INTRO,
                   OUTRO,
                   filestr)

    FILENAME_EXTENSION['sphinx'] = FILENAME_EXTENSION['rst']
    BLANKLINE['sphinx'] = BLANKLINE['rst']
    CODE['sphinx'] = CODE['rst']
    LIST['sphinx'] = LIST['rst']
    FIGURE_EXT['sphinx'] = ('.png', '.gif', '.jpg', '.jpeg')
    CROSS_REFS['sphinx'] = sphinx_ref_and_label
    INDEX_BIB['sphinx'] = sphinx_index_bib
    TABLE['sphinx'] = TABLE['rst']
    EXERCISE['sphinx'] = EXERCISE['rst']
    INTRO['sphinx'] = INTRO['rst']
    ENVIRS['sphinx'] = ENVIRS['rst']

    # make true copy of INLINE_TAGS_SUBST:
    INLINE_TAGS_SUBST['sphinx'] = {}
    for tag in INLINE_TAGS_SUBST['rst']:
        INLINE_TAGS_SUBST['sphinx'][tag] = INLINE_TAGS_SUBST['rst'][tag]

    # modify some tags:
    INLINE_TAGS_SUBST['sphinx']['math'] = r'\g<begin>:math:`\g<subst>`\g<end>'
    INLINE_TAGS_SUBST['sphinx']['math2'] = r'\g<begin>:math:`\g<latexmath>`\g<end>'
    INLINE_TAGS_SUBST['sphinx']['figure'] = sphinx_figure
    CODE['sphinx'] = sphinx_code  # function for typesetting code

    ARGLIST['sphinx'] = {
        'parameter': ':param',
        'keyword': ':keyword',
        'return': ':return',
        'instance variable': ':ivar',
        'class variable': ':cvar',
        'module variable': ':var',
        }

    TOC['sphinx'] = lambda s: ''  # Sphinx automatically generates a toc


#---------------------------------------------------------------------------
def sphinx_code_orig(filestr, format):
    # NOTE: THIS FUNCTION IS NOT USED!!!!!!

    # In rst syntax, code blocks are typeset with :: (verbatim)
    # followed by intended blocks. This function indents everything
    # inside code (or TeX) blocks.

    # grab #sphinx code-blocks: cod=python cpp=c++ etc line
    # (do this before code is inserted in case verbatim blocks contain
    # such specifications for illustration)
    m = re.search(r'#\s*[Ss]phinx\s+code-blocks?:(.+?)\n', filestr)
    if m:
        defs_line = m.group(1)
        # turn defs into a dictionary definition:
        defs = {}
        for definition in defs_line.split():
            key, value = definition.split('=')
            defs[key] = value
    else:
        # default mappings:
        defs = dict(cod='python',
                    pro='python',
                    pycod='python', cycod='cython',
                    pypro='python', cypro='cython',
                    fcod='fortran', fpro='fortran',
                    ccod='c', cppcod='c++',
                    cpro='c', cpppro='c++',
                    mcod='matlab', mpro='matlab',
                    plcod='perl', plpro='perl',
                    shcod='bash', shpro='bash',
                    rbcod='ruby', rbpro='ruby',
                    sys='console',
                    dat='python',
                    ipy='python',
                    xmlcod='xml', xmlpro='xml', xml='xml',
                    htmlcod='html', htmlpro='html', html='html',
                    texcod='latex', texpro='latex', tex='latex',
                    )
        # (the "python" typesetting is neutral if the text
        # does not parse as python)

    # first indent all code/tex blocks by 1) extracting all blocks,
    # 2) intending each block, and 3) inserting the blocks:
    filestr, code_blocks, tex_blocks = remove_code_and_tex(filestr)
    for i in range(len(code_blocks)):
        code_blocks[i] = indent_lines(code_blocks[i], format)
    for i in range(len(tex_blocks)):
        tex_blocks[i] = indent_lines(tex_blocks[i], format)
        # remove all \label{}s inside tex blocks:
        tex_blocks[i] = re.sub(fix_latex(r'\label\{.+?\}', application='match'),
                              '', tex_blocks[i])
        # remove those without \ if there are any:
        tex_blocks[i] = re.sub(r'label\{.+?\}', '', tex_blocks[i])

        # fix latex constructions that do not work with sphinx math
        commands = [r'\begin{equation}',
                    r'\end{equation}',
                    r'\begin{equation*}',
                    r'\end{equation*}',
                    r'\begin{eqnarray}',
                    r'\end{eqnarray}',
                    r'\begin{eqnarray*}',
                    r'\end{eqnarray*}',
                    r'\begin{align}',
                    r'\end{align}',
                    r'\begin{align*}',
                    r'\end{align*}',
                    r'\begin{multline}',
                    r'\end{multline}',
                    r'\begin{multline*}',
                    r'\end{multline*}',
                    r'\begin{split}',
                    r'\end{split}',
                    r'\begin{gather}',
                    r'\end{gather}',
                    r'\begin{gather*}',
                    r'\end{gather*}',
                    r'\[',
                    r'\]',
                    # some common abbreviations (newcommands):
                    r'\beqan',
                    r'\eeqan',
                    r'\beqa',
                    r'\eeqa',
                    r'\balnn',
                    r'\ealnn',
                    r'\baln',
                    r'\ealn',
                    r'\beq',
                    r'\eeq',  # the simplest, contained in others, must come last!
                    ]
        for command in commands:
            tex_blocks[i] = tex_blocks[i].replace(command, '')
        tex_blocks[i] = re.sub('&\s*=\s*&', ' &= ', tex_blocks[i])
        # provide warnings for problematic environments
        if '{alignat' in tex_blocks[i]:
            print '*** warning: the "alignat" environment will give errors in Sphinx:\n', tex_blocks[i], '\n'


    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, 'rst')

    for key in defs:
        language = defs[key]
        if not language in legal_pygments_languages:
            raise TypeError('%s is not a legal Pygments language '\
                            '(lexer) in line with:\n  %s' % \
                                (language, defs_line))
        #filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
        #                 '\n.. code-block:: %s\n\n' % defs[key], filestr,
        #                 flags=re.MULTILINE)
        cpattern = re.compile(r'^!bc\s+%s\s*\n' % key, flags=re.MULTILINE)
        filestr, n = cpattern.subn('\n.. code-block:: %s\n\n' % defs[key], filestr)
        print key, n
        if n > 0:
            print 'sphinx: %d subst %s by %s' % (n, key, defs[key])

    # any !bc with/without argument becomes a py (python) block:
    #filestr = re.sub(r'^!bc.+\n', '\n.. code-block:: py\n\n', filestr,
    #                 flags=re.MULTILINE)
    cpattern = re.compile(r'^!bc.+$', flags=re.MULTILINE)
    filestr = cpattern.sub('\n.. code-block:: py\n\n', filestr)

    filestr = re.sub(r'^!ec *\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!bt *\n', '\n.. math::\n\n', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'^!et *\n', '\n\n', filestr,
                     flags=re.MULTILINE)

    return filestr

def sphinx_code_newmathlabels(filestr, format):
    # NOTE: THIS FUNCTION IS NOT USED!!!!!!

    # In rst syntax, code blocks are typeset with :: (verbatim)
    # followed by intended blocks. This function indents everything
    # inside code (or TeX) blocks.

    # grab #sphinx code-blocks: cod=python cpp=c++ etc line
    # (do this before code is inserted in case verbatim blocks contain
    # such specifications for illustration)
    m = re.search(r'#\s*[Ss]phinx\s+code-blocks?:(.+?)\n', filestr)
    if m:
        defs_line = m.group(1)
        # turn defs into a dictionary definition:
        defs = {}
        for definition in defs_line.split():
            key, value = definition.split('=')
            defs[key] = value
    else:
        # default mappings:
        defs = dict(cod='python', pycod='python', cppcod='c++',
                    fcod='fortran', ccod='c',
                    pro='python', pypro='python', cpppro='c++',
                    fpro='fortran', cpro='c',
                    sys='console', dat='python')
        # (the "python" typesetting is neutral if the text
        # does not parse as python)

    # First indent all code/tex blocks by 1) extracting all blocks,
    # 2) intending each block, and 3) inserting the blocks.
    # In between, handle the math blocks.

    filestr, code_blocks, tex_blocks = remove_code_and_tex(filestr)
    for i in range(len(code_blocks)):
        code_blocks[i] = indent_lines(code_blocks[i], format)

    math_labels = []
    for i in range(len(tex_blocks)):
        tex_blocks[i] = indent_lines(tex_blocks[i], format)
        # extract all \label{}s inside tex blocks and typeset them
        # with :label: tags
        label_regex1 = fix_latex(r'\label\{(.+?)\}', application='match')
        label_regex2 = fix_latex( r'label\{(.+?)\}', application='match')
        math_labels.extend(re.findall(label_regex1, tex_blocks[i]))
        tex_blocks[i] = re.sub(label_regex1,
                              r' :label: \g<1> ', tex_blocks[i])
        # handle also those without \ if there are any:
        math_labels.extend(re.findall(label_regex2, tex_blocks[i]))
        tex_blocks[i] = re.sub(label_regex2, r' :label: \g<1> ', tex_blocks[i])

    # replace all references to equations:
    for label in math_labels:
        filestr = filestr.replace(':ref:`%s`' % label, ':eq:`%s`' % label)

    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, 'rst')

    for key in defs:
        language = defs[key]
        if not language in legal_pygments_languages:
            raise TypeError('%s is not a legal Pygments language '\
                            '(lexer) in line with:\n  %s' % \
                                (language, defs_line))
        #filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
        #                 '\n.. code-block:: %s\n\n' % defs[key], filestr,
        #                 flags=re.MULTILINE)
        cpattern = re.compile(r'^!bc\s+%s\s*\n' % key, flags=re.MULTILINE)
        filestr = cpattern.sub('\n.. code-block:: %s\n\n' % defs[key], filestr)

    # any !bc with/without argument becomes a py (python) block:
    #filestr = re.sub(r'^!bc.+\n', '\n.. code-block:: py\n\n', filestr,
    #                 flags=re.MULTILINE)
    cpattern = re.compile(r'^!bc.+$', flags=re.MULTILINE)
    filestr = cpattern.sub('\n.. code-block:: py\n\n', filestr)

    filestr = re.sub(r'!ec *\n', '\n', filestr)
    #filestr = re.sub(r'!ec\n', '\n', filestr)
    #filestr = re.sub(r'!ec\n', '', filestr)
    filestr = re.sub(r'!bt *\n', '\n.. math::\n   :nowrap:\n\n', filestr)
    filestr = re.sub(r'!et *\n', '\n\n', filestr)

    return filestr


