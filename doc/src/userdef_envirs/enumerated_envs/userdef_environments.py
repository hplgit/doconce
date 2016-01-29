#!/usr/bin/env python
#
# (c) Ilya V. Schurov <ilya@schurov.com>, 2016
# Based on example_and_colorbox example by Hans Petter Langtangen
# Licensed under BSD 3-Clause License (like the rest of DocOnce, see LICENSE)
#
# -*- coding: utf-8 -*-
from mako.template import Template
import re

envir2format = {
    'intro': {
        'latex': u"""
\\usepackage{amsthm}
\\theoremstyle{definition}
\\newtheorem{remark}{Remark}
\\newtheorem{example}{Example}
\\newtheorem{definition}{Definition}
""",}
}
envirs = ['remark', 'example', 'definition']
for env in envirs:
    envir2format.update({
        env: {
            'latex': lambda text, titleline, counter, format, env=env: latex_env(env, text, titleline, counter, format),
            'do': lambda text, titleline, counter, format, env=env: do_env(env, text, titleline, counter, format),
            'html': lambda text, titleline, counter, format, env=env: html_env(env, text, titleline, counter, format),
        },
    })

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

def latex_env(env, text, titleline, counter, format):
    """LaTeX typesetting of theorem-style environment."""
    label, titleline = get_label(titleline)
    titleline = titleline.strip()
    template = ur"""
\begin{${env}}
% if label:
label{${label}}
% endif
% if titleline:
\noindent\emph{${titleline}.
%endif
${text}
\end{${env}}
"""
    return Template(template).render(**vars())

def do_env(env, text, titleline, counter, format):
    """General typesetting of theorem-style environment via a section."""
    label, titleline = get_label(titleline)
    titleline = titleline.strip()
    if titleline:
        titleline = ": "+titleline
    template = ur"""
===== ${env.capitalize()} ${counter} ${titleline} =====
% if label:
label{${label}}
% endif
${text}

"""
    return Template(template).render(**vars())

def html_env(env, text, titleline, counter, format):
    """HTML typesetting of theorem-style environment."""
    label, titleline = get_label(titleline)
    titleline = titleline.strip()
    template = ur"""
% if label:
<!-- custom environment: label=${label}, number=${counter} -->
% endif
<p class='env-${env}'><strong>${env.capitalize()} ${counter}${titleline}.</strong> 
${text}
</p>
"""
    return Template(template).render(**vars())
