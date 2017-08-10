from __future__ import absolute_import
from builtins import str
from builtins import range
import re, sys, shutil, os
from .common import default_movie, plain_exercise, table_analysis, \
     insert_code_and_tex, indent_lines
from .html import html_movie, html_table
from .pandoc import pandoc_ref_and_label, pandoc_index_bib, pandoc_quote, \
     language2pandoc, pandoc_quiz
from .misc import option, _abort
from .doconce import errwarn

# Global variables
figure_encountered = False
movie_encountered = False
figure_files = []
movie_files = []
html_encountered = False

def ipynb_author(authors_and_institutions, auth2index,
                 inst2index, index2inst, auth2email):
    # Old code
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
    # -----------------------------------------------------
    # New code: typeset as lines, but insert a comment so we
    # can convert back <!-- dom:AUTHOR: ... ->
    s = '\n'
    first_pass = True
    for author, i, e in authors_and_institutions:
        s+= '<!-- dom:AUTHOR: ' + author
        if e is not None:
            s += ' Email:' + e
        if i is not None:
            s += ' at ' + ' & '.join(i)
        s += ' -->\n'
        # Add extra line between heading and first author
        if first_pass:
            s+= '<!-- Author: -->  \n_%s_' % (author)
        else:
            s+= '<!-- Author: --> _%s_' % (author)
        if e is not None:
            s += ' (email: `%s`)' % e
        if i is not None:
            s += ', ' + ' and '.join(i)
        first_pass = False
        s += '  \n'
    return s

def ipynb_table(table):
    text = html_table(table)
    # Fix the problem that `verbatim` inside the table is not
    # typeset as verbatim (according to the ipynb translator rules)
    # in the GitHub Issue Tracker
    text = re.sub(r'`([^`]+?)`', '<code>\g<1></code>', text)
    return text

def ipynb_figure(m):
    # m.group() must be called before m.group('name')
    text = '<!-- dom:%s -->\n<!-- begin figure -->\n' % m.group()

    filename = m.group('filename')
    caption = m.group('caption').strip()
    opts = m.group('options').strip()
    if opts:
        info = [s.split('=') for s in opts.split()]
        opts = ' ' .join(['%s=%s' % (opt, value)
                          for opt, value in info
                          if opt not in ['frac', 'sidecap']])

    global figure_files
    if not filename.startswith('http'):
        figure_files.append(filename)

    # Extract optional label in caption
    label = None
    pattern = r' *label\{(.+?)\}'
    m = re.search(pattern, caption)
    if m:
        label = m.group(1).strip()
        caption = re.sub(pattern, '', caption)

    display_method = option('ipynb_figure=', 'imgtag')
    if display_method == 'md':
        # Markdown image syntax for embedded image in text
        # (no control of size, then one must use HTML syntax)
        if label is not None:
            #text += '<a name="%s"></a>\n' % label
            text += '<div id="%s"></div>\n' % label
        text += '![%s](%s)' % (caption, filename)
    elif display_method == 'imgtag':
        # Plain <img tag, allows specifying the image size
        if label is not None:
            #text += '<a name="%s"></a>' % label
            text += '<div id="%s"></div>\n' % label
        # Fix caption markup so it becomes html
        from .doconce import INLINE_TAGS_SUBST, INLINE_TAGS
        for tag in 'bold', 'emphasize', 'verbatim':
            caption = re.sub(INLINE_TAGS[tag], INLINE_TAGS_SUBST['html'][tag],
                             caption, flags=re.MULTILINE)
        text += """
<p>%s</p>
<img src="%s" %s>

""" % (caption, filename, opts)
    elif display_method == 'Image':
        # Image object
        # NOTE: This code will normally not work because it inserts a verbatim
        # block in the file *after* all such blocks have been removed and
        # numbered. doconce.py makes a test prior to removal of blocks and
        # runs the handle_figures and movie substitution if ipynb format
        # and Image or movie object display.
        text += '\n'
        if label is not None:
            text += '<div id="%s"></div>' % label
        text += '<!-- options: %s -->\n' % opts
        text = '!bc pycod\n'
        global figure_encountered
        if not figure_encountered:
            # First time we have a figure, we must import Image
            text += 'from IPython.display import Image\n'
            figure_encountered = True
        if caption:
            text += '# ' + caption
        if filename.startswith('http'):
            keyword = 'url'
        else:
            keyword = 'filename'
        text += 'Image(%s="%s")\n' % (keyword, filename)
        text += '!ec\n'
    else:
        errwarn('*** error: --ipynb_figure=%s is illegal, must be md, imgtag or Image' % display_method)
        _abort()
    text += '<!-- end figure -->\n'
    return text

