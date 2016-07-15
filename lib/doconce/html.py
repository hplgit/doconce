import re, os, glob, sys, glob
from common import table_analysis, plain_exercise, insert_code_and_tex, \
     indent_lines, online_python_tutor, bibliography, \
     is_file_or_url, envir_delimiter_lines, doconce_exercise_output, \
     get_legal_pygments_lexers, has_custom_pygments_lexer, emoji_url, \
     fix_ref_section_chapter
from misc import option, _abort
from doconce import errwarn, locale_dict

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
    Add filename to the collection of needed files for a DocOnce-based
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
            background-image: url(RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/%(icon_notice)s); }
.summary  { color: #4F8A10; background-color: %(background_summary)s;
            background-image:url(RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/%(icon_summary)s); }
.warning  { color: #9F6000; background-color: %(background_warning)s;
            background-image: url(RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/%(icon_warning)s); }
.question { color: #4F8A10; background-color: %(background_question)s;
            background-image:url(RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/%(icon_question)s); }
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
.alert-notice { background-image: url(RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/%(icon_notice)s); }
.alert-summary  { background-image:url(RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/%(icon_summary)s); }
.alert-warning { background-image: url(RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/%(icon_warning)s); }
.alert-question {background-image:url(RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/%(icon_question)s); }
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
hr { border: 0; width: 80%; border-bottom: 1px solid #aaa; }
p { text-indent: 0px; }
p.caption { width: 80%; font-style: normal; text-align: left; }
hr.figure { border: 0; width: 80%; border-bottom: 1px solid #aaa; }
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
<link href="RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_styles/style_solarized_box/css/solarized_%(style)s_code.css" rel="stylesheet" type="text/css" title="%(style)s"/>
<script src="RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_styles/style_solarized_box/js/highlight.pack.js"></script>
<script>hljs.initHighlightingOnLoad();</script>
""" % vars()

css_link_solarized_thomasf_light = '<link href="http://thomasf.github.io/solarized-css/solarized-light.min.css" rel="stylesheet">'
css_link_solarized_thomasf_dark = '<link href="http://thomasf.github.io/solarized-css/solarized-dark.min.css" rel="stylesheet">'
css_solarized_thomasf_gray = """\
h1, h2, h3, h4 { color:#839496; font-weight: bold; } /* gray */
code { padding: 0px; background-color: inherit; }
pre {
  border: 0pt solid #93a1a1;
  box-shadow: none;
}
"""
css_solarized_thomasf_green = """\
h1 {color: #b58900;}  /* yellow */
/* h1 {color: #cb4b16;}  orange */
/* h1 {color: #d33682;}  magenta, the original choice of thomasf */
code { padding: 0px; background-color: inherit; }
pre {
  border: 0pt solid #93a1a1;
  box-shadow: none;
}
"""  # h2, h3 are green


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
/* blueish2 style (as blueish style, but different pre and code tags
   (only effective if not pygments is used))
*/

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

# Tactile theme from GitHub web page generator
css_tactile = """
/* Builds on
   http://meyerweb.com/eric/tools/css/reset/
   v2.0 | 20110126
   License: none (public domain)
   Many changes for DocOnce by Hans Petter Langtangen.
*/
html, body, div, span, applet, object, iframe,
h1, h2, h3, h4, h5, h6, p, blockquote, pre,
a, abbr, acronym, address, big, cite, code,
del, dfn, em, img, ins, kbd, q, s, samp,
small, strike, strong, sub, sup, tt, var,
b, u, i, center,
dl, dt, dd, ol, ul, li,
fieldset, form, label, legend,
table, caption, tbody, tfoot, thead, tr, th, td,
article, aside, canvas, details, embed,
figure, figcaption, footer, header, hgroup,
menu, nav, output, ruby, section, summary,
time, mark, audio, video {
	margin: 0;
	padding: 0;
	border: 0;
	font-size: 100%%;
	font: inherit;
	vertical-align: baseline;
}
/* HTML5 display-role reset for older browsers */
article, aside, details, figcaption, figure,
footer, header, hgroup, menu, nav, section {
	display: block;
}

body { line-height: 1; }
ol, ul { list-style: none; }
blockquote, q {	quotes: none; }
blockquote:before, blockquote:after,
q:before, q:after { content: ''; content: none; }
table {	border-collapse: collapse; border-spacing: 0; }

body {
  font-size: 1em;
  line-height: 1.5;
  background: #e7e7e7 url(RAW_GITHUB_URL/hplgit/num-methods-for-PDEs/master/doc/web/images/body-bg.png) 0 0 repeat;
  font-family: 'Helvetica Neue', Helvetica, Arial, serif;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);
  color: #6d6d6d;
  width: 620px;
  margin: 0 auto;
}

pre, code {
  font-family: "Monospace";
  margin-bottom: 30px;
  font-size: 14px;
}

code {
  border: solid 2px #ddd;
  padding: 0 3px;
}

pre {
  padding: 20px;
  color: #222;
  text-shadow: none;
  overflow: auto;
  border: solid 4px #ddd;
}

a { color: #d5000d; }
a:hover { color: #c5000c; }
ul, ol, dl { margin-bottom: 20px; }

hr {
  height: 1px;
  line-height: 1px;
  margin-top: 1em;
  padding-bottom: 1em;
  border: none;
}

b, strong { font-weight: bold; }
em { font-style: italic; }
table { width: 100%%; border: 1px solid #ebebeb; }
th { font-weight: 500; }
td { border: 4px solid #ddd; text-align: center; font-weight: 300; }

/* red color: #d5000d; /*black color: #303030; gray is default */

h1 {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
  %s
}

h2 {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 8px;
  %s
}

h3 { font-size: 18px; }
p { font-weight: 300; margin-bottom: 20px; margin-top: 12px; }
a { text-decoration: none; }
p a { font-weight: 400; }

blockquote {
  font-size: 1.6em;
  border-left: 10px solid #e9e9e9;
  margin-bottom: 20px;
  padding: 0 0 0 30px;
}

ul li {
  list-style: disc inside;
  padding-left: 20px;
}

ol li {
  list-style: decimal inside;
  padding-left: 3px;
}

dl dt {
  color: #303030;
}

footer {
  background: transparent url('../images/hr.png') 0 0 no-repeat;
  margin-top: 40px;
  padding-top: 20px;
  padding-bottom: 30px;
  font-size: 13px;
  color: #aaa;
}

footer a {
  color: #666;
}
footer a:hover {
  color: #444;
}


/* #Media Queries
================================================== */

/* Smaller than standard 960 (devices and browsers) */
@media only screen and (max-width: 959px) {}

/* Tablet Portrait size to standard 960 (devices and browsers) */
@media only screen and (min-width: 768px) and (max-width: 959px) {}

/* Mobile Landscape Size to Tablet Portrait (devices and browsers) */
@media only screen and (min-width: 480px) and (max-width: 767px) {}

/* Mobile Portrait Size to Mobile Landscape Size (devices and browsers) */
@media only screen and (max-width: 479px) {}
"""

# too small margin bottom: h1 { font-size: 1.8em; color: #1e36ce; margin-bottom: 3px; }

css_rossant = """
/* Style from http://cyrille.rossant.net/theme/css/styles.css */

html, button, input, select, textarea {
    font-family: "Source Sans Pro", sans-serif;
    font-size: 18px;
    font-weight: 300;
    color: #000;
}

a { color: #0088cc; text-decoration: none; }

a:hover { color: #005580; }

code {
    /*font-size: .9em;*/
    font-family: 'Ubuntu Mono';
    padding: 0 .1em;
}

.highlight pre {
    font-family: 'Ubuntu Mono';
    font-size: .9em;
    padding: .5em;
    word-wrap: normal;
    overflow: auto;
    white-space: pre;
}

blockquote {
    color: #777;
    border-left: .5em solid #eee;
    padding: 0 0 0 .75em;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 300;
}

h1 {
    font-size: 2.25em;
    margin: 0 0 .1em -.025em;
    padding: 0 0 .25em 0;
    border-bottom: 1px solid #aaa;
}


h2 {
    color: #555;
    font-size: 1.75em;
    margin: 1.75em 0 .5em 0;
    padding: 0 0 .25em 0;
    border-bottom: 1px solid #ddd;
}

h3 {
    margin: 1.25em 0 .75em 0;
    font-size: 1.35em;
    color: #777;
}
"""

def share(code_type,
          url=None,
          buttons=['email', 'facebook', 'google+', 'linkedin',
                   'twitter', 'print'],
          method='simplesharebuttons.com'):
    namespace =  {'url': url}
    s = ''
    if method == 'simplesharebuttons.com':
        if code_type == 'css':
            s += """
<style type="text/css">

#share-buttons img {
width: 35px;
padding: 5px;
border: 0;
box-shadow: 0;
display: inline;
}

</style>
"""
        elif code_type == 'buttons':
            s += """
<!-- Got these buttons from simplesharebuttons.com -->
<center>
<div id="share-buttons">
"""
            if 'email' in buttons:
                s += """
    <!-- Email -->
    <a href="mailto:?Subject=Interesting link&amp;Body=I%%20saw%%20this%%20and%%20thought%%20of%%20you!%%20 %(url)s">
        <img src="https://simplesharebuttons.com/images/somacro/email.png" alt="Email" />
    </a>
""" % namespace
            if 'facebook' in buttons:
                s += """
    <!-- Facebook -->
    <a href="http://www.facebook.com/sharer.php?u=%(url)s" target="_blank">
        <img src="https://simplesharebuttons.com/images/somacro/facebook.png" alt="Facebook" />
    </a>
""" % namespace
            if 'google+' in buttons:
                s += """
    <!-- Google+ -->
    <a href="https://plus.google.com/share?url=%(url)s" target="_blank">
        <img src="https://simplesharebuttons.com/images/somacro/google.png" alt="Google" />
    </a>
""" % namespace

            if 'linkedin' in buttons:
                s += """
    <!-- LinkedIn -->
    <a href="http://www.linkedin.com/shareArticle?mini=true&amp;url=%(url)s" target="_blank">
        <img src="https://simplesharebuttons.com/images/somacro/linkedin.png" alt="LinkedIn" />
    </a>
""" % namespace

            if 'twitter' in buttons:
                s += """
    <!-- Twitter -->
    <a href="https://twitter.com/share?url=%(url)s&amp;name=Interesting link&amp;hashtags=interesting" target="_blank">
        <img src="https://simplesharebuttons.com/images/somacro/twitter.png" alt="Twitter" />
    </a>
""" % namespace

            if 'print' in buttons:
                s += """
<!-- Print -->
    <a href="javascript:;" onclick="window.print()">
        <img src="https://simplesharebuttons.com/images/somacro/print.png" alt="Print" />
    </a>

</div>
""" % namespace
        s += '</center>\n'
    return s

def toc2html(html_style, bootstrap=True,
             max_headings=17, # max no of headings in pull down menu
             ):
    global tocinfo  # computed elsewhere

    # level_depth: how many levels that are represented in the toc
    level_depth = int(option('toc_depth=', '-1'))
    if level_depth == -1:  # Use -1 to indicate that doconce decides
        # Compute suitable depth in toc
        if bootstrap:
            # We can have max 17 lines in a dropdown box without a scrollbar
            # so see what is suitable to include in such a box
            level2no = {}
            for item in tocinfo['sections']:
                level = item[1]
                if level in level2no:
                    level2no[level] += 1
                else:
                    level2no[level] = 1
            level_depth = 0
            num_headings = 0  # total no of headings in n levels
            for n in 0, 1, 2, 3:
                if n in level2no:
                    num_headings += level2no[n]
                    if num_headings <= max_headings:
                        level_depth += 1
                    else:
                        break
        else:
            level_depth = 2  # default in a normal toc

    indent = int(option('html_toc_indent=', '3'))
    nested_list = indent == 0

    level_min = tocinfo['highest level']
    if level_depth == 0:  # too many sections? avoid empty navigation...
        level_max = level_min  # include all top levels
    else:
        level_max = level_min + level_depth - 1

    # font types (bootstrap pull-down Contents menu)
    style = 'font-size: 80%;'
    if html_style in ['bootswatch_yeti', 'bootswatch_lumen', 'bootswatch_slate', 'bootswatch_superhero']:
        style = 'font-size: 14px; padding: 4px 15px;'

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
        if level_depth >= 2 and level == level_min:
            btitle = '<b>%s</b>' % btitle  # bold for highest level
        toc_html += '     <!-- navigation toc: --> <li><a href="#%s" style="%s">%s%s</a></li>\n' % (href, style, spaces, btitle)
        if nested_list and i < len(tocinfo['sections'])-1 and \
               tocinfo['sections'][i+1][1] < level:
            toc_html += '     </ul>\n'
            uls -= 1
    # remaining </ul>s
    if nested_list:
        for j in range(uls):
            toc_html += '     </ul>\n'
    if toc_html == '' and tocinfo['sections']:
        errwarn('*** error: no table of contents generated from toc2html - BUG in doconce')
        _abort()
    return toc_html

class CreateApp():
    """Class for interactive Bokeh plots."""
    def __init__(self, plot_info):
        from numpy import linspace
        from bokeh.models.widgets import Slider, TextInput
        from bokeh.models import ColumnDataSource, HBox, VBoxForm

        N = 200
        colors = ['red', 'green', 'indigo', 'orange', 'blue', 'grey', 'purple']
        possible_inputs = ['x_axis_label', 'xrange', 'yrange', 'sliderDict', 'title', 'number_of_graphs']

        y = None
        self.curve = plot_info[0]
        x_axis_label = None
        y_axis_label = None
        xrange = (0, 10)
        yrange = (0, 10)
        sliderDict = None
        title = None
        number_of_graphs = None
        legend = None
        reverseAxes = False

        self.source = []
        self.sliderList = []

        for n in range(1,len(plot_info)):
            # Update inputs

            exec(plot_info[n].strip())

        self.x = linspace(xrange[0], xrange[1], N)
        self.reverseAxes = reverseAxes
        if sliderDict != None:
            self.parameters = sliderDict.keys()

            for n, param in enumerate(self.parameters):
                exec("sliderInstance = Slider(" + sliderDict[param] + ")") # Todo: Fix so exec is not needed
                exec("self.sliderList.append(sliderInstance)") # Todo: Fix so exec is not needed
                # get first value of param
                exec(param + " = "  + 'self.sliderList[n].value') # Todo: Fix so exec is not needed

        # Set up plot
        from bokeh.plotting import Figure
        self.plot = Figure(
            plot_height=400, plot_width=400, title=title,
            tools="crosshair,pan,reset,resize,save,wheel_zoom",
            x_range=xrange, y_range=yrange)
        self.plot.xaxis.axis_label = x_axis_label
        self.plot.yaxis.axis_label = y_axis_label
        # generate the first curve:
        x = self.x
        exec(plot_info[0]) #  execute y = f(x, params)

        if type(y) is list:
            if legend == None:
                legend = [legend]*len(y)
            for n in range(len(y)):

                if self.reverseAxes:
                    x_plot = y[n]
                    y_plot = self.x
                else:
                    x_plot = self.x
                    y_plot = y[n]
                self.source.append(
                    ColumnDataSource(data=dict(x=x_plot, y=y_plot)))
                self.plot.line(
                    'x', 'y',
                    source=self.source[n], line_width=3,
                    line_color=colors[n], legend=legend[n])
        else:
            if self.reverseAxes:
                x_plot = y
                y_plot = self.x
            else:
                x_plot = self.x
                y_plot = y
            self.source.append(
                ColumnDataSource(data=dict(x=x_plot, y=y_plot)))
            self.plot.line(
                'x', 'y',
                source=self.source[0], line_width=3, legend=legend)

    def update_data(self, attrname, old, new):
        # Get the current slider values
        y = None
        x = self.x
        for n, param in enumerate(self.parameters):
            exec(param + " = "  + 'self.sliderList[n].value')
        # generate the new curve:
        exec(self.curve) #  execute y = f(x, params)

        if type(y) is list:
            for n in range(len(y)):
                if self.reverseAxes:
                    x_plot = y[n]
                    y_plot = self.x
                else:
                    x_plot = self.x
                    y_plot = y[n]
                self.source[n].data = dict(x=x_plot, y=y_plot)
        else:
            if self.reverseAxes:
                x_plot = y
                y_plot = x
            else:
                x_plot = x
                y_plot = y
            self.source[0].data = dict(x=x_plot, y=y_plot)


def embed_IBPLOTs(filestr, format):
    """
    Replace all IBPLOT tags by proper script and bokeh code.
    Written by Fredrik Eikeland Fossan with edits by H. P. Langtangen.
    """
    from bokeh.document import Document
    from bokeh.client import push_session
    from bokeh.embed import autoload_server
    from bokeh.models import HBox, VBoxForm

    document = Document()
    session = push_session(document)

    # Find all IBPLOT tags and store them
    IBPLOT_tags = []
    IBPLOT_lines = []
    for line in filestr.splitlines():
        if line.startswith('IBPLOT:'):
            try:
                plot_info = line[8:-1].split(';')
            except Exception:
                plot_info = []
            if not plot_info:
                errwarn('*** error: inline plot specification\n    %s\ncould not be split wrt ;' % line)
                _abort()

            new_plot_info = []
            n = 0
            for element in plot_info:
                if element[0] ==' ':
                    element = element[1:]
                if element[-1] ==' ':
                    element = element[:-1]
                if element[-1] == ']' and n == len(plot_info) -1:
                    element = element[:-1]
                new_plot_info.append(element)
                n += 1
            IBPLOT_tags.append(new_plot_info)
            IBPLOT_lines.append(line)

    appLayoutList = []
    for app_info in IBPLOT_tags:
        app = CreateApp(app_info)
        for w in app.sliderList:
            w.on_change('value', app.update_data)
        inputs = VBoxForm(children=app.sliderList)
        layout = HBox(children=[inputs, app.plot], width=800)
        document.add_root(layout)
        appLayoutList.append(layout)

    # Replace each IBPLOT tag by proper HTML code
    app_no = 0
    for tags, line in zip(IBPLOT_tags, IBPLOT_lines):
        text = autoload_server(appLayoutList[app_no], session_id=session.id)
        if format == 'html':
            filestr = filestr.replace(line, '<!--\n%s\n-->\n' % line + text)
        else:
            filestr = filestr.replace(line, '')
        app_no += 1

    document.add_root(layout)
    return filestr, session

def embed_newcommands(filestr):
    from expand_newcommands import process_newcommand
    newcommands_files = list(
        sorted([name
                for name in glob.glob('newcommands*.tex')
                if not name.endswith('.p.tex')]))
    newcommands = ''
    for filename in newcommands_files:
        f = open(filename, 'r')
        text = ''
        for line in f.readlines():
            if line.startswith(r'\newcommand') or \
               line.startswith(r'\renewcommand'):
                pattern, dummy = process_newcommand(line)
                m = re.search(pattern, filestr)
                if m:
                    text += line
        text = text.strip()
        if text:
            newcommands += '\n<!-- %s -->\n' % filename + '$$\n' + text \
                           + '\n$$\n\n'
    return newcommands

def mathjax_header(filestr):
    newcommands = embed_newcommands(filestr)
    mathjax_script_tag = """

<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  TeX: {
     equationNumbers: {  autoNumber: "AMS"  },
     extensions: ["AMSmath.js", "AMSsymbols.js", "autobold.js", "color.js"]
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

def html_verbatim(m):
    code = m.group('subst')
    begin = m.group('begin')
    end = m.group('end')
    # Must quote special characters
    code = code.replace('&', '&amp;')
    code = code.replace('<', '&lt;')
    code = code.replace('>', '&gt;')
    code = code.replace('"', '&quot;')
    return r'%(begin)s<code>%(code)s</code>%(end)s' % vars()

def html_code(filestr, code_blocks, code_block_types,
              tex_blocks, format):
    """Replace code and LaTeX blocks by html environments."""

    # The test below is not needed anymore: doconce tests valid
    # refs and labels for all formats now
    '''
    # Do one fix before verbatim blocks are inserted
    # (where ref{} and label{} constructions are to be as is)
    allow_refs_to_external_docs = option('allow_refs_to_external_docs')
    find_remaining_references = True
    if find_remaining_references:
        # Find remaining ref{...} that is not referring to labels in the
        # document (everything should have been substituted, except eq.refs)
        # leave out eq.ref, verbatim (<code>ref... etc)
        remaining = re.findall('[^(>A-Za-z](ref\{.+?\})[^)<]', filestr)
        if remaining:
            errwarn('*** error: references to labels not defined in this document')
            #errwarn('\n + '\n'.join(remaining))
            index = 0
            for r in remaining:
                errwarn(r + ':')
                index = filestr.find(r, index)  # search since last occurence
                errwarn('   ' + filestr[index-35:index+35] + '\n---------------')
                index += len(r)
            errwarn("""
Causes of missing labels:
1: label is inside a generalized reference ref[][][],
   use the --allow_refs_to_external_docs option to remove
   the error message
2: label is defined in another file
3: preprocessor if-else has left the label out
4: forgotten to define the label
""")
            if not allow_refs_to_external_docs:
                _abort()
    '''

    html_style = option('html_style=', '')
    pygm_style = option('pygments_html_style=', default=None)
    legal_pygm_styles = 'monokai manni rrt perldoc borland colorful default murphy vs trac tango fruity autumn bw emacs vim pastie friendly native'.split()
    if pygm_style not in legal_pygm_styles:
        if pygm_style not in (None, "none", "None", "off", "no"):
            errwarn('*** error: wrong pygments style "%s"' % pygm_style)
            errwarn('    must be among\n%s' % str(legal_pygm_styles)[1:-1])
            _abort()

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
                if 'pyscpro' in code_block_types:
                    # Must have pygments style for Sage Cells to work
                    pygm_style = 'perldoc'
                else:
                    pygm_style = 'none'
                    # 2nd best: perldoc (light), see below
            elif option('html_style=', '').startswith('tactile'):
                pygm_style = 'trac'
            elif option('html_style=', '') == 'rossant':
                pygm_style = 'monokai'
            else:
                pygm_style = 'default'
        else:
            # Fix style for solarized and rossant
            if option('html_style=') == 'solarized':
                if pygm_style != 'perldoc':
                    errwarn('*** warning: --pygm_style=%s is not recommended when --html_style=solarized' % pygm_style)
                    errwarn('    automatically changed to --html_style=perldoc')
                    pygm_style = 'perldoc'
            elif option('html_style=') == 'solarized_dark':
                if pygm_style != 'friendly':
                    errwarn('*** warning: --pygm_style=%s is not recommended when --html_style=solarized_dark' % pygm_style)
                    errwarn('    automatically changed to --html_style=friendly')
                    errwarn('    (it is recommended not to specify --pygm_style for solarized_dark)')
                    pygm_style = 'friendly'

        legal_lexers = get_legal_pygments_lexers()
        legal_styles = list(get_all_styles())
        legal_styles += ['no', 'none', 'off']
        if pygm_style not in legal_styles:
            errwarn('pygments style "%s" is not legal, must be among\n%s' % (pygm_style, ', '.join(legal_styles)))
            #_abort()
            errwarn('using the "default" style...')
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

        elif code_block_types[i].startswith('pyscpro'):
            # Wrap Sage Cell code around the code
            # https://github.com/sagemath/sagecell/blob/master/doc/embedding.rst
            code_blocks[i] = """
<div class="compute"><script type="text/x-sage">
%s
</script></div>
""" % code_blocks[i]

        elif pygm is not None:
            # Typeset with pygments
            #lexer = guess_lexer(code_blocks[i])
            if code_block_types[i].endswith('cod') or \
               code_block_types[i].endswith('pro'):
                type_ = code_block_types[i][:-3]
            elif code_block_types[i].endswith('cod-h') or \
                 code_block_types[i].endswith('pro-h'):
                type_ = code_block_types[i][:-5]
            elif code_block_types[i].endswith('-h'):
                type_ = code_block_types[i][:-2]
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

            if code_block_types[i].endswith('-h'):
                # Embed some jquery JavaScript for a show/hide button
                result = """
<script type="text/javascript">
function show_hide_code%d(){
  $("#code%d").toggle();
}
</script>
<button type="button" onclick="show_hide_code%d()">Show/hide code</button>
<div id="code%d" style="display:none">
%s
</div>
""" % (i, i, i, i, result)

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

    # Inline math cannot have x<z<w as this is interpreted as tags
    # and becomes invisible
    filestr2 = re.sub(r'<!--(.+?)-->', '', filestr)  # remove comments first
    inline_math = re.findall(r'\\\( (.+?) \\\)', filestr2, flags=re.DOTALL)
    for m in inline_math:
        if '<' in m:
            m_new = m
            m_new = re.sub(r'([^ ])<', '\g<1> <', m_new)
            m_new = re.sub(r'<([^ ])', '< \g<1>', m_new)
            if m_new != m:
                errwarn('*** warning: inline math in HTML must have space around <:')
                errwarn('    %s  ->  %s' % (m, m_new))
            filestr = filestr.replace(r'\( %s \)' % m, r'\( %s \)' % m_new)
    for i in range(len(tex_blocks)):
        if re.search(r'[^ {}]<', tex_blocks[i]) or re.search(r'<[^ {}]', tex_blocks[i]):
            errwarn('*** warning: math block in HTML must have space around <:')
            errwarn(tex_blocks[i])
            tex_blocks[i] = re.sub(r'([^ {}])<', '\g<1> <', tex_blocks[i])
            tex_blocks[i] = re.sub(r'<([^ {}])', '< \g<1>', tex_blocks[i])
            errwarn('    changed to')
            errwarn(tex_blocks[i])
            print

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

        # Newlines in HTML become real newlines on wordpress.com,
        # remove newlines between words (but don't merge with code
        # blocks and don't merge lines starting with !),
        # word and link, word and emphasize, etc.
        # Technique: add \n and remove it if the line qualifies for
        # merging with the next
        lines = filestr.splitlines()
        ignorelines = ['^![be]', '^\d+ <<<!!(MATH|CODE)',]
        acceptlines_next = ['^[(A-Za-z0-9]', '^ +ref\{',
                            '^ *(<a +href=|<em>|<b>|<code>|\$latex |<font)',]
        acceptlines_present = ['([A-Za-z0-9.,;:?)]|</a>|</em>|</b>|</code>|\$|</font>) *$',]
        for i in range(len(lines)-1):
            #errwarn('Line:', i, lines[i])
            lines[i] += '\n'
            # Ignore merging this line with the next?
            ignore = False
            for pattern in ignorelines:
                if re.search(pattern, lines[i]):
                    ignore = True
                    #errwarn('This is an ignore line ' + pattern)
                    break
            if not ignore:
                # Next line must not be an ignore line
                ignore = False
                for pattern in ignorelines:
                    if re.search(pattern, lines[i+1]):
                        ignore = True
                        #errwarn('Next line is an ignore line ' + pattern)
                        break
                # Present line must be an accept line
                accept_present = False
                for pattern in acceptlines_present:
                    if re.search(pattern, lines[i]):
                        accept_present = True
                        #errwarn('Present line is an accept line ' + pattern)
                        break
                # Next line must be an accept line
                accept_next = False
                for pattern in acceptlines_next:
                    if re.search(pattern, lines[i+1]):
                        accept_next = True
                        #errwarn('Next line is an accept line', pattern)
                        break
                if (not ignore) and accept_present and accept_next:
                    # Line ends in correct character
                    # Merge with next line
                    lines[i] = lines[i].rstrip() + ' '
                    #errwarn('Merge!')
        filestr = ''.join(lines)
        # Must do the removal of \n in <li>.+?</li> later when </li> is added

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
            tex_blocks[i] = re.sub(r'^label\{', '\\label{', tex_blocks[i],
                                   flags=re.MULTILINE)

    from doconce import debugpr
    debugpr('File before call to insert_code_and_tex (format html):', filestr)
    filestr = insert_code_and_tex(filestr, code_blocks, tex_blocks, format)
    debugpr('File after call to insert_code_and tex (format html):', filestr)

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

    # Replace old-fashion <a name=""></a> anchors with id=""
    if option('html_style=', '').startswith('boots'):
        filestr = re.sub(r'<h(\d)(.*?)>(.+?) <a name="(.+?)"></a>',
                     r'<h\g<1>\g<2> id="\g<4>" class="anchor">\g<3>', filestr)
        # (use class="anchor" such that we can easily set the position of
        # headings in e.g. bootstrap CSS; use :_id to make h1/h2 identifier different)
    filestr = re.sub(r'<h(\d)(.*?)>(.+?) <a name="(.+?)"></a>',
                     r'<h\g<1>\g<2> id="\g<4>">\g<3>', filestr)
    filestr = re.sub(r'<a name="([^"]+)"></a>',
                     r'<div id="\g<1>"></div>', filestr)

    # Add MathJax script if math is present (math is defined right above)
    if math and MATH_TYPESETTING == 'MathJax':
        latex = mathjax_header(filestr)
        if '<body>' in filestr:
            # Add MathJax stuff after <body> tag
            filestr = filestr.replace('<body>\n', '<body>' + latex)
        else:
            # Add MathJax stuff to the beginning
            filestr = latex + filestr

    # Copyright
    from common import get_copyfile_info
    cr_text = get_copyfile_info(filestr, format=format)
    if cr_text is not None:
        filestr = filestr.replace('Copyright COPYRIGHT_HOLDERS',
                                  cr_text)

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
    if option('wordpress'):
        # Remove \n from <li>...</li>
        pattern = r'<li>.+?</li>'
        filestr = re.sub(pattern, lambda m: m.group().replace('\n', ' '),
                         filestr, flags=re.DOTALL)

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
        errwarn('*** warning: --html_style=vagrant is deprecated,')
        errwarn('    just use bootstrap as style and combine with')
        errwarn('    template from bundled/html_styles/style_vagrant')
        html_style == 'bootstrap'

    # Make toc for navigation
    toc_html = ''
    if html_style.startswith('boots'):
        toc_html = toc2html(html_style, bootstrap=True, max_headings=10000)
        # Fix
        toc_html = re.sub(r'id="table_of_contents">', 'id="table_of_contents" class="anchor">', toc_html)
    elif html_style in ('solarized',):
        toc_html = toc2html(html_style, bootstrap=False)
    # toc_html lacks formatting, run some basic formatting here
    tags = 'emphasize', 'bold', 'math', 'verbatim', 'colortext'
    # drop URLs in headings?
    import common
    for tag in tags:
        toc_html = re.sub(common.INLINE_TAGS[tag],
                          common.INLINE_TAGS_SUBST[format][tag],
                          toc_html)

    if template:
        title = ''
        date = ''

        header = '<!-- document title -->' in filestr  # will the html file get a header?
        if header:
            errwarn("""\
*** warning: TITLE may look strange with a template -
             it is recommended to comment out the title: #TITLE:""")
            pattern = r'<center><h1>(.+?)</h1></center>  <!-- document title -->'
            m = re.search(pattern, filestr)
            if m:
                title = m.group(1).strip()

        authors = '<!-- author(s):' in filestr
        if authors:
            errwarn("""\
*** warning: AUTHOR may look strange with a template -
             it is recommended to comment out all authors: #AUTHOR.
             Usually better to hardcode authors in a footer in the template.""")

        # Extract title
        if title == '':
            # The first section heading or a #TITLE: ... line becomes the title
            pattern = r'<!--\s+TITLE:\s*(.+?) -->'
            m = re.search(pattern, filestr)
            if m:
                title = m.group(1).strip()
                filestr = re.sub(pattern, '\n<h1>%s</h1>\n' % title, filestr)
            else:
                # Use the first ordinary heading as title
                m = re.search(r'<h\d id=.+?">(.+?)<', filestr)
                if m:
                    title = m.group(1).strip()

        # Extract date
        pattern = r'<center><h\d>(.+?)</h\d></center>\s*<!-- date -->'
        m = re.search(pattern, filestr)
        if m:
            date = m.group(1).strip()
            # remove date since date is in template
            filestr = re.sub(pattern, '', filestr)

        # Load template file
        try:
            f = open(template, 'r'); template = f.read(); f.close()
        except IOError as e:
            errwarn('*** error: could not find template "%s"' % template)
            errwarn(e)
            _abort()

        # Check that template does not have "main content" begin and
        # end lines that may interfere with the automatically generated
        # ones in DocOnce (may destroy the split_html command)
        from doconce import main_content_char as _c
        m = re.findall(r'(<!-- %s+ main content %s+)' % (_c,_c), template)
        if m:
            errwarn('*** error: template contains lines that may interfere')
            errwarn('    with markers that doconce inserts - remove these')
            for line in m:
                errwarn(line)
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
            errwarn('*** warning: template contains date (%(date)s)')
            errwarn('    but no date is specified in the document')
        filestr = template % variables

    if html_style.startswith('boots'):
        # Change chapter headings to page
        filestr = re.sub(r'<h1>(.+?)</h1> <!-- chapter heading -->',
                         '<h1 class="page-header">\g<1></h1>', filestr)
    else:
        filestr = filestr.replace(' <!-- chapter heading -->', ' <hr>')
    if html_style.startswith('boots'):
        # Insert toc if toc
        if '***TABLE_OF_CONTENTS***' in filestr:
            contents = locale_dict[locale_dict['language']]['Contents']
            try:
                filestr = filestr.replace('***TABLE_OF_CONTENTS***',
                                          toc_html)
                filestr = filestr.replace('***CONTENTS_PULL_DOWN_MENU***',
                                          contents)
            except UnicodeDecodeError:
                filestr = filestr.replace('***TABLE_OF_CONTENTS***',
                                          toc_html.decode('utf-8'))
                filestr = filestr.replace('***CONTENTS_PULL_DOWN_MENU***',
                                          contents.decode('utf-8'))

        jumbotron = option('html_bootstrap_jumbotron=', 'on')
        if jumbotron != 'off':
            # Fix jumbotron for title, author, date, toc, abstract, intro
            pattern = r'(^<center><h1>[^\n]+</h1></center>[^\n]+document title.+?)(^<!-- !split -->|^<h[123] id="|^<center><h1 id="|^<div class="page-header">)'
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
                # re.sub might be problematic for large amounts of text as
                # group symbols in text, like $1,\ 2,\ 3$ may fool the regex
                # subst. Since we have m.group() we can use str.replace
                #filestr = re.sub(pattern, text, filestr, flags=re.DOTALL|re.MULTILINE)
                filestr = filestr.replace(m.group(), text)
                # Last line may give trouble if there is no !split
                # before first section and the document is long...

        # Fix slidecells? Just a start...this is hard...
        if '<!-- !bslidecell' in filestr:
            filestr = process_grid_areas(filestr)


    if MATH_TYPESETTING == 'WordPress':
        # Remove all comments for wordpress.com html
        pattern = re.compile('<!-- .+? -->', re.DOTALL)
        filestr = re.sub(pattern, '', filestr)

    # Add social media sharing buttons
    url = option('html_share=', None)
    # --html_share=http://mysite.com/specials,twitter,facebook,linkedin
    if url is not None:
        if ',' in url:
            words = url.split(',')
            url = words[0]
            buttons = words[1:]
            code = share(code_type='buttons', url=url, buttons=buttons)
        else:
            code = share(code_type='buttons', url=url)
        filestr = re.sub(r'^</body>\n', code + '\n\n' + '</body>\n',
                         filestr, flags=re.MULTILINE)

    # Add links for Bokeh plots
    if 'Bokeh.logger.info(' in filestr:
        bokeh_version = '0.9.0'
        head = """
<!-- Tools for embedded Bokeh plots -->
<link rel="stylesheet"
      href="http://cdn.pydata.org/bokeh/release/bokeh-%(bokeh_version)s.min.css"
      type="text/css" />
<script type="text/javascript"
	src="http://cdn.pydata.org/bokeh/release/bokeh-%(bokeh_version)s.min.js">
</script>
<script type="text/javascript">
  Bokeh.set_log_level("info");
</script>
""" % vars()
        filestr = re.sub(r'^</head>\n', head + '\n\n</head>\n',
                         filestr, flags=re.MULTILINE)

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
        icon_path = 'RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/' + icon
        pattern = r'(<h3>(Exercise|Project|Problem) \d+:.+</h3>)'
        filestr = re.sub(pattern, '\g<1>\n\n<img src="%s" width=%s align="right">\n' % (icon_path, icon_width), filestr)

    filestr = html_remove_whitespace(filestr)

    return filestr

def html_remove_whitespace(filestr):
    # Reduce redunant newlines and <p> (easy with lookahead pattern)
    # Eliminate any <p> that goes with blanks up to <p> or a section
    # heading
    pattern = r'<p>\s+(?=<p>|<p id=|<[hH]\d[^>]*>)'
    filestr = re.sub(pattern, '', filestr)
    # Extra blank before section heading
    pattern = r'\s+(?=^<[hH]\d[^>]*>)'
    filestr = re.sub(pattern, '\n\n', filestr, flags=re.MULTILINE)
    # Elimate <p> before equations $$ and before lists
    filestr = re.sub(r'<p>\s+(\$\$|<ul>|<ol>)', r'\g<1>', filestr)
    # Eliminate <p> after </h1>, </h2>, etc.
    #filestr = re.sub(r'(</[hH]\d[^>]*>)\s+<p>', '\g<1>\n', filestr)
    #bad side effect in deck.js slides
    # Remove remaining too much space before <p>
    filestr = re.sub(r'\s{3,}<p>', r'\n\n<p>', filestr)
    # Remove repeated <p>'s
    filestr = re.sub(r'(\s+<p>){2,}', r'\g<1>', filestr)
    # Remove <p> + space up to </endtag>
    filestr = re.sub(r'<p>\s+(?=</)', r'<p>\n', filestr)
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
                new_text += '  <div class="col-sm-4">\n    <p> <!-- subsequent paragraphs come in larger fonts, so start with a paragraph -->'
                for r in range(num_rows):
                    new_text += table[r][c]
                new_text += '  </div> <!-- column col-sm-4 -->\n'
            new_text += '</div> <!-- end cell row -->\n'
            filestr = filestr.replace(full_text, new_text)
    return filestr

def interpret_bokeh_plot(text):
    """Find script and div tags in a Bokeh HTML file."""
    # Structure of the file
    """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Damped vibrations</title>

        <link rel="stylesheet" href="http://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.css" type="text/css" />
        <script type="text/javascript" src="http://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.js"></script>
        <script type="text/javascript">
            Bokeh.set_log_level("info");
        </script>

        <script type="text/javascript">
            Bokeh.$(function() {
                var modelid = "af0bc57e-f573-4a7f-be80-504fab00b254";
                var modeltype = "PlotContext";
                var elementid = "4a9dd7a1-f20c-4fe5-9917-13d172ef031a";
                Bokeh.logger.info("Realizing plot:")
                Bokeh.logger.info(" - modeltype: PlotContext");
                Bokeh.logger.info(" - modelid: af0bc57e-f573-4a7f-be80-504fab00b254");
                Bokeh.logger.info(" - elementid: 4a9dd7a1-f20c-4fe5-9917-13d172ef031a");
                var all_models = ...

                Bokeh.load_models(all_models);
                var model = Bokeh.Collections(modeltype).get(modelid);
                var view = new model.default_view({model: model, el: '#4a9dd7a1-f20c-4fe5-9917-13d172ef031a'});
                Bokeh.index[modelid] = view
            });
        </script>
    </head>
    <body>
        <div class="plotdiv" id="4a9dd7a1-f20c-4fe5-9917-13d172ef031a"></div>
    </body>
</html>
    """
    # Extract the script and all div tags
    scripts = re.findall(r'<script type="text/javascript">.+?</script>', text, flags=re.DOTALL)
    if len(scripts) != 2:
        errwarn('*** warning: bokeh file contains more than two script tags,')
        errwarn('    will be using the last one! (use output_file(..., mode="cdn"))')
    script = scripts[-1]
    divs = re.findall(r'<div class="plotdiv".+?</div>', text, flags=re.DOTALL)
    return script, divs


def html_figure(m):
    caption = m.group('caption').strip()
    filename = m.group('filename').strip()
    opts = m.group('options').strip()

    # Extract figure label
    pattern = r'(label\{(.+?)\})'
    m = re.search(pattern, caption)
    if m:
        label = '<!-- figure label: --> %s' % m.group(1)
        caption = re.sub(pattern,
                         ' <!-- caption label: %s -->' % m.group(2),
                         caption)
    else:
        label = ''
    # Place label in top of the figure such that links point to the
    # top regardless of whether the caption is at the top of bottom

    sidecaption = 0
    if opts:
        info = [s.split('=') for s in opts.split()]
        opts = ' '.join(['%s=%s' % (opt, value)
                         for opt, value in info
                         if opt not in ['frac', 'sidecap']])
        for opt, value in info:
            if opt == 'sidecap':
                sidecaption = 1
                break

    # Bokeh plot?
    bokeh_plot = False
    if filename.endswith('.html') and not filename.startswith('http'):
        f = open(filename, 'r')
        text = f.read()
        f.close()
        if 'Bokeh.set_log_level' in text:
            bokeh_plot = True
            script, divs = interpret_bokeh_plot(text)
        else:
            errwarn('*** error: figure file "%s" must be a Bokeh plot' % filename)
            _abort()

    if not filename.startswith('http') and not bokeh_plot:
        add_to_file_collection(filename)

    if bokeh_plot:
        image = '\n<!-- Bokeh plot -->\n%s\n%s' %  (script, '\n'.join(divs))
    else:
        image = '<img src="%s" align="bottom" %s>' % (filename, opts)

    if caption:
       # Caption above figure and an optional horizontal rules:
       hrules = option('html_figure_hrule=', 'top')
       top_hr = bottom_hr = ''
       if 'top' in hrules:
           top_hr = '\n<hr class="figure">'
       if 'bottom' in hrules:
           bottom_hr = '\n<hr class="figure">'

       placement = option('html_figure_caption=', 'top')
       if sidecaption == 0:
           if placement == 'top':
               s = """
<center> %s <!-- FIGURE -->%s
<center><p class="caption"> %s </p></center>
<p>%s</p>%s
</center>
""" % (label, top_hr, caption, image, bottom_hr)
           else:
               s = """
<center> %s <!-- FIGURE -->%s
<p>%s</p>
<center><p class="caption"> %s </p></center>%s
</center>
""" % (label, top_hr, image, caption, bottom_hr)
       else:
           # sidecaption is implemented as table
           s = """
<center> %s <!-- FIGURE -->%s
<table><tr>
<td>%s</td>
<td><p class="caption"> %s </p></td>
</tr></table>%s
</center>
""" % (label, top_hr, image, caption, bottom_hr)
       return s
    else:
       # Just insert image file when no caption
       #s = '<center><p>%s</p></center>' % image # without <linebreak>
       # with two <linebreak>:
       s = '<br /><br /><center><p>%s</p></center><br /><br />' % image
       return s


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
        html = '\n<p id="def_footnote_%s"><a href="#link_footnote_%s"><b>%s:</b></a> %s</p>\n' % (name2index[name], name2index[name], name2index[name], text)
        # (<a name=""></a> is later replaced by a div tag)
        return html

    filestr = re.sub(pattern_def, subst_def, filestr,
                     flags=re.MULTILINE|re.DOTALL)

    def subst_footnote(m):
        name = m.group('name').strip()
        if name in name2index:
            i = name2index[m.group('name')]
        else:
            errwarn('*** error: found footnote with name "%s", but this one is not defined' % name)
            _abort()
        if option('html_style=', '').startswith('boots'):
            # Use a tooltip construction so the footnote appears when hovering over
            text = ' '.join(footnotes[name].strip().splitlines())
            # Note: formatting does not work well with a tooltip
            # could issue a warning of we find * (emphasis) or ` or "..": ".." link
            if '*' in text:
                newtext, n = re.subn(r'\*(.+?)\*', r'\g<1>', text)
                if n > 0:
                    errwarn('*** warning: found emphasis tag *...* in footnote, which was removed')
                    errwarn('    in tooltip (since it does not work with bootstrap tooltips)')
                    errwarn('    but not in the footnote itself.')
                    errwarn(text + '\n')
                text = newtext
            if '`' in text:
                newtext, n = re.subn(r'`(.+?)`', r'\g<1>', text)
                if n > 0:
                    errwarn('*** warning: found inline code tag `...` in footnote, which was removed')
                    errwarn('    in tooltip (since it does not work with bootstrap tooltips):')
                    errwarn(text + '\n')
                text = newtext
            if '"' in text:
                newtext, n1 = re.subn(r'"(.+?)" ?:\s*"(.+?)"', r'\g<1>', text)
                newtext, n2 = re.subn(r'URL ?:\s*"(.+?)"', r'\g<1>', newtext)
                if n1 > 0 or n2 > 0:
                    errwarn('*** warning: found link tag "...": "..." in footnote, which was removed')
                    errwarn('    from tooltip (since it does not work with bootstrap tooltips)')
                    errwarn(text)
                text = newtext
            html = ' <button type="button" class="btn btn-primary btn-xs" rel="tooltip" data-placement="top" title="%s"><a href="#def_footnote_%s" id="link_footnote_%s" style="color: white">%s</a></button>' % (text, i, i, i)
            # (<a name=""></a> is later replaced by a div tag)
        else:
            html = r' [<a id="link_footnote_%s" href="#def_footnote_%s">%s</a>]' % (i, i, i)
            # (<a name=""></a> is later replaced by a div tag)
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
        #span = ncolumns+1
        # Base span on total width of all columns
        span = min(int(sum(column_width)/100.0*12), 12)
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
        s += '    </table>\n  </div> <!-- col-xs-%d -->\n</div> <!-- cell row -->\n' % span
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
            errwarn('*** error: %s' % str(e))
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
            errwarn('*** error: never specify movie file without extension')
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
            movie_exists = False
            mp4_exists = False
            if sources3:
                # Set up loading of three alternatives.
                # Specify mp4 as first video because on iOS only
                # the first specified video is loaded, and mp4
                # can play on iOS.
                msg = 'movie: trying to find'
                if is_file_or_url(stem + '.mp4', msg) in ('file', 'url'):
                    text += ext2source_command['.mp4']
                    movie_exists = True
                    mp4_exists = True
                if is_file_or_url(stem + '.webm', msg) in ('file', 'url'):
                    text += ext2source_command['.webm']
                    movie_exists = True
                if is_file_or_url(stem + '.ogg', msg) in ('file', 'url'):
                    text += ext2source_command['.ogg']
                    movie_exists = True
            else:
                # Load just the specified file
                if is_file_or_url(stem + ext, msg) in ('file', 'url'):
                    text += ext2source_command[ext]
                    movie_exists = True
            if not movie_exists:
                errwarn('*** warning: movie "%s" was not found' % filename)
                if sources3:
                    errwarn('    could not find any .ogg/.mp4/.webm version of this filename')
                    import time
                    time.sleep(5)  # let the warning shine for a while
                    _abort()

            text += """
</video>
</div>
<p><em>%(caption)s</em></p>
""" % vars()
            #if not mp4_exists:
            if True:
                # Seems that there is a problem with .mp4 movies as well...
                text += """
<!-- Issue warning if in a Safari browser -->
<script language="javascript">
if (!!(window.safari)) {
  document.write("<div style=\\"width: 95%%; padding: 10px; border: 1px solid #100; border-radius: 4px;\\"><p><font color=\\"red\\">The above movie will not play in Safari - use Chrome, Firefox, or Opera.</font></p></div>")}
</script>

"""
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
    text += '<br>\n\n'
    return text


def html_abstract(m):
    # m is r'<b>\g<type>.</b> \g<text>\n\g<rest>'
    type = m.group('type')
    type = locale_dict[locale_dict['language']].get(type, type)
    text = m.group('text')
    rest = m.group('rest')
    if type.lower() == 'preface':
        # Drop heading
        return '%(text)s\n%(rest)s' % vars()
    else:
        return '<b>%(type)s.</b> %(text)s\n%(rest)s' % vars()

def html_ref_and_label(section_label2title, format, filestr):
    # This is the first format-specific function to be called.
    # We therefore do some HTML-specific fixes first.

    filestr = fix_ref_section_chapter(filestr, format)

    # extract the labels in the text (filestr is now without
    # mathematics and associated labels)
    running_text_labels = re.findall(r'label\{(.+?)\}', filestr)

    # make special anchors for all the section titles with labels:
    for label in section_label2title:
        # make new anchor for this label (put in title):
        title = section_label2title[label]
        title_pattern = r'(_{3,9}|={3,9})\s*%s\s*(_{3,9}|={3,9})\s*label\{%s\}' % (re.escape(title), label)
        title_new = '\g<1> %s <a name="%s"></a> \g<2>' % (title.replace('\\', '\\\\'), label)
        # (Note: the <a name=""> anchor is replaced by id="" in html_code)
        filestr, n = re.subn(title_pattern, title_new, filestr)
        # (a little odd with mix of doconce title syntax and html NAME tag...)
        if n == 0:
            #raise Exception('problem with substituting "%s"' % title)
            pass

    # turn label{myname} to anchors <a name="myname"></a>
    filestr = re.sub(r'label\{(.+?)\}', r'<a name="\g<1>"></a>', filestr)
    # (<a name=""></a> is later replaced by a div tag)

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
    #
    caption_start = '<p class="caption">'
    caption_pattern = r'%s(.+?)</p>' % caption_start
    #label_pattern = r'%s.+?<a name="(.+?)">' % caption_start
    label_pattern = r'%s.+? <!-- caption label: (.+?) -->' % caption_start
    # Should have <h\d id=""> type of labels too

    # References to custom numbered environments are also handled here
    # We look for all such environments, extract their numbers
    # from special comment tag and record it to label2no along with Figure's
    # numbers
    #
    # We allow 'no-number numbers' like 'Theorem A', so use number=([^\s]+?) pattern
    # instead of number=(\d+?)

    custom_env_pattern = r'<!--\s*custom environment:\s*label=([^\s]+?),\s*number=([^\s]+?)\s*-->'

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

        # process custom environments
        m = re.search(custom_env_pattern, lines[i])
        if m:
            label2no[m.group(1)] = m.group(2)

            # replace the special comment with an anchor
            lines[i] = re.sub(custom_env_pattern,
                    "<div id=\"%s\" />" % m.group(1), lines[i])

    filestr = '\n'.join(lines)

    for label, no in label2no.iteritems():
        filestr = filestr.replace('ref{%s}' % label,
                                  '<a href="#%s">%s</a>' % (label, str(no)))
        # we allow 'non-number numbers' for custom environments like 'theorem A'
        # so str(no)

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
            # (Note: the <a name=""> anchor is replaced by id="" in html_code)
            filestr = filestr.replace(heading1 + title + heading2,
                                      heading1 + newtitle + heading2,
                                      1) # count=1: only the first!

    return filestr


def html_exercise(exer):
    exerstr, solstr = doconce_exercise_output(
        exer,
        solution_header='__Solution.__',
        answer_header='__Answer.__',
        hint_header='__Hint.__')

    bootstrap = option('html_style=', '').startswith('boots')
    if not bootstrap:
        return exerstr, solstr
    # Bootstrap typesetting where hints and solutions can be folded
    envir2heading = dict(hint=r'(?P<heading>__Hint(?P<hintno> \d+)?\.__)',
                         ans=r'(?P<heading>__Answer\.__)',
                         sol=r'(?P<heading>__Solution\.__)')

    global _id_counter # need this trick to update this var in subst func
    _id_counter = 0
    for envir in 'hint', 'ans', 'sol':

        def subst(m):
            global _id_counter
            _id_counter += 1
            heading = m.group('heading')
            body = m.group('body')
            id = 'exer_%d_%d' % (exer['no'], _id_counter)
            visible_text = heading
            unfold = bootstrap_collapse(
                visible_text=heading, collapsed_text=body,
                id=id, button_text='', icon='hand-right')
            replacement = '\n# ' + envir_delimiter_lines[envir][0] + '\n' + unfold + '\n# ' + envir_delimiter_lines[envir][1] + '\n'
            return replacement

        pattern = '\n# ' + envir_delimiter_lines[envir][0] + '\s+' + envir2heading[envir] + '(?P<body>.+?)' + '\n# ' + envir_delimiter_lines[envir][1] + '\n'
        exerstr = re.sub(pattern, subst, exerstr, flags=re.DOTALL)
        solstr = re.sub(pattern, subst, solstr, flags=re.DOTALL)

    return exerstr, solstr

def html_index_bib(filestr, index, citations, pubfile, pubdata):
    if citations:
        from common import cite_with_multiple_args2multiple_cites
        filestr = cite_with_multiple_args2multiple_cites(filestr)
    for label in citations:
        filestr = filestr.replace('cite{%s}' % label,
                                  '<a href="#%s">[%d]</a>' % \
                                  (label, citations[label]))
    if pubfile is not None:
        bibtext = bibliography(pubdata, citations, format='doconce')
        for label in citations:
            try:
                bibtext = bibtext.replace(
                    'label{%s}' % label, '<a name="%s"></a>' % label)
                # (<a name=""></a> is later replaced by a div tag)
            except UnicodeDecodeError, e:
                if "can't decode byte" in str(e):
                    try:
                        bibtext = bibtext.decode('utf-8').replace(
                            'label{%s}' % label, '<a name="%s"></a>' % label)
                    except UnicodeDecodeError, e:
                        errwarn('UnicodeDecodeError: ' + e)
                        errwarn('*** error: problems in %s' % pubfile)
                        errwarn('    with key ' + label)
                        errwarn('    tried to do decode("utf-8"), but it did not work')
                        _abort()
                else:
                    errwarn(e)
                    errwarn('*** error: problems in %s' % pubfile)
                    errwarn('    with key ' + label)
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

def html_toc(sections, filestr):
    # Find minimum section level
    level_min = 4
    for title, level, label in sections:
        if level < level_min:
            level_min = level

    toc_depth = int(option('toc_depth=', 2))

    extended_sections = []  # extended list for toc in HTML file
    toc = locale_dict[locale_dict['language']]['toc']
    # This function is always called, only extend headings if a TOC is wanted
    m = re.search(r'^TOC: +[Oo]n', filestr, flags=re.MULTILINE)
    if m:
        extended_sections.append(
            (toc, level_min, 'table_of_contents', 'table_of_contents'))
    #hr = '<hr>'
    hr = ''
    s = '<h1 id="table_of_contents">%s</h2>\n\n%s\n<p>\n' % (toc, hr)
    # (we add class="anchor" in the calling code the above heading, if necessary)
    for i in range(len(sections)):
        title, level, label = sections[i]
        href = label if label is not None else '___sec%d' % i
        indent = '&nbsp; '*(3*(level - level_min))
        if level <= toc_depth:
            s += indent + '<a href="#%s">%s</a>' % (href, title ) + '<br>\n'
        extended_sections.append((title.strip(), level, label, href))
    s += '</p>%s\n<p>\n' % hr

    # Store for later use in navgation panels etc.
    global tocinfo
    tocinfo = {'sections': extended_sections, 'highest level': level_min}

    return s

def bootstrap_collapse(visible_text, collapsed_text,
                       id, button_text='', icon='pencil'):
    """Generate HTML Bootstrap code for a collapsing/unfolding text."""
    # icon types:
    # http://www.w3schools.com/bootstrap/bootstrap_ref_comp_glyphs.asp
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
                errwarn('*** wrong syntax in inline comment:')
                errwarn(comment)
                errwarn('(more than two ->)')
                _abort()
            orig, new = comment.split(' -> ')
            return r' <font color="red">(<b>%s</b>:)</font> <del> %s </del> <font color="red">%s</font>' % (name, orig, new)
        else:
            # Ordinary comment
            return '\n<!-- begin inline comment -->\n<font color="red">(<b>%s</b>: %s)</font>\n<!-- end inline comment -->\n' % (name, comment)

def html_quiz(quiz):
    import string
    bootstrap = option('html_style=', '').startswith('boots')
    button_text = option('html_quiz_button_text=', '')
    question_prefix = quiz.get('question prefix',
                               option('quiz_question_prefix=', 'Question:'))
    common_choice_prefix = option('quiz_choice_prefix=', 'Choice')
    hr = '<hr>' if option('quiz_horizontal_rule=', 'on') == 'on' else ''
    quiz_expl = option('quiz_explanations=', 'on')

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
        if not bootstrap:  # plain html: show tooltip when hovering over choices
            tooltip = answer
            expl = ''
            if len(choice) == 3 and quiz_expl == 'on':
                expl = choice[2]
            if '<img' in expl or '$$' in expl or '<pre' in expl:
                errwarn('*** warning: quiz explanation contains block (fig/code/math)')
                errwarn('    and is therefore skipped')
                errwarn(expl + '\n')
                expl = ''  # drop explanation when it needs blocks
            # Should remove markup
            pattern = r'<a href="(.+?)">(.*?)</a>'  # URL
            expl = re.sub(pattern, '\g<2> (\g<1>)', expl)
            pattern = r'\\( (.+?) \\)'  # inline math
            expl = re.sub(pattern, '\g<1>', expl)  # mimic italic....
            tags = 'p blockquote em code b'.split()
            for tag in tags:
                expl = expl.replace('<%s>' % tag, ' ')
                expl = expl.replace('</%s>' % tag, ' ')
            tooltip = answer + ' ' + ' '.join(expl.splitlines())
            text += '\n<p><div title="%s"><b>%s</b>\n%s\n</div></p>\n' % (tooltip, choice_prefix, choice[1])
        else:
            id = 'quiz_id_%d_%s' % (quiz['no'], choice_no)
            if len(choice) == 3:
                expl = choice[2]
            else:
                if choice[0] == 'right':
                    expl = 'Correct!'
                else:
                    expl = 'Wrong!'
            # Use collapse functionality, see http://jsfiddle.net/8cYFj/
            visible_text = '&nbsp;<b>%s</b>\n%s' % (choice_prefix, choice[1])
            collapsed_text = '<img src="RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/%s.gif">\n%s' % ('correct' if choice[0] == 'right' else 'incorrect', expl)
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
    # _Admon is constructed at import time, used as default title, but
    # will always be in English because of the early construction
    _Admon = locale_dict[locale_dict['language']].get(_admon, _admon).capitalize()  # upper first char

    # Below we could use
    # <img src="data:image/png;base64,iVBORw0KGgoAAAANSUh..."/>
    # for embedding images in the html code rather than just including them
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
<p> <!-- subsequent paragraphs come in larger fonts, so start with a paragraph -->
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
        # Strip off <p> at the end of block to reduce space below the text
        block = re.sub('(<p>\s*)+$', '', block)
        # Need a <p> after the title to ensure some space before the text
        alert = """<div class="alert alert-block alert-%(_admon)s alert-text-%%s">
<b>%%s</b>
<p>
%%s
</div>
""" %% (text_size, title, block)
        return alert

    elif html_admon_style == 'lyx':
        block = '<div class="alert-text-%%s">%%s</div>' %% (text_size, block)
        if '%(_admon)s' != 'block':
            lyx = """
<table width="95%%%%" border="0">
<tr>
<td width="25" align="center" valign="top">
<img src="RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_images/lyx_%(_admon)s.png" hspace="5" alt="%(_admon)s"></td>
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

    elif html_admon_style.startswith('paragraph'):
        # Plain paragraph
        if '-' in html_admon_style:
            font_size = html_admon_style.split('-')[1]
            if font_size in ('small', 'large'):
                text_size = font_size
            else:
                if int(font_size) < 100:
                    text_size = 'small'
                else:
                    text_size = 'large'

        paragraph = """

<!-- admonition: %(_admon)s, typeset as paragraph -->
<div class="alert-text-%%s"><b>%%s</b>
%%s
</div>
""" %% (text_size, title, block)
        return paragraph
    else:
        errwarn('*** error: illegal --html_admon=%%s' %% html_admon_style)
        errwarn('    legal values are colors, gray, yellow, apricot, lyx,')
        errwarn('    paragraph, paragraph-80, paragraph-120; and')
        errwarn('    bootstrap_alert or bootstrap_panel for --html_style=bootstrap*|bootswatch*')
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
        'verbatim':      html_verbatim,
        'colortext':     r'<font color="\g<color>">\g<text></font>',
        #'linkURL':       r'\g<begin><a href="\g<url>">\g<link></a>\g<end>',
        'linkURL2':      r'<a href="\g<url>" target="_self">\g<link></a>',
        'linkURL3':      r'<a href="\g<url>" target="_self">\g<link></a>',
        'linkURL2v':     r'<a href="\g<url>" target="_self"><tt>\g<link></tt></a>',
        'linkURL3v':     r'<a href="\g<url>" target="_self"><tt>\g<link></tt></a>',
        'plainURL':      r'<a href="\g<url>" target="_self"><tt>\g<url></tt></a>',
        'inlinecomment': html_inline_comment,
        'chapter':       r'\n<center><h1>\g<subst></h1></center> <!-- chapter heading -->',
        'section':       r'\n<h1>\g<subst></h1>',
        'subsection':    r'\n<h2>\g<subst></h2>',
        'subsubsection': r'\n<h3>\g<subst></h3>\n',
        'paragraph':     r'<b>\g<subst></b>\n',
        'abstract':      html_abstract,
        'title':         r'\n\n<center><h1>\g<subst></h1></center>  <!-- document title -->\n',
        'date':          r'<p>\n<center><h4>\g<subst></h4></center> <!-- date -->\n<br>',
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
        'emoji':         r'\g<1><img src="%s\g<2>.png" width="22px" height="22px" align="center">\g<3>' % emoji_url
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

    FIGURE_EXT['html'] = {
        'search': ('.html', '.png', '.gif', '.jpg', '.jpeg', '.svg'),
        'convert': ('.png', '.gif', '.jpg')}

    CROSS_REFS['html'] = html_ref_and_label
    TABLE['html'] = html_table
    INDEX_BIB['html'] = html_index_bib
    EXERCISE['html'] = html_exercise
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
        css = css_solarized_thomasf_gray
        css_links = css_link_solarized_highlight('light') + '\n' + \
                    css_link_solarized_thomasf_light
    elif html_style == 'solarized2_dark':
        css = css_solarized_thomasf_gray
        css_links = css_link_solarized_highlight('dark') + '\n' + \
                    css_link_solarized_thomasf_dark

    elif html_style in ('solarized3_light', 'solarized3'):
        # Note: have tried to remove the extra box around code,
        # but did not succeed, think the original css file of thomasf
        # must be manipulated in some way...a lot of tries did not
        # succeed
        css = css_solarized_thomasf_green
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
    elif html_style.startswith('tactile'):
        h1_color = h2_color = ''
        if '-' in html_style:
            if html_style.endswith('red'):
                h1_color = h2_color = 'color: #d5000d;'
            elif html_style.endswith('black'):
                h1_color = h2_color = 'color: #303030;'

        css = css_tactile % (h1_color, h2_color)
    elif html_style == 'rossant':
        css = css_rossant
    elif html_style == 'plain':
        css = ''
    else:
        css = css_blueish # default

    if option('pygments_html_style=', None) not in ('no', 'none', 'off') \
        and not option('html_style=', 'blueish').startswith('solarized') \
        and not option('html_style=', 'blueish').startswith('tactile'):
        # Remove pre style as it destroys the background for pygments
        css = re.sub(r'(pre|pre, code) +\{.+?\}', r'/* \g<1> style removed because it will interfer with pygments */', css, flags=re.DOTALL)

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
        errwarn(' '.join(google_fonts))
        _abort()
    link = "@import url(http://fonts.googleapis.com/css?family=%s);"
    import_body_font = ''
    if body_font_family is not None:
        if body_font_family in google_fonts:
            import_body_font = link % body_font_family
        else:
            errwarn('*** warning: --html_body_font=%s is not valid' % body_font_family)
    import_heading_font = ''
    if heading_font_family is not None:
        if heading_font_family in google_fonts:
            import_heading_font = link % heading_font_family
        else:
            errwarn('*** warning: --html_heading_font=%s is not valid' % heading_font_family)
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
                break
            elif html_admon_style in ('gray', 'yellow', 'apricot',
                                      'solarized_light', 'solarized_dark'):
                css += (admon_styles2 % admon_css_vars[html_admon_style])
                break
            elif html_admon_style in ('lyx',) or html_admon_style.startswith('paragraph'):
                css += admon_styles_text.replace('%%', '%')
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
                add_to_file_collection(css_filename)


    if html_style.startswith('boots'):
        boots_version = '3.1.1'
        if html_style == 'bootstrap':
            boots_style = 'boostrap'
            urls = ['http://netdna.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css' % boots_version]
        elif html_style == 'bootstrap_bootflat':
            boots_style = 'bootflat'
            urls = ['http://netdna.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css' % boots_version,
                    'RAW_GITHUB_URL/bootflat/bootflat.github.io/master/bootflat/css/bootflat.css']
        elif html_style.startswith('bootstrap_'):
            # Local DocOnce stored or modified bootstrap themes
            boots_style = html_style.split('_')[1]
            urls = ['http://netdna.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css' % boots_version,
                    'RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_styles/style_bootstrap/css/%s.css' % html_style]
        elif html_style.startswith('bootswatch'):
            default = 'cosmo'
            boots_style = default if 'bootswatch_' not in html_style else \
                          html_style.split('_')[1]
            legal_bootswatch_styles = 'cerulean cosmo flatly journal lumen readable simplex spacelab united yeti amelia cyborg darkly slate spruce superhero'.split()
            if boots_style not in legal_bootswatch_styles:
                errwarn('*** error: wrong bootswatch style %s' % boots_style)
                errwarn('    legal choices:\n    %s' % ', '.join(legal_bootswatch_styles))
                _abort()
            urls = ['http://netdna.bootstrapcdn.com/bootswatch/%s/%s/bootstrap.min.css' % (boots_version, boots_style)]
            # Dark styles need some recommended options
            dark_styles = 'amelia cyborg darkly slate superhero'.split()
            if boots_style in dark_styles:
                if not option('keep_pygments_html_bg') or option('pygments_html_style=', None) is None or option('html_code_style=', None) is None or option('html_pre_style=', None) is None:
                    errwarn("""\
*** warning: bootswatch style "%s" is dark and some
    options to doconce format html are recommended:
    --pygments_html_style=monokai     # dark background
    --keep_pygments_html_bg           # keep code background in admons
    --html_code_style=inherit         # use <code> style in surroundings (no red)
    --html_pre_style=inherit          # use <pre> style in surroundings
    """ % boots_style)
        else:
            errwarn('*** wrong --html_style=%s' % html_style)
            _abort()

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
    if html_style.startswith('boots'):
        height = 50  # fixed header hight in pixels, varies with style
        if 'bootswatch' in html_style:
            _style = html_style.split('_')[-1]
            if _style in ('simplex', 'superhero'):
                height = 40
            elif _style in ('yeti',):
                height = 45
            elif _style in ('cerulean', 'cosmo', 'lumen', 'spacelab', 'united', 'slate', 'cyborg', 'amelia'):
                height = 50
            elif _style.startswith('journal') or _style in ('flatly', 'darkly'):
                height = 60
            elif _style in ('readable',):
                height = 64
        if html_style.startswith('bootstrap'):
            height = 50
        style_changes += """
/* Add scrollbar to dropdown menus in bootstrap navigation bar */
.dropdown-menu {
   height: auto;
   max-height: 400px;
   overflow-x: hidden;
}

/* Adds an invisible element before each target to offset for the navigation
   bar */
.anchor::before {
  content:"";
  display:block;
  height:%spx;      /* fixed header height for style %s */
  margin:-%spx 0 0; /* negative fixed header height */
}
""" % (height, html_style, height)
        if '!bquiz' in filestr:
        # Style for buttons for collapsing paragraphs
            style_changes += """
/*
in.collapse+a.btn.showdetails:before { content:'Hide details'; }
.collapse+a.btn.showdetails:before { content:'Show details'; }
*/
"""
    body_style = option('html_body_style=', None)
    if body_style is not None:
        style_changes += """
body { %s; }
""" % body_style
    if style_changes:
        style += """
<style type="text/css">
%s</style>
""" % style_changes

    # Add sharing buttons
    url = option('html_share=', None)
    if url is not None:
        style += share(code_type='css')

    meta_tags = """\
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="generator" content="DocOnce: https://github.com/hplgit/doconce/" />
"""
    bootstrap_title_bar = ''
    title = ''
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
                custom_links = option('html_bootstrap_navbar_links=', None)
                code_custom_links = ''
                if custom_links is not None:
                    custom_links = custom_links.split(';')
                    for custom_link in custom_links:
                        link, url = custom_link.split('|')
                        link = link.strip()
                        url = url.strip()
                        code_custom_links += """
  <div class="navbar-header">
    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-responsive-collapse">
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
    </button>
    <a class="navbar-brand" href="%s">%s</a>
  </div>
""" % (url, link)

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
%s
  <div class="navbar-collapse collapse navbar-responsive-collapse">
    <ul class="nav navbar-nav navbar-right">
      <li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">***CONTENTS_PULL_DOWN_MENU*** <b class="caret"></b></a>
        <ul class="dropdown-menu">
***TABLE_OF_CONTENTS***
        </ul>
      </li>
    </ul>
  </div>
</div>
</div> <!-- end of navigation bar -->
""" % (outfilename, title, code_custom_links)


    keywords = re.findall(r'idx\{(.+?)\}', filestr)
    # idx with verbatim is usually too specialized - remove them
    keywords = [keyword for keyword in keywords
                if not '`' in keyword]
    # Keywords paragraph
    import common
    m = re.search(common.INLINE_TAGS['keywords'], filestr, flags=re.MULTILINE)
    if m:
        keywords += re.split(r', *', m.group(1))
    # keyword!subkeyword -> keyword subkeyword
    keywords = ','.join(keywords).replace('!', ' ')

    if keywords:
        meta_tags += '<meta name="keywords" content="%s">\n' % keywords

    scripts = ''
    if option('pygments_html_style=', 'default') == 'highlight.js':
        scripts += """
<!-- use highlight.js and styles for code -->
<script src="RAW_GITHUB_URL/hplgit/doconce/master/bundled/html_styles/style_solarized_box/js/highlight.pack.js"></script>
<script>hljs.initHighlightingOnLoad();</script>
"""

    if '!bc pyscpro' in filestr or 'envir=pyscpro' in filestr:
        # Embed Sage Cell server
        # See https://github.com/sagemath/sagecell/blob/master/doc/embedding.rst
        scripts += """
<script src="http://sagecell.sagemath.org/static/jquery.min.js"></script>
<script src="http://sagecell.sagemath.org/embedded_sagecell.js"></script>
<link rel="stylesheet" type="text/css" href="https://sagecell.sagemath.org/static/sagecell_embed.css">
<script>
$(function () {
    // Make the div with id 'mycell' a Sage cell
    sagecell.makeSagecell({inputLocation:  '#mycell',
                           template:       sagecell.templates.minimal,
                           evalButtonText: 'Activate'});
    // Make *any* div with class 'compute' a Sage cell
    sagecell.makeSagecell({inputLocation: 'div.compute',
                           evalButtonText: 'Evaluate'});
});
</script>
"""
    if '!bu-' in filestr:
        scripts += """
<!-- USER-DEFINED ENVIRONMENTS -->
"""

    # Had to take DOCTYPE out from 1st line to load css files from github...
    # <!DOCTYPE html>
    INTRO['html'] = """\
<!--
Automatically generated HTML file from DocOnce source
(https://github.com/hplgit/doconce/)
-->
<html>
<head>
%s
<title>%s</title>
%s
%s
</head>
<body>

    """ % (meta_tags, title, style, scripts)

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
    # Need for jquery library? !bc pypro-h (show/hide button for code)
    m = re.search(r'^!bc +([a-z0-9]+)-h', filestr, flags=re.MULTILINE)
    if m and 'ajax.googleapis.com/ajax/libs/jquery' not in OUTRO['html']:
        OUTRO['html'] += """
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.js"></script>
"""

    from common import has_copyright
    copyright_, symbol = has_copyright(filestr)
    if copyright_:
        OUTRO['html'] += """

<center style="font-size:80%">
<!-- copyright --> {} Copyright COPYRIGHT_HOLDERS
</center>
""".format("&copy;" if symbol else "")
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
            errwarn('Tried to interpret the file as utf-8 (failed) and latin-1 (failed) - aborted')
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
            errwarn(e)
            errwarn('character causing problems: ' + c)
            raise e.__class__('%s: character causing problems: %s' % \
                              (e.__class__.__name__, c))
    return ''.join(text_new)
