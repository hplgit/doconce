# -*- coding: iso-8859-15 -*-
from latex import *

def pdflatex_emoji(m):
    space1 = m.group(1)
    space2 = m.group(3)
    name = m.group(2)
    if not os.path.isdir(latexfigdir):
        os.mkdir(latexfigdir)
    emojifile = os.path.join(latexfigdir, name + '.png')
    if not os.path.isfile(emojifile):
        # Download emoji image
        from common import emoji_url
        url = emoji_url + name + '.png'
        import urllib
        urllib.urlretrieve(url, filename=emojifile)
        # Check that this was successful
        with open(emojifile, 'r') as f:
            if 'Not Found' in f.read():
                print '*** error: emoji "name" is probably misspelled - cannot find any emoji with that name'
                _abort()
    s = space1 + r'\raisebox{-\height+\ht\strutbox}{\includegraphics[height=1.5em]{%s}}' % emojifile + space2
    return s

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

    if not 'latex' in BLANKLINE:
        # latex.define is not yet ran on these dictionaries, do it:
        import latex
        latex.define(FILENAME_EXTENSION,
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
                     filestr)

    # The big difference between pdflatex and latex is the image formats
    FIGURE_EXT['pdflatex'] = ('.pgf', '.pdf', '.png', '.jpg', '.jpeg')

    # The rest is copy
    ENVIRS['pdflatex'] = ENVIRS['latex']
    FILENAME_EXTENSION['pdflatex'] = FILENAME_EXTENSION['latex']
    BLANKLINE['pdflatex'] = BLANKLINE['latex']
    CODE['pdflatex'] = CODE['latex']
    LIST['pdflatex'] = LIST['latex']
    CROSS_REFS['pdflatex'] = CROSS_REFS['latex']
    INDEX_BIB['pdflatex'] = INDEX_BIB['latex']
    TABLE['pdflatex'] = TABLE['latex']
    EXERCISE['pdflatex'] = EXERCISE['latex']
    INTRO['pdflatex'] = INTRO['latex'].replace('.eps', '.pdf').replace('epsfig,', '')
    latex_style = option('latex_style=', 'std')
    if latex_style not in ('Springer_T2',):
        INTRO['pdflatex'] = INTRO['pdflatex'].replace(
            'usepackage{graphicx}', 'usepackage[pdftex]{graphicx}')
    OUTRO['pdflatex'] = OUTRO['latex']
    ARGLIST['pdflatex'] = ARGLIST['latex']
    TOC['pdflatex'] = TOC['latex']
    QUIZ['pdflatex'] = QUIZ['latex']

    # make true copy of INLINE_TAGS_SUBST:
    INLINE_TAGS_SUBST['pdflatex'] = {}
    for tag in INLINE_TAGS_SUBST['latex']:
        INLINE_TAGS_SUBST['pdflatex'][tag] = INLINE_TAGS_SUBST['latex'][tag]
    INLINE_TAGS_SUBST['pdflatex']['emoji'] = pdflatex_emoji