def ipynb_movie(m):
    # m.group() must be called before m.group('name')
    text = '<!-- dom:%s -->' % m.group()

    global html_encountered, movie_encountered, movie_files
    filename = m.group('filename')
    caption = m.group('caption').strip()
    youtube = False

    if 'youtu.be' in filename or 'youtube.com' in filename:
        youtube = True
    if '*' in filename or '->' in filename:
        errwarn('*** warning: * or -> in movie filenames is not supported in ipynb')
        return text

    def YouTubeVideo(filename):
        # Use YouTubeVideo object
        if 'watch?v=' in filename:
            name = filename.split('watch?v=')[1]
        elif 'youtu.be/' in filename:
            name = filename.split('youtu.be/')[1]
        else:
            errwarn('*** error: youtube movie name "%s" could not be interpreted' % filename)
            _abort()

        text = ''
        global movie_encountered
        if not movie_encountered:
            text += 'from IPython.display import YouTubeVideo\n'
            movie_encountered = True
        text += 'YouTubeVideo("%s")\n' % name
        return text

    text += '\n<!-- begin movie -->\n'
    display_method = option('ipynb_movie=', 'HTML')
    if display_method == 'md':
        text += html_movie(m)
    elif display_method.startswith('HTML'):
        text += '\n!bc pycod\n'
        if youtube and 'YouTube' in display_method:
            text += YouTubeVideo(filename)
            if caption:
                text += '\nprint "%s"' % caption
        else:
            # Use HTML formatting
            if not html_encountered:
                text += 'from IPython.display import HTML\n'
                html_encountered = True
            text += '_s = """' + html_movie(m) + '"""\n'
            text += 'HTML(_s)\n'
            if not filename.startswith('http'):
                movie_files.append(filename)
        text += '!ec\n'
    elif display_method == 'ipynb':
        text += '!bc pycod\n'
        if youtube:
            text += YouTubeVideo(filename)
            if caption:
                text += '\nprint "%s"' % caption
        else:
            # see http://nbviewer.ipython.org/github/ipython/ipython/blob/1.x/examples/notebooks/Part%205%20-%20Rich%20Display%20System.ipynb
            # http://stackoverflow.com/questions/18019477/how-can-i-play-a-local-video-in-my-ipython-notebook
            # http://python.6.x6.nabble.com/IPython-User-embedding-non-YouTube-movies-in-the-IPython-notebook-td5024035.html
            # Just support .mp4, .ogg, and.webm
            stem, ext = os.path.splitext(filename)
            if ext not in ('.mp4', '.ogg', '.webm'):
                errwarn('*** error: movie "%s" in format %s is not supported for --ipynb_movie=%s' % (filename, ext, display_method))
                errwarn('    use --ipynb_movie=HTML instead')
                _abort()
            height = 365
            width = 640
            if filename.startswith('http'):
                file_open = 'import urllib\nvideo = urllib.urlopen("%s").read()' % filename
            else:
                file_open = 'video = open("%s", "rb").read()' % filename
            text += """
%s
from base64 import b64encode
video_encoded = b64encode(video)
video_tag = '<video controls loop alt="%s" height="%s" width="%s" src="data:video/%s;base64,{0}">'.format(video_encoded)
""" % (file_open, filename, height, width, ext[1:])
            if not filename.startswith('http'):
                movie_files.append(filename)
            if not html_encountered:
                text += 'from IPython.display import HTML\n'
                html_encountered = True
            text += 'HTML(data=video_tag)\n'
            if caption:
                text += '\nprint "%s"' % caption
        text += '!ec\n'
    else:
        errwarn('*** error: --ipynb_movie=%s is not supported' % display_method)
        _abort()
    text += '<!-- end movie -->\n'
    return text

