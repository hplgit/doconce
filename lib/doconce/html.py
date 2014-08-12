import re, os, glob, sys, glob
from common import table_analysis, plain_exercise, insert_code_and_tex, \
     indent_lines, online_python_tutor, bibliography, \
     cite_with_multiple_args2multiple_cites, _abort, is_file_or_url, \
     get_legal_pygments_lexers, has_custom_pygments_lexer
from misc import option

# fold/unfold: use !bblock Title unfold
# to indicate and use bootstrap choice unfolding for quiz as technique
# Can with bootstrap typeset all answers and solutions in exercises
# using folding

box_shadow = 'box-shadow: 8px 8px 5px #888888;'
#box_shadow = 'box-shadow: 0px 0px 10px #888888'

global _file_collection_filename

# From http://service.real.com/help/library/guides/realone/ProductionGuide/HTML/htmfiles/colors.htm:
color_table = [
('white', '#FFFFFF', 'rgb(255,255,255)'),
('silver', '#C0C0C0', 'rgb(192,192,192)'),
('gray', '#808080', 'rgb(128,128,128)'),
('black', '#000000', 'rgb(0,0,0)'),
('yellow', '#FFFF00', 'rgb(255,255,0)'),
('fuchsia', '#FF00FF', 'rgb(255,0,255)'),
('red', '#FF0000', 'rgb(255,0,0)'),
('maroon', '#800000', 'rgb(128,0,0)'),
('lime', '#00FF00', 'rgb(0,255,0)'),
('olive', '#808000', 'rgb(128,128,0)'),
('green', '#008000', 'rgb(0,128,0)'),
('purple', '#800080', 'rgb(128,0,128)'),
('aqua', '#00FFFF', 'rgb(0,255,255)'),
('teal', '#008080', 'rgb(0,128,128)'),
('blue', '#0000FF', 'rgb(0,0,255)'),
('navy', '#000080', 'rgb(0,0,128)'),]



def add_to_file_collection(filename, doconce_docname=None, mode='a'):
    """
    Add filename to the collection of needed files for a Doconce-based
    HTML document to work.

    The first time the function is called, `doconce_docname` != None
    and this name is used to set the filename of the file collection.
    Later, `doconce_docname` is not given (otherwise previous info is erased).
    """
    if isinstance(filename, (str,unicode)):
        filenames = [filename]
    elif isinstance(filename, (list,tuple)):
        filenames = filename
    else:
        raise TypeError('filename=%s is %s, not supported' % (filename, type(filename)))

    # bin/doconce functions that add info to the file collection
    # must provide the right doconce_docname and mode='a' in order
    # to write correctly to an already existing file.
    global _file_collection_filename
    if isinstance(doconce_docname, str) and doconce_docname != '':
        if doconce_docname.endswith('.do.txt'):
            doconce_docname = doconce_docname[:-7]
        if doconce_docname.endswith('.html'):
            doconce_docname = doconce_docname[:-5]
        _file_collection_filename = '.' + doconce_docname + \
                                    '_html_file_collection'
    if mode == 'a':
        try:
            f = open(_file_collection_filename, 'r')
        except (IOError, NameError):
            # sphinx, rst makes use of html functions that call
            # add_to_file_collection, and in those cases the
            # _file_collection_filename variable is not defined
            return
        files = [name.strip() for name in f.read().split()]
        f.close()
    else:
        files = []
    f = open(_file_collection_filename, mode)
    for name in filenames:
        if not name in files:  # already registered?
            f.write(name + '\n')
    f.close()

# Style sheets

admon_styles_text = """\
.alert-text-small   { font-size: 80%%;  }
.alert-text-large   { font-size: 130%%; }
.alert-text-normal  { font-size: 90%%;  }
"""

admon_styles1 = admon_styles_text + """\
.notice, .summary, .warning, .question, .block {
  border: 1px solid; margin: 10px 0px; padding:15px 10px 15px 50px;
  background-repeat: no-repeat; background-position: 10px center;
}
.notice   { color: #00529B; background-color: %(background_notice)s;
            background-image: url(https://raw.github.com/hplgit/doconce/master/bundled/html_images/%(icon_notice)s); }
.summary  { color: #4F8A10; background-color: %(background_summary)s;
            background-image:url(https://raw.github.com/hplgit/doconce/master/bundled/html_images/%(icon_summary)s); }
.warning  { color: #9F6000; background-color: %(background_warning)s;
            background-image: url(https://raw.github.com/hplgit/doconce/master/bundled/html_images/%(icon_warning)s); }
.question { color: #4F8A10; background-color: %(background_question)s;
            background-image:url(https://raw.github.com/hplgit/doconce/master/bundled/html_images/%(icon_question)s); }
.block    { color: #00529B; background-color: %(background_notice)s; }
"""

admon_styles2 = admon_styles_text + """\
.alert {
  padding:8px 35px 8px 14px; margin-bottom:18px;
  text-shadow:0 1px 0 rgba(255,255,255,0.5);
  border:1px solid %(boundary)s;
  border-radius: 4px;
  -webkit-border-radius: 4px;
  -moz-border-radius: 4px;
  color: %(color)s;
  background-color: %(background)s;
  background-position: 10px 5px;
  background-repeat: no-repeat;
  background-size: 38px;
  padding-left: 55px;
  width: 75%%;
 }
.alert-block {padding-top:14px; padding-bottom:14px}
.alert-block > p, .alert-block > ul {margin-bottom:1em}
.alert li {margin-top: 1em}
.alert-block p+p {margin-top:5px}
.alert-notice { background-image: url(https://raw.github.com/hplgit/doconce/master/bundled/html_images/%(icon_notice)s); }
.alert-summary  { background-image:url(https://raw.github.com/hplgit/doconce/master/bundled/html_images/%(icon_summary)s); }
.alert-warning { background-image: url(https://raw.github.com/hplgit/doconce/master/bundled/html_images/%(icon_warning)s); }
.alert-question {background-image:url(https://raw.github.com/hplgit/doconce/master/bundled/html_images/%(icon_question)s); }
"""
# alt: background-image: url(data:image/png;base64,iVBORw0KGgoAAAAN...);

css_solarized = """\
/* solarized style */
body {
  margin:5;
  padding:0;
  border:0; /* Remove the border around the viewport in old versions of IE */
  width:100%;
  background: #fdf6e3;
  min-width:600px;	/* Minimum width of layout - remove if not required */
  font-family: Verdana, Helvetica, Arial, sans-serif;
  font-size: 1.0em;
  line-height: 1.3em;
  color: #657b83;
}
a { color: #859900; text-decoration: underline; }
a:hover, a:active { outline:none }
a, a:active, a:visited { color: #859900; }
a:hover { color: #268bd2; }
h1, h2, h3 { margin:.8em 0 .2em 0; padding:0; line-height: 125%; }
h2 { font-variant: small-caps; }
tt, code { font-family: monospace, sans-serif; box-shadow: none; }
hr { border: 0; width: 80%; border-bottom: 1px solid #aaa}
p { text-indent: 0px; }
p.caption { width: 80%; font-style: normal; text-align: left; }
hr.figure { border: 0; width: 80%; border-bottom: 1px solid #aaa}
"""

css_solarized_dark = """\
    /* solarized dark style */
body {
  background-color: #002b36;
  color: #839496;
  font-family: Menlo;
}
code { background-color: #073642; color: #93a1a1; box-shadow: none; }
a { color: #859900; text-decoration: underline; }
a:hover, a:active { outline:none }
a, a:active, a:visited { color: #b58900; }
a:hover { color: #2aa198; }
"""

def css_link_solarized_highlight(style='light'):
    return """
<link href="https://raw.githubusercontent.com/hplgit/doconce/master/bundled/html_styles/style_solarized_box/css/solarized_%(style)s_code.css" rel="stylesheet" type="text/css" title="%(style)s"/>
<script src="http://www.peterhaschke.com/assets/highlight.pack.js"></script>
<script>hljs.initHighlightingOnLoad();</script>
""" % vars()

css_link_solarized_thomasf_light = '<link href="http://thomasf.github.io/solarized-css/solarized-light.min.css" rel="stylesheet">'
css_link_solarized_thomasf_dark = '<link href="http://thomasf.github.io/solarized-css/solarized-dark.min.css" rel="stylesheet">'
css_solarized_thomasf = 'h1, h2, h3, h4 {color:#839496;}'  # gray colors


css_blueish = """\
/* blueish style */

/* Color definitions:  http://www.december.com/html/spec/color0.html
   CSS examples:       http://www.w3schools.com/css/css_examples.asp */

body {
  margin-top: 1.0em;
  background-color: #ffffff;
  font-family: Helvetica, Arial, FreeSans, san-serif;
  color: #000000;
}
h1 { font-size: 1.8em; color: #1e36ce; }
h2 { font-size: 1.6em; color: #1e36ce; }
h3 { font-size: 1.4em; color: #1e36ce; }
a { color: #1e36ce; text-decoration:none; }
tt { font-family: "Courier New", Courier; }
pre { background: #ededed; color: #000; padding: 15px;}
p { text-indent: 0px; }
hr { border: 0; width: 80%; border-bottom: 1px solid #aaa}
p.caption { width: 80%; font-style: normal; text-align: left; }
hr.figure { border: 0; width: 80%; border-bottom: 1px solid #aaa}
"""

