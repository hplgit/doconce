# http://sphinx.pocoo.org/ext/math.html#

# can reuse most of rst module:
from rst import *
from common import align2equations, online_python_tutor, \
     get_legal_pygments_lexers, has_custom_pygments_lexer
from misc import option, _abort
from doconce import errwarn

# RunestoneInteractive book counters
question_counter = 0
video_counter = 0

edit_markup_warning = False

def sphinx_figure(m):
    result = ''
    # m is a MatchObject

    filename = m.group('filename')
    caption = m.group('caption').strip()

    # Stubstitute DocOnce label by rst label in caption
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
        # or if not boldface or emphasize already in the caption
        caption_font = option('sphinx_figure_captions=', 'emphasize')
        if parts[0] and \
           caption_font == 'emphasize' and \
           not parts[0].startswith('$') and \
           not parts[0].endswith('$') and \
           not '*' in parts[0] and \
           not '_' in parts[0]:
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
        errwarn('*** warning: math only in sphinx figure caption (it will be ignored by sphinx, resulting in empty caption)\n  %s\n    FIGURE: [%s' % (caption, filename))

    #stem = os.path.splitext(filename)[0]
    #result += '\n.. figure:: ' + stem + '.*\n'  # utilize flexibility  # does not work yet
    result += '\n.. figure:: ' + filename + '\n'
    opts = m.group('options')
    if opts:
        # opts: width=600 frac=0.5 align=center
        # opts: width=600, frac=0.5, align=center
        info = [s.split('=') for s in opts.split()]
        fig_info = ['   :%s: %s' % (opt, value.replace(',', ''))
                    for opt, value in info
                    if opt not in ['frac', 'sidecap']]
        result += '\n'.join(fig_info)
    if caption:
        result += '\n\n   ' + caption + '\n'
    else:
        result += '\n\n'
    #errwarn('sphinx figure: caption=\n', caption, '\nresult:\n', result)
    return result

def sphinx_movie(m):
    filename = m.group('filename')
    special_movie = '*' in filename or '->' in filename or 'youtu.be' in filename or 'youtube.com' in filename or 'vimeo.com' in filename
    if option('runestone') and not special_movie:
        # Use RunestoneInteractive video environment
        global video_counter
        video_counter += 1
        text = """
.. video:: video_%d
   :controls:

   %s
""" % (video_counter, filename)
        return text
    else:
        # Use plain html code
        return rst_movie(m)


