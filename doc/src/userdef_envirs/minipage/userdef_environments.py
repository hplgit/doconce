import re

def get_label(titleline):
    """
    Extract label from title line in begin environment.
    Return label and title (without label).
    """
    label = ''
    if 'label=' in titleline:
        pattern = r'label=([^\s]+)'
        m = re.search(pattern, titleline)
        if m:
            label = m.group(1)
            titleline = re.sub(pattern, '', titleline).strip()
    return label, titleline

def latex_minipage(text, titleline, counter, format):
    """LaTeX typesetting of admon-based "minipage" environment."""
    label, titleline = get_label(titleline)
    s = r"""
\begin{notice_minipage}[%s]
""" % titleline
    if label:
        s += 'label{%s}\n' % label  # no \ (is added by DocOnce)
    s += r"""
%s
\end{notice_minipage}
""" % text
    return s

def html_minipage(text, titleline, counter, format):
    """HTML typesetting of admon-based "minipage" environment."""
    label, titleline = get_label(titleline)
    s = r"""
<quote style="font-size: 80%%">
"""
    if label:
        s += '<a name="%s"></a>\n' % label
    s += r"""
%s
</quote>
""" % (titleline, text)
    return s


def do_minipage(text, titleline, counter, format):
    """General typesetting of minipage environment via a section."""
    label, titleline = get_label(titleline)
    s = """

===== %s =====
""" % (titleline)
    if label:
        s += 'label{%s}\n' % label
    s += '\n%s\n\n' % text
    return s


envir2format = {
    'intro': {
        'latex': r"""
\usepackage[framemethod=TikZ]{mdframed}
\newmdenv[
  skipabove=15pt,
  skipbelow=15pt,
  outerlinewidth=0,
  backgroundcolor=white,
  linecolor=black,
  linewidth=0pt,
  frametitlebackgroundcolor=white,
  frametitlerule=false,
  frametitlefont=\normalfont\bfseries,
  shadow=false,        % frame shadow?
  shadowsize=11pt,
  leftmargin=1.5cm,
  rightmargin=1.5cm,
  font=\footnotesize,
  roundcorner=5,
  needspace=0pt,
]{minipage_mdfboxmdframed}

\newenvironment{notice_minipage}[1][]{
\begin{minipage_mdfboxmdframed}[frametitle=#1]
}
{
\end{minipage_mdfboxmdframed}
}
""",},
    'minipage': {
        'latex': latex_minipage,
        'html': html_minipage,
        'do': do_minipage,
        },
}