def ipynb_code(filestr, code_blocks, code_block_types,
               tex_blocks, format):
    """
    # We expand all newcommands now
    from html import embed_newcommands
    newcommands = embed_newcommands(filestr)
    if newcommands:
        filestr = newcommands + filestr
    """
    # Fix pandoc citations to normal internal links: [[key]](#key)
    filestr = re.sub(r'\[@(.+?)\]', r'[[\g<1>]](#\g<1>)', filestr)

    # filestr becomes json list after this function so we must typeset
    # envirs here. All envirs are typeset as pandoc_quote.
    from .common import _CODE_BLOCK, _MATH_BLOCK
    envir_format = option('ipynb_admon=', 'paragraph')
    # Remove all !bpop-!epop environments (they cause only problens and
    # have no use)
    for envir in 'pop', 'slidecell':
        filestr = re.sub('^<!-- !b%s .*\n' % envir, '', filestr,
                         flags=re.MULTILINE)
        filestr = re.sub('^<!-- !e%s .*\n' % envir, '', filestr,
                         flags=re.MULTILINE)
    filestr = re.sub('^<!-- !bnotes.*?<!-- !enotes -->\n', '', filestr,
                     flags=re.DOTALL|re.MULTILINE)
    filestr = re.sub('^<!-- !split -->\n', '', filestr, flags=re.MULTILINE)
    from .doconce import doconce_envirs
    envirs = doconce_envirs()[8:-2]
    for envir in envirs:
        pattern = r'^!b%s(.*?)\n(.+?)\s*^!e%s' % (envir, envir)
        if envir_format in ('quote', 'paragraph', 'hrule'):
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
                # so native format must be used!
                if title:
                    title = '**' + title + '**\n'
                    # Could also consider subsubsection formatting
                block = m.group(2)

                # Always use quote typesetting for quotes
                if envir_format == 'quote' or envir == 'quote':
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

                if envir_format == 'hrule':
                    # Native ------ does not work, use <hr/>
                    #text = '\n\n----------\n' + title + '----------\n' + \
                    #       block + '\n----------\n\n'
                    text = '\n\n<hr/>\n' + title + \
                           block + '\n<hr/>\n\n'
                else:
                    text = title + block + '\n\n'
                return text
        else:
            errwarn('*** error: --ipynb_admon=%s is not supported'  % envir_format)
        filestr = re.sub(pattern, subst, filestr,
                         flags=re.DOTALL | re.MULTILINE)

    # Fix pyshell and ipy interactive sessions: remove prompt and output.
    # or split in multiple cells such that output comes out at the end of a cell
    # Fix sys environments and use run prog.py so programs can be run in cell
    # Insert %matplotlib inline in the first block using matplotlib
    # Only typeset Python code as blocks, otherwise !bc environmens
    # become plain indented Markdown.
    from .doconce import dofile_basename
    ipynb_tarfile = 'ipynb-%s-src.tar.gz' % dofile_basename
    src_paths = set()
    mpl_inline = False

    split_pyshell = option('ipynb_split_pyshell=', 'on')
    if split_pyshell is None:
        split_pyshell = False
    elif split_pyshell in ('no', 'False', 'off'):
        split_pyshell = False
    else:
        split_pyshell = True

    ipynb_code_tp = [None]*len(code_blocks)
    for i in range(len(code_blocks)):
        # Check if continuation lines are in the code block, because
        # doconce.py inserts a blank after the backslash
        if '\\ \n' in code_blocks[i]:
            code_blocks[i] = code_blocks[i].replace('\\ \n', '\\\n')

        if not mpl_inline and (
            re.search(r'import +matplotlib', code_blocks[i]) or \
            re.search(r'from +matplotlib', code_blocks[i]) or \
            re.search(r'import +scitools', code_blocks[i]) or \
            re.search(r'from +scitools', code_blocks[i])):
            code_blocks[i] = '%matplotlib inline\n\n' + code_blocks[i]
            mpl_inline = True

        tp = code_block_types[i]
        if tp.endswith('-t'):
            # Standard Markdown code with pandoc/github extension
            language = tp[:-2]
            language_spec = language2pandoc.get(language, '')
            #code_blocks[i] = '\n' + indent_lines(code_blocks[i], format) + '\n'
            code_blocks[i] = "```%s\n" % language_spec + \
                             indent_lines(code_blocks[i].strip(), format) + \
                             "```"
            ipynb_code_tp[i] = 'markdown'
        elif tp.startswith('pyshell') or tp.startswith('ipy'):
            lines = code_blocks[i].splitlines()
            last_cell_end = -1
            if split_pyshell:
                new_code_blocks = []
                # Split for each output an put in separate cell
                for j in range(len(lines)):
                    if lines[j].startswith('>>>') or lines[j].startswith('... '):
                        lines[j] = lines[j][4:]
                    elif lines[j].startswith('In ['):  # IPython
                        lines[j] = ':'.join(lines[j].split(':')[1:]).strip()
                    elif lines[j].startswith('   ...: '): # IPython
                        lines[j] = lines[j][8:]
                    else:
                        # output (no prefix or Out)
                        lines[j] = ''
                        new_code_blocks.append(
                            '\n'.join(lines[last_cell_end+1:j+1]))
                        last_cell_end = j
                code_blocks[i] = new_code_blocks
                ipynb_code_tp[i] = 'cell'
            else:
                # Remove prompt and output lines; leave code executable in cell
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

        elif tp.startswith('sys'):
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
                        src_paths.add(os.path.dirname(name))
                        lines[j] = '%%run "%s"' % fullpath
                else:
                    found_unix_lines = True
            src_paths = list(src_paths)
            if src_paths and not found_unix_lines:
                # This is a sys block with run commands only
                code_blocks[i] = '\n'.join(lines)
                ipynb_code_tp[i] = 'cell'
            else:
                # Standard Markdown code
                code_blocks[i] = '\n'.join(lines)
                code_blocks[i] = indent_lines(code_blocks[i], format)
                ipynb_code_tp[i] = 'markdown'
        elif tp.endswith('hid'):
            ipynb_code_tp[i] = 'cell_hidden'
        elif tp.endswith('out'):
            ipynb_code_tp[i] = 'cell_output'
        elif tp.startswith('py'):
            ipynb_code_tp[i] = 'cell'
        else:
            # Should support other languages as well, but not for now
            code_blocks[i] = indent_lines(code_blocks[i], format)
            ipynb_code_tp[i] = 'markdown'

    # figure_files and movie_files are global variables and contain
    # all figures and movies referred to
    src_paths = list(src_paths)
    if figure_files:
        src_paths += figure_files
    if movie_files:
        src_paths += movie_files

    if src_paths:
        # Make tar file with all the source dirs with files
        # that need to be executed
        os.system('tar cfz %s %s' % (ipynb_tarfile, ' '.join(src_paths)))
        errwarn('collected all required additional files in ' + ipynb_tarfile + ' which must be distributed with the notebook')
    elif os.path.isfile(ipynb_tarfile):
        os.remove(ipynb_tarfile)


    # Parse document into markdown text, code blocks, and tex blocks.
    # Store in nested list notebook_blocks.
    notebook_blocks = [[]]
    authors = ''
    for line in filestr.splitlines():
        if line.startswith('authors = [new_author(name='):  # old author method
            authors = line[10:]
        elif _CODE_BLOCK in line:
            code_block_tp = line.split()[-1]
            if code_block_tp in ('pyhid',) or not code_block_tp.endswith('hid'):
                notebook_blocks[-1] = '\n'.join(notebook_blocks[-1]).strip()
                notebook_blocks.append(line)
            # else: hidden block to be dropped (may include more languages
            # with time in the above tuple)
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
            elif ipynb_code_tp[idx] == 'cell_hidden':
                notebook_blocks[i] = ['cell_hidden', notebook_blocks[i]]
            elif ipynb_code_tp[idx] == 'cell_output':
                notebook_blocks[i] = ['cell_output', notebook_blocks[i]]
            else:
                notebook_blocks[i] = ['text', notebook_blocks[i]]
        elif re.match(pattern % _MATH_BLOCK, notebook_blocks[i]):
            notebook_blocks[i] = ['math', notebook_blocks[i]]
        else:
            notebook_blocks[i] = ['text', notebook_blocks[i]]

    # Go through tex_blocks and wrap in $$
    # (doconce.py runs align2equations so there are no align/align*
    # environments in tex blocks)
    label2tag = {}
    tag_counter = 1
    for i in range(len(tex_blocks)):
        # Extract labels and add tags
        labels = re.findall(r'label\{(.+?)\}', tex_blocks[i])
        for label in labels:
            label2tag[label] = tag_counter
            # Insert tag to get labeled equation
            tex_blocks[i] = tex_blocks[i].replace(
                'label{%s}' % label, 'label{%s} \\tag{%s}' % (label, tag_counter))
            tag_counter += 1

        # Remove \[ and \] or \begin/end{equation*} in single equations
        tex_blocks[i] = tex_blocks[i].replace(r'\[', '')
        tex_blocks[i] = tex_blocks[i].replace(r'\]', '')
        tex_blocks[i] = tex_blocks[i].replace(r'\begin{equation*}', '')
        tex_blocks[i] = tex_blocks[i].replace(r'\end{equation*}', '')
        # Check for illegal environments
        m = re.search(r'\\begin\{(.+?)\}', tex_blocks[i])
        if m:
            envir = m.group(1)
            if envir not in ('equation', 'equation*', 'align*', 'align',
                             'array'):
                errwarn("""\
*** warning: latex envir \\begin{%s} does not work well in Markdown.
    Stick to \\[ ... \\], equation, equation*, align, or align*
    environments in math environments.
""" % envir)
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

        # Add labels for the eqs above the block (for reference)
        if labels:
            #label_tp = '<a name="%s"></a>'
            label_tp = '<div id="%s"></div>'
            tex_blocks[i] = '<!-- Equation labels as ordinary links -->\n' + \
                            ' '.join([label_tp % label
                                      for label in labels]) + '\n\n' + \
                                      tex_blocks[i]

    # blocks is now a list of text chunks in markdown and math/code line
    # instructions. Insert code and tex blocks
    for i in range(len(notebook_blocks)):
        if _CODE_BLOCK in notebook_blocks[i][1] or _MATH_BLOCK in notebook_blocks[i][1]:
            words = notebook_blocks[i][1].split()
            # start of notebook_blocks[i]: number block-indicator code-type
            n = int(words[0])
            if _CODE_BLOCK in notebook_blocks[i][1]:
                notebook_blocks[i][1] = code_blocks[n]  # can be list!
            if _MATH_BLOCK in notebook_blocks[i][1]:
                notebook_blocks[i][1] = tex_blocks[n]

    # Make IPython structures

    nb_version = int(option('ipynb_version=', '4'))
    if nb_version == 3:
        try:
            from IPython.nbformat.v3 import (
                new_code_cell, new_text_cell, new_worksheet,
                new_notebook, new_metadata, new_author)
            nb = new_worksheet()
        except ImportError:
            errwarn('*** error: could not import IPython.nbformat.v3!')
            errwarn('    set --ipynb_version=4 or leave out --ipynb_version=3')
            _abort()
    elif nb_version == 4:
        try:
            from nbformat.v4 import (
                new_code_cell, new_markdown_cell, new_notebook)
        except ImportError:
            # Try old style
            try:
                from IPython.nbformat.v4 import (
                    new_code_cell, new_markdown_cell, new_notebook)
            except ImportError:
                errwarn('*** error: cannot do import nbformat.v4 or IPython.nbformat.v4')
                errwarn('    make sure IPython notebook or Jupyter is installed correctly')
                _abort()
        cells = []

    mdstr = []  # plain md format of the notebook
    prompt_number = 1
    for block_tp, block in notebook_blocks:
        if (block_tp == 'text' or block_tp == 'math') and block != '' and block != '<!--  -->':
            if nb_version == 3:
                nb.cells.append(new_text_cell(u'markdown', source=block))
            elif nb_version == 4:
                cells.append(new_markdown_cell(source=block))
            mdstr.append(('markdown', block))
        elif block_tp == 'cell' and block != '' and block != []:
            if isinstance(block, list):
                for block_ in block:
                    block_ = block_.rstrip()
                    if block_ != '':
                        if nb_version == 3:
                            nb.cells.append(new_code_cell(
                                input=block_,
                                prompt_number=prompt_number,
                                collapsed=False))
                        elif nb_version == 4:
                            cells.append(new_code_cell(
                                source=block_,
                                execution_count=prompt_number,
                                metadata=dict(collapsed=False)))
                        prompt_number += 1
                        mdstr.append(('codecell', block_))
            else:
                block = block.rstrip()
                if block != '':
                    if nb_version == 3:
                        nb.cells.append(new_code_cell(
                            input=block,
                            prompt_number=prompt_number,
                            collapsed=False))
                    elif nb_version == 4:
                        cells.append(new_code_cell(
                            source=block,
                            execution_count=prompt_number,
                            metadata=dict(collapsed=False)))
                    prompt_number += 1
                    mdstr.append(('codecell', block))
        elif block_tp == 'cell_output' and block != '':
            block = block.rstrip()
            if nb_version == 3:
                print("WARNING: Output not implemented for nbformat v3.")
            elif nb_version == 4:
                outputs = [
                    {
                        "data": {
                            "text/plain": [
                                block
                            ]
                        },
                        "execution_count": prompt_number-1,
                        "metadata": {},
                        "output_type": "execute_result"
                    }
                ]
                previous_cell = cells[-1]
                if previous_cell.cell_type == "code":
                    previous_cell.outputs = outputs
                else:
                    print("WARNING: DocOnce ipynb got code output,",
                          "but previous was not code.")
                    cells.append(new_code_cell(
                        source="#",
                        outputs=outputs,
                        execution_count=prompt_number,
                        metadata=dict(collapsed=False)
                    ))
                    mdstr.append(('codecell', block))
        elif block_tp == 'cell_hidden' and block != '':
            block = block.rstrip()
            if nb_version == 3:
                nb.cells.append(new_code_cell(
                    input=block, prompt_number=prompt_number, collapsed=True))
            elif nb_version == 4:
                cells.append(new_code_cell(
                    source=block,
                    execution_count=prompt_number,
                    metadata=dict(collapsed=True)))
            prompt_number += 1
            mdstr.append(('codecell', block))

    """
    # Dump the notebook cells in a simple ASCII format
    # (doc/src/ipynb/ipynb_generator.py can translate it back to .ipynb file)
    f = open(dofile_basename + '.md-ipynb', 'w')
    for cell_tp, block in mdstr:
        if cell_tp == 'markdown':
            f.write('\n-----\n\n')
        elif cell_tp == 'codecell':
            f.write('\n-----py\n\n')
        f.write(block)
    f.close()
    """

    if nb_version == 3:
        # Catch the title as the first heading
        m = re.search(r'^#+\s*(.+)$', filestr, flags=re.MULTILINE)
        title = m.group(1).strip() if m else ''
        # md below is not used for anything
        if authors:
            authors = eval(authors)
            md = new_metadata(name=title, authors=authors)
        else:
            md = new_metadata(name=title)
        nb = new_notebook(worksheets=[nb], metadata=new_metadata())
        # Let us make v4 notebook here by upgrading
        from IPython.nbformat.v4 import upgrade
        nb = upgrade(nb)
        import IPython.nbformat.v4.nbjson as nbjson

        # Convert nb to json format
        filestr = nbjson.writes(nb)
    elif nb_version == 4:
        nb = new_notebook(cells=cells)
        try:
            from nbformat import writes
        except ImportError:
            from IPython.nbformat import writes
        filestr = writes(nb, version=4)

    # Check that there are no empty cells:
    if '"input": []' in filestr:
        errwarn('*** error: empty cells in notebook - report bug in DocOnce')
        _abort()
    # must do the replacements here at the very end when json is written out
    # \eqref and labels will not work, but labels (only in math) do no harm
    filestr = re.sub(r'([^\\])label\{', r'\g<1>\\\\label{', filestr,
                     flags=re.MULTILINE)
    # \\eqref{} just gives (???) link at this stage - future versions
    # will probably support labels
    #filestr = re.sub(r'\(ref\{(.+?)\}\)', r'\\eqref{\g<1>}', filestr)
    # Now we use explicit references to tags
    def subst(m):
        label = m.group(1)
        try:
            return r'[(%s)](#%s)' % (label2tag[label], label)
        except KeyError as e:
            errwarn('*** error: label "%s" is not defined' % str(e))

    filestr = re.sub(r'\(ref\{(.+?)\}\)', subst, filestr)
    """
    # MathJax reference to tag (recall that the equations have both label
    # and tag (know that tag only works well in HTML, but this mjx-eqn-no
    # label does not work in ipynb)
    filestr = re.sub(r'\(ref\{(.+?)\}\)',
                     lambda m: r'[(%s)](#mjx-eqn-%s)' % (label2tag[m.group(1)], label2tag[m.group(1)]), filestr)
    """
    #filestr = re.sub(r'\(ref\{(.+?)\}\)', r'Eq (\g<1>)', filestr)

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