def sphinx_quiz_runestone(quiz):
    quiz_feedback = option('quiz_explanations=', 'on')

    text = ''
    if 'new page' in quiz:
        text += '.. !split\n%s\n%s' % (quiz['new page'], '-'*len(quiz['new page']))

    text += '.. begin quiz\n\n'
    global question_counter
    question_counter += 1
    # Multiple correct answers?
    if sum([1 for choice in quiz['choices'] if choice[0] == 'right']) > 1:
        text += '.. mchoicema:: question_%d' % question_counter + '\n'
    else:
        text += '.. mchoicemf:: question_%d' % question_counter + '\n'

    def fix_text(s, tp='answer'):
        """
        Answers and feedback in RunestoneInteractive book quizzes
        cannot contain math, figure and rst markup. Perform fixes.
        """
        drop = False
        if 'math::' in s:
            errwarn('\n*** warning: quiz %s with math block not supported:' % tp)
            errwarn(s)
            drop = True
        if '.. code-block::' in s:
            errwarn('\n*** warning: quiz %s with code block not supported:' % tp)
            errwarn(s)
            drop = True
        if '.. figure::' in s:
            errwarn('\n*** warning: quiz %s with figure not supported:' % tp)
            errwarn(s)
            drop = True
        if drop:
            return ''
        # Make multi-line paragraph a one-liner
        s = ' '.join(s.splitlines()).rstrip()
        # Fixes
        pattern = r'`(.+?) (<https?.+?)>`__'  # URL
        s = re.sub(pattern, '<a href="\g<2>"> \g<1> </a>', s)
        pattern = r'``(.+?)``'  # verbatim
        s = re.sub(pattern, '<tt>\g<1></tt>', s)
        pattern = r':math:`(.+?)`'  # inline math
        s = re.sub(pattern, '<em>\g<1></em>', s)  # mimic italic....
        pattern = r':\*(.+?)\*'  # emphasize
        s = re.sub(pattern, '\g<1>', s, flags=re.DOTALL)
        return s

    import string
    correct = []
    for i, choice in enumerate(quiz['choices']):
        if i > 4:  # not supported
            errwarn('*** warning: quiz with %d choices gets truncated (first 5)' % len(quiz['choices']))
            break
        letter = string.ascii_lowercase[i]
        text += '   :answer_%s: ' % letter
        answer = fix_text(choice[1], tp='answer')
        if not answer:
            answer = 'Too advanced typesetting prevents the text from being rendered'
        text += answer + '\n'
        if choice[0] == 'right':
            correct.append(letter)
    if correct:
        text += '   :correct: ' + ', '.join(correct) + '\n'
    else:
        errwarn('*** error: correct choice in quiz has index > 5 (max 5 allowed for RunestoneInteractive books)')
        errwarn(quiz['question'])
        _abort()
    for i, choice in enumerate(quiz['choices']):
        if i > 4:  # not supported
            break
        letter = string.ascii_lowercase[i]
        text += '   :feedback_%s: ' % letter  # must be present
        if len(choice) == 3 and quiz_feedback == 'on':
            feedback = fix_text(choice[2], tp='explanation')
            if not feedback:
                feedback = '(Too advanced typesetting prevents the text from being rendered)'
            text += feedback
        text += '\n'

    text += '\n' + indent_lines(quiz['question'], 'sphinx', ' '*3) + '\n\n\n'
    return text

def sphinx_quiz(quiz):
    if option('runestone'):
        return sphinx_quiz_runestone(quiz)
    else:
        return rst_quiz(quiz)


from latex import fix_latex_command_regex as fix_latex

