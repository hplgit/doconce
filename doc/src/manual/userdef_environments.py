import re

def get_label(titleline):
    label = ''
    if 'label=' in titleline:
        pattern = r'label=([^\s]+)'
        m = re.search(pattern, titleline)
        if m:
            label = m.group(1)
            titleline = re.sub(pattern, '', titleline).strip()
    return label, titleline

def example(text, titleline, counter, format):
    """LaTeX typesetting of example environment."""
    label, titleline = get_label(titleline)
    s = r"""
\begin{example}
"""
    if label:
        s += 'label{%s}\n' % label  # no \ (is added by DocOnce)
    s += r"""
\noindent\emph{%s}.

%s
\end{example}
""" % (titleline, text)
    return s


def do_example(text, titleline, counter, format):
    """General typesetting of example environment via a section."""
    label, titleline = get_label(titleline)
    s = """

===== Example %d: %s =====
""" % (counter, titleline)
    if label:
        s += 'label{%s}\n' % label
    s += '\n%s\n\n' % text
    return s


def tcolorbox(text, titleline, counter, format):
    label, titleline = get_label(titleline)
    s = r"""
\begin{tcolorbox}[%%skin=widget,
boxrule=1mm,
coltitle=black,
colframe=blue!45!white,
colback=blue!15!white,
width=(.9\linewidth),before=\hfill,after=\hfill,
adjusted title={%s}]
%s
\end{tcolorbox}
""" % (titleline.strip(), text)
    return s

def htmlbox(text, titleline, counter, format):
    s = """
<div style="width: 60%%; padding: 10px; border: 1px solid #000;
 border-radius: 4px; box-shadow: 8px 8px 5px #888888;
 background: #cce5ff;">
 <b>%s</b><hr>
%s
</div>
""" % (titleline.strip(), text)
    return s

def do_highlight(text, titleline, counter, format):
    return '!bnotice %s\n%s\n!enotice\n' % (titleline.strip(), text)

envir2format = {
    'intro': {
        'latex': r"""
\usepackage{amsthm,tcolorbox}
\theoremstyle{definition}
\newtheorem{example}{Example}[section]
""",},
    'example': {
        'latex': example,
        'do': do_example,
        },
    'highlight': {
        'latex': tcolorbox,
        'html': htmlbox,
        'do': do_highlight,
        },
}