def ipynb_index_bib(filestr, index, citations, pubfile, pubdata):
    # ipynb has support for latex-style bibliography.
    # Quite some code here is copy from latex_index_bib
    # http://nbviewer.ipython.org/github/ipython/nbconvert-examples/blob/master/citations/Tutorial.ipynb
    if citations:
        from .common import cite_with_multiple_args2multiple_cites
        filestr = cite_with_multiple_args2multiple_cites(filestr)
    for label in citations:
        filestr = filestr.replace('cite{%s}' % label,
                                  '<cite data-cite="%s">[%d]</cite>' %
                                  (label, citations[label]))

    if pubfile is not None:
        # Always produce a new bibtex file
        bibtexfile = pubfile[:-3] + 'bib'
        errwarn('\nexporting publish database %s to %s:' % (pubfile, bibtexfile))
        publish_cmd = 'publish export %s' % os.path.basename(bibtexfile)
        # Note: we have to run publish in the directory where pubfile resides
        this_dir = os.getcwd()
        pubfile_dir = os.path.dirname(pubfile)
        if not pubfile_dir:
            pubfile_dir = os.curdir
        os.chdir(pubfile_dir)
        os.system(publish_cmd)
        os.chdir(this_dir)

        bibstyle = option('latex_bibstyle=', 'plain')
        from .latex import fix_latex_command_regex
        bibtext = fix_latex_command_regex(r"""
((*- extends 'latex_article.tplx' -*))

((* block bibliography *))
\bibliographystyle{%s}
\bibliography{%s}
((* endblock bibliography *))
""" % (bibstyle, bibtexfile[:-4]), application='replacement')
        filestr = re.sub(r'^BIBFILE:.+$', bibtext, filestr,
                         flags=re.MULTILINE)

    # Save idx{} and label{} as metadata, also have labels as div tags
    filestr = re.sub(r'((idx\{.+?\})', r'<!-- dom:\g<1> -->', filestr)
    filestr = re.sub(r'(label\{(.+?)\})', r'<!-- dom:\g<1> --><div id="\g<2>"></div>', filestr)
    # Also treat special cell delimiter comments that might appear from
    # doconce ipynb2doconce conversions
    filestr = re.sub(r'^# ---------- (markdown|code) cell$', '',
                     filestr, flags=re.MULTILINE)
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
        'movie':     ipynb_movie,
        'verbatim':  None,
        #'linkURL':   r'\g<begin>\g<link> (\g<url>)\g<end>',
        'linkURL2':  r'[\g<link>](\g<url>)',
        'linkURL3':  r'[\g<link>](\g<url>)',
        'linkURL2v': r'[`\g<link>`](\g<url>)',
        'linkURL3v': r'[`\g<link>`](\g<url>)',
        'plainURL':  r'<\g<url>>',
        'colortext': r'<font color="\g<color>">\g<text></font>',
        'title':     r'<!-- dom:TITLE: \g<subst> -->\n# \g<subst>',
        'author':    ipynb_author,
        'date':      '\nDate: _\g<subst>_\n',
        'chapter':       lambda m: '# '   + m.group('subst'),  # seldom used in notebooks
        'section':       lambda m: '# '   + m.group('subst'),
        'subsection':    lambda m: '## '  + m.group('subst'),
        'subsubsection': lambda m: '### ' + m.group('subst') + '\n',
        'paragraph':     r'**\g<subst>**\g<space>',
        'abstract':      r'\n**\g<type>.** \g<text>\n\n\g<rest>',
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

    from .common import DEFAULT_ARGLIST
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

    TABLE['ipynb'] = ipynb_table
    cite = option('ipynb_cite=', 'plain')
    if cite == 'latex':
        INDEX_BIB['ipynb'] = ipynb_index_bib
    else:
        INDEX_BIB['ipynb'] = pandoc_index_bib
    EXERCISE['ipynb'] = plain_exercise
    TOC['ipynb'] = lambda s, f: ''
    FIGURE_EXT['ipynb'] = {
        'search': ('.png', '.gif', '.jpg', '.jpeg', '.tif', '.tiff'),
        'convert': ('.png', '.gif', '.jpg')}
    QUIZ['ipynb'] = pandoc_quiz