def sphinx_code(filestr, code_blocks, code_block_types,
                tex_blocks, format):
    # In rst syntax, code blocks are typeset with :: (verbatim)
    # followed by intended blocks. This function indents everything
    # inside code (or TeX) blocks.

    # default mappings of !bc environments and pygments languages:
    envir2pygments = dict(
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
        #sys='console',
        sys='text',
        rst='rst',
        css='css', csspro='css', csscod='css',
        dat='text', csv='text', txt='text',
        cc='text', ccq='text',  # not possible with extra indent for ccq
        ipy='ipy',
        xmlcod='xml', xmlpro='xml', xml='xml',
        htmlcod='html', htmlpro='html', html='html',
        texcod='latex', texpro='latex', tex='latex',
        latexcod='latex', latexpro='latex', latex='latex',
        do='doconce',
        pyshell='python',
        pyoptpro='python', pyscpro='python',
        )

    # grab line with: # sphinx code-blocks: cod=python cpp=c++ etc
    # (do this before code is inserted in case verbatim blocks contain
    # such specifications for illustration)
    m = re.search(r'.. *[Ss]phinx +code-blocks?:(.+)', filestr)
    if m:
        defs_line = m.group(1)
        # turn specifications into a dictionary:
        for definition in defs_line.split():
            key, value = definition.split('=')
            envir2pygments[key] = value

    # First indent all code blocks

    for i in range(len(code_blocks)):
        if code_block_types[i].startswith('pyoptpro') and not option('runestone'):
            code_blocks[i] = online_python_tutor(code_blocks[i],
                                                 return_tp='iframe')
        if code_block_types[i].endswith('-h'):
            indentation = ' '*8
        else:
            indentation = ' '*4
        code_blocks[i] = indent_lines(code_blocks[i], format,
                                      indentation)

    # After transforming align environments to separate equations
    # the problem with math labels in multiple eqs has disappeared.
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
        #if '{alignat' in tex_blocks[i]:
        #    errwarn('*** warning: the "alignat" environment will give errors in Sphinx:\n\n' + tex_blocks[i] + '\n')

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
        errwarn("""
*** warning: detected non-align math environment with multiple labels
    (Sphinx cannot handle this equation system - labels will be removed
    and references to them will be empty):""")
        for label in multiple_math_labels_with_refs:
            errwarn('    label{%s}' % label)
        print

    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, 'sphinx')

    # Remove all !bc ipy and !bc pyshell since interactive sessions
    # are automatically handled by sphinx without indentation
    # (just a blank line before and after)
    filestr = re.sub(r'^!bc +d?ipy *\n(.*?)^!ec *\n',
                     '\n\g<1>\n', filestr, re.DOTALL|re.MULTILINE)
    filestr = re.sub(r'^!bc +d?pyshell *\n(.*?)^!ec *\n',
                     '\n\g<1>\n', filestr, re.DOTALL|re.MULTILINE)

    # Check if we have custom pygments lexers
    if 'ipy' in code_block_types:
        if not has_custom_pygments_lexer('ipy'):
            envir2pygments['ipy'] = 'python'
    if 'do' in code_block_types:
        if not has_custom_pygments_lexer('doconce'):
            envir2pygments['do'] = 'text'

    # Make correct code-block:: language constructions
    legal_pygments_languages = get_legal_pygments_lexers()
    for key in set(code_block_types):
        if key in envir2pygments:
            if not envir2pygments[key] in legal_pygments_languages:
                errwarn("""*** warning: %s is not a legal Pygments language (lexer)
found in line:
  %s

    The 'text' lexer will be used instead.
""" % (envir2pygments[key], defs_line))
                envir2pygments[key] = 'text'

        #filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
        #                 '\n.. code-block:: %s\n\n' % envir2pygments[key], filestr,
        #                 flags=re.MULTILINE)

        # Check that we have code installed to handle pyscpro
        if 'pyscpro' in filestr and key == 'pyscpro':
            try:
                import icsecontrib.sagecellserver
            except ImportError:
                errwarn("""
*** warning: pyscpro for computer code (sage cells) is requested, but'
    icsecontrib.sagecellserver from https://github.com/kriskda/sphinx-sagecell
    is not installed. Using plain Python typesetting instead.""")
                key = 'pypro'

        if key == 'pyoptpro':
            if option('runestone'):
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                    '\n.. codelens:: codelens_\n   :showoutput:\n\n',
                    filestr, flags=re.MULTILINE)
            else:
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                                 '\n.. raw:: html\n\n',
                                 filestr, flags=re.MULTILINE)
        elif key == 'pyscpro':
            if option('runestone'):
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                                 """
.. activecode:: activecode_
   :language: python

""", filestr, flags=re.MULTILINE)
            else:
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                                 '\n.. sagecellserver::\n\n',
                                 filestr, flags=re.MULTILINE)
        elif key == 'pysccod':
            if option('runestone'):
                # Include (i.e., run) all previous code segments...
                # NOTE: this is most likely not what we want
                include = ', '.join([i for i in range(1, activecode_counter)])
                filestr = re.sub(r'^!bc\s+%s\s*\n' % key,
                                 """
.. activecode:: activecode_
   :language: python
   "include: %s
""" % include, filestr, flags=re.MULTILINE)
            else:
                errwarn('*** error: pysccod for sphinx is not supported without the --runestone flag\n    (but pyscpro is via Sage Cell Server)')
                _abort()

        elif key == '':
            # any !bc with/without argument becomes a text block:
            filestr = re.sub(r'^!bc$', '\n.. code-block:: text\n\n', filestr,
                             flags=re.MULTILINE)
        elif key.endswith('hid'):
            if key in ('pyhid', 'jshid', 'htmlhid') and option('runestone'):
                # Allow runestone books to run hidden code blocks
                # (replace pyhid by pycod, then remove all !bc *hid)
                for i in range(len(code_block_types)):
                    if code_block_types[i] == key:
                        code_block_types[i] = key.replace('hid', 'cod')

                key2language = dict(py='python', js='javascript', html='html')
                language = key2language[key.replace('hid', '')]
                include = ', '.join([i for i in range(1, activecode_counter)])
                filestr = re.sub(r'^!bc +%s\s*\n' % key,
                                 """
.. activecode:: activecode_
   :language: %s
   :include: %s
   :hidecode:

""" % (language, include), filestr, flags=re.MULTILINE)
            else:
                # Remove hidden code block
                pattern = r'^!bc +%s\n.+?^!ec' % key
                filestr = re.sub(pattern, '', filestr,
                                 flags=re.MULTILINE|re.DOTALL)
        else:
            show_hide = False
            if key.endswith('-h'):
                key_orig = key
                key = key[:-2]
                show_hide = True
            # Use the standard sphinx code-block directive
            if key in envir2pygments:
                pygments_language = envir2pygments[key]
            elif key in legal_pygments_languages:
                pygments_language = key
            else:
                errwarn('*** error: detected code environment "%s"' % key)
                errwarn('    which is not registered in sphinx.py (sphinx_code)')
                errwarn('    or not a language registered in pygments')
                _abort()
            if show_hide:
                filestr = re.sub(r'^!bc +%s\s*\n' % key_orig,
                                 '\n.. container:: toggle\n\n    .. container:: header\n\n        **Show/Hide Code**\n\n    .. code-block:: %s\n\n' % \
                                 pygments_language, filestr, flags=re.MULTILINE)
                # Must add 4 indent in corresponding code_blocks[i], done above
            else:
                filestr = re.sub(r'^!bc +%s\s*\n' % key,
                                 '\n.. code-block:: %s\n\n' % \
                                 pygments_language, filestr, flags=re.MULTILINE)

    # any !bc with/without argument becomes a text block:
    filestr = re.sub(r'^!bc.*$', '\n.. code-block:: text\n\n', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'^!ec *\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '\n', filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!ec\n', '', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!bt *\n', '\n.. math::\n', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^!et *\n', '\n', filestr, flags=re.MULTILINE)

    # Insert counters for runestone blocks
    if option('runestone'):
        codelens_counter = 0
        activecode_counter = 0
        lines = filestr.splitlines()
        for i in range(len(lines)):
            if '.. codelens:: codelens_' in lines[i]:
                codelens_counter += 1
                lines[i] = lines[i].replace('codelens_', 'codelens_%d' %
                                            codelens_counter)
            if '.. activecode:: activecode_' in lines[i]:
                activecode_counter += 1
                lines[i] = lines[i].replace('activecode_', 'activecode_%d' %
                                            activecode_counter)
        filestr = '\n'.join(lines)


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

    # Remove double !split (TOC with a prefix !split gives two !splits)
    pattern = '^.. !split\s+.. !split'
    filestr = re.sub(pattern, '.. !split', filestr, flags=re.MULTILINE)

    if option('html_links_in_new_window'):
        # Insert a comment to be recognized by automake_sphinx.py such that it
        # can replace the default links by proper modified target= option.
        #filestr = '\n\n.. NOTE: Open external links in new windows.\n\n' + filestr
        # Use JavaScript instead
        filestr = """.. raw:: html

        <script type="text/javascript">
        $(document).ready(function() {
            $("a[href^='http']").attr('target','_blank');
        });
        </script>

""" + filestr


    # Remove too much vertical space
    filestr = re.sub(r'\n{3,}', '\n\n', filestr)

    return filestr