css_blueish2 = """\
/* blueish2 style */

/* Color definitions:  http://www.december.com/html/spec/color0.html
   CSS examples:       http://www.w3schools.com/css/css_examples.asp */

body {
  margin-top: 1.0em;
  background-color: #ffffff;
  font-family: Helvetica, Arial, FreeSans, san-serif;
  color: #000000;
}
h1 { font-size: 1.8em; color: #1e36ce; }
h2 { font-size: 1.6em; color: #1e36ce; }
h3 { font-size: 1.4em; color: #1e36ce; }
a { color: #1e36ce; text-decoration:none; }
tt { font-family: "Courier New", Courier; }
pre {
background-color: #fefbf3;
vpadding: 9px;
border: 1px solid rgba(0,0,0,.2);
-webkit-box-shadow: 0 1px 2px rgba(0,0,0,.1);
   -moz-box-shadow: 0 1px 2px rgba(0,0,0,.1);
        box-shadow: 0 1px 2px rgba(0,0,0,.1);
}
pre, code { font-size: 90%; line-height: 1.6em; }
pre > code { background-color: #fefbf3; border: none }
p { text-indent: 0px; }
hr { border: 0; width: 80%; border-bottom: 1px solid #aaa}
p.caption { width: 80%; font-style: normal; text-align: left; }
hr.figure { border: 0; width: 80%; border-bottom: 1px solid #aaa}
"""

css_bloodish = """\
/* bloodish style */

body {
  font-family: Helvetica, Verdana, Arial, Sans-serif;
  color: #404040;
  background: #ffffff;
}
h1 { font-size: 1.8em;  color: #8A0808; }
h2 { font-size: 1.6em;  color: #8A0808; }
h3 { font-size: 1.4em;  color: #8A0808; }
h4 { color: #8A0808; }
a { color: #8A0808; text-decoration:none; }
tt { font-family: "Courier New", Courier; }
pre { background: #ededed; color: #000; padding: 15px;}
p { text-indent: 0px; }
hr { border: 0; width: 80%; border-bottom: 1px solid #aaa}
p.caption { width: 80%; font-style: normal; text-align: left; }
hr.figure { border: 0; width: 80%; border-bottom: 1px solid #aaa}
"""

# too small margin bottom: h1 { font-size: 1.8em; color: #1e36ce; margin-bottom: 3px; }


def toc2html(font_size=80, bootstrap=True):
    global tocinfo  # computed elsewhere
    # level_depth: how many levels that are represented in the toc
    level_depth = int(option('html_toc_depth=', '-1'))
    if level_depth == -1:
        if bootstrap:
            # We can have max 17 lines, so analyze the toc
            level2no = {}
            for item in tocinfo:
                level = item[1]
                if level in level2no:
                    level2no[level] += 1
                else:
                    level2no[level] = 1
            level_depth = 1
            if 2 in level2no:
                if level2no[1] + level2no[2] <= 17:
                    level_depth = 2
            if 3 in level2no:
                if level2no[1] + level2no[2] + level2no[3] <= 17:
                    level_depth = 3
        else:
            level_depth = 2  # default in a normal toc

    indent = int(option('html_toc_indent=', '3'))
    nested_list = indent == 0

    level_min = tocinfo['highest level']
    level_max = level_min + level_depth - 1

    ul_class = ' class="nav"' if bootstrap else ''
    toc_html = ''
    uls = 0  # no of active <ul> sublists
    for i in range(len(tocinfo['sections'])):
        title, level, label, href = tocinfo['sections'][i]
        if level > level_max:
            continue
        spaces = '&nbsp;'*(indent*(level - level_min))
        if nested_list and i > 0 and level > tocinfo['sections'][i-1][1]:
            toc_html += '     <ul%s>\n' % ul_class
            uls += 1
        btitle = title = title.strip()
        if level_depth == 2 and level == level_min:
            btitle = '<b>%s</b>' % btitle  # bold for highest level
        toc_html += '     <!-- navigation toc: --> <li><a href="#%s" style="font-size: %d%%;">%s%s</a></li>\n' % (href, font_size, spaces, btitle)
        if nested_list and i < len(tocinfo['sections'])-1 and \
               tocinfo['sections'][i+1][1] < level:
            toc_html += '     </ul>\n'
            uls -= 1
    # remaining </ul>s
    if nested_list:
        for j in range(uls):
            toc_html += '     </ul>\n'
    return toc_html


def mathjax_header():
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
    mathjax_script_tag = """

<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  TeX: {
     equationNumbers: {  autoNumber: "AMS"  },
     extensions: ["AMSmath.js", "AMSsymbols.js", "autobold.js"]
  }
});
</script>
<script type="text/javascript"
 src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>
"""
    #<meta tag is valid only in html head anyway, so this was removed:
    #<!-- Fix slow MathJax rendering in IE8 -->
    #<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7">
    latex = '\n\n' + mathjax_script_tag + newcommands + '\n\n'
    return latex