def sphinx_ref_and_label(section_label2title, format, filestr):
    # Special fix early in the process:
    # Deal with !split - by default we place splits before
    # the all the topmost sections
    # (This must be done before labels are put above section
    # headings)
    if '!split' in filestr and not option('sphinx_keep_splits'):
        errwarn('*** warning: new !split inserted (override all existing !split)')
        # Note: the title is at this stage translated to a chapter heading!
        # This title/heading must be removed for the algorithm below to work
        # (remove it, then insert afterwards)
        pattern = r'^.. Document title:\n\n={3,9}.+?={3,9}'
        m = re.search(pattern, filestr, flags=re.MULTILINE)
        title_replacement = '<<<<<<<DOCUMENT TITLE>>>>>>>>>>>>' # "unlikely" str
        if m:
            title = m.group()
            filestr = filestr.replace(title, title_replacement)
        else:
            title = ''

        topmost_section = 0
        for i in [9, 7, 5]:
            if re.search(r'^%s' % ('='*i), filestr, flags=re.MULTILINE):
                topmost_section = i
                errwarn('    before every %s heading %s' % \
                        ('='*topmost_section, '='*topmost_section))
                errwarn('    because this strategy gives a well-functioning')
                errwarn('    table of contents in Sphinx')
                errwarn('    (use --sphinx_keep_splits to enforce your own !split commands)')
                break
        if topmost_section:
            # First remove all !split
            filestr = re.sub(r'^!split *\n', '', filestr, flags=re.MULTILINE)
            # Insert new splits before all topmost sections
            pattern = r'^%s (.+?) %s' % \
                      ('='*topmost_section, '='*topmost_section)
            lines = filestr.splitlines()
            for i in range(len(lines)):
                if re.search(pattern, lines[i]):
                    lines[i] = '!split\n' + lines[i]

            filestr = '\n'.join(lines)
        filestr = filestr.replace(title_replacement, title)

    filestr = ref_and_label_commoncode(section_label2title, format, filestr)

    # replace all references to sections:
    for label in section_label2title:
        filestr = filestr.replace('ref{%s}' % label, ':ref:`%s`' % label)

    # Not of interest after sphinx got equation references:
    #from common import ref2equations
    #filestr = ref2equations(filestr)

    # Replace remaining ref{x} as :ref:`x`
    filestr = re.sub(r'ref\{(.+?)\}', ':ref:`\g<1>`', filestr)

    return filestr