def html_code(filestr, code_blocks, code_block_types,
              tex_blocks, format):
    """Replace code and LaTeX blocks by html environments."""
    html_style = option('html_style=', '')
    pygm_style = option('pygments_html_style=', default=None)

    # Mapping from envir (+cod/pro if present) to pygment style
    envir2pygments = dict(
        py='python', cy='cython', f='fortran',
        c='c', cpp='c++', sh='bash', rst='rst',
        m='matlab', pl='perl', rb='ruby',
        swig='c++', latex='latex', tex='latex',
        html='html', xml='xml',
        js='js', java='java',
        #sys='console',
        sys='text',
        #sys='bash'
        dat='text', txt='text', csv='text',
        cc='text', ccq='text',
        pyshell='python', ipy='ipy',
        pyopt='python', pysc='python',
        do='doconce')
    try:
        import pygments as pygm
        from pygments.lexers import guess_lexer, get_lexer_by_name
        from pygments.formatters import HtmlFormatter
        from pygments import highlight
        from pygments.styles import get_all_styles
    except ImportError:
        pygm = None
    # Can turn off pygments on the cmd line
    if pygm_style in ('no', 'none', 'off'):
        pygm = None
    if pygm is not None:
        if 'ipy' in code_block_types:
            if not has_custom_pygments_lexer('ipy'):
                envir2pygments['ipy'] = 'python'
        if 'do' in code_block_types:
            if not has_custom_pygments_lexer('doconce'):
                envir2pygments['do'] = 'text'

        if pygm_style is None:
            # Set sensible default values
            if option('html_style=', '').startswith('solarized'):
                pygm_style = 'none'
            else:
                pygm_style = 'default'
        else:
            # Fix style for solarized
            if option('html_style=') == 'solarized':
                if pygm_style != 'perldoc':
                    print '*** warning: --pygm_style=%s is not recommended when --html_style=solarized' % pygm_style
                    print '    automatically changed to --html_style=perldoc'
                    pygm_style = 'perldoc'
            elif option('html_style=') == 'solarized_dark':
                if pygm_style != 'friendly':
                    print '*** warning: --pygm_style=%s is not recommended when --html_style=solarized_dark' % pygm_style
                    print '    automatically changed to --html_style=friendly'
                    print '    (even better not to specify --pygm_style for solarized_dark)'
                    pygm_style = 'friendly'

        legal_lexers = get_legal_pygments_lexers()
        legal_styles = list(get_all_styles())
        legal_styles += ['no', 'none', 'off']
        if pygm_style not in legal_styles:
            print 'pygments style "%s" is not legal, must be among\n%s' % (pygm_style, ', '.join(legal_styles))
            #_abort()
            print 'using the "default" style...'
            pygm_style = 'default'
        if pygm_style in ['no', 'none', 'off']:
            pygm = None

        linenos = option('pygments_html_linenos')

    needs_online_python_tutor = False  # True if one occurence
    for i in range(len(code_blocks)):
        if code_block_types[i].startswith('pyoptpro'):
            needs_online_python_tutor = True
            code_blocks[i] = online_python_tutor(code_blocks[i],
                                                 return_tp='iframe')

        #elif code_block_types[i].startswith('pyscpro'):
        # not yet implemented
        elif pygm is not None:
            # Typeset with pygments
            #lexer = guess_lexer(code_blocks[i])
            if code_block_types[i].endswith('cod') or \
               code_block_types[i].endswith('pro'):
                type_ = code_block_types[i][:-3]
            else:
                type_ = code_block_types[i]
            if type_ in envir2pygments:
                language = envir2pygments[type_]
            elif type_ in legal_lexers:
                language = type_
            else:
                language = 'text'
            lexer = get_lexer_by_name(language)
            formatter = HtmlFormatter(linenos=linenos, noclasses=True,
                                      style=pygm_style)
            result = highlight(code_blocks[i], lexer, formatter)

            if code_block_types[i] == 'ccq':
                result = '<blockquote>\n%s</blockquote>' % result

            result = '<!-- code=%s%s typeset with pygments style "%s" -->\n' % (language, '' if code_block_types[i] == '' else ' (!bc %s)' % code_block_types[i], pygm_style) + result
            # Fix ugly error boxes
            result = re.sub(r'<span style="border: 1px .*?">(.+?)</span>',
                            '\g<1>', result)

            code_blocks[i] = result

        else:
            # Plain <pre>: This does not catch things like '<x ...<y>'
            #code_blocks[i] = re.sub(r'(<)([^>]*?)(>)',
            #                        '&lt;\g<2>&gt;', code_blocks[i])
            # Substitute & first, otherwise & in &quot; becomes &amp;quot;
            code_blocks[i] = code_blocks[i].replace('&', '&amp;')
            code_blocks[i] = code_blocks[i].replace('<', '&lt;')
            code_blocks[i] = code_blocks[i].replace('>', '&gt;')
            code_blocks[i] = code_blocks[i].replace('"', '&quot;')

    if option('wordpress'):
        # Change all equations to $latex ...$\n
        replace = [
            (r'\[', '$latex '),
            (r'\]', ' $\n'),
            (r'\begin{equation}', '$latex '),
            (r'\end{equation}', ' $\n'),
            (r'\begin{equation*}', '$latex '),
            (r'\end{equation*}', ' $\n'),
            (r'\begin{align}', '$latex '),
            (r'\end{align}', ' $\n'),
            (r'\begin{align*}', '$latex '),
            (r'\end{align*}', ' $\n'),
            ]
        for i in range(len(tex_blocks)):
            if '{align' in tex_blocks[i]:
                tex_blocks[i] = tex_blocks[i].replace('&', '')
                tex_blocks[i] = tex_blocks[i].replace('\\\\', ' $\n\n$latex ')
            for from_, to_ in replace:
                tex_blocks[i] = tex_blocks[i].replace(from_, to_)
            tex_blocks[i] = re.sub(r'label\{.+?\}', '', tex_blocks[i])

    for i in range(len(tex_blocks)):
        """
        Not important - the problem was repeated label.
        if 'begin{equation' in tex_blocks[i]:
            # Make sure label is on a separate line inside begin{equation}
            # environments (insert \n after labels with something before)
            tex_blocks[i] = re.sub('([^ ]) +label\{', '\g<1>\nlabel{',
                                   tex_blocks[i])
        """
        if 'label' in tex_blocks[i]:
            # Fix label -> \label in tex_blocks
            tex_blocks[i] = tex_blocks[i].replace(' label{', ' \\label{')
            pattern = r'^label\{'
            cpattern = re.compile(pattern, re.MULTILINE)
            tex_blocks[i] = cpattern.sub('\\label{', tex_blocks[i])

    from doconce import debugpr
    debugpr('File before call to insert_code_and_tex (format html):', filestr)
    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, format)
    debugpr('File after call to isnert_code_and tex (format html):', filestr)

    if pygm or needs_online_python_tutor:
        c = re.compile(r'^!bc(.*?)\n', re.MULTILINE)
        filestr = c.sub(r'<p>\n\n', filestr)
        filestr = re.sub(r'!ec\n', r'<p>\n', filestr)
        debugpr('After replacement of !bc and !ec (pygmentized code):', filestr)
    else:
        c = re.compile(r'^!bc(.*?)\n', re.MULTILINE)
        # <code> gives an extra line at the top unless the code starts
        # right after (do that - <pre><code> might be important for many
        # HTML/CSS styles).
        filestr = c.sub(r'<!-- begin verbatim block \g<1>-->\n<pre><code>', filestr)
        filestr = re.sub(r'!ec\n',
                r'</code></pre>\n<!-- end verbatim block -->\n',
                filestr)
        # Note: ccq envir is not put in blockquote tags, only if
        # pygments is used (would need to first substitute !bc ccq, but
        # !ec poses problems - drop this for plan pre/code tags since
        # pygments is the dominating style)

    if option('wordpress'):
        MATH_TYPESETTING = 'WordPress'
    else:
        MATH_TYPESETTING = 'MathJax'
    c = re.compile(r'^!bt *\n', re.MULTILINE)
    m1 = c.search(filestr)
    # common.INLINE_TAGS['math'] won't work since we have replaced
    # $...$ by \( ... \)
    pattern = r'\\\( .+? \\\)'
    m2 = re.search(pattern, filestr)
    math = bool(m1) or bool(m2)

    if MATH_TYPESETTING == 'MathJax':
        # LaTeX blocks are surrounded by $$
        filestr = re.sub(r'!bt *\n', '$$\n', filestr)
        # Add more space before and after equations
        #filestr = re.sub(r'!bt *\n', '&nbsp;<br>&nbsp;<br>\n$$\n', filestr)
        # (add extra newline after $$ since Google's blogspot HTML
        # needs that line to show the math right - otherwise it does not matter)
        filestr = re.sub(r'!et *\n', '$$\n\n', filestr)
        #filestr = re.sub(r'!et *\n', '$$\n&nbsp;<br>\n\n', filestr)

        # Remove inner \[..\] from equations $$ \[ ... \] $$
        filestr = re.sub(r'\$\$\s*\\\[', '$$', filestr)
        filestr = re.sub(r'\\\]\s*\$\$', '$$', filestr)
        # Equation references (ref{...}) must be \eqref{...} in MathJax
        # (note: this affects also (ref{...}) syntax in verbatim blocks...)
        filestr = re.sub(r'\(ref\{(.+?)\}\)', r'\eqref{\g<1>}', filestr)

    elif MATH_TYPESETTING == 'WordPress':
        filestr = re.sub(r'!bt *\n', '\n', filestr)
        filestr = re.sub(r'!et *\n', '\n', filestr)
        # References are not supported
        # (note: this affects also (ref{...}) syntax in verbatim blocks...)
        filestr = re.sub(r'\(ref\{(.+?)\}\)',
                         r'<b>(REF to equation \g<1> not supported)</b>', filestr)
    else:
        # Plain verbatim display of LaTeX syntax in math blocks
        filestr = c.sub(r'<blockquote><pre>\n', filestr)
        filestr = re.sub(r'!et *\n', r'</pre></blockquote>\n', filestr)

    # --- Final fixes for html format ---

    # Add MathJax script if math is present (math is defined right above)
    if math and MATH_TYPESETTING == 'MathJax':
        latex = mathjax_header()
        if '<body>' in filestr:
            # Add MathJax stuff after <body> tag
            filestr = filestr.replace('<body>\n', '<body>' + latex)
        else:
            # Add MathJax stuff to the beginning
            filestr = latex + filestr

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

    # Find all URLs to files (non http, ftp)
    import common
    pattern = '<a href=' + common._linked_files
    files = re.findall(pattern, filestr)
    for f, dummy in files:
        if not (f.startswith('http') or f.startswith('ftp') or \
           f.startswith('file:')):
            add_to_file_collection(f)

    # Change a href links so they open URLs in new windows?
    if option('html_links_in_new_window'):
        filestr = filestr.replace('target="_self"', 'target="_blank"')

    # Add info about the toc (for construction of navigation panels etc.).
    # Just dump the tocinfo dict so that we can read it and take eval
    # later
    import pprint
    global tocinfo
    if tocinfo is not None and isinstance(tocinfo, dict):
        toc = '\n<!-- tocinfo\n%s\nend of tocinfo -->\n\n' % \
              pprint.pformat(tocinfo)

        if '<body>' in filestr:
            # toc before the <body> tag
            filestr = filestr.replace('<body>\n', toc + '<body>\n')
        else:
            # Insert tocinfo at the beginning
            filestr = toc + filestr

    # Add header from external template
    template = option('html_template=', default='')
    if html_style == 'vagrant':
        print '*** warning: --html_style=vagrant is deprecated,'
        print '    just use bootstrap as style and combine with'
        print '    template from bundled/html_styles/style_vagrant'
        html_style == 'bootstrap'

    if template:
        title = ''
        date = ''

        header = '<title>' in filestr  # will the html file get a header?
        if header:
            print """\
*** warning: TITLE may look strange with a template -
             it is recommended to comment out the title: #TITLE:"""
            pattern = r'<title>(.+?)</title>'
            m = re.search(pattern, filestr)
            if m:
                title = m.group(1).strip()

        authors = '<!-- author(s):' in filestr
        if authors:
            print """\
*** warning: AUTHOR may look strange with a template -
             it is recommended to comment out all authors: #AUTHOR.
             Usually better to hardcode authors in a footer in the template."""

        # Extract title
        if title == '':
            # No real title found above.
            # The first section heading or a #TITLE: ... line becomes the title
            pattern = r'<!--\s+TITLE:\s*(.+?) -->'
            m = re.search(pattern, filestr)
            if m:
                title = m.group(1).strip()
                filestr = re.sub(pattern, '\n<h1>%s</h1>\n' % title, filestr)
            else:
                # Use the first ordinary heading as title
                m = re.search(r'<h\d>(.+?)<a name=', filestr)
                if m:
                    title = m.group(1).strip()

        # Extract date
        pattern = r'<center><h\d>(.+?)</h\d></center>\s*<!-- date -->'
        m = re.search(pattern, filestr)
        if m:
            date = m.group(1).strip()
            # remove date since date is in template
            filestr = re.sub(pattern, '', filestr)

        # Make toc for navigation
        toc_html = ''
        if html_style == 'bootstrap':
            toc_html = toc2html(bootstrap=True)
        elif html_style in ('solarized',):
            toc_html = toc2html(bootstrap=False)
        # toc_html lacks formatting, run some basic formatting here
        tags = 'emphasize', 'bold', 'math', 'verbatim', 'colortext'
        # drop URLs in headings?
        import common
        for tag in tags:
            toc_html = re.sub(common.INLINE_TAGS[tag],
                              common.INLINE_TAGS_SUBST[format][tag],
                              toc_html)
        # Load template file
        try:
            f = open(template, 'r'); template = f.read(); f.close()
        except IOError as e:
            print '*** error: could not find template "%s"' % template
            print e
            _abort()

        # Check that template does not have "main content" begin and
        # end lines that may interfere with the automatically generated
        # ones in Doconce (may destroy the split_html command)
        from doconce import main_content_char as _c
        m = re.findall(r'(<!-- %s+ main content %s+)' % (_c,_c), template)
        if m:
            print '*** error: template contains lines that may interfere'
            print '    with markers that doconce inserts - remove these'
            for line in m:
                print line
            _abort()

        # template can only have slots for title, date, main, table_of_contents
        template = latin2html(template) # code non-ascii chars
        # replate % by %% in template, except for %(title), %(date), %(main),
        # etc which are the variables we can plug into the template.
        # The keywords list holds the names of these variables (can define
        # more than we actually use).
        keywords = ['title', 'date', 'main', 'table_of_contents',
                    ]
        for keyword in keywords:
            from_ = '%%(%s)s' % keyword
            to_ = '@@@%s@@@' % keyword.upper()
            template = template.replace(from_, to_)
        template = template.replace('%', '%%')
        for keyword in keywords:
            to_ = '%%(%s)s' % keyword
            from_ = '@@@%s@@@' % keyword.upper()
            template = template.replace(from_, to_)

        variables = {keyword: '' for keyword in keywords} # init
        variables.update({'title': title, 'date': date, 'main': filestr,
                          'table_of_contents': toc_html})
        if '%(date)s' in template and date == '':
            print '*** warning: template contains date (%(date)s)'
            print '    but no date is specified in the document'
        filestr = template % variables

    if html_style.startswith('boots'):
        # Change chapter headings to page
        filestr = re.sub(r'<h1>(.+?)</h1> <!-- chapter heading -->',
                         '<h1 class="page-header">\g<1></h1>', filestr)
        # Some fancy functionality (e.g., in the bootstrap_wtoc template)
        # requires use of id tag in headings rather than the primitve <a name..
        filestr = re.sub(r'<h(\d)(.*?)>(.+?) <a name="(.+?)"></a>', r'<h\g<1>\g<2> id="\g<4>">\g<3><a name="\g<4>"></a>', filestr) # for highlighted toc in , but did not work,
    else:
        filestr = filestr.replace(' <!-- chapter heading -->', ' <hr>')
    if html_style.startswith('boots'):
        # Insert toc
        if '***TABLE_OF_CONTENTS***' in filestr:
            filestr = filestr.replace('***TABLE_OF_CONTENTS***', toc2html())
        jumbotron = option('html_bootstrap_jumbotron=', 'on')
        if jumbotron != 'off':
            # Fix jumbotron for title, author, date, toc, abstract, intro
            pattern = r'(^<center><h1>[^\n]+</h1></center>[^\n]+document title.+?)(^<!-- !split -->|^<h[123]>[^\n]+?<a name=[^\n]+?</h[123]>|^<div class="page-header">)'
            # Exclude lists (not a good idea if they are part of the intro...)
            #pattern = r'(^<center><h1>[^\n]+</h1></center>[^\n]+document title.+?)(^<!-- !split -->|^<h[123]>[^\n]+?<a name=[^\n]+?</h[123]>|^<div class="page-header">|<[uo]l>)'
            m = re.search(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
            if m:
                # If the user has a !split in the beginning, insert a button
                # to click (typically bootstrap design).
                # Also make the title h2 instead of h1 since h1 is REALLY
                # big in the jumbotron.
                core = m.group(1)
                rest = m.group(2)
                if jumbotron == 'h2':
                    core = core.replace('h1>', 'h2>')
                button = '<!-- potential-jumbotron-button -->' \
                         if '!split' in m.group(2) else ''
                text = '<div class="jumbotron">\n' + core + \
                       button + '\n</div> <!-- end jumbotron -->\n\n' + rest
                filestr = re.sub(pattern, text, filestr, flags=re.DOTALL|re.MULTILINE)
        # Fix slidecells? Just a start...this is hard...
        if '<!-- !bslidecell' in filestr:
            filestr = process_grid_areas(filestr)


    if MATH_TYPESETTING == 'WordPress':
        # Remove all comments for wordpress.com html
        pattern = re.compile('<!-- .+? -->', re.DOTALL)
        filestr = re.sub(pattern, '', filestr)

    # Add exercise logo
    html_style = option('html_style=', 'blueish')
    icon = option('html_exercise_icon=', 'None')
    icon_width = option('html_exercise_icon_width=', '100')
    if icon.lower() != 'none':
        if icon == 'default':
            if html_style == 'solarized' or html_style == 'bloodish':
                icon = 'question_black_on_gray.png'
                #icon = 'question_white_on_black.png'
            elif html_style.startswith('blue'):
                #icon = 'question_blue_on_white1.png'
                #icon = 'question_white_on_blue_tiny.png'
                icon = 'question_blue_on_white2.png'
            else:
                icon = 'exercise1.svg'
        icon_path = 'https://raw.github.com/hplgit/doconce/master/bundled/html_images/' + icon
        pattern = r'(<h3>(Exercise|Project|Problem) \d+:.+</h3>)'
        filestr = re.sub(pattern, '\g<1>\n\n<img src="%s" width=%s align="right">\n' % (icon_path, icon_width), filestr)

    # Reduce redunant newlines and <p> (easy with lookahead pattern)
    # Eliminate any <p> that goes with blanks up to <p> or a section
    # heading
    pattern = r'<p>\s+(?=<p>|<[hH]\d[^>]*>)'
    filestr = re.sub(pattern, '', filestr)
    # Extra blank before section heading
    pattern = r'\s+(?=^<[hH]\d[^>]*>)'
    filestr = re.sub(pattern, '\n\n', filestr, flags=re.MULTILINE)
    # Elimate <p> before equations $$ and before lists
    filestr = re.sub(r'<p>\s+(\$\$|<ul>|<ol>)', r'\g<1>', filestr)
    filestr = re.sub(r'<p>\s+<title>', '<title>', filestr)
    # Eliminate <p> after </h1>, </h2>, etc.
    filestr = re.sub(r'(</[hH]\d[^>]*>)\s+<p>', '\g<1>\n', filestr)

    return filestr

def process_grid_areas(filestr):
    # Extract all cell areas
    pattern = r'(^<!-- +begin-grid-area +-->(.+?)^<!-- +end-grid-area +-->)'
    cell_areas = re.findall(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
    # Work with each cell area
    for full_text, internal in cell_areas:
        cell_pos = [(int(p[0]), int(p[1])) for p in
                    re.findall(r'<!-- !bslidecell +(\d\d)', internal)]
        if cell_pos:
            # Find the table size
            num_rows    = max([p[0] for p in cell_pos]) + 1
            num_columns = max([p[1] for p in cell_pos]) + 1
            table = [[None]*(num_columns) for j in range(num_rows+1)]
            # Grab the content of each cell
            cell_pattern = r'(<!-- !bslidecell +(\d\d) *[.0-9 ]*?-->(.+?)<!-- !eslidecell -->)'
            cells = re.findall(cell_pattern, internal,
                               flags=re.DOTALL|re.MULTILINE)
            # Insert individual cells in table
            for cell_envir, pos, cell_text in cells:
                table[int(pos[0])][int(pos[1])] = cell_text
            # Construct new HTML text by looping over the table
            # (note that the input might have the cells in arbitrary
            # order while the output is traversed in correct cell order)
            new_text = '<div class="row"> <!-- begin cell row -->\n'
            for c in range(num_columns):
                new_text += '  <div class="col-sm-4">'
                for r in range(num_rows):
                    new_text += table[r][c]
                new_text += '  </div> <!-- column col-sm-4 -->\n'
            new_text += '</div> <!-- end cell row -->\n'
            filestr = filestr.replace(full_text, new_text)
    return filestr

def html_figure(m):
    caption = m.group('caption').strip()
    filename = m.group('filename').strip()
    opts = m.group('options').strip()

    if not filename.startswith('http'):
        add_to_file_collection(filename)

    if opts:
        info = [s.split('=') for s in opts.split()]
        opts = ' ' .join(['%s=%s' % (opt, value)
                          for opt, value in info if opt not in ['frac']])

    if caption:
       # Caption above figure and a horizontalrule (fine for anchoring):
       return """
<center> <!-- figure -->
<hr class="figure">
<center><p class="caption"> %s </p></center>
<p><img src="%s" align="bottom" %s></p>
</center>
""" % (caption, filename, opts)
    else:
       # Just insert image file
       return '<center><p><img src="%s" align="bottom" %s></p></center>' % \
              (filename, opts)

def html_footnotes(filestr, format, pattern_def, pattern_footnote):
    # Keep definitions where they are
    # (a bit better: place definitions before next !split)
    # Number the footnotes

    footnotes = re.findall(pattern_def, filestr, flags=re.MULTILINE|re.DOTALL)
    names = [name for name, footnote, dummy in footnotes]
    footnotes = {name: text for name, text, dummy in footnotes}

    name2index = {names[i]: i+1 for i in range(len(names))}

    def subst_def(m):
        # Make a table for the definition
        name = m.group('name').strip()
        text = m.group('text').strip()
        html = '\n<p><a name="def_footnote_%s"></a><a href="#link_footnote_%s"><b>%s:</b></a> %s\n' % (name2index[name], name2index[name], name2index[name], text)
        return html

    filestr = re.sub(pattern_def, subst_def, filestr,
                     flags=re.MULTILINE|re.DOTALL)

    def subst_footnote(m):
        name = m.group('name').strip()
        if name in name2index:
            i = name2index[m.group('name')]
        else:
            print '*** error: found footnote with name "%s", but this one is not defined' % name
            _abort()
        if option('html_style=', '').startswith('boots'):
            # Use a tooltip construction so the footnote appears when hovering over
            text = ' '.join(footnotes[name].strip().splitlines())
            # Note: formatting does not work well with a tooltip
            # could issue a warning of we find * (emphasis) or ` or "..": ".." link
            if '*' in text:
                newtext, n = re.subn(r'\*(.+?)\*', r'\g<1>', text)
                if n > 0:
                    print '*** warning: found emphasis tag *...* in footnote, which was removed'
                    print '    since it does not work with bootstrap tooltips'
                    print text
                text = newtext
            if '`' in text:
                newtext, n = re.subn(r'`(.+?)`', r'\g<1>', text)
                if n > 0:
                    print '*** warning: found inline code tag `...` in footnote, which was removed'
                    print '    since it does not work with bootstrap tooltips'
                    print text
                text = newtext
            if '"' in text:
                newtext, n = re.subn(r'"(.+?)" ?:\s*"(.+?)"', r'\g<1>', text)
                if n > 0:
                    print '*** warning: found link tag "...": "..." in footnote, which was removed'
                    print '    since it does not work with bootstrap tooltips'
                    print text
                text = newtext
            html = ' <button type="button" class="btn btn-primary btn-xs" rel="tooltip" data-placement="top" title="%s"><a name="link_footnote_%s"><a><a href="#def_footnote_%s" style="color: white">%s</a></button>' % (text, i, i, i)
        else:
            html = r' [<a name="link_footnote_%s"><a><a href="#def_footnote_%s">%s</a>]' % (i, i, i)
        return html

    filestr = re.sub(pattern_footnote, subst_footnote, filestr)
    return filestr

def html_table(table):
    column_width = table_analysis(table['rows'])
    ncolumns = len(column_width)
    column_spec = table.get('columns_align', 'c'*ncolumns).replace('|', '')
    heading_spec = table.get('headings_align', 'c'*ncolumns).replace('|', '')
    a2html = {'r': 'right', 'l': 'left', 'c': 'center'}
    bootstrap = option('html_style=', '').startswith('boots')

    if bootstrap:
        span = ncolumns+1
        s = """
<div class="row">
  <div class="col-xs-%d">
    <table class="table table-striped table-hover table-condensed">
""" % span
    else:
        s = '<table border="1">\n'
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

        if headline and not skip_headline:
            s += '<thead>\n'
        s += '<tr>'
        for column, w, ha, ca in \
                zip(row, column_width, heading_spec, column_spec):
            if headline:
                if not skip_headline:
                    # Use td tag if math or code or bootstrap
                    if r'\(' in column or '<code>' in column or bootstrap:
                        tag = 'td'
                        if bootstrap:
                            if r'\(' in column or '<code>' in column:
                                bold = '', ''
                            else:
                                bold = '<b>', '</b>'
                        else:
                            bold = '', ''
                    else:
                        tag = 'th'
                        bold = '', ''
                    s += '<%s align="%s">%s%s%s</%s> ' % \
                    (tag, a2html[ha], bold[0], column.center(w), bold[1], tag)
            else:
                s += '<td align="%s">   %s    </td> ' % \
                     (a2html[ca], column.ljust(w))
        s += '</tr>\n'
        if headline:
            if not skip_headline:
                s += '</thead>\n'
            s += '<tbody>\n'
    s += '</tbody>\n'
    if bootstrap:
        s += '    </table>\n  </div>\n</div> <!-- col-xs-%d -->\n' % span
    else:
        s += '</table>\n'
    return s

def html_movie(m):
    filename = m.group('filename')
    options = m.group('options')
    caption = m.group('caption').strip()

    if not filename.startswith('http'):
        add_to_file_collection(filename)

    # Turn options to dictionary
    if ',' in options:
        options = options.split(',')
    else:
        options = options.split()
    kwargs = {}
    for opt in options:
        if opt.startswith('width') or opt.startswith('WIDTH'):
            kwargs['width'] = int(opt.split('=')[1])
        if opt.startswith('height') or opt.startswith('HEIGHT'):
            kwargs['height'] = int(opt.split('=')[1])
    autoplay = option('html_video_autoplay=', 'False')
    if autoplay in ('on', 'off', 'True', 'true'):
        autoplay = True
    else:
        autoplay = False

    if 'youtu.be' in filename:
        filename = filename.replace('youtu.be', 'youtube.com')

    if '*' in filename or '->' in filename:
        # frame_*.png
        # frame_%04d.png:0->120
        # http://some.net/files/frame_%04d.png:0->120
        import DocWriter
        try:
            header, jscode, form, footer, frames = \
                    DocWriter.html_movie(filename, **kwargs)
        except ValueError as e:
            print '*** error: %s' % str(e)
            _abort()
        text = jscode + form
        if caption:
            text += '\n<br><em>' + caption + '</em><br>\n\n'
        if not frames[0].startswith('http'):
            add_to_file_collection(frames)
    elif 'youtube.com' in filename:
        if not 'youtube.com/embed/' in filename:
            filename = filename.replace('watch?v=', '')
            filename = filename.replace('youtube.com/', 'youtube.com/embed/')
            filename = filename.replace('http://youtube.com/', 'http://www.youtube.com/')
        # Make html for a local YouTube frame
        width = kwargs.get('width', 640)
        height = kwargs.get('height', 365)
        text = """
<iframe width="%s" height="%s" src="%s" frameborder="0" allowfullscreen></iframe>
""" % (width, height, filename)
        if caption:
            text += """\n<p><em>%s</em></p>\n\n""" % caption
    elif 'vimeo.com' in filename:
        if not 'player.vimeo.com/video/' in filename:
            if not filename.startswith('http://'):
                filename = 'http://' + filename
            filename = filename.replace('http://vimeo.com', 'http://player.vimeo.com/video')
        # Make html for a local Vimeo frame
        width = kwargs.get('width', 640)
        height = kwargs.get('height', 365)
        text = """
<iframe width="%s" height="%s" src="%s" frameborder="0" allowfullscreen></iframe>
""" % (width, height, filename)
        if caption:
            text += """\n<em>%s</em>\n\n""" % caption
    else:
        # Some movie file
        width = kwargs.get('width', 640)
        height = kwargs.get('height', 365)
        #basename = os.path.basename(filename)
        stem, ext = os.path.splitext(filename)
        if ext == '':
            print '*** error: never specify movie file without extension'
            _abort()

        if ext in ('.mp4', '.ogg', '.webm'):
            # Use new HTML5 video tag
            autoplay = 'autoplay' if autoplay else ''
            sources3 = option('no_mp4_webm_ogg_alternatives', True)
            text = """
<div>
<video %(autoplay)s loop controls width='%(width)s' height='%(height)s' preload='none'>""" % vars()
            ext2source_command = {
                '.mp4': """
    <source src='%(stem)s.mp4'  type='video/mp4;  codecs="avc1.42E01E, mp4a.40.2"'>""" % vars(),
                '.webm': """
    <source src='%(stem)s.webm' type='video/webm; codecs="vp8, vorbis"'>""" % vars(),
                '.ogg': """
    <source src='%(stem)s.ogg'  type='video/ogg;  codecs="theora, vorbis"'>""" % vars(),
                }
            if sources3:
                # Set up loading of three alternatives.
                # Specify mp4 as first video because on iOS only
                # the first specified video is loaded, and mp4
                # can play on iOS.
                msg = 'movie: trying to find'
                if is_file_or_url(stem + '.mp4', msg) in ('file', 'url'):
                    text += ext2source_command['.mp4']
                if is_file_or_url(stem + '.webm', msg) in ('file', 'url'):
                    text += ext2source_command['.webm']
                if is_file_or_url(stem + '.ogg', msg) in ('file', 'url'):
                    text += ext2source_command['.ogg']
            else:
                # Load just the specified file
                text += ext2source_command[ext]
            text += """
</video>
</div>
<p><em>%(caption)s</em></p>
""" % vars()
        elif ext in ('.mp3', '.m4a',):
            # Use HTML5 audio tag
            text = """
<audio src="%s"><p>Your browser does not support the audio element.</p>
</audio>
""" % filename
        else:
            # Old HTML embed tag
            autoplay = 'true' if autoplay else 'false'
            text = """
<embed src="%s" %s autoplay="%s" loop="true"></embed>
<p><em>%s</em></p>
""" % (filename, ' '.join(options), autoplay, caption)
    return text

def html_author(authors_and_institutions, auth2index,
                inst2index, index2inst, auth2email):
    # Make a short list of author names - can be extracted elsewhere
    # from the HTML code and used in, e.g., footers.
    authors = [author for author in auth2index]
    if len(authors) > 1:
        authors[-1] = 'and ' + authors[-1]
    authors = ', '.join(authors)
    text = """

<p>
<!-- author(s): %s -->
""" % authors

    def email(author):
        address = auth2email[author]
        if address is None:
            email_text = ''
        else:
            name, place = address.split('@')
            #email_text = ' (<tt>%s</tt> at <tt>%s</tt>)' % (name, place)
            email_text = ' (<tt>%s at %s</tt>)' % (name, place)
        return email_text

    one_author_at_one_institution = False
    if len(auth2index) == 1:
        author = list(auth2index.keys())[0]
        if len(auth2index[author]) == 1:
            one_author_at_one_institution = True
    if one_author_at_one_institution:
        # drop index
        author = list(auth2index.keys())[0]
        text += '\n<center>\n<b>%s</b> %s\n</center>\n' % \
            (author, email(author))
        text += '\n\n<p>\n<!-- institution -->\n\n'
        text += '<center><b>%s</b></center>\n' % (index2inst[1])
    else:
        for author in auth2index:
            text += '\n<center>\n<b>%s</b> %s%s\n</center>\n' % \
                (author, str(auth2index[author]), email(author))
        text += '\n\n<p>\n<!-- institution(s) -->\n\n'
        for index in index2inst:
            text += '<center>[%d] <b>%s</b></center>\n' % \
                    (index, index2inst[index])
    text += '\n\n'
    return text


def html_ref_and_label(section_label2title, format, filestr):
    # This is the first format-specific function to be called.
    # We therefore do some HTML-specific fixes first.

    # Section references:
    # .... see section ref{my:sec} is replaced by
    # see the section "...section heading..."
    pattern = r'[Ss]ection(s?)\s+ref\{'
    replacement = r'the section\g<1> ref{'
    filestr = re.sub(pattern, replacement, filestr)
    pattern = r'[Cc]hapter(s?)\s+ref\{'
    replacement = r'the chapter\g<1> ref{'
    filestr = re.sub(pattern, replacement, filestr)
    # Do not use "the appendix" since the headings in appendices
    # have "Appendix: title"
    pattern = r'[Aa]ppendix\s+ref\{'
    #replacement = r'the appendix ref{'
    replacement = r' ref{'
    filestr = re.sub(pattern, replacement, filestr)
    pattern = r'[Aa]ppendices\s+ref\{'
    #replacement = r'the appendices ref{'
    replacement = r' ref{'
    filestr = re.sub(pattern, replacement, filestr)
    # Need special adjustment to handle start of sentence (capital) or not.
    # Check: end of previous sentence (?.!) or start of new paragraph.
    #pattern = r'([.?!]\s+|\n\n)the (sections?|chapters?|appendix|appendices)\s+ref'
    pattern = r'([.?!]\s+|\n\n)the (sections?|chapters?)\s+ref'
    replacement = r'\g<1>The \g<2> ref'
    filestr = re.sub(pattern, replacement, filestr, flags=re.MULTILINE)

    # Remove "the" Exercise, Project, Problem in references since those words
    # are used in the title of the section too
    pattern = r'(the\s*)?([Ee]xercises?|[Pp]rojects?|[Pp]roblems?)\s+ref\{'
    replacement = r'ref{'
    filestr = re.sub(pattern, replacement, filestr)

    # Fix side effect from the above that one gets constructions 'the The'
    filestr = re.sub(r'the\s+The', 'the', filestr)

    # Recognize mdash ---
    # Must be attached to text or to a quote (ending in ., quotes, or
    # emphasis *)
    pattern = r'''([A-Za-z0-9.'"*])---([A-Za-z ])'''
    filestr = re.sub(pattern, '\g<1>&mdash;\g<2>', filestr)

    # extract the labels in the text (filestr is now without
    # mathematics and those labels)
    running_text_labels = re.findall(r'label\{(.+?)\}', filestr)

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
    s = '<h2>Table of contents</h2>\n\n%s\n<p>\n' % hr
    for i in range(len(sections)):
        title, level, label = sections[i]
        href = label if label is not None else '___sec%d' % i
        indent = '&nbsp; '*(3*(level - level_min))
        s += indent + '<a href="#%s">%s</a>' % (href, title ) + '<br>\n'
        extended_sections.append((title, level, label, href))
    s += '</p>%s\n<p>\n' % hr

    # Store for later use in navgation panels etc.
    global tocinfo
    tocinfo = {'sections': extended_sections, 'highest level': level_min}

    return s

def bootstrap_collapse(visible_text, collapsed_text,
                       id, button_text='', icon='pencil'):
    """Generate HTML Bootstrap code for a collapsing/unfolding text."""
    text = """
<p>
<a class="glyphicon glyphicon-%(icon)s showdetails" data-toggle="collapse"
 data-target="#%(id)s" style="font-size: 80%%;">%(button_text)s</a>
%(visible_text)s
<div class="collapse-group">
<p><div class="collapse" id="%(id)s">
%(collapsed_text)s
</div></p>
</div>
</p>
""" % vars()
    return text

def html_inline_comment(m):
    # See latex.py for explanation
    name = m.group('name').strip()
    comment = m.group('comment').strip()
    chars = {',': 'comma', ';': 'semicolon', '.': 'period'}
    if name[:4] == 'del ':
        for char in chars:
            if comment == char:
                return r' <font color="red"> (<b>edit %s</b>: delete %s)</font>' % (name[4:], chars[char])
        return r' <font color="red">(<b>edit %s</b>:)</font> <del> %s </del>' % (name[4:], comment)
    elif name[:4] == 'add ':
        for char in chars:
            if comment == char:
                return r'<font color="red">%s (<b>edit %s</b>: add %s)</font>' % (comment, name[4:], chars[char])
        return r' <font color="red">(<b>edit %s</b>:) %s</font>' % (name[4:], comment)
    else:
        # Ordinary name
        comment = ' '.join(comment.splitlines()) # '\s->\s' -> ' -> '
        if ' -> ' in comment:
            # Replacement
            if comment.count(' -> ') != 1:
                print '*** wrong syntax in inline comment:'
                print comment
                print '(more than two ->)'
                _abort()
            orig, new = comment.split(' -> ')
            return r' <font color="red">(<b>%s</b>:)</font> <del> %s </del> <font color="red">%s</font>' % (name, orig, new)
        else:
            # Ordinary comment
            return '\n<!-- begin inline comment -->\n<font color="red">(<b>%s</b>: %s)</font>\n<!-- end inline comment -->\n' % (name, comment)

def html_quiz(quiz):
    bootstrap = option('html_style=', '').startswith('boots')
    button_text = option('html_quiz_button_text=', '')
    question_prefix = quiz.get('question prefix',
                               option('quiz_question_prefix=', 'Question:'))
    common_choice_prefix = option('quiz_choice_prefix=', 'Choice')
    hr = '<hr>' if option('quiz_horizontal_rule=', 'on') == 'on' else ''

    text = ''
    if 'new page' in quiz:
        text += '<!-- !split -->\n<h2>%s</h2>\n\n' % quiz['new page']

    text += '<!-- begin quiz -->\n'
    # Don't write Question: ... if inside an exercise section
    if quiz.get('embedding', 'None') in ['exercise',]:
        pass
    else:
        text += '%s\n<p>\n<b>%s</b> ' % (hr, question_prefix)

    text += quiz['question'] + '</p>\n'

    # List choices as paragraphs
    for i, choice in enumerate(quiz['choices']):
        choice_no = i+1
        answer = choice[0].capitalize() + '!'
        choice_prefix = common_choice_prefix
        if 'choice prefix' in quiz:
            if isinstance(quiz['choice prefix'][i], basestring):
                choice_prefix = quiz['choice prefix'][i]
        if choice_prefix == '' or choice_prefix[-1] in ['.', ':', '?']:
            pass  # don't add choice number
        else:
            choice_prefix += ' %d:' % choice_no
        if not bootstrap:  # plain html: show tooltip when hovering over choices
            tooltip = answer
            if len(choice) == 3:
                expl = choice[2]
                formatted_code = False
                for c in '\\$<>{}':
                    if c in expl:
                        # formatted code in explanation, don't show
                        expl = ''
            else:
                expl = ''
            if expl:
                tooltip += ' ' + ' '.join(expl.splitlines())
            tooltip = ' title="%s"' % tooltip
            text += '\n<p><div%s><b>%s</b>\n%s\n</div></p>\n' % (tooltip, choice_prefix, choice[1])
        else:
            id = 'quiz_id_%d_%d' % (quiz['no'], choice_no)
            if len(choice) == 3:
                expl = choice[2]
            else:
                if choice[0] == 'right':
                    expl = 'Correct!'
                else:
                    expl = 'Wrong!'
            # Use collapse functionality, see http://jsfiddle.net/8cYFj/
            '''
            text += """
<p><b>%s</b>
%s
<div class="collapse-group">
<p><div class="collapse" id="%s">
<img src="https://raw.github.com/hplgit/doconce/master/bundled/html_images/%s.gif">
%s
</div></p>
<a class="btn btn-default btn-xs showdetails" data-toggle="collapse"
 data-target="#%s" style="font-size: 80%%;">%s</a>
</div>
</p>
""" % (choice_prefix, choice[1], id, 'correct' if choice[0] == 'right' else 'incorrect', expl, id, button_text)
            '''
            '''
            text += """
<p>
<a class="glyphicon glyphicon-pencil showdetails" data-toggle="collapse"
 data-target="#%s" style="font-size: 80%%;">%s</a>
&nbsp;<b>%s</b>
%s
<div class="collapse-group">
<p><div class="collapse" id="%s">
<img src="https://raw.github.com/hplgit/doconce/master/bundled/html_images/%s.gif">
%s
</div></p>
</div>
</p>
""" % (id, button_text, choice_prefix, choice[1], id, 'correct' if choice[0] == 'right' else 'incorrect', expl)
            '''
            visible_text = '&nbsp;<b>%s</b>\n%s' % (choice_prefix, choice[1])
            collapsed_text = '<img src="https://raw.github.com/hplgit/doconce/master/bundled/html_images/%s.gif">\n%s' % ('correct' if choice[0] == 'right' else 'incorrect', expl)
            text += bootstrap_collapse(
               visible_text, collapsed_text,
               id, button_text, icon='pencil')

    if not bootstrap and hr:
        text += '%s\n' % hr
    text += '<!-- end quiz -->\n'
    return text

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
    if re.search(r'solarized\d?_dark', option('html_style=', '')):
        html_admon_style = 'solarized_dark'
    elif option('html_style=', '').startswith('solarized'):
        html_admon_style = 'solarized_light'
    elif option('html_style=') == 'blueish2':
        html_admon_style = 'yellow'
    elif option('html_style=', '').startswith('boots'):
        html_admon_style = 'bootstrap_alert'
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

    if title and (title[-1] not in ('.', ':', '!', '?')) and \
       html_admon_style != 'bootstrap_panel':
        # Make sure the title ends with puncuation
        title += '.'

    # Make pygments background equal to admon background for colored admons?
    keep_pygm_bg = option('keep_pygments_html_bg')
    pygments_pattern = r'"background: .+?">'

    # html_admon_style is global variable
    if option('html_style=', '')[:5].startswith('boots'):
        # Bootstrap/Bootswatch html style

        if html_admon_style == 'bootstrap_panel':
            alert_map = {'warning': 'warning', 'notice': 'primary',
                         'summary': 'danger', 'question': 'success',
                         'block': 'default'}
            text = '<div class="panel panel-%%s">' %% alert_map['%(_admon)s']
            if '%(_admon)s' != 'block':  # heading?
                text += """
  <div class="panel-heading">
  <h3 class="panel-title">%%s</h3>
  </div>""" %% title
            text += """
<div class="panel-body">
%%s
</div>
</div>
""" %% block
        else: # bootstrap_alert
            alert_map = {'warning': 'danger', 'notice': 'success',
                         'summary': 'warning', 'question': 'info',
                         'block': 'success'}

            if not keep_pygm_bg:
                # 2DO: fix background color!
                block = re.sub(pygments_pattern, r'"background: %%s">' %%
                               admon_css_vars[html_admon_style]['background'], block)
            text = """<div class="alert alert-block alert-%%s alert-text-%%s"><b>%%s</b>
%%s
</div>
""" %% (alert_map['%(_admon)s'], text_size, title, block)
        return text

    elif html_admon_style == 'colors':
        if not keep_pygm_bg:
            block = re.sub(pygments_pattern, r'"background: %%s">' %%
                           admon_css_vars['colors']['background_%(_admon)s'], block)
        janko = """<div class="%(_admon)s alert-text-%%s"><b>%%s</b>
%%s
</div>
""" %% (text_size, title, block)
        return janko

    elif html_admon_style in ('gray', 'yellow', 'apricot', 'solarized_light', 'solarized_dark'):
        if not keep_pygm_bg:
            block = re.sub(pygments_pattern, r'"background: %%s">' %%
                           admon_css_vars[html_admon_style]['background'], block)
        return """<div class="alert alert-block alert-%(_admon)s alert-text-%%s"><b>%%s</b>
%%s
</div>
""" %% (text_size, title, block)

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

    elif html_admon_style == 'paragraph':
        # Plain paragraph
        paragraph = """

<!-- admonition: %(_admon)s, typeset as paragraph -->
<div class="alert-text-%%s"><b>%%s</b>
%%s
</div>
""" %% (text_size, title, block)
        return paragraph
    else:
        print '*** error: illegal --html_admon=%%s' %% html_admon_style
        print '    legal values are colors, gray, yellow, apricot, lyx,'
        print '    paragraph; and bootstrap_alert or bootstrap_panel for'
        print '    --html_style=bootstrap*|bootswatch*'
        _abort()
''' % vars()
    exec(_text)

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

    FILENAME_EXTENSION['html'] = '.html'  # output file extension
    BLANKLINE['html'] = '\n<p>\n'         # blank input line => new paragraph

    INLINE_TAGS_SUBST['html'] = {         # from inline tags to HTML tags
        # keep math as is:
        'math':          r'\g<begin>\( \g<subst> \)\g<end>',
        #'math2':         r'\g<begin>\g<puretext>\g<end>',
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
        'inlinecomment': html_inline_comment,
        'chapter':       r'\n<h1>\g<subst></h1> <!-- chapter heading -->',
        'section':       r'\n<h1>\g<subst></h1>',
        'subsection':    r'\n<h2>\g<subst></h2>',
        'subsubsection': r'\n<h3>\g<subst></h3>\n',
        'paragraph':     r'<b>\g<subst></b>\n',
        'abstract':      r'<b>\g<type>.</b> \g<text>\n\g<rest>',
        'title':         r'\n<title>\g<subst></title>\n\n<center><h1>\g<subst></h1></center>  <!-- document title -->\n',
        'date':          r'<p>\n<center><h4>\g<subst></h4></center> <!-- date -->',
        'author':        html_author,
        'figure':        html_figure,
        'movie':         html_movie,
        'comment':       '<!-- %s -->',
        'linebreak':     r'\g<text><br />',
        'footnote':      html_footnotes,
        'non-breaking-space': '&nbsp;',
        'horizontal-rule': '<hr>',
        'ampersand1':    r'\g<1> &amp; \g<2>',
        'ampersand2':    r' \g<1>&amp;\g<2>',
        }

    if option('wordpress'):
        INLINE_TAGS_SUBST['html'].update({
            'math':          r'\g<begin>$latex \g<subst>$\g<end>',
            'math2':         r'\g<begin>$latex \g<latexmath>$\g<end>'
            })

    ENVIRS['html'] = {
        'quote':         html_quote,
        'warning':       html_warning,
        'question':      html_question,
        'notice':        html_notice,
        'summary':       html_summary,
        'block':         html_block,
        'box':           html_box,
    }

    CODE['html'] = html_code

    # how to typeset lists and their items in html:
    LIST['html'] = {
        'itemize':
        {'begin': '\n<ul>\n', 'item': '<li>', 'end': '</ul>\n\n'},

        'enumerate':
        {'begin': '\n<ol>\n', 'item': '<li>', 'end': '</ol>\n\n'},

        'description':
        {'begin': '\n<dl>\n', 'item': '<dt>%s<dd>', 'end': '</dl>\n\n'},

        'separator': '',  # no need for blank lines between items and before/after
        }

    # how to typeset description lists for function arguments, return
    # values, and module/class variables:
    ARGLIST['html'] = {
        'parameter': '<b>argument</b>',
        'keyword': '<b>keyword argument</b>',
        'return': '<b>return value(s)</b>',
        'instance variable': '<b>instance variable</b>',
        'class variable': '<b>class variable</b>',
        'module variable': '<b>module variable</b>',
        }

    FIGURE_EXT['html'] = ('.png', '.gif', '.jpg', '.jpeg', '.svg')
    CROSS_REFS['html'] = html_ref_and_label
    TABLE['html'] = html_table
    INDEX_BIB['html'] = html_index_bib
    EXERCISE['html'] = plain_exercise
    TOC['html'] = html_toc
    QUIZ['html'] = html_quiz

    # Embedded style sheets and links to styles
    css_links = ''
    css = ''
    html_style = option('html_style=', '')
    if  html_style in ('solarized', 'solarized_light'):
        css = css_solarized
        css_links = css_link_solarized_highlight('light')
    elif  html_style == 'solarized_dark':
        css = css_solarized_dark
        css_links = css_link_solarized_highlight('dark')
    elif html_style in ('solarized2_light', 'solarized2'):
        css = css_solarized_thomasf
        css_links = css_link_solarized_highlight('light') + '\n' + \
                    css_link_solarized_thomasf_light
    elif html_style == 'solarized2_dark':
        css = css_solarized_thomasf
        css_links = css_link_solarized_highlight('dark') + '\n' + \
                    css_link_solarized_thomasf_dark
    elif html_style in ('solarized3_light', 'solarized3'):
        css_links = css_link_solarized_highlight('light') + '\n' + \
                    css_link_solarized_thomasf_light
    elif html_style == 'solarized3_dark':
        css_links = css_link_solarized_highlight('dark') + '\n' + \
                    css_link_solarized_thomasf_dark
    elif html_style == 'blueish':
        css = css_blueish
    elif html_style == 'blueish2':
        css = css_blueish2
    elif html_style == 'bloodish':
        css = css_bloodish
    elif html_style == 'plain':
        css = ''
    else:
        css = css_blueish # default

    if option('pygments_html_style=', None) not in ('no', 'none', 'off') \
        and not option('html_style=', 'blueish').startswith('solarized'):
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
    admon_styles = ['gray', 'yellow', 'apricot', 'colors', 'lyx', 'paragraph',
                    'bootstrap_alert', 'bootstrap_panel',
                    'solarized_light', 'solarized_dark']
    admon_css_vars = {style: {} for style in admon_styles}
    admon_css_vars['yellow']  = dict(boundary='#fbeed5', background='#fcf8e3')
    admon_css_vars['apricot'] = dict(boundary='#FFBF00', background='#fbeed5')
    #admon_css_vars['gray']    = dict(boundary='#bababa', background='whiteSmoke')
    admon_css_vars['gray']    = dict(boundary='#bababa', background='#f8f8f8') # same color as in pygments light gray background
    admon_css_vars['bootstrap_alert']  = dict(background='#ffffff')
    admon_css_vars['bootstrap_panel']  = dict(background='#ffffff')
    admon_css_vars['solarized_light'] = dict(boundary='#93a1a1', background='#eee8d5')
    admon_css_vars['solarized_dark'] = dict(boundary='#93a1a1', background='#073642')
    for style in admon_styles:
        admon_css_vars[style]['color'] = '#555'
    admon_css_vars['solarized_dark']['color'] = '#93a1a1'
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
            admon_css_vars['solarized_light']['icon_' + a] = 'small_yellow_%s.png' % a
            admon_css_vars['solarized_dark']['icon_' + a] = 'small_gray_%s.png' % a
        else:
            admon_css_vars['yellow']['icon_' + a]  = ''
            admon_css_vars['apricot']['icon_' + a] = ''
            admon_css_vars['gray']['icon_' + a]    = ''
            admon_css_vars['solarized_light']['icon_' + a] = ''
            admon_css_vars['solarized_dark']['icon_' + a] = ''
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
            elif html_admon_style in ('gray', 'yellow', 'apricot',
                                      'solarized_light', 'solarized_dark'):
                css += (admon_styles2 % admon_css_vars[html_admon_style])
            elif html_admon_style in ('lyx', 'paragraph'):
                css += admon_styles_text
            break

    style = """
%s
<style type="text/css">
%s
div { text-align: justify; text-justify: inter-word; }
</style>
""" % (css_links, css)
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


    if html_style.startswith('boots'):
        boots_version = '3.1.1'
        if html_style == 'bootstrap':
            boots_style = 'boostrap'
            urls = ['http://netdna.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css' % boots_version]
        elif html_style == 'bootstrap_bootflat':
            boots_style = 'bootflat'
            urls = ['http://netdna.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css' % boots_version,
                    'https://raw.githubusercontent.com/bootflat/bootflat.github.io/master/bootflat/css/bootflat.css']
        elif html_style.startswith('bootstrap_'):
            # Local Doconce stored or modified bootstrap themes
            boots_style = html_style.split('_')[1]
            urls = ['http://netdna.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css' % boots_version,
                    'https://raw.github.com/hplgit/doconce/master/bundled/html_styles/style_bootstrap/css/%s.css' % html_style]
        elif html_style.startswith('bootswatch'):
            default = 'cosmo'
            boots_style = default if 'bootswatch_' not in html_style else \
                          html_style.split('_')[1]
            urls = ['http://netdna.bootstrapcdn.com/bootswatch/%s/%s/bootstrap.min.css' % (boots_version, boots_style)]
            # Dark styles need some recommended options
            dark_styles = 'amelia cyborg darkly slate superhero'.split()
            if boots_style in dark_styles:
                if not option('keep_pygments_html_bg') or option('pygments_html_style=', None) is None or option('html_code_style=', None) is None or option('html_pre_style=', None) is None:
                    print """\
*** warning: bootswatch style "%s" is dark and some
    options to doconce format html are recommended:
    --pygments_html_style=monokai     # dark background
    --keep_pygments_html_bg           # keep code background in admons
    --html_code_style=inherit         # use <code> style in surroundings (no red)
    --html_pre_style=inherit          # use <pre> style in surroundings
    """

        style = """
<!-- Bootstrap style: %s -->
%s
<!-- not necessary
<link href="http://netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css" rel="stylesheet">
-->
"""% (html_style, '\n'.join(['<link href="%s" rel="stylesheet">' % url
                   for url in urls]))

    style_changes = ''
    if option('html_code_style=', 'on') in ('off', 'transparent', 'inherit'):
        style_changes += """\
/* Let inline verbatim have the same color as the surroundings */
code { color: inherit; background-color: transparent; }
"""
    if option('html_pre_style=', 'on') in ('off', 'transparent', 'inherit'):
        style_changes += """\
/* Let pre tags for code blocks have the same color as the surroundings */
pre { color: inherit; background-color: transparent; }
"""
    if html_style.startswith('boots') and '!bquiz' in filestr:
        # Style for buttons for collapsing paragraphs
        style_changes += """
/*
in.collapse+a.btn.showdetails:before { content:'Hide details'; }
.collapse+a.btn.showdetails:before { content:'Show details'; }
*/
"""
    if style_changes:
        style += """
<style type="text/css">
%s</style>
""" % style_changes

    meta_tags = """\
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="generator" content="Doconce: https://github.com/hplgit/doconce/" />
"""
    bootstrap_title_bar = ''
    m = re.search(r'^TITLE: *(.+)$', filestr, flags=re.MULTILINE)
    if m:
        title = m.group(1).strip()
        meta_tags += '<meta name="description" content="%s">\n' % title

        if html_style.startswith('boots'):

            # Make link back to the main HTML file
            outfilename = option('html_output=', None)
            if outfilename is None:
                from doconce import dofile_basename
                outfilename = dofile_basename + '.html'
            else:
                if not outfilename.endswith('html'):
                    outfilename += '.html'

            if option('html_bootstrap_navbar=', 'on') != 'off':
                bootstrap_title_bar = """
<!-- Bootstrap navigation bar -->
<div class="navbar navbar-default navbar-fixed-top">
  <div class="navbar-header">
    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-responsive-collapse">
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
    </button>
    <a class="navbar-brand" href="%s">%s</a>
  </div>
  <div class="navbar-collapse collapse navbar-responsive-collapse">
    <ul class="nav navbar-nav navbar-right">
      <li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Contents <b class="caret"></b></a>
        <ul class="dropdown-menu">
***TABLE_OF_CONTENTS***
        </ul>
      </li>
    </ul>
  </div>
</div>
</div> <!-- end of navigation bar -->
""" % (outfilename, title)


    keywords = re.findall(r'idx\{(.+?)\}', filestr)
    # idx with verbatim is usually too specialized - remove them
    keywords = [keyword for keyword in keywords
                if not '`' in keyword]
    # keyword!subkeyword -> keyword subkeyword
    keywords = ','.join(keywords).replace('!', ' ')

    if keywords:
        meta_tags += '<meta name="keywords" content="%s">\n' % keywords


    # Had to take DOCTYPE out from 1st line to load css files from github...
    # <!DOCTYPE html>
    INTRO['html'] = """\
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

    OUTRO['html'] = ''
    if html_style.startswith('boots'):
        INTRO['html'] += bootstrap_title_bar
        INTRO['html'] += """
<div class="container">

<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p> <!-- add vertical space -->
"""
        OUTRO['html'] += """
</div>  <!-- end container -->
<!-- include javascript, jQuery *first* -->
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
<script src="http://netdna.bootstrapcdn.com/bootstrap/3.0.0/js/bootstrap.min.js"></script>

<!-- Bootstrap footer
<footer>
<a href="http://..."><img width="250" align=right src="http://..."></a>
</footer>
-->
"""
    OUTRO['html'] += """

</body>
</html>
    """


def latin2html(text):
    """
    Transform a text with possible latin-1 characters to the
    equivalent valid text in HTML with all special characters
    with ordinal > 159 encoded as &#number;

    Method: convert from plain text (open(filename, 'r')) to utf-8,
    run through each character c, if ord(c) > 159,
    add the HTML encoded text to a list, otherwise just add c to the list,
    then finally join the list to make the new version of the text.

    Note: A simpler method is just to set
    <?xml version="1.0" encoding="utf-8" ?>
    as the first line in the HTML file, see how rst2html.py
    starts the HTML file.
    (However, the method below shows how to cope with special
    European characters in general.)
    """
    # Only run this algorithm for plain ascii files, otherwise
    # text is unicode utf-8 which is easily shown without encoding
    # non-ascii characters in html.
    if not isinstance(text, str):
        return text

    # Turn ascii into utf-8 or latin-1 before finding the ord(c)
    # codes and writing them out in html
    text_new = []
    try:
        text = text.decode('utf-8')
    except UnicodeDecodeError, e:
        try:
            text = text.decode('latin-1')
        except UnicodeDecodeError, e:
            print 'Tried to interpret the file as utf-8 (failed) and latin-1 (failed) - aborted'
            raise e
    #except UnicodeEncodeError, e:
    #    pass
    for c in text:
        try:
            if ord(c) > 159:
                text_new.append('&#%d;' % ord(c))
            else:
                text_new.append(c)
        except Exception, e:
            print e
            print 'character causing problems:', c
            raise e.__class__('%s: character causing problems: %s' % \
                              (e.__class__.__name__, c))
    return ''.join(text_new)