def sphinx_index_bib(filestr, index, citations, pubfile, pubdata):
    filestr = rst_bib(filestr, citations, pubfile, pubdata)
    from common import INLINE_TAGS

    for word in index:
        # Drop verbatim, emphasize, bold, and math in index
        word2 = word.replace('`', '')
        word2 = word2.replace('$', '').replace('\\', '')
        word2 = re.sub(INLINE_TAGS['bold'],
                       r'\g<begin>\g<subst>\g<end>', word2,
                       flags=re.MULTILINE)
        word2 = re.sub(INLINE_TAGS['emphasize'],
                       r'\g<begin>\g<subst>\g<end>', word2,
                       flags=re.MULTILINE)

        # Typeset idx{word} as ..index::
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

def sphinx_inline_comment(m):
    # Explicit HTML typesetting does not work, we just use bold
    name = m.group('name').strip()
    comment = m.group('comment').strip()

    global edit_markup_warning
    if (not edit_markup_warning) and \
           (name[:3] in ('add', 'del', 'edi') or '->' in comment):
        errwarn('*** warning: sphinx/rst is a suboptimal format for')
        errwarn('    typesetting edit markup such as')
        errwarn('    ' + m.group())
        errwarn('    Use HTML or LaTeX output instead, implement the')
        errwarn('    edits (doconce apply_edit_comments) and then use sphinx.')
        edit_markup_warning = True

    chars = {',': 'comma', ';': 'semicolon', '.': 'period'}
    if name[:4] == 'del ':
        for char in chars:
            if comment == char:
                return r' (**edit %s**: delete %s)' % (name[4:], chars[char])
        return r'(**edit %s**: **delete** %s)' % (name[4:], comment)
    elif name[:4] == 'add ':
        for char in chars:
            if comment == char:
                return r'%s (**edit %s: add %s**)' % (comment, name[4:], chars[char])
        return r' (**edit %s: add**) %s (**end add**)' % (name[4:], comment)
    else:
        # Ordinary name
        comment = ' '.join(comment.splitlines()) # '\s->\s' -> ' -> '
        if ' -> ' in comment:
            # Replacement
            if comment.count(' -> ') != 1:
                errwarn('*** wrong syntax in inline comment:')
                errwarn(comment)
                errwarn('(more than two ->)')
                _abort()
            orig, new = comment.split(' -> ')
            return r'(**%s: remove** %s) (**insert:**)%s (**end insert**)' % (name, orig, new)
        else:
            # Ordinary comment
            return r'[**%s**: %s]' % (name, comment)

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
    FIGURE_EXT['sphinx'] = {
        'search': ('.png', '.gif', '.jpg', '.jpeg'),
        'convert': ('.png', '.gif', '.jpg')}
    CROSS_REFS['sphinx'] = sphinx_ref_and_label
    INDEX_BIB['sphinx'] = sphinx_index_bib
    TABLE['sphinx'] = TABLE['rst']
    EXERCISE['sphinx'] = EXERCISE['rst']
    ENVIRS['sphinx'] = ENVIRS['rst']
    INTRO['sphinx'] = INTRO['rst'].replace(
        '.. Automatically generated reStructuredText',
        '.. Automatically generated Sphinx-extended reStructuredText')

    # make true copy of INLINE_TAGS_SUBST:
    INLINE_TAGS_SUBST['sphinx'] = {}
    for tag in INLINE_TAGS_SUBST['rst']:
        INLINE_TAGS_SUBST['sphinx'][tag] = INLINE_TAGS_SUBST['rst'][tag]

    # modify some tags:
    #INLINE_TAGS_SUBST['sphinx']['math'] = r'\g<begin>:math:`\g<subst>`\g<end>'
    # Important to strip the math expression
    INLINE_TAGS_SUBST['sphinx']['math'] = lambda m: r'%s:math:`%s`%s' % (m.group('begin'), m.group('subst').strip(), m.group('end'))
    #INLINE_TAGS_SUBST['sphinx']['math2'] = r'\g<begin>:math:`\g<latexmath>`\g<end>'
    INLINE_TAGS_SUBST['sphinx']['math2'] = lambda m: r'%s:math:`%s`%s' % (m.group('begin'), m.group('latexmath').strip(), m.group('end'))
    INLINE_TAGS_SUBST['sphinx']['figure'] = sphinx_figure
    INLINE_TAGS_SUBST['sphinx']['movie'] = sphinx_movie
    INLINE_TAGS_SUBST['sphinx']['inlinecomment'] = sphinx_inline_comment
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
    QUIZ['sphinx'] = sphinx_quiz



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
    filestr, code_blocks, tex_blocks = remove_code_and_tex(filestr, format)
    for i in range(len(code_blocks)):
        code_blocks[i] = indent_lines(code_blocks[i], format)
    for i in range(len(tex_blocks)):
        tex_blocks[i] = indent_lines(tex_blocks[i], format)
        # remove all \label{}s inside tex blocks:
        tex_blocks[i] = re.sub(fix_latex(r'\label\{.+?\}', application='match'),
                              '', tex_blocks[i])
        # remove those without \ if there are any:
        tex_blocks[i] = re.sub(r'label\{.+?\}', '', tex_blocks[i])
        # side effects: `label{eq1}` as verbatim, but this is mostly a
        # problem for doconce documentation and can be rephrased...

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
        #if '{alignat' in tex_blocks[i]:
        #    errwarn('*** warning: the "alignat" environment will give errors in Sphinx:\n' + tex_blocks[i] + '\n')


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
        errwarn(key + ' ' + n)
        if n > 0:
            errwarn('sphinx: %d subst %s by %s' % (n, key, defs[key]))

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

    filestr, code_blocks, tex_blocks = remove_code_and_tex(filestr, format)
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
