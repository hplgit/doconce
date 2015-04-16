import os, sys, shutil, re, glob, sets, time, commands

_part_filename = '._%s%03d'
_part_filename_wildcard = '._*[0-9][0-9][0-9]'

_registered_command_line_options = [
    ('--help',
     'Print all options to the doconce program.'),
    ('--debug',
     """Write a debugging file _doconce_debugging.log with lots
of intermediate results"""),
    ('--no_abort',
     'Do not abort the execution if syntax errors are found.'),
    ('--verbose=',
     """Write progress of intermediate steps if they take longer than X seconds.
0: X=15
1: X=5
2: 0.5"""),
    ('--syntax_check=',
     """Values: on/off. Turns on/off fix of illegal constructions and the syntax check
(may be time consuming for large books)."""),
    ('--skip_inline_comments',
     'Remove all inline comments of the form [ID: comment].'),
    ('--encoding=',
     'Specify encoding (e.g., latin1 or utf-8).'),
    ('--no_ampersand_quote', 'Turn off special treatment of ampersand (&). Needed, e.g., when native latex code for tables are inserted in the document.'),
    ('--no_mako',
     'Do not run the Mako preprocessor program.'),
    ('--no_preprocess',
     'Do not run the Preprocess preprocessor program.'),
    ('--mako_strict_undefined',
     'Make Mako report on undefined variables.'),
    ('--no_header_footer',
     'Do not include header and footer in (LaTeX and HTML) documents.'),
    ('--no_emoji', 'Remove all emojis.'),
    ('--runestone',
     'Make a RunestoneInteractive version of a Sphinx document.'),
    ('--max_bc_linelength=',
     """Strip lines in !bc environments that are longer than specified
(to prevent too long lines). Default: None (no length restriction)."""),
    ('--keep_pygments_html_bg',
     """Do not allow change of background in code blocks in HTML."""),
    ('--minted_latex_style=',
     """Specify the minted style to be used for typesetting code in LaTeX.
See pygmetize -L styles for legal names."""),
    ('--pygments_html_style=',
     """Specify the minted/pygments style to be used for typesetting code
in HTML.
Default: default (other values: monokai, manni, rrt, perldoc,
borland, colorful, murphy, trac, tango, fruity, autumn, emacs,
vim, pastie, friendly, native, see pygmentize -L styles).
none, no, off: turn off pygments to typeset computer code in HTML,
use plain <pre> tags.
highlight.js: use highlight.js syntax highlighting, not pygments."""),
    ('--pygments_html_linenos',
     """Turn on line numbers in pygmentized computer code in HTML.
(In LaTeX line numbers can be added via doconce subst or
doconce replace such that the verbatim environments get
the linenos=true parameter.)"""),
    ('--html_output=',
     'Alternative basename of files associated with the HTML format.'),
    ('--html_style=', """Name of theme for HTML style:
plain, blueish, blueish2, bloodish, tactile-black, tactile-red, rossant
solarized, solarized2_light, solarized2_dark,
bootstrap, bootswatch,
bootstrap_X,  X=bloodish, blue, bluegray, brown, cbc, FlatUI, red,
bootswatch_X, X=cerulean, cosmo, flatly, journal, lumen, readable,
                simplex, spacelab, united, yeti
                (dark:) amelia, cyborg, darkly, slate, spruce,
                superhero (demos at bootswatch.com)"""),
    ('--html_template=',
     """Specify an HTML template with header/footer in which the doconce
document is embedded. (Often preferred to run with --no_title)"""),
    ('--no_title', 'Comment out TITLE, AUTHOR, DATE.\nOften used with HTML templates.'),
    ('--html_code_style=',
     """off, inherit, or transparent: enable normal inline verbatim font
where foreground and background color is inherited from the
surroundnings (e.g., to avoid the red Boostrap color).
Default: on (use the css-specified typesetting of <pre> tags).
NOTE: the naming "html_code_style" is not optimal: it has nothing
to do with code block style, but the <code> tag for inline verbatim text
in the context of bootstrap css styles.
"""),
    ('--html_pre_style=',
     """off, inherit, or transparent: let code blocks inside <pre> tags have
foreground and background color inherited from the surroundnings.
Default: on (use the css-specified typesetting of <pre> tags).
This option is most relevant for Bootstrap styles to
avoid white background in code blocks inside colorful admons.
"""),
    ('--html_toc_depth=',
     """No of levels in the table of contents in HTML output. Default: 2 (includes subsections but not subsubsections)."""),
    ('--html_toc_indent=',
     """No of spaces for indentation of subsections in the table of
contents in HTML output. Default: 3 (0 gives toc as nested list
in Bootstrap-based styles)."""),
    ('--html_body_font=',
     """Specify HTML font for text body. =? lists available fonts."""),
    ('--html_heading_font=',
     """Specify HTML font for headings. =? lists available fonts."""),
    ('--html_video_autoplay=',
     """True for autoplay when HTML is loaded, otherwise False (default)."""),
    ('--html_admon=',
     """\
Type of admonition and color:
colors, gray, yellow, apricot, lyx, paragraph.
For html_style=bootstrap*,bootswatch*,
the two legal values are boostrap_panel, bootstrap_alert."""),
    ('--html_admon_shadow',
     'Add a shadow effect to HTML admon boxes (gray, yellow, apricot).'),
    ('--html_admon_bg_color=',
     'Background color of admon in HTML.'),
    ('--html_admon_bd_color=',
     'Boundary color of admon in HTML.'),
    ('--css=',
     """Specify a .css style file for HTML output.
If the file does not exist, the default or specified style
(--html_style=) is written to it."""),
    ('--html_box_shadow',
     'Add a shadow effect in HTML box environments.'),
    ('--html_exercise_icon=',
     """Specify a question icon (as a filename in the bundled/html_images
directory in the doconce repo) for being inserted to the right in exercises.
default: turn on predefined question icons according to the chosen style.
none: no icons (this is the default value)."""),
    ('--html_exercise_icon_width=',
     """Width of the icon image in pixels (must be used with --html_exercise_icon)."""),
    ('--html_raw_github_url=', """URLs to files hosted on the doconce github account.
Internet Explorer (and perhaps other browsers) will not show raw.github.com
files. Instead on should use rawgit.com. For development of HTML sites
in Safari and Chrome and can use rawgit.com.

Values of --html_raw_github_url=:
safe or cdn.rawgit: use this for ready-made sites with potentially some traffic.
The URL becomes https://cdn.rawgit.com/hplgit/doconce/...

test or rawgit: use this for test purposes and development with low traffic.
The URL becomes https://rawgit.com/hplgit/doconce/...

github or raw.github: the URL becomes https://raw.github.com and may fail to
load properly.

githubusercontent or raw.githubusercontent: The URL becomes
https://raw.githubusercontent.com and may fail to load properly.
"""),
    ('--html_DOCTYPE', """Insert <!DOCTYPE HTML> in the top of the HTML file.
This is required for Internet Explorer and Mozilla.
However, some of the CSS files used by DocOnce may not load properly if
they are not well formed. That is why no doctype is default in the
generated HTML files."""),
    ('--html_links_in_new_window',
     """Open HTML links in a new window/tab."""),
    ('--html_quiz_button_text=',
     """Text on buttons for collapsing/expanding answers and explanations
in quizzes (with bootstrap styles).
Default: Empty (just pencil glyphion)."""),
    ('--html_bootstrap_navbar=',
     'Turns the Bootstrap navigation bar on/off. Default: on.'),
    ('--html_bootstrap_jumbotron=',
     """Turns the Bootstrap jumbotron intro on/off and governs the
size of the document title. Default: on. Other values: h2, off
(h2 gives h2 heading instead of h1, off gives no jumbotron)."""),
    ('--html_figure_hrule=', """Set horizontal rule(s) above and/or below a figure.
none, off: no rules
top: rule at top (default)
bottom: rule at bottom
top+bottom: rule at top and bottom"""),
    ('--device=',
     """Set device to paper, screen, or other (paper impacts LaTeX output)."""),
    ('--number_all_equations',
     """Switch latex environments such that all equations get a number."""),
    ('--denumber_all_equations',
     """Switch latex environments such no equations get a number (useful for removing equation labels in slides). Error messages are issued about references to numbered equations in the text."""),
    ('--latex_style=',
     """LaTeX style package used for the document.
std: standard LaTeX article or book style,
Springer_lncse: Springer's Lecture Notes in Computational Science and
   Engineering (LNCSE) style,
Springer_llncs: Springer's Lecture Notes in Computer Science style,
Springer_T2: Springer's T2 book style,
Springer_collection: Springer's style for chapters in LNCSE proceedings,
Korma_Script: Korma Script style,
siamltex: SIAM's standard LaTeX style for papers,
siamltexmm: SIAM's extended (blue) multimedia style for papers."""),
    ('--latex_font=',
     """LaTeX font choice: helvetica, palatino, std (Computer Modern, default)."""),
    ('--latex_code_style=', """Typesetting of code blocks.
pyg: use pygments (minted), style is set with --minted_latex_style=
lst: use lstlistings
vrb: use Verbatim (default)

Specifications across languages:
pyg-blue1
lst, lst-yellowgray[style=redblue]
vrb[frame=lines,framesep=2.5mm,framerule=0.7pt]

Detailed specification for each language:
default:vrb-red1[frame=lines]@pycod:lst[style=redblue]@pypro:lst-blue1[style=default]@sys:vrb[frame=lines,label=\\fbox{{\\tiny Terminal}},framesep=2.5mm,framerule=0.7pt]

Here, Verbatim[frame=lines] is used for all code environments, except
pycod, pypro and sys, which have their own specifications.
pycod: lst package with redblue style (and white background)
pypro: lst package with default style and blue1 background
style, sys: Verbatim with the specified arguments and white background.

(Note: @ is delimiter for the language specifications, syntax is
envir:package-background[style parameters]@)
"""),
    ('--latex_code_leftmargin=', 'Sets the left margin in code blocks. Default: 7 (mm).'),
    ('--latex_code_bg=', 'Background color code blocks. Default: white.'),
    ('--latex_code_lststyles=', """Filename with LaTeX definitions of lst styles."""),
    ('--latex_bibstyle=',
     'LaTeX bibliography style. Default: plain.'),
    ('--section_numbering=',
     'Turn section numbering on/off. Default: off for all formats except latex and pdflatex (on for those).'),
    ('--latex_table_format=',
     'Default: quote. Other values: left, center, footnotesize, tiny.'),
    ('--latex_title_layout=',
     """Layout of the title, authors, and date:
std: traditional LaTeX layout,
titlepage: separate page,
doconce_heading (default): authors with "footnotes" for institutions,
beamer: layout for beamer slides."""),
    ('--latex_title_reference=', """latex code placed in a footnote for the title,
typically used for acknowledging publisher/source of original
version of the document."""),
    ('--latex_encoding=', 'Encoding for \\usepackage[encoding]{inputenc}.\nValues: utf8 (default) or latin1.'),
    ('--latex_papersize=',
     """Geometry of page size: a6, a4, std (default)."""),
    ('--latex_list_of_exercises=',
    """LaTeX typesetting of list of exercises:
loe: special, separate list of exercises,
toc: exercises included as part of the table of contents,
none (default): no list of exercises."""),
    ('--latex_movie=',
     """Specify package for handling movie/video content.
Default: href (hyperlink to movie file).
Other options: media9, movie15, multimedia (Beamer's \\movie command)."""),
    ('--latex_movie_controls=',
     'Specify control panel for movies. Default: on. Other options: off.'),
    ('--latex_external_movie_viewer',
     'Allow external movie viewer for movie15 package.'),
    ('--latex_fancy_header',
     """Typesetting of headers on each page:
If article: section name to the left and page number to the right
on even page numbers, the other way around on odd page numners.
If book: section name to the left and page numner to the right
on even page numbers, chapter name to the right and page number to
the left on odd page numbers."""),
    ('--latex_section_headings=',
"""Typesetting of title/section/subsection headings:
std (default): standard LaTeX,
blue: gray blue color,
strongblue: stronger blue color,
gray: white text on gray background, fit to heading width,
gray-wide: white text on gray background, wide as the textwidth."""),
    ('--latex_colored_table_rows=',
     """Colors on every two line in tables: no (default), gray, blue."""),
    ('--latex_line_numbers',
     """Include line numbers for the running text (only active if there
are inline comments."""),
    ('--latex_todonotes',
     """Use the todonotes package to typeset inline comments.
Gives colored bubbles in the margin for small inline comments and
in the text for larger comments."""),
    ('--latex_double_spacing',
     """Sets the LaTeX linespacing to 1.5 (only active if there are
inline comments)."""),
    ('--latex_labels_in_margin',
     """Print equation, section and other LaTeX labels in the margin."""),
    ('--latex_index_in_margin',
     'Place entries in the index also in the margin.'),
    ('--latex_preamble=',
     """User-provided LaTeX preamble file, either complete or additions
to the doconce-generated preamble."""),
    ('--latex_no_program_footnotelink',
     """If --device=paper, this option removes footnotes with links to
computer programs."""),
    ('--latex_admon=',
     """Type of admonition in LaTeX:
colors1:
(inspired by the NumPy User Guide) applies different colors
for the different admons with an embedded icon,

colors2:
like `colors1` but the text is wrapped around the icon,

mdfbox:
rounded boxes with a optional title and no icon (default),

graybox2:
box with square corners, gray background, and narrower
than mdfbox, if code it reduces to something like mdfbox
(mdframed based); the summary admon is in case of A4 format
only half of the text width with text wrapped around
(effective for proposals and articles),

grayicon:
box with gray icons and a default light gray background,

yellowicon:
box yellow icons and a default light yellow background,

paragraph:  plain paragraph with boldface heading.

Note: the colors in mdfbox and other boxes can customized.
"""),
    ('--latex_admon_color=',
     """The color to be used as background in admonitions.
Either rgb tuple or saturated color a la yellow!5:
  --latex_admon_color=0.1,0.1,0.4
 '--latex_admon_color=yellow!5'
Note the quotes, needed for bash, in the latter example.

If --latex_admon=mdfbox, the background of the title and
the color of the border of box can also be customized by
direct editing. For example, a dark blue border and light
blue title background is obtained by editing the .tex file as

doconce replace 'linecolor=black,' 'linecolor=darkblue,' mydoc.tex
doconce subst 'frametitlebackgroundcolor=.*?,' 'frametitlebackgroundcolor=blue!5,' mydoc.tex
"""),
    ('--latex_admon_title_no_period',
     """By default, a period is added to title admons that do not have a period, question mark, or similar. This option prevents adding a period such that the title acts like a heading."""),
    ('--latex_admon_envir_map=',
     """Mapping of code envirs to new envir names inside admons, e.g.,
to get a different code typesetting inside admons. This is useful
if admons have a special color and the color background of code
blocks does not fit will with the color background inside admons.
Then it is natural to use a different verbatim code style inside
admons.
If specifying a number, say 2, as in --latex_admon_envir_map=2,
an envir like pycod gets the number appended: pycod2. One can
then in doconce ptex2tex (or ptex2tex) specify the typesetting
of pycod2 environments.
Otherwise the specification must be a mapping for each envir
that should be changed inside the admons:
--latex_admon_envir_map=pycod-pycod_yellow,fpro-fpro2
(from-to,from-to,... syntax)."""),
    ('--latex_exercise_numbering=',
     """absolute: exercises numbered as 1, 2, ...
chapter: exercises numbered as 1.1, 1.2, ... , 3.1, 3.2, etc.
         with a chapter prefix."""),
    ('--latex_subex_header_postfix=',
     """Default: ).
Gives headers a), b), etc. Can be set to period, colon, etc."""),
    ('--xelatex', 'Use xelatex instead of latex/pdflatex.'),
    ('--latex_double_hyphen',
     """Replace single dash - by double dash -- in LaTeX output.
Somewhat intelligent, but may give unwanted edits. Use with great care!"""),
    ('--latex_elsevier_journal=',
     """Sets the journal name for the --latex_style=elsevier style.
Default: none (no journal name)."""),
    ('--ipynb_admon=',
     """\
Typesetting of admonitions and quotes.
quote: as Markdown quote (default) with gray line on the left.
paragraph: just the content with the title as paragraph heading."""),
    ('--ipynb_figure=', """\
How to typeset figures in ipynb:
md (plain Markdown syntax),
imgtag (<img src="..." width=...> tag, default)
Image (python cell with Image object)."""),
    ('--ipynb_movie=', """\
How to typeset movies in ipynb:
md (plain Markdown syntax, default)
HTML (python cell with HTML object containing the code that is used
in the HTML format)
HTML-YouTubeVideo: If YouTube video, use YouTubeVideo object, otherwise
use the HTML object with appropriat HTML code.
local: local video files with encoding."""),
    ('--verbose',
     'Write out all OS commands run by doconce.'),
    ('--examples_as_exercises',
     """Treat examples of the form "==== Example: ..."
as in exercise environments."""),
    ('--solutions_at_end',
     'Place solutions to exercises at the end of the document.'),
    ('--without_solutions',
     'Leave out solution environments from exercises.'),
    ('--without_answers',
     'Leave out answer environments from exercises.'),
    ('--without_hints',
     'Leave out hints from exercises.'),
    ('--wordpress',
     'Make HTML output for wordpress.com pages.'),
    ('--tables2csv',
     """Write each table to a CSV file table_X.csv,
where X is the table number (autonumbered in according to
appearance in the DocOnce source file)."""),
    ('--sections_up',
     """Upgrade all sections: sections to chapters, subsections
to sections, etc."""),
    ('--sections_down',
     """Downgrade all sections: chapters to sections, sections
to subsections, etc."""),
    ('--os_prompt=',
     """Terminal prompt in output from running OS commands (the
@@@OSCMD instruction). None or empty: no prompt, just the command;
nocmd: no command, just the output. Default is "Terminal>"."""),
    ('--code_prefix=',
     'Prefix all @@@CODE imports with some path.'),
    ('--figure_prefix=',
     'Prefix all figure filenames with, e.g., an URL.'),
    ('--movie_prefix=',
     'Prefix all movie filenames with, e.g., an URL.'),
    ('--no_mp4_webm_ogg_alternatives',
     """Use just the specified (.mp4, .webm, .ogg) movie file;
do not allow alternatives in HTML5 video tag.
Used if the just the specified movie format should be played."""),
    ('--handout',
     'Makes slides output suited for printing.'),
    ('--urlcheck',
     'Check that all URLs referred to in the document are valid.'),
    ('--labelcheck=',
     'Check that all ref{X} has a corresponding label{X}. Fake examples will fail this check and so will generalized references.\nTurn on when useful. Values: off (default), on.'),
    ('--short_title=',
     "Short version of the document's title."),
    ('--markdown',
     'Allow Markdown (and some Extended Markdown) syntax as input.'),
    ('--md2do_output=',
     """Dump to file the DocOnce code arising from converting from
Markdown. Default value is None (no dump).
Any filename can be specified: --md2do_output=myfile.do.txt"""),
    ('--github_md',
     'Turn on github-flavored-markdown dialect of the pandoc translator'),
    ('--strapdown',
     """Wrap Markdown output in HTML header/footer such that the
output file (renamed as .html) can automatically be rendered as
an HTML via strapdownjs.com technology. Combine with --github_md
for richer output. Styles are set with --bootswatch_theme=cyborg
(for instance)."""),
    ('--bootswatch_theme=', 'Bootswatch theme for use with --strapdown option.'),
    ('--strict_markdown_output', 'Ensure strict/basic Markdown as output.'),
    ('--multimarkdown_output', 'Allow MultiMarkdown as output.'),
    ('--quiz_question_prefix=', """\
Prefix/title before question in quizzes. Default: "Question:".
Can also be set in square brackets for each individual question.
("Q: [] What is 1+1?"
results in no prefix/title before the "What is 1+1?"."""),
    ('--quiz_choice_prefix=', """\
Prefix/title before choices in quizzes.
Default for HTML: "Choice", resulting in numbered choices
"Choice 1:", "Choice 2:", etc.
A value with colon, period, or question mark (e.g., "Answer:")
leaves out the numbering.
Default for latex/pdflatex: letter or letter+checkbox.
Other values: number, number+checkbox, number+circle, letter+circle,
letter.
The checkbox or circle is always omitted if answers or solutions are
included (i.e., if none of the --without_answers and
--without_solutions is set).
The choice prefix can also be set in square brackets for each
individual choice.
("Cr: [] Two"
results in no prefix/title before the the answer "Two".
"""),
    ('--quiz_horizontal_rule=',
     'on (default): <hr> before and after quiz in HTML. off: no <hr>.'),
    ('--quiz_explanations=',
     """on/off
(some output formats do not support explanations with figures,
math and/or code, this option turns all explanations off."""),
    ('--rst_uio',
     'Univ. of Oslo version of rst files for their Vortex system.'),
    ('--rst_mathjax',
     'Use raw HTML with MathJax for LaTeX mathematics in rst files.'),
    ('--sphinx_keep_splits',
     """Respect user's !split commands. Default: Override user's !split
and insert new !split before all topmost sections. This is what
makes sense in a Sphinx Table of Contents if one wants to split
the document into multiple parts."""),
    ('--oneline_paragraphs',
     'Combine paragraphs to one line (does not work well).'),
    ]

_legal_command_line_options = \
      [opt for opt, help in _registered_command_line_options]

def get_legal_command_line_options():
    """Return list of legal command-line options."""
    return _legal_command_line_options

def help_format():
    print """
doconce format X doconcefile

where X can be any of the formats
html, latex, pdflatex, rst, sphinx, plain, gwiki, mwiki, cwiki,
pandoc, epytext.
"""
    for opt, help in _registered_command_line_options:
        if opt.endswith('='):
            opt += '...'
        print '\n%s\n\n%s\n' % (opt, help)

# Import options from config file instead of the command line
try:
    import doconce_config
    # Above module must do from doconce.doconce_config_default import *
except ImportError:
    # No doconce_config module, rely on this package's default
    import doconce_config_default as doconce_config

# Challenge: want different doconce_config files: just
# use different dirs and have one local in each
# or have system wide directories that one adjusts in PYTHONPATH


def option(name, default=None):
    """
    Return value of command-line option with the given name.
    If name ends with a = (as in ``--name=value``), return the value,
    otherwise return True or False whether the option ``--name``
    is found or not. If value of `default` is returned
    in case the option was not found.
    """
    # Note: Do not use fancy command-line parsers as much functionality
    # is dependent on command-line info (preprocessor options for instance)
    # that is not compatible with simple options( --name).

    option_name = '--' + name
    if not option_name in _legal_command_line_options:
        print 'test for illegal option:', option_name
        _abort()

    # Check if a command-line option has dash instead of underscore,
    # which is a common mistake
    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            if '=' in arg:
                arg = arg.split('=')[0] + '='
            if arg not in _legal_command_line_options and \
              ('--' + arg[2:].replace('-', '_')) in _legal_command_line_options:
                print 'found option %s, should be %s' % \
                      (arg, '--' + arg[2:].replace('-', '_'))
                _abort()

    value = None  # initialization

    # Check if name is in configuration file (doconce_config)
    # and get a default value from there
    name_dash2underscore = name.replace('-', '_')
    if hasattr(doconce_config, name_dash2underscore):
        value = getattr(doconce_config, name_dash2underscore)

    # Let the user's default value override that in the config file
    if default is not None:
        value = default

    # Finally, let the command line override everything
    if option_name.endswith('='):
        for arg in sys.argv[1:]:
            if arg.startswith(option_name):
                parts = arg.split('=')
                opt = parts[0]
                value = '='.join(parts[1:])
                break
    elif option_name in sys.argv:
        value = True

    return value

def check_command_line_options(option_start):
    # Error handling: check if all command-line options are of known types
    for arg in sys.argv[option_start:]:
        arg_user = arg
        if '=' in arg:
            arg = arg.split('=')[0] + '='
        if arg[:2] == '--':
            if not arg in _legal_command_line_options:
                print '*** warning: unrecognized command-line option'
                print '   ', arg_user


def misc_option(name, default=None):
    """
    As option, but for options related to other doconce programs
    than doconce format.
    """
    option_name = '--' + name
    value = default
    if option_name.endswith('='):
        for arg in sys.argv[1:]:
            if arg.startswith(option_name):
                parts = arg.split('=')
                opt = parts[0]
                value = '='.join(parts[1:])
                break
    elif option_name in sys.argv:
        value = True
    return value

def _abort():
    if '--no_abort' in sys.argv:
        print 'avoided abortion because of --no-abort'
    else:
        print 'Abort! (add --no_abort on the command line to avoid this abortion)'
        sys.exit(1)

def system(cmd, abort_on_failure=True, verbose=False, failure_info=''):
    """
    Run OS command cmd.
    If abort_on_failure: abort when cmd gives failure and print
    command and failure_info (to explain what the command does).
    If verbose: print cmd.
    """
    if verbose or '--verbose' in sys.argv:
        print 'running', cmd
    failure = os.system(cmd)
    if failure:
        print 'could not run', cmd, failure_info
        if abort_on_failure:
            _abort()
    return failure

def remove_verbatim_blocks(text, format):
    if format in ("latex", "pdflatex"):
        envirs = r'([Vv]erbatim|minted|lstlisting|latex|tex)'
        pattern = r'^\\begin\{%s\}.*^\\end\{%s\}' % (envirs, envirs)
        text = re.sub(pattern, '', text, flags=re.MULTILINE|re.DOTALL)
        # Do not remove comments too (they are actively used when searching
        # text returned from this function)
        ##text = re.sub(r'(?<=[^!?@|\\])%.*', '', text)
        return text


def recommended_html_styles_and_pygments_styles():
    """
    List good combinations of HTML slide styles and
    pygments styles for typesetting code.
    """
    combinations = {
        'html': {
            'blueish': ['default'],
            'bloodish': ['default'],
            'solarized': ['perldoc'],
            'solarized2': ['perldoc'],
            'solarized3': ['perldoc'],
            'solarized3_dark': ['native'],
            },
        'deck': {
            'neon': ['fruity', 'native'],
            'sandstone.aurora': ['fruity'],
            'sandstone.dark': ['native', 'fruity'],
            'sandstone.mdn': ['fruity'],
            'sandstone.mightly': ['default', 'autumn', 'manni', 'emacs'],
            'beamer': ['autumn', 'perldoc', 'manni', 'default', 'emacs'],
            'mnml': ['default', 'autumn', 'manni', 'emacs'],
            'sandstone.firefox': ['default', 'manni', 'autumn', 'emacs'],
            'sandstone.default': ['perldoc', 'autumn', 'manni', 'default'],
            'sandstone.light': ['emacs', 'autumn'],  # purple
            'swiss': ['autumn', 'default', 'perldoc', 'manni', 'emacs'],
            'web-2.0': ['autumn', 'default', 'perldoc', 'emacs'],
            'cbc': ['default', 'autumn'],
            },
        'reveal': {
            'beige': ['perldoc',],
            'beigesmall': ['perldoc',],
            'solarized': ['perldoc',],
            'serif': ['perldoc'],
            'simple': ['autumn', 'default', 'perldoc'],
            'blood': ['monokai', 'native'],
            'sky': ['default'],
            'moon': ['fruity', 'native'],
            'night': ['fruity', 'native'],
            'moon': ['fruity', 'native'],
            'darkgray': ['native', 'monokai'],
            'cbc': ['default', 'autumn'],
            'simula': ['autumn', 'default'],
            },
        'csss': {
            'csss_default': ['monokai'],
            },
        'dzslides': {
            'dzslides_default': ['autumn', 'default'],
            },
        'html5slides': {
            'template-default': ['autumn', 'default'],
            'template-io2011': ['autumn', 'default'],
            },
        'remark': {
            'light': ['autumn', 'default'],
            'dark': ['native', 'monokai'],
            },
        }
    return combinations

# -------------- functions used by the doconce program -------------

def remove_inline_comments():
    try:
        filename = sys.argv[1]
    except IndexError:
        print 'Usage: doconce remove_inline_comments myfile.do.txt'
        _abort()

    if not os.path.isfile(filename):
        print '*** error: file %s does not exist!' % filename
        sys.exit(1)

    shutil.copy(filename, filename + '.old~~')
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    import doconce
    filestr = doconce.subst_away_inline_comments(filestr)
    f = open(filename, 'w')
    f.write(filestr)
    f.close()
    print 'inline comments removed in', filename

def apply_inline_edits():
    try:
        filename = sys.argv[1]
    except IndexError:
        print 'Usage: doconce apply_inline_comments_edits myfile.do.txt'
        _abort()

    if not os.path.isfile(filename):
        print '*** error: file %s does not exist!' % filename
        sys.exit(1)

    shutil.copy(filename, filename + '.old~~')
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    # pattern is taken as INLINE_TAGS['inlinecomment'] but with
    # modified names and comments patterns.
    # 1. Replacements
    pattern = r'''\[(?P<name>[A-Za-z0-9 '+-]+?):(?P<space>\s+)(?P<subst>[^\]]+?) -> (?P<replacement>.+?)\]'''
    filestr = re.sub(pattern, r'\g<replacement>', filestr, flags=re.DOTALL)
    # 2. Deletes
    pattern = r'''\[del:\s+(.*?)\]'''
    filestr = re.sub(pattern, '', filestr, flags=re.DOTALL)
    # 3. Adds
    pattern = r'''\[add:\s+(.*?)\]'''
    filestr = re.sub(pattern, r'\g<1>', filestr, flags=re.DOTALL)

    f = open(filename, 'w')
    f.write(filestr)
    f.close()
    print 'inline comments removed in', filename

def latin2html():
    """
    Substitute latin characters by their equivalent HTML encoding
    in an HTML file. See doconce.html.latin2html for more
    documentation.
    """
    from doconce.html import latin2html
    import os, shutil, sys
    for filename in sys.argv[1:]:
        if not os.path.isfile(filename):
            print '*** error: file %s does not exist!' % filename
            continue
        oldfilename = filename + '.old~~'
        shutil.copy(filename, oldfilename)
        print 'transformin latin characters to HTML encoding in', filename
        f = open(oldfilename, 'r')
        try:
            text = f.read()
            newtext = latin2html(text)
            f.close()
            f = open(filename, 'w')
            f.write(newtext)
            f.close()
        except Exception, e:
            print e.__class__.__name__, ':', e,

def gwiki_figsubst():
    try:
        gwikifile = sys.argv[1]
        URLstem = sys.argv[2]
    except IndexError:
        print 'Usage: %s wikifile URL-stem' % sys.argv[0]
        print 'Ex:    %s somefile.gwiki http://code.google.com/p/myproject/trunk/doc/somedir' % sys.argv[0]
        _abort()

    if not os.path.isfile(gwikifile):
        print '*** error: file %s does not exist!' % gwikifile
        sys.exit(1)

    # first grep out all filenames with local path:
    shutil.copy(gwikifile, gwikifile + '.old~~')
    f = open(gwikifile, 'r')
    fstr = f.read()
    f.close()

    pattern = r'\(the URL of the image file (.+?) must be inserted here\)'
    #figfiles = re.findall(pattern, fstr)
    replacement = r'%s/\g<1>' % URLstem
    fstr, n = re.subn(pattern, replacement, fstr)
    pattern = re.compile(r'<wiki:comment>\s+Put the figure file .*?</wiki:comment>', re.DOTALL)
    fstr, n2 = pattern.subn('', fstr)
    f = open(gwikifile, 'w')
    f.write(fstr)
    f.close()
    print 'Replaced %d figure references in' % n, gwikifile
    if n != n2:
        print 'Something strange: %d fig references and %g comments... Bug.' % \
              (n, n2)



# subst is taken from scitools
def _usage_subst():
    print 'Usage: doconce subst [-s -m -x --restore] pattern '\
          'replacement file1 file2 file3 ...'
    print '--restore brings back the backup files'
    print '-s is the re.DOTALL or re.S modifier'
    print '-m is the re.MULTILINE or re.M modifier'
    print '-x is the re.VERBODE or re.X modifier'

def _scitools_subst(patterns, replacements, filenames,
                    pattern_matching_modifiers=0):
    """
    Replace a set of patterns by a set of replacement strings (regular
    expressions) in a series of files.
    The function essentially performs::

      for filename in filenames:
          file_string = open(filename, 'r').read()
          for pattern, replacement in zip(patterns, replacements):
              file_string = re.sub(pattern, replacement, file_string)

    A copy of the original file is taken, with extension `.old~~`.
    """
    # if some arguments are strings, convert them to lists:
    if isinstance(patterns, basestring):
        patterns = [patterns]
    if isinstance(replacements, basestring):
        replacements = [replacements]
    if isinstance(filenames, basestring):
        filenames = [filenames]

    # pre-compile patterns:
    cpatterns = [re.compile(pattern, pattern_matching_modifiers) \
                 for pattern in patterns]
    modified_files = dict([(p,[]) for p in patterns])  # init
    messages = []   # for return info

    for filename in filenames:
        if not os.path.isfile(filename):
            print '*** error: file %s does not exist!' % filename
            continue
        f = open(filename, 'r');
        filestr = f.read()
        f.close()

        for pattern, cpattern, replacement in \
            zip(patterns, cpatterns, replacements):
            if cpattern.search(filestr):
                filestr = cpattern.sub(replacement, filestr)
                shutil.copy2(filename, filename + '.old~~') # backup
                f = open(filename, 'w')
                f.write(filestr)
                f.close()
                modified_files[pattern].append(filename)

    # make a readable return string with substitution info:
    for pattern in sorted(modified_files):
        if modified_files[pattern]:
            replacement = replacements[patterns.index(pattern)]
            messages.append('%s replaced by %s in %s' % \
                                (pattern, replacement,
                                 ', '.join(modified_files[pattern])))

    return ', '.join(messages) if messages else 'no substitutions'

def wildcard_notation(files):
    """
    On Unix, a command-line argument like *.py is expanded
    by the shell. This is not done on Windows, where we must
    use glob.glob inside Python. This function provides a
    uniform solution.
    """
    if isinstance(files, basestring):
        files = [files]  # ensure list when single filename is given
    if sys.platform[:3] == 'win':
        import glob, operator
        filelist = [glob.glob(arg) for arg in files]
        files = reduce(operator.add, filelist)  # flatten
    return files

def subst():
    if len(sys.argv) < 3:
        _usage_subst()
        sys.exit(0)

    from getopt import getopt
    optlist, args = getopt(sys.argv[1:], 'smx', ['restore'])
    if not args:
        print 'no filename(s) given'
        sys.exit(1)

    restore = False
    pmm = 0  # pattern matching modifiers (re.compile flags)
    for opt, value in optlist:
        if opt in ('-s',):
            if not pmm:  pmm = re.DOTALL
            else:        pmm = pmm|re.DOTALL
        if opt in ('-m',):
            if not pmm:  pmm = re.MULTILINE
            else:        pmm = pmm|re.MULTILINE
        if opt in ('-x',):
            if not pmm:  pmm = re.VERBOSE
            else:        pmm = pmm|re.VERBOSE
        if opt in ('--restore',):
            restore = True

    if restore:
        for oldfile in args:
            newfile = re.sub(r'\.old~~$', '', oldfile)
            if not os.path.isfile(oldfile):
                print '%s is not a file!' % oldfile; continue
            os.rename(oldfile, newfile)
            print 'restoring %s as %s' % (oldfile,newfile)
    else:
        pattern = args[0]; replacement = args[1]
        s = _scitools_subst(pattern, replacement,
                            wildcard_notation(args[2:]), pmm)
        print s  # print info about substitutions

# replace is taken from scitools
def _usage_replace():
    print 'Usage: doconce replace from-text to-text file1 file2 ...'

def replace():
    if len(sys.argv) < 4:
        _usage_replace()
        sys.exit(0)

    from_text = sys.argv[1]
    to_text = sys.argv[2]
    filenames = wildcard_notation(sys.argv[3:])
    for filename in filenames:
        if not os.path.isfile(filename):
            print '*** error: file %s does not exist!' % filename
            continue
        f = open(filename, 'r')
        text = f.read()
        f.close()
        if from_text in text:
            backup_filename = filename + '.old~~'
            shutil.copy(filename, backup_filename)
            print 'replacing %s by %s in' % (from_text, to_text), filename
            text = text.replace(from_text, to_text)
            f = open(filename, 'w')
            f.write(text)
            f.close()

def _usage_replace_from_file():
    print 'Usage: doconce replace_from_file file-with-from-to file1 file2 ...'

def replace_from_file():
    """
    Replace one set of words by another set of words in a series
    of files. The set of words are stored in a file (given on
    the command line). The data format of the file is

    word replacement-word
    word
    # possible comment line, recognized by starting with #
    word
    word replacement-word

    That is, there are either one or two words on each line. In case
    of two words, the first is to be replaced by the second.
    (This format fits well with the output of list_labels.)
    """
    if len(sys.argv) < 3:
        _usage_replace_from_file()
        sys.exit(0)

    fromto_file = sys.argv[1]
    f = open(fromto_file, 'r')
    fromto_lines = f.readlines()
    f.close()

    filenames = wildcard_notation(sys.argv[2:])

    for filename in filenames:
        f = open(filename, 'r')
        text = f.read()
        f.close()
        replacements = False
        for line in fromto_lines:
            if line.startswith('#'):
                continue
            words = line.split()
            if len(words) == 2:
                from_text, to_text = words

                if from_text in text:
                    backup_filename = filename + '.old~~'
                    shutil.copy(filename, backup_filename)
                    print 'replacing %s by %s in' % (from_text, to_text), filename
                    text = text.replace(from_text, to_text)
                    replacements = True
        if replacements:
            f = open(filename, 'w')
            f.write(text)
            f.close()

def _usage_expand_mako():
    print 'Usage: doconce expand_mnako mako_code_file.txt funcname mydoc.do.txt'

# This replacement function for re.sub must be global since expand_mako,
# where it is used, has an exec statement

def expand_mako():
    if len(sys.argv) < 4:
        _usage_expand_mako()
        sys.exit(0)

    mako_filename = sys.argv[1]
    funcname = sys.argv[2]
    filenames = wildcard_notation(sys.argv[3:])

    # Get mako function code
    f = open(mako_filename, 'r')
    mako_text = f.read()
    f.close()
    func_lines = []
    inside_func = False
    for line in mako_text.splitlines():
        if re.search(r'^\s*def\s+%s' % funcname, line):  # starts with funcname?
            inside_func = True
            func_lines.append(line)
        elif inside_func:
            if line == '' or line[0] == ' ':  # indented line?
                func_lines.append(line)
            else:
                inside_func = False

    funcname_text = '\n'.join(func_lines)
    print 'Extracted function %s from %s:\n' % (funcname, mako_filename), funcname_text
    print func_lines
    try:
        exec(funcname_text)
    except Exception as e:
        print '*** error: could not turn function code into a Python function'
        print e
        _abort()
        # Note: if funcname has FORMAT tests the exec will fail, but
        # one can make an alternative version of funcname in another file
        # where one returns preprocess # #if FORMAT in ... statements
        # in the returned text.

    # Substitute ${funcname(..., ..., ...)}
    pattern = r'(\$\{(%(funcname)s\s*\(.+?\))\})' % vars()

    for filename in filenames:
        # Just the filestem without .do.txt is allowed
        if not filename.endswith('.do.txt'):
            filename += '.do.txt'
        if not os.path.isfile(filename):
            print '*** error: file %s does not exist!' % filename
            continue
        f = open(filename, 'r')
        text = f.read()
        f.close()
        m = re.search(pattern, text, flags=re.DOTALL)
        if m:
            backup_filename = filename + '.old~~'
            shutil.copy(filename, backup_filename)
            print 'expanding mako function %s in' % funcname, filename
            calls = re.findall(pattern, text, flags=re.DOTALL)
            for mako_call, python_call in calls:
                try:
                    replacement = eval(python_call)
                except Exception as e:
                    print '*** error: could not run call\n%s' % python_call
                    _abort()
                text = text.replace(mako_call, replacement)

            f = open(filename, 'w')
            f.write(text)
            f.close()

def _usage_linkchecker():
    print 'Usage: doconce linkchecker file1.html|file1.do.txt|tmp_mako__file1.do.txt ...'
    print 'Check if URLs or links to local files in DocOnce or HTML files are valid.'

def linkchecker():
    if len(sys.argv) <= 1:
        _usage_linkchecker()
        sys.exit(0)
    from common import is_file_or_url
    prefix = '(file:///|https?://|ftp://)'
    pattern_html = r'href="(%s.+?)"' % prefix
    pattern_do = r'''"[^"]+?" ?:\s*"(%s.+?)"''' % prefix
    missing = []
    for filename in sys.argv[1:]:
        ext = os.path.splitext(filename)[1]
        if not ext in ('.html', '.htm', '.txt'):
            print '*** error: %s is not a DocOnce or HTML file' % filename
            continue
        f = open(filename, 'r')
        text = f.read()
        f.close()
        if filename.endswith('.do.txt'):
            pattern = pattern_do
        else:
            patterh = pattern_html
        links = re.findall(pattern, text, flags=re.IGNORECASE)
        missing.append([filename, []])
        for link in links:
            check = is_file_or_url(link, msg=None)
            if check in ('file', 'url'):
                print '%s:' % filename, link, 'exists as', check
            else:
                print '%s:' % filename, link, 'WAS NOT FOUND'
                missing[-1][1].append(link)
    for filename, missing_links in missing:
        if missing_links:
            print '\n\n*** missing links in %s:\n%s' % \
                  (filename, '\n'.join(['"%s"' % link
                                        for link in missing_links]))


def _dofix_localURLs(filename, exclude_adr):
    if os.path.splitext(filename)[1] != '.rst':
        print 'Wrong filename extension in "%s" - must be a .rst file' \
              % filename
        _abort()

    f = open(filename, 'r')
    text = f.read()
    f.close()
    """
    # This is for doconce format:
    link1 = r'''"(?P<link>[^"]+?)" ?:\s*"(?P<url>([^"]+?\.html?|[^"]+?\.txt|[^"]+?\.pdf|[^"]+?\.f|[^"]+?\.c|[^"]+?\.cpp|[^"]+?\.cxx|[^"]+?\.py|[^"]+?\.java|[^"]+?\.pl))"'''
    link2 = r'("URL"|"url"|URL|url) ?:\s*"(?P<url>.+?)"'
    groups1 = [(link, url) for link, url, url in re.findall(link1, text)]
    print groups1
    print groups2
    """
    link_pattern = r'<([A-Za-z0-9/._-]+?)>`_'
    links = re.findall(link_pattern, text)
    num_fixed_links = 0
    for link in links:
        if link in exclude_adr:
            print 'not modifying', link
            if link.endswith('htm') or link.endswith('html'):
                print 'Note: %s\n      is an HTML file that may link to other files.\n      This may require copying many files! Better: link to _static directly in the doconce document.' % link
            continue
        if not (link.startswith('http') or link.startswith('file:/') or \
            link.startswith('_static')):
            if os.path.isfile(link):
                if not os.path.isdir('_static'):
                    os.mkdir('_static')
                newlink = os.path.join('_static', os.path.basename(link))
                text = text.replace('<%s>' % link, '<%s>' % newlink)
                print 'fixing link to %s as link to %s' % \
                      (link, newlink)
                print '       copying %s to _static' % os.path.basename(link)
                shutil.copy(link, newlink)
                if link.endswith('htm') or link.endswith('html'):
                    print 'Note: %s\n      is an HTML file that may link to other files.\n      This may require copying many files! Better: link to _static directly in the doconce document.' % link
                num_fixed_links += 1
    if num_fixed_links > 0:
        os.rename(filename, filename + 'old~~')
        f = open(filename, 'w')
        f.write(text)
        f.close()
    return num_fixed_links


def _usage_sphinxfix_localURLs():
    print """\
Usage: doconce sphinxfix_localURLs file1.rst file2.rst ... -not adr1 adr2 ...

Each link to a local file, e.g., "link": "src/dir1/myfile.txt",
is replaced by a link to the file placed in _static:
"link": "_static/myfile.txt". The file myfile.txt is copied
from src/dir1 to _static. The user must later copy all _static/*
files to the _static subdirectory in the sphinx directory.
Note that local links to files in _static are not modified.

The modification of links is not always wanted. The -not adr1 adr2 makes
it possible to exclude modification of a set of addresses adr1, adr2, ...

Example: doconce sphinxfix_localURLs file1.rst file2.rst \
         -not src/dir1/mymod1.py src/dir2/index.html

The old files are available as file1.rst.old~~, file2.rst.old~~ etc.

Note that local links to HTML files which are linked to other local HTML
documents (say a Sphinx document) demand all relevant files to be
copied to _static. In such cases it is best to physically place
the HTML documents in _static and let the DocOnce document link
directly to _static.

In general, it is better to link to _static from the DocOnce document
rather than relying on the fixes in this script...
"""

def sphinxfix_localURLs():
    if len(sys.argv) < 2:
        _usage_sphinxfix_localURLs()
        sys.exit(0)

    # Find addresses to exclude
    idx = -1  # index in sys.argv for the -not option
    for i, arg in enumerate(sys.argv[1:]):
        if arg.endswith('-not'):
            idx = i+1
    exclude_adr = sys.argv[idx+1:] if idx > 0 else []
    if idx > 0:
       del sys.argv[idx:]

    for filename in sys.argv[1:]:
        if os.path.dirname(filename) != '':
            print 'doconce sphinxfix_localURLs must be run from the same directory as %s is located in' % filename
        num_fixed_links = _dofix_localURLs(filename, exclude_adr)
        if num_fixed_links > 0:
            print "\nYou must copy _static/* to the sphinx directory's _static directory"


def _usage_latex_exercise_toc():
    print 'Usage: doconce latex_exercise_toc myfile.do.txt ["List of exercises"]'
    print """
Can insert
# Short: My own short title
in the text of an exercise and this defines a short version of the
title of the exercise to be used in the toc table.
This is convenient when the automatic truncation of (long) titles
fails (happens if truncated in the middle of mathematical $...$
constructions). Any short title is appearing in the table exactly
how it is written, so this is also a method to avoid truncating
a title.
"""

def latex_exercise_toc():
    if len(sys.argv) < 2:
        _usage_latex_exercise_toc()
        sys.exit(0)
    dofile = sys.argv[1]
    if dofile.endswith('.do.txt'):
        dofile = dofile[:-7]
    exerfile = '.' + dofile + '.exerinfo'
    if not os.path.isfile(exerfile):
        print 'no file %s with exercises from %s found' % (exerfile, dofile)
        return

    f = open(exerfile, 'r')
    exer = eval(f.read())
    f.close()

    try:
        heading = sys.argv[2]
    except IndexError:
        # Build default heading from types of environments found
        import sets
        types_of_exer = sets.Set()
        for ex in exer:
            if ex['type'] != 'Example':
                types_of_exer.add(ex['type'])
        types_of_exer = list(types_of_exer)
        types_of_exer = ['%ss' % tp for tp in types_of_exer]  # plural
        types_of_exer = [tp for tp in sorted(types_of_exer)]  # alphabetic order
        if len(types_of_exer) == 1:
            types_of_exer = types_of_exer[0]
        elif len(types_of_exer) == 2:
            types_of_exer = ' and '.join(types_of_exer)
        elif len(types_of_exer) > 2:
            types_of_exer[-1] = 'and ' + types_of_exer[-1]
            types_of_exer = ', '.join(types_of_exer)
        heading = "List of %s" % types_of_exer
    latex = r"""
\clearpage %% pagebreak before list of exercises
\subsection*{%s}
\\begin{tabular}{lrll}
""" % heading
    max_title_length = 45
    for ex in exer:
        if ex['type'] == 'Example':
            continue
        title = ex['title']
        # Short title?
        short = ''
        for line in ex['text'].splitlines():
            m = re.search(r'#\s*[Ss]hort:\s*(.+)', line)
            if m:
                short = m.group(1).strip()
                title = short
                break
        if not short:
            # Truncate long titles
            if len(title) > max_title_length:
                words = title.split()
                title = []
                for word in words:
                    title.append(word)
                    if len(' '.join(title)) > max_title_length - 5:
                        title.append('...')
                        break
                title = ' '.join(title)
        title = title.replace('\\', '\\\\') # re.sub later swallows \
        latex += ex['type'] + ' & ' + str(ex['no']) + ' & ' + title
        if ex['label']:
            latex += r' & p.~\pageref{%s}' % ex['label']
        else:
            # Leave pageref empty
            latex += ' &'
        latex += ' \\\\\\\\' + '\n'
        # (need 8 \ for \\ to survive because re.sub below eats them)
    latex += r"""\end{tabular}
% --- end of table of exercises
\clearpage % pagebreak after list of exercises

"""
    ptexfile = dofile + '.p.tex'
    f = open(ptexfile, 'r')
    shutil.copy(ptexfile, ptexfile + '.old~~')
    filestr = f.read()
    f.close()
    if r'\tableofcontents' in filestr:
        # Insert table of exercises on the next line
        filestr = re.sub(r'(tableofcontents.*$)', '\g<1>\n' + latex,
                         filestr, flags=re.MULTILINE)
        f = open(ptexfile, 'w')
        f.write(filestr)
        print 'table of exercises inserted in', ptexfile
        f.close()
    else:
        print '*** error: cannot insert table of exercises because there is no'
        print '    table of contents requested in the', dofile, 'document'


def _usage_combine_images():
    print """\
Usage: doconce combine_images [pdf|png] [-4] image1 image2 ... output_file
Applies montage if not PDF or EPS images, else
pdftk, pdfnup and pdfcrop.
Images are combined with two each row, by default, but
doconce combine_images -3 ... gives 3 images in each row.
The first command-line argument can be a file extension and
the filenames can then be given without extension:

doconce combine_images pdf -2 u1 u2 u12
"""

def combine_images():

    if len(sys.argv) < 3:
        _usage_combine_images()
        sys.exit(0)

    if sys.argv[1] in ('pdf', 'png', 'jpg', 'eps', 'ps', 'jpeg', 'tif', 'tiff'):
        extension = sys.argv[1]
        del sys.argv[1]
    else:
        extension = None

    if sys.argv[1].startswith('-'):
        num_columns = int(sys.argv[1][1:])
        del sys.argv[1]
    else:
        num_columns = 2

    bitmap_formats = '.png', '.tif.', '.tiff', '.gif', '.jpeg', 'jpg'
    imagefiles = sys.argv[1:-1]
    # See if files have extension
    for i in range(len(imagefiles)):
        basename, ext = os.path.splitext(imagefiles[i])
        if not ext and extension is not None:
            imagefiles[i] = imagefiles[i] + '.' + extension

    for name in imagefiles:
        if not os.path.isfile(name):
            print '*** error: file "%s" is non-existing' % name
            _abort()
    output_file = sys.argv[-1]
    basename, ext = os.path.splitext(output_file)
    if not ext and extension is not None:
        output_file += '.' + extension

    ext = [os.path.splitext(f)[1] for f in imagefiles]
    montage = False
    # If one of the formats in formats: montage = True
    for format in bitmap_formats:
        if format in ext:
            montage = True

    cmds = []
    if montage:
        cmds.append('montage -background white -geometry 100%% -tile %dx %s %s' % (num_columns, ' '.join(imagefiles), output_file))
        cmds.append('convert -trim %s %s' % (output_file, output_file))

    else:
        # Assume all are .pdf or .eps
        # Convert EPS to PDF
        for i in range(len(imagefiles)):
            f = imagefiles[i]
            if '.eps' in f:
                cmds.append('ps2pdf -DEPSCrop %s' % f)
                imagefiles[i] = f.replace('.eps', '.pdf')

        # Combine PDF images
        num_rows = int(round(len(imagefiles)/float(num_columns)))
        cmds.append('pdftk %s output tmp.pdf' % ' '.join(imagefiles))
        cmds.append('pdfnup --nup %dx%d --outfile tmp.pdf tmp.pdf' % (num_columns, num_rows))
        cmds.append('pdfcrop tmp.pdf %s' % output_file)
        cmds.append('rm -f tmp.pdf')
    print
    for cmd in cmds:
        system(cmd, verbose=True)
    print 'output in', output_file


def _usage_expand_commands():
    print 'Usage: doconce expand_commands file1 file2 ...'
    print """
A file .expand_commands may define _replace and _regex_subst lists
for str.replace and re.sub substitutions (respectively) to be applied
to file1 file2 ...

By default we use some common LaTeX math abbreviations:
_replace = [
(r'\bals', r'\begin{align*}'),  # must appear before \bal
(r'\eals', r'\end{align*}'),
(r'\bal', r'\begin{align}'),
(r'\eal', r'\end{align}'),
(r'\beq', r'\begin{equation}'),
(r'\eeq', r'\end{equation}'),
]

_regex_subst = []
"""

def expand_commands():
    if len(sys.argv) < 2:
        _usage_expand_commands()
        sys.exit(0)

    # Default set of str.replace and re.sub substitutions
    _replace = [
    (r'\bals', r'\begin{align*}'),  # must appear before \bal
    (r'\eals', r'\end{align*}'),
    (r'\bal', r'\begin{align}'),
    (r'\eal', r'\end{align}'),
    (r'\beq', r'\begin{equation}'),
    (r'\eeq', r'\end{equation}'),
    ]

    # These \ep subst don't work properly
    _regex_subst = [
    (r'^\ep\n', r'\\thinspace .\n', re.MULTILINE),
    (r'\ep\n', r' \\thinspace .\n'),
    (r'\ep\s*\\\]', r' \\thinspace . \]'),
    (r'\ep\s*\\e', r' \\thinspace . \e'),
    (r' \\thinspace', 'thinspace'),
    ]
    _regex_subst = []

    expand_commands_file = '.expand_commands'
    if os.path.isfile(expand_commands_file):
        execfile(expand_commands_file)
    else:
        replace = []
        regex_subst = []
    # Add standard definitions (above)
    replace += _replace
    regex_subst += _regex_subst

    filenames = sys.argv[1:]
    for filename in filenames:
        changed = False
        f = open(filename, 'r')
        text = f.read()
        f.close()
        for from_, to_ in replace:
            if from_ in text:
                text = text.replace(from_, to_)
                print 'replacing %s by %s in %s' % (from_, to_, filename)
                changed = True
        for item in regex_subst:
            if len(item) == 2:
                from_, to_ = item
                if re.search(from_, text):
                    text = re.sub(from_, to_, text)
                    print 'substituting %s by %s in %s' % (from_, to_, filename)
                    changed = True
            elif len(item) == 3:
                frm_, to_, modifier = item
                if re.search(from_, text, flags=modifier):
                    text = re.sub(from_, to_, text, flags=modifier)
                    print 'substituting %s by %s in %s' % (from_, to_, filename)
                    changed = True
        if changed:
            shutil.copy(filename, filename + '.old~~')
            f = open(filename, 'w')
            f.write(text)
            f.close()


def copy_latex_packages(packages):
    """
    Copy less well-known latex packages to the current directory
    if the packages are not found on the (Unix) system.
    """
    datafile = latexstyle_files  # global variable (latex_styles.zip)
    missing_files = []
    import commands
    for style in packages:
        stem, ext = os.path.splitext(style)
        if ext == '':
            style += '.sty'
        failure, output = commands.getstatusoutput('kpsewhich %s' % style)
        if output == '':
            missing_files.append(style)
    if missing_files:
        # Copy zipfile with styles to current dir
        print '*** missing style files:'
        print '   ', ', '.join(missing_files)
        import doconce
        doconce_dir = os.path.dirname(doconce.__file__)
        doconce_datafile = os.path.join(doconce_dir, datafile)
        shutil.copy(doconce_datafile, os.curdir)
        import zipfile
    for filename in missing_files:
        # Extract file from zip archive
        if not os.path.isfile(filename):
            try:
                zipfile.ZipFile(datafile).extract(filename)
                msg = 'extracted'
            except:
                msg = 'could not extract'
            print '%s %s (from %s in the doconce installation)' % \
            (msg, filename, latexstyle_files)
    if os.path.isfile(datafile):
        os.remove(datafile)

def _usage_ptex2tex():
    print r"""\
Usage: doconce ptex2tex [file | file.p.tex] [-Dvar1=val1 ...] \
       [cod=\begin{quote}\begin{verbatim}@\end{verbatim}\end{quote} \
        pypro=Verbatim fcod=minted ccod=ans cpppro=anslistings:nt]'

or
       doconce ptex2tex file -Dvar1=val1 ... envir=ans:nt

or
       doconce ptex2tex file "sys=\begin{Verbatim}[frame=lines,label=\fbox{{\tiny Terminal}},framesep=2.5mm,framerule=0.7pt]@\end{Verbatim}" envir=minted --minted_leftmargin=2

(recall quotes in arguments with backslash), or

       doconce ptex2tex file envir=Verbatim

Here the Verbatim (from fancyvrb) is used for all environments, with
some options added (base linestretch 0.85 and font size 9pt).

The last command is equivalent to the default

   doconce ptex2tex


Note that specifications of how "!bc environment" is to be typeset
in latex is done by environment=begin@end, where begin is the latex
begin command, end is the latex end command, and the two must
be separated by the at sign (@). Writing just environment=package implies
the latex commands \begin{package} and \end{package}.

Choosing environment=minted gives the minted environment with
the specified language inserted. Similarly, environment=ans,
environment=ans:nt, environment=anslistings, or environment=anslistings:nt
imply the anslistings package with the right environment
(\begin{c++:nt} for instance for !bc cppcod or !bc cpppro,
environment=ans:nt - :nt means no title over the code box).

If environment is simply the string "envir", the value applies to all
registered environments. Specifying (e.g.) sys=... and then envir=ans,
will substitute the sys environment by the specified syntax and all
other environments will apply the latex construct from anslistings.sty.
"""

def ptex2tex():
    if len(sys.argv) <= 1:
        _usage_ptex2tex()
        sys.exit(0)

    filename = sys.argv[1]
    if filename.endswith('.p.tex'):
        filename = filename[:-6]
    if not os.path.isfile(filename + '.p.tex'):
        print 'no file %s' % (filename + '.p.tex')
        _abort()
    f = open(filename + '.p.tex', 'r')
    ptex2tex_filestr = f.read()
    f.close()

    # All envirs in the .ptex2tex.cfg file as of June 2012.
    # (Recall that the longest names must come first so that they
    # are substituted first, e.g., \bcc after \bccod)
    envirs = 'pro pypro cypro cpppro cpro fpro plpro shpro mpro cod pycod cycod cppcod ccod fcod plcod shcod mcod rst cppans pyans fans bashans swigans uflans sni dat dsni sys slin ipy pyshell rpy plin ver warn rule summ ccq cc ccl txt'.split()
    envirs += ['htmlcod', 'htmlpro', 'html',
               'rbpro', 'rbcod', 'rb',
               'xmlpro', 'xmlcod', 'xml',
               'latexpro', 'latexcod', 'latex']
    # envirs is not longer used - we just read what the user has in the file

    # Accept all envirs in envir2pygments, plus all
    # registered lexers in pygments
    from common import get_legal_pygments_lexers
    ptex2tex_begin_pattern = r'^\\b([a-z0-9+_]+)$'
    user_envirs = re.findall(ptex2tex_begin_pattern, ptex2tex_filestr,
                             flags=re.MULTILINE)

    # Process command-line options

    preprocess_options = []  # -Dvariable or -Dvariable=value
    envir_user_spec = []     # user's specified environments
    for arg in sys.argv[2:]:
        if arg.startswith('-D') or arg.startswith('-U'):
            preprocess_options.append(arg)
        elif '=' in arg:
            # envir
            items = arg.split('=')
            envir, value = items[0], '='.join(items[1:])
            if '@' in value:
                begin, end = value.split('@')

                if envir == 'envir':
                    # User specifies all ptex2tex environments at once
                    # as "envir=begin@end"
                    for e in user_envirs:
                        envir_user_spec.append((e, begin, end))
                else:
                    envir_user_spec.append((envir, begin, end))
            else:
                # Fix value=minted and value=ans*:
                # they need the language explicitly
                if value == 'minted':
                    envir2pygments = dict(
                        pyshell='python',
                        py='python', cy='cython', f='fortran',
                        c='c', cpp='c++', sh='bash', rst='rst',
                        m ='matlab', pl='perl', swig='c++',
                        latex='latex', html='html', js='js',
                        java='java',
                        xml='xml', rb='ruby', sys='console',
                        dat='text', txt='text', csv='text',
                        ipy='ipy', do='doconce',
                        # pyopt and pysc are treated in latex.py
                        )
                    # Find substitutes for ipy and doconce if these lexers
                    # are not installed
                    # (third-party repos, does not come with pygments, but
                    # warnings have been issued by doconce format, with
                    # URLs to where the code can be obtained)
                    from pygments.lexers import get_lexer_by_name
                    try:
                        get_lexer_by_name('ipy')
                    except:
                        envir2pygments['ipy'] = 'python'
                    try:
                        get_lexer_by_name('doconce')
                    except:
                        envir2pygments['do'] = 'text'

                    legal_lexers = get_legal_pygments_lexers()
                    for user_envir in user_envirs:
                        if user_envir in envir2pygments:
                            pass
                        elif user_envir in legal_lexers:
                            envir2pygments[user_envir] = user_envir

                    if envir == 'envir':
                        leftmargin = '7' # mm
                        for arg in sys.argv[1:]:
                            if arg.startswith('--minted_leftmargin='):
                                leftmargin = arg.split('=')[1]
                        for lang in envir2pygments:
                            # mathescape can be used with minted and lstlisting
                            # see http://tex.stackexchange.com/questions/149710/how-to-write-math-symbols-in-a-verbatim, minted can only have math in comments within the code
                            # but mathescape make problems with bash and $#
                            # (can perhaps be fixed with escapechar=... but
                            # I haven't found out)
                            if lang != 'sh':
                                begin = '\\' + 'begin{minted}[fontsize=\\fontsize{9pt}{9pt},linenos=false,mathescape,baselinestretch=1.0,fontfamily=tt,xleftmargin=%smm]{' % leftmargin + envir2pygments[lang] + '}'
                            else:
                                begin = '\\' + 'begin{minted}[fontsize=\\fontsize{9pt}{9pt},linenos=false,baselinestretch=1.0,fontfamily=tt,xleftmargin=%smm]{' % leftmargin + envir2pygments[lang] + '}'
                            end = '\\' + 'end{minted}'
                            envir_user_spec.append((lang, begin, end))
                    else:
                        for lang in envir2pygments:
                            if envir.startswith(lang + 'cod') or \
                               envir.startswith(lang + 'pro'):
                                begin = '\\' + 'begin{' + value + '}{' \
                                        + envir2pygments[lang] + '}'
                                end = '\\' + 'end{' + value + '}'
                                envir_user_spec.append((envir, begin, end))
                elif value.startswith('ans'):
                    # Mapping from code envirs to valid anslistings names
                    envir2listings = dict(
                        pyshell='python',
                        py='python', cy='python', f='fortran',
                        cpp='c++', sh='bash', swig='swigcode',
                        ufl='uflcode', m='matlab', c='c++',
                        latex='latexcode', xml='xml',
                        pyopt='python', ipy='python')
                    if envir == 'envir':
                        for lang in envir2listings:
                            language = envir2listings[lang]
                            if value.endswith(':nt'):
                                language += ':nt'
                            begin = '\\' + 'begin{' + language + '}'
                            end = '\\' + 'end{' + language + '}'
                            envir_user_spec.append((lang, begin, end))
                    else:
                        for lang in envir2listings:
                            if envir.startswith(lang + 'cod') or \
                               envir.startswith(lang + 'pro'):
                                lang = envir2listings[lang]
                                if value.endswith(':nt'):
                                    lang += ':nt'
                                begin = '\\' + 'begin{' + lang + '}'
                                end = '\\' + 'end{' + lang + '}'
                                envir_user_spec.append((envir, begin, end))
                else:
                    # value is not minted or ans*
                    options = ''
                    if value == 'Verbatim':
                        # provide lots of options
                        options = r'[numbers=none,fontsize=\fontsize{9pt}{9pt},baselinestretch=0.95,xleftmargin=0mm]'
                    elif value == 'Verbatim-0.85':
                        # provide lots of options
                        options = r'[numbers=none,fontsize=\fontsize{9pt}{9pt},baselinestretch=0.85,xleftmargin=0mm]'
                    elif value == 'Verbatim-indent':
                        options = r'[numbers=none,fontsize=\fontsize{9pt}{9pt},baselinestretch=0.95,xleftmargin=8mm]'

                    begin = '\\' + 'begin{' + value + '}' + options
                    end = '\\' + 'end{' + value + '}'
                    if envir == 'envir':
                        for e in user_envirs:
                            envir_user_spec.append((e, begin, end))
                    else:
                        envir_user_spec.append((envir, begin, end))

    # Find which environments that will be defined and which
    # latex packages that must be included.

    ans = ['c++', 'c', 'fortran', 'python', 'cython', 'xml',
           'bash', 'swigcode', 'uflcode', 'matlab', 'progoutput',
           'latexcode', 'anycode']
    ans = ans + [i+':nt' for i in ans]
    package2envir = dict(fancyvrb='Verbatim', anslistings=ans, minted='minted')
    latexenvir2package = {}
    for package in package2envir:

        if isinstance(package2envir[package], list):
            for latexenvir in package2envir[package]:
                latexenvir2package[latexenvir] = package
        else: # str
            latexenvir2package[package2envir[package]] = package
    #print 'envir_user_spec:' #
    #import pprint; pprint.pprint(envir_user_spec)
    #print 'latex2envir2package:'; pprint.pprint(latexenvir2package)
    # Run through user's specifications and grab latexenvir from
    # end = \end{latexenvir}, find corresponding package and add to set
    import sets
    packages = sets.Set()
    for envir, begin, end in envir_user_spec:
        m = re.search(r'\\end\{(.+?)\}', end)
        if m:
            latexenvir = m.group(1)
            if latexenvir in latexenvir2package:
                packages.add(latexenvir2package[latexenvir])
            else:
                print 'No package known for latex environment "%s" ' % latexenvir
    packages = list(packages)
    # fancyvrb is needed for \code{...} -> \Verb!...! translation
    if not 'fancyvrb' in packages:
        packages.append('fancyvrb')

    #print 'packages:';  pprint.pprint(packages)

    # Run preprocess
    if not preprocess_options:
        if 'minted' in packages:
            preprocess_options += ['-DMINTED']
    if '-DMINTED' in preprocess_options and 'minted' in packages:
        packages.remove('minted')  # nicer with just one \usepackage{minted}


    output_filename = filename + '.tex'
    cmd = 'preprocess %s %s > %s' % \
          (' '.join(preprocess_options),
           filename + '.p.tex',
           output_filename)
    system(cmd, failure_info="""
preprocess failed or is not installed;
download preprocess from http://code.google.com/p/preprocess""")

    # Mimic ptex2tex by replacing all code environments by
    # a plain verbatim command
    f = open(output_filename, 'r')
    filestr = f.read()
    f.close()

    # Replace the environments specified by the user
    from latex import fix_latex_command_regex
    for envir, begin, end in envir_user_spec:
        for postfix in ['cod', 'pro', '']:
            ptex2tex_begin = '\\' + 'b' + envir + postfix
            ptex2tex_end = '\\' + 'e' + envir + postfix
            begin_pattern = r'^\%s$' % ptex2tex_begin
            end_pattern = r'^\%s$' % ptex2tex_end
            if re.search(fix_latex_command_regex(begin_pattern),
                         filestr, flags=re.MULTILINE):
                filestr = re.sub(
                    begin_pattern,
                    fix_latex_command_regex(begin, application='replacement'),
                    filestr, flags=re.MULTILINE)
                filestr = re.sub(
                    end_pattern,
                    fix_latex_command_regex(end, application='replacement'),
                    filestr, flags=re.MULTILINE)
                print '%s (!bc %s) -> %s\n' % (ptex2tex_begin, envir, begin)

    # Replace other environments by a default choice
    begin = r"""\begin{Verbatim}[numbers=none,fontsize=\fontsize{9pt}{9pt},baselinestretch=0.95]"""
    end = r"""\end{Verbatim}"""
    #begin = r"""\begin{quote}\begin{verbatim}"""
    #end = r"""\end{verbatim}\end{quote}"""
    for envir in user_envirs:
        ptex2tex_begin = '\\' + 'b' + envir
        ptex2tex_end = '\\' + 'e' + envir
        begin_pattern = r'^\%s$' % ptex2tex_begin
        end_pattern = r'^\%s$' % ptex2tex_end
        if re.search(fix_latex_command_regex(begin_pattern),
                     filestr, flags=re.MULTILINE):
            filestr = re.sub(
                begin_pattern,
                fix_latex_command_regex(begin, application='replacement'),
                filestr, flags=re.MULTILINE)
            filestr = re.sub(
                end_pattern,
                fix_latex_command_regex(end, application='replacement'),
                filestr, flags=re.MULTILINE)
            print '%s (!bc %s) -> %s ("%s" is unsupported so we use Verbatim)\n' % (ptex2tex_begin, envir, begin, envir)

    # Make sure we include the necessary verbatim packages
    if packages:
        filestr = filestr.replace(r'\usepackage{ptex2tex}',
           r'\usepackage{%s} %% packages needed for verbatim environments' %
                                          (','.join(packages)))
    else:
        filestr = filestr.replace(r'\usepackage{ptex2tex}', '')

    # Copy less well-known latex packages to the current directory
    stylefiles = [name for name in ['minted', 'anslistings', 'fancyvrb']
                  if name in packages]
    # preprocess is run so we can check which less known packages
    # that are required
    less_known_packages = ['mdframed', 'titlesec',]  # more?
    #stylefiles += less_known_packages
    copy_latex_packages(stylefiles)


    if 'minted' in packages:
        failure, output = commands.getstatusoutput('pygmentize')
        if failure:
            print 'You have requested the minted latex style, but this'
            print 'requires the pygments package to be installed. On Debian/Ubuntu: run'
            print 'Terminal> sudo apt-get install python-pygments'
            print 'Or'
            print 'Terminal> hg clone http://bitbucket.org/birkenfeld/pygments-main pygments'
            print 'Terminal> cd pygments; sudo python setup.py install'
            _abort()

    filestr = replace_code_command(filestr)

    f = open(output_filename, 'w')
    f.write(filestr)
    f.close()
    print 'output in', output_filename

def replace_code_command(filestr):
    """Replace \code{...} by \Verb!...! or \textttt{...}."""

    # Remove one newline (two implies far too long inline verbatim)
    pattern = re.compile(r'\\code\{([^\n}]*?)\n(.*?)\}', re.DOTALL)
    # (this pattern does not handle \code{...} with internal } AND \n!)
    filestr = pattern.sub(r'\code{\g<1> \g<2>}', filestr)
    verb_command = 'Verb'  # requires fancyvrb package, otherwise use std 'verb'

    verb_delimiter = '!'
    alt_verb_delimiters = '?', '@', '|'  # can't use ~,%,#,$,^,&,* in latex headings
    cpattern = re.compile(r"""\\code\{(.*?)\}([ \n,.;:?!)"'-])""", re.DOTALL)
    # Check if the verbatim text contains verb_delimiter and make
    # special solutions for these first
    alt_verb_delimiter = None
    for verbatim, dummy in cpattern.findall(filestr):
        if verb_delimiter in verbatim:
            for delimiter in alt_verb_delimiters:
                if delimiter not in verbatim:
                    alt_verb_delimiter = delimiter
                    break
            if alt_verb_delimiter is None:
                alt_verb_delimiter = alt_verb_delimiters[0]
                print """
*** warning: inline verbatim "%s"
    contains all delimiters %s that the LaTeX
    command \\Verb can make use of - be prepared for strange output that
    requires manual editing (or use doconce replace/subst) of
    \\Verb%s%s%s
    or move this line verbatim expression to a code block !bc ... !ec.
""" % (verbatim, [verb_delimiter] + list(alt_verb_delimiter),
       alt_verb_delimiter, verbatim, alt_verb_delimiter)
            # Here one can have a problem in that verbatim contains
            # special regex chars such as $, \, ., etc. Use re.escape
            pattern = re.escape(r'\code{%s}' % verbatim) + r"""([ \n,.;:?!)"'-])"""
            replacement = r'\\%s%s%s%s\g<1>' % \
            (verb_command, alt_verb_delimiter, verbatim, alt_verb_delimiter)
            # Note: A previous occurence in cpattern.findall may have performed
            # this substitution
            filestr = re.sub(pattern, replacement, filestr, flags=re.DOTALL)
    # Exceptional cases are dealt with, proceed with the standard case
    filestr = cpattern.sub(r'\\%s%s\g<1>%s\g<2>' %
                           (verb_command, verb_delimiter, verb_delimiter),
                           filestr)

    '''
    # If fontsize is part of the \Verb command (which is not wise, since
    # explicit fontsize is not suitable for section headings),
    # first handle combination of \protect and \code
    fontsize = 10          # should be configurable from the command line
    cpattern = re.compile(r"""\\protect\s*\\code\{(.*?)\}([ \n,.;:?!)"'-])""", re.DOTALL)
    filestr = cpattern.sub(r'{\\fontsize{%spt}{%spt}\protect\\%s!\g<1>!}\g<2>' %
                           (fontsize, fontsize, verb_command), filestr)
    # Handle ordinary \code
    cpattern = re.compile(r"""\\code\{(.*?)\}([ \n,.;:?!)"'-])""", re.DOTALL)
    filestr = cpattern.sub(r'{\\fontsize{%spt}{%spt}\\%s!\g<1>!}\g<2>' %
                           (fontsize, fontsize, verb_command), filestr)
    '''
    # \Verb!...! does not cause linebreak in latex, therefore shift to \texttt{}
    # where possible since this will reduce overfull hboxes
    filestr = re.sub(r'\{\\Verb!([^{}_$\^#%&\\]+?)!\}',
                     r'\\texttt{\g<1>}', filestr)
    filestr = re.sub(r'\{\\protect\s*\\Verb!([^{}_$\^#%&\\]+?)!\}',
                     r'\\texttt{\g<1>}', filestr)
    return filestr

def _usage_grab():
    print 'Usage: doconce grab --from[-] from-text [--to[-] to-text] file'

def grab():
    """
    Grab a portion of text from a file, starting with from-text
    (included if specified as --from, not included if specified
    via --from-) up to the first occurence of to-text (--to implies
    that the last line is included, --to_ excludes the last line).
    If --to[-] is not specified, all text up to the end of the file
    is returned.

    from-text and to-text are specified as regular expressions.
    """
    if len(sys.argv) < 4:
        _usage_grab()
        sys.exit(0)

    filename = sys.argv[-1]
    if not sys.argv[1].startswith('--from'):
        print 'missing --from fromtext or --from_ fromtext option on the command line'
        _abort()
    from_included = sys.argv[1] == '--from'
    from_text = sys.argv[2]

    # Treat --to

    # impossible text (has newlines) that will never be found
    # is used as to-text if this is not specified
    impossible_text = '@\n\n@'
    try:
        to_included = sys.argv[3] == '--to'
        to_text = sys.argv[4]
    except IndexError:
        to_included = True
        to_text = impossible_text

    from_found = False
    to_found = False
    copy = False
    lines = []  # grabbed lines
    for line in open(filename, 'r'):
        m_from = re.search(from_text, line)
        m_to = re.search(to_text, line)
        if m_from and not from_found:
            copy = True
            from_found = True
            if from_included:
                lines.append(line)
        elif m_to:
            copy = False
            to_found = True
            if to_included:
                lines.append(line)
        elif copy:
            lines.append(line)
    if not from_found:
        print 'Could not find match for from regex "%s"' % from_text
        sys.exit(1)
    if not to_found and to_text != impossible_text:
        print 'Could not find match for to   regex "%s"' % to_text
        sys.exit(1)
    print ''.join(lines).rstrip()

def remove_text(filestr, from_text, from_included, to_text, to_included):
    """
    Remove a portion of text from the string filestr.
    See remove() for explanation of arguments.
    """
    impossible_text = '@\n\n@'  # must be compatible with remove()

    from_found = False
    to_found = False
    remove = False
    lines = []  # survived lines
    for line in filestr.splitlines():
        m_from = re.search(from_text, line)
        m_to = re.search(to_text, line)
        if m_from:
            remove = True
            from_found = True
            if not from_included:
                lines.append(line)
        elif m_to:
            remove = False
            to_found = True
            if not to_included:
                lines.append(line)
        elif not remove:
            lines.append(line)

    return '\n'.join(lines).rstrip() + '\n', from_found, to_found

def _usage_remove():
    print 'Usage: doconce remove --from[-] from-text [--to[-] to-text] file'

def remove():
    """
    Remove a portion of text from a file, starting with from-text
    (included if specified as --from, not included if specified
    via --from-) up to the first occurence of to-text (--to implies
    that the last line is included, --to_ excludes the last line).
    If --to[-] is not specified, all text up to the end of the file
    is returned.

    from-text and to-text are specified as regular expressions.
    """
    if len(sys.argv) < 4:
        _usage_remove()
        sys.exit(0)

    filename = sys.argv[-1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()

    if not sys.argv[1].startswith('--from'):
        print 'missing --from fromtext or --from_ fromtext option on the command line'
        sys.exit(1)
    from_included = sys.argv[1] == '--from'
    from_text = sys.argv[2]

    # Treat --to

    # impossible text (has newlines) that will never be found
    # is used as to-text if this is not specified
    impossible_text = '@\n\n@'
    try:
        to_included = sys.argv[3] == '--to'
        to_text = sys.argv[4]
    except IndexError:
        to_included = True
        to_text = impossible_text

    filestr, from_found, to_found = remove_text(
        filestr, from_text, from_included, to_text, to_included)

    if not from_found:
        print 'Could not find match for from regex "%s"' % from_text
        sys.exit(1)
    if not to_found and to_text != impossible_text:
        print 'Could not find match for to   regex "%s"' % to_text
        sys.exit(1)

    os.rename(filename, filename + '.old~~')
    f = open(filename, 'w')
    f.write(filestr)
    f.close()

def _usage_remove_exercise_answers():
    print 'Usage: doconce remove_exercise_answers file_in_some_format'

def remove_exercise_answers():
    if len(sys.argv) < 2:
        _usage_remove_exercise_answers()
        sys.exit(0)

    filename = sys.argv[1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()

    envirs = ['solution of exercise', 'short answer in exercise']
    from_texts = [r'--- begin ' + envir for envir in envirs]
    to_texts = [r'--- end ' + envir for envir in envirs]
    for from_text, to_text in zip(from_texts, to_texts):
        filestr, from_found, to_found = remove_text(
            filestr, from_text, True, to_text, True)
    if from_found and to_found:
        pass
    else:
        print 'no answers/solutions to exercises found in', filename

    os.rename(filename, filename + '.old~~')
    f = open(filename, 'w')
    f.write(filestr)
    f.close()


def clean():
    """
    Remove all DocOnce generated files and trash files.
    Place removed files in generated subdir Trash.

    For example, if ``d1.do.txt`` and ``d2.do.txt`` are found,
    all files ``d1.*`` and ``d1.*`` are deleted, except when ``*``
    is ``.do.txt`` or ``.sh``. The subdirectories ``sphinx-rootdir``
    and ``html_images`` are also removed, as well as all ``*~`` and
    ``tmp*`` files and all files made from splitting (split_html,
    split_rst).
    """
    if os.path.isdir('Trash'):
        print
        shutil.rmtree('Trash')
        print 'Removing Trash directory'
    removed = []

    trash_files = '_doconce_debugging.log', '__tmp.do.txt', 'texput.log'
    for trash_file in trash_files:
        if os.path.isfile(trash_file):
            removed.append(trash_file)

    doconce_files = glob.glob('*.do.txt')
    for dof in doconce_files:
        namestem = dof[:-7]
        generated_files = glob.glob(namestem + '.*')
        extensions_to_keep = '.sh', '.do.txt'
        #print 'generated_files:', namestem + '.*', generated_files
        for ext in extensions_to_keep:
            filename = namestem + ext
            if os.path.isfile(filename):
                generated_files.remove(filename)
        for f in generated_files:
            removed.append(f)
    removed.extend(glob.glob('*~') + glob.glob('.*~') + glob.glob('tmp*') +
                   glob.glob(_part_filename_wildcard + '.html') +
                   glob.glob(_part_filename_wildcard + '.rst') +
                   glob.glob('.*.exerinfo') +
                   glob.glob('.*.quiz*') +
                   glob.glob('.*_html_file_collection'))
    directories = ['html_images', 'latex_figs'] + glob.glob('sphinx-*') + \
                  glob.glob('sphinx_*')
    for d in directories:
        if os.path.isdir(d):
            removed.append(d)
    if removed:
        print 'Remove:', ' '.join(removed), '(-> Trash)'
        os.mkdir('Trash')
        for f in removed:
            try:
                shutil.move(f, 'Trash')
            except shutil.Error, e:
                if 'already exists' in str(e):
                    pass
                else:
                    print 'Move problems with', f, e
            if os.path.isdir(f):
                shutil.rmtree(f)

def _usage_guess_encoding():
    print 'Usage: doconce guess_encoding filename'

def _encoding_guesser(filename, verbose=False):
    """Try to guess the encoding of a file."""
    f = open(filename, 'r')
    text = f.read()
    f.close()
    encodings = ['ascii', 'us-ascii', 'iso-8859-1', 'iso-8859-2',
                 'iso-8859-3', 'iso-8859-4', 'cp37', 'cp930', 'cp1047',
                 'utf-8', 'utf-16', 'windows-1250', 'windows-1252',]
    for encoding in encodings:
        try:
            if verbose:
                print 'Trying encoding', encoding, 'with unicode(text, encoding)'
            unicode(text, encoding, "strict")
        except Exception, e:
            if verbose:
                print 'failed:', e
        else:
            break
    return encoding

def guess_encoding():
    if len(sys.argv) != 2:
        _usage_guess_encoding()
        sys.exit(0)
    filename = sys.argv[1]
    print _encoding_guesser(filename, verbose=False)

def _usage_change_encoding():
    print 'Usage: doconce change_encoding from-encoding to-encoding file1 file2 ...'
    print 'Example: doconce change_encoding utf-8 latin1 myfile.do.txt'

def _change_encoding_unix(filename, from_enc, to_enc):
    backupfile = filename + '.old~~'
    if sys.platform == 'linux2':
        cmd = 'iconv -f %s -t %s %s --output %s' % \
              (from_enc, to_enc, backupfile, filename)
    elif sys.platform == 'darwin':
        cmd = 'iconv -f %s -t %s %s > %s' % \
              (from_enc, to_enc, backupfile, filename)
    else:
        print 'changing encoding is not implemented on Windows machines'
        _abort()
    os.rename(filename, backupfile)
    failure = system(cmd, abort_on_failure=False)
    if failure:
        # Restore file
        shutil.copy(backupfile, filename)
        os.remove(backupfile)

def _change_encoding_python(filename, from_enc, to_enc):
    f = codecs.open(filename, 'r', from_enc)
    text = f.read()
    f.close()
    f = codecs.open(filename, 'w', to_enc)
    f.write(text)
    f.close()

def change_encoding():
    if len(sys.argv) < 4:
        _usage_change_encoding()
        sys.exit(0)

    from_encoding = sys.argv[1]
    to_encoding = sys.argv[2]
    filenames = wildcard_notation(sys.argv[3:])
    for filename in filenames:
        _change_encoding_unix(filename, from_encoding, to_encoding)
        # Perhaps better alternative with pure Python:
        #_change_encoding_python(filename, from_encoding, to_encoding)


html_images = 'html_images.zip'
reveal_files = 'reveal.js.zip'
csss_files = 'csss.zip'
deck_files = 'deck.js.zip'
latexstyle_files = 'latex_styles.zip'

def html_imagefile(imagename):
    filename = os.path.join(html_images[:-4], imagename + '.png')
    return filename

def copy_datafiles(datafile):
    """
    Get a doconce datafile, ``files.zip`` or ``files.tar.gz``, to
    the current directory and pack it out unless the subdirectory
    ``files`` (with all the files) already exists.
    """
    if datafile.endswith('.zip'):
        subdir = datafile[:-4]
        import zipfile
        uncompressor = zipfile.ZipFile
    elif datafile.endswith('.tar.gz'):
        subdir = datafile[:-7]
        import tarfile
        uncompressor = tarfile.TarFile
    if not os.path.isdir(subdir):
        import doconce
        doconce_dir = os.path.dirname(doconce.__file__)
        doconce_datafile = os.path.join(doconce_dir, datafile)
        shutil.copy(doconce_datafile, os.curdir)
        uncompressor(datafile).extractall()
        print 'made subdirectory', subdir
        os.remove(datafile)
        return True
    else:
        return False


def _usage_html_colorbullets():
    print 'Usage: doconce html_colorbullets mydoc.html'

def html_colorbullets():
    # A much better implementation, avoiding tables, is given
    # here: http://www.eng.buffalo.edu/webguide/Bullet_Lists.html
    """
    Replace unordered lists by a table, in order to replace
    ``<li>`` tags (and the default bullets) by
    images of balls with colors.
    """
    if len(sys.argv) <= 1:
        _usage_html_collorbullets()
        sys.exit(0)

    red_bullet = 'bullet_red2.png'
    green_bullet = 'bullet_green2.png'
    #red_bullet = 'bullet_red1.png'
    #green_bullet = 'bullet_green1.png'

    filenames = sys.argv[1:]
    for filename in filenames:
        f = open(filename, 'r')
        text = f.read()
        f.close()
        #if '<li>' in text:
        #    copy_datafiles(html_images)  # copy html_images subdir if needed
        lines = text.splitlines()
        f = open(filename, 'w')
        level = 0
        for line in lines:
            linel = line.lower()
            if '<ul>' in linel:
                level += 1
                line = '<p><table border="0">\n'
            if '</ul>' in linel:
                line = '</td></tr></table>\n'
                level -= 1
            if '<li>' in linel:
                line = line.replace('<li>', """</tr><p><tr><td valign='top'><img src="BULLET"></td><td>""")
                if level == 1:
                    #image_filename = html_imagefile(red_bullet)
                    image_filename = 'http://hplgit.github.io/doconce/bundled/html_images/' + red_bullet
                elif level >= 2:
                    #image_filename = html_imagefile(green_bullet)
                    image_filename = 'http://hplgit.github.io/doconce/bundled/html_images/' + green_bullet
                line = line.replace('BULLET', image_filename)
            f.write(line + '\n')
        f.close()

def _usage_split_html():
    print """\
Usage: doconce split_html mydoc.html --method=... --nav_button=name --pagination --acknowledgment="..."'
--method=split|space8|hrule|colorline specifies physical pagebreak
split (split) or just N blank lines (spaceN) or a horizontal
rule (hrule) with blank lines above and below, or a colored rule
instead of <hr> rule. Default is split.

--nav_button=name sets the type of navigation button (next, previous):
text, gray1 (default), gray2, bigblue, blue, green.
See (https://raw.github.com/hplgit/doconce/master/doc/src/manual/fig/nav_buttons.png
for examples on these types (from left to right).
A value like gray2,top gives buttons only at the top of the page,
gray2,top+bottom gives buttons at the top and bottom (default), while
gray2,bottom gives buttons only at the bottom.
If the "doconce format html" command used bootstrap styles (with
--html_style=bootstrap*|bootswatch*), set just --nav_button=top or
bottom (default) or top+bottom.

--pagination means that one can click on pages at the button
if a bootstrap theme is used in the document.

--reference=... is used to insert a reference for acknowledging where
the source of the text is published, typically the reference of a
book if the document is the HTML version of a chapter in the book.
Example:
--reference="This text is taken from Appendix H.2 in the book <em>A Primer on Scientific Programming with Python</em> by H. P. Langtangen, 4th edition, Springer, 2014."
"""

def split_html():
    """
    Split html file into parts. Use !split command as separator between
    parts.
    """
    if len(sys.argv) <= 1:
        _usage_split_html()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.html'):
        basename = filename
        filename += '.html'
    else:
        basename = filename[:-5]

    method = misc_option('method=', 'split')

    # Note: can only do tablify and support slidecell specifications
    # if --method=split (tablify requires the file split into parts)

    if method != 'split':
        # Load text
        f = open(filename, 'r')
        filestr = f.read()
        f.close()

    if method.startswith('space'):
        if len(method) > len('space'):
            num_lines = int(method[5:])
        else:
            num_lines = 8
        filestr = filestr.replace(
            '<!-- !split -->',
            '<!-- !split -->' + '<br>'*num_lines)
    elif method in ('hr', 'hrule'):
        filestr = filestr.replace(
            '<!-- !split -->',
            '<!-- !split -->' + '<br><br><br><hr><br><br><br>')
    elif method in ('colorline',):
        filestr = filestr.replace(
            '<!-- !split -->',
            '<!-- !split -->' + '<br><br><br><br><br><br><img src="%s"><br><br>'
            % 'http://hplgit.github.io/doconce/bundled/html_images/colorline.png')
    else:
        header, parts, footer = get_header_parts_footer(filename, "html")
        parts = tablify(parts, "html")

        files = doconce_split_html(header, parts, footer, basename, filename)
        print '%s now links to the generated files' % filename
        print ', '.join(files)

    if method != 'split':
        # Remove notes
        filestr = re.sub(r'^<!-- !bnotes.+?^<!-- !enotes -->', '',
                         filestr, flags=re.MULTILINE|re.DOTALL)
        # Fix font size for solarized slides
        if re.search(r'''<link href=[""]http.+?solarized.*?\.css''', filestr):
            filestr = filestr.replace(r'<style type="text/css">',
                                      """<style type="text/css">
body, td {font-size: 140%;}
h1 {font-size: 200%;}
h2 {font-size: 180%;}
""")

        f = open(filename, 'w')
        f.write(filestr)
        f.close()

        if '<!-- !bslidecell' in filestr:
            print '*** warning: !bslidecell-!eslidecell constructions are'
            print '    ignored unless --method=split is specified'
            print '    (--method=spaceX|hr|hrule|colorline all ignores cells)'


def _usage_slides_html():
    print """
Usage: doconce slides_html mydoc.html slide_type --html_slide_theme=themename --html_footer_logo=name --nav_button=name

slide_type: reveal deck csss dzslides
note: reveal and deck slide styles are doconce variants, different from the
original styles
(note: remark style is not generated by slides_html, but by slides_markdown)

alternative:  doconce slides_html mydoc.html all  (generate all types of slides)

themename is the reveal or deck theme:

reveal.js: beige, beigesmall, solarized, serif, simple, blood, sky,
moon, night, moon, darkgray, cbc, simula

deck.js: neon, sandstone.aurora, sandstone.dark, sandstone.mdn,
sandstone.mightly, sandstone.firefox, sandstone.default,
sandstone.light, beamer, mnml, swiss, web-2.0, cbc

(The generated HTML file contains a comment with link tags for the
the various stylesheets for the various available themes.)

--html_footer_logo=name sets the footer logo to be used, name is
a full URL to the logo image file,
or cbc_footer, cbc_symbol, simula_footer, simula_symbol,
uio_footer, uio_symbol (for which the full path is automatically created)

--nav_button=name sets the type of navigation button (next, previous):
text, gray1 (default), gray2, bigblue, blue, green.
See (https://raw.github.com/hplgit/doconce/master/doc/src/manual/fig/nav_buttons.png
for examples on these types (from left to right).
A value like gray2,top gives buttons only at the top of the page,
gray2,top+bottom gives buttons at the top and bottom (default), while
gray2,bottom gives buttons only at the bottom.
If the "doconce format html" command used bootstrap styles (with
--html_style=bootstrap*|bootswatch*), set just --nav_button=top or
bottom (default) or top+bottom.

--pagination means that one can click on page numbers if a bootstrap
theme is used in the document.

Note: if slide_tp is doconce, the doconce split_html command is
more versatile than slides_html since it allows the --method
argument, which can be used for physical splits (as in slides_html)
or "split" via just space or rules for separating the parts in
one (big) file.
"""

def slides_html():
    """
    Split html file into slides and typeset slides using
    various tools. Use !split command as slide separator.
    """
    # Overview: http://www.impressivewebs.com/html-slidedeck-toolkits/
    # Overview: http://www.sitepoint.com/5-free-html5-presentation-systems/
    # x http://leaverou.github.com/CSSS/
    # x http://lab.hakim.se/reveal-js/ (easy and fancy)
    # x http://paulrouget.com/dzslides/ (easy and fancy, Keynote like)
    # http://imakewebthings.com/deck.js/ (also easy)
    # http://code.google.com/p/html5slides/ (also easy)
    # http://slides.seld.be/?file=2010-05-30+Example.html#1 (also easy)
    # http://www.w3.org/Talks/Tools/Slidy2/#(1) (also easy)
    # http://johnpolacek.github.com/scrolldeck.js/ (inspired by reveal.js)
    # http://meyerweb.com/eric/tools/s5/ (easy)
    # https://github.com/mbostock/stack (very easy)
    # https://github.com/markdalgleish/fathom
    # http://shama.github.com/jmpress.js/#/home  # jQuery version of impress
    # https://github.com/bartaz/impress.js/

    # Fancy and instructive demo:
    # http://yihui.name/slides/2011-r-dev-lessons.html
    # (view the source code)

    # pandoc can make dzslides and embeds all javascript (no other files needed)
    # pandoc -s -S -i -t dzslides --mathjax my.md -o my.html

    if len(sys.argv) <= 2:
        _usage_slides_html()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.html'):
        filename += '.html'
    if not os.path.isfile(filename):
        print 'doconce file in html format, %s, does not exist' % filename
        _abort()
    basename = os.path.basename(filename)
    filestem = os.path.splitext(basename)[0]

    slide_type = sys.argv[2]

    for arg in sys.argv[1:]:
        if arg.startswith('--method='):
            opt = arg.split('=')[1]
            if opt != 'split':
                print '*** error: slides_html cannot accept --method=%s' % opt
                print '    (the slides will always be split)'
                print '    use split_html with --method=...'
                _abort()

    # Treat the special case of generating a script for generating
    # all the different slide versions that are supported
    if slide_type == 'all':
         #from doconce.misc import recommended_html_styles_and_pygments_styles
         r = recommended_html_styles_and_pygments_styles()
         f = open('tmp_slides_html_all.sh', 'w')
         f.write('#!/bin/sh\n\n')
         f.write('doconce format html %s SLIDE_TYPE=dummy SLIDE_THEME=dummy\ndoconce slides_html %s doconce\n\n' %
                 (filestem, filestem))
         for sl_tp in r:
             for style in r[sl_tp]:
                 pygm_style = r[sl_tp][style][0]
                 if sl_tp == 'html':
                     if style.startswith('solarized'):
                         f.write('doconce format html %s SLIDE_TYPE=%s SLIDE_THEME=%s --html_style=%s --html_output=%s_html_%s\ndoconce slides_html %s_html_%s doconce --nav_button=text\n\n' % (filestem, sl_tp, style, style, filestem, style, filestem, style))
                     else:
                         method = 'colorline' if style == 'blueish' else 'space8'
                         f.write('doconce format html %s --pygments_html_style=%s --keep_pygments_html_bg SLIDE_TYPE=%s SLIDE_THEME=%s --html_style=%s --html_output=%s_html_%s\ndoconce split_html %s_html_%s --method=%s  # one long file\n\n' % (filestem, pygm_style, sl_tp, style, style, filestem, style, filestem, style, method))
                 else:
                     f.write('doconce format html %s --pygments_html_style=%s --keep_pygments_html_bg SLIDE_TYPE=%s SLIDE_THEME=%s\ndoconce slides_html %s %s --html_slide_theme=%s\ncp %s.html %s_%s_%s.html\n\n' % (filestem, pygm_style, sl_tp, style, filestem, sl_tp, style, filestem, filestem, sl_tp, style.replace('.', '_')))
         f.write('echo "Here are the slide shows:"\n/bin/ls %s_*_*.html\n' % filestem)
         print 'run\n  sh tmp_slides_html_all.sh\nto generate the slides'
         #print 'names:', ' '.join(glob.glob('%s_*_*.html' % filestem))
         return


    # --- Create a slide presentation from the HTML file ---

    header, parts, footer = get_header_parts_footer(filename, "html")
    parts = tablify(parts, "html")

    filestr = None
    if slide_type == 'doconce':
        doconce_split_html(header, parts, footer, filestem, filename, slides=True)
    elif slide_type in ('reveal', 'csss', 'dzslides', 'deck', 'html5slides'):
        filestr = generate_html5_slides(header, parts, footer,
                                        basename, filename, slide_type)
    else:
        print 'unknown slide type "%s"' % slide_type

    if filestr is not None:
        # Make whitespace nicer (clean up code)
        from html import html_remove_whitespace
        filestr = html_remove_whitespace(filestr)
        # More fixes for html5 slides
        filestr = re.sub(r'<section>\s+(?=<h[12])', r'<section>\n', filestr)
        filestr = re.sub(r'<p>\n</section>', '</section>', filestr)
        filestr = re.sub(r'\s+</section>', '\n</section>', filestr)

        from html import html_remove_whitespace
        filestr = html_remove_whitespace(filestr)
        # More fixes for html5 slides
        filestr = re.sub(r'<section>\s+(?=<h[12])', r'<section>\n', filestr)
        filestr = re.sub(r'<p>\n</section>', '</section>', filestr)
        filestr = re.sub(r'\s+</section>', '\n</section>', filestr)

        f = open(filename, 'w')
        f.write(filestr)
        f.close()
        print 'slides written to', filename


def tablify(parts, format="html"):
    """
    Detect !bslidecell XY and !eslidecell environments and typeset
    elements of a part (slide page) as a table.
    """
    begin_comment, end_comment = _format_comments(format)
    for i in range(len(parts)):
        part = ''.join(parts[i])

        if '%s !bslidecell' % begin_comment in part:
            pattern = r'%s !bslidecell +(\d\d) *([.0-9 ]*?)%s\s+(.+?)%s !eslidecell *%s' % (begin_comment, end_comment, begin_comment, end_comment)
            pattern00 = r'%s !bslidecell +00 *[.0-9 ]*?%s\s+(.+?)%s !eslidecell *%s' % (begin_comment, end_comment, begin_comment, end_comment)
            cpattern = re.compile(pattern, re.DOTALL)
            cells = cpattern.findall(part)
            #print 'CELLS:'; import pprint; pprint.pprint(cells)
            data = []
            row_max = 0
            col_max = 0
            for pos, width, entry in cells:
                try:
                    width = float(width)
                except:
                    width = None

                ypos = int(pos[0])
                xpos = int(pos[1])
                if ypos > row_max:
                    row_max += 1
                if xpos > col_max:
                    col_max += 1
                data.append([(ypos, xpos), entry, width])
            table = [[None]*(col_max+1) for j in range(row_max+1)]
            for r in range(len(table)):
                for s in range(len(table[r])):
                    table[r][s] = ['', None]
            #print 'data:', data
            for pos, body, width in data:
                table[pos[0]][pos[1]] = [body, width]
            #print 'table 1:'; import pprint; pprint.pprint(table)
            # Check consistency of widths
            for r, row in enumerate(table):
                widths = []
                has_width = False
                for column, width in row:
                    if width is not None:
                        has_width = True
                        widths.append(width)
                if has_width:
                    if len(row) != len(widths):
                        # Can accept if only two columns
                        if len(row) == 2 and len(widths) == 1:
                            # Find the missing one
                            if table[r][0][1] is None:
                                table[r][0][1] = 1 - widths[0]
                            elif table[r][1][1] is None:
                                table[r][1][1] = 1 - widths[0]
                        else:
                            print '*** error: must specify width of all columns in slidecell table!'
                            print '   ',
                            for s, c in enumerate(row):
                                column, width = c
                                print ' %d%d: ' (r, s),
                                if width is not None:
                                    print 'no width',
                                else:
                                    print '%g' % width,
                            _abort()
                else:
                    width = 1./len(row)
                    for s, c in enumerate(row):
                        table[r][s][1] = width

            #print 'table 2:'; import pprint; pprint.pprint(table)

            if format == 'html':
                # typeset table in html
                tbl = '\n<table border="0">\n'
                for row in table:
                    tbl += '<tr>\n'
                    for column, width in row:
                        tbl += '<td class="padding">\n%s</td>\n' % (column)
                        # This is an attempt to control the width of columns,
                        # but it does not work well.
                        #tbl += '<td class="padding"><div style="width: %d%%"> %s </div></td>\n' % (int(100*width), column)

                    tbl += '</tr>\n'
                tbl += '</table>\n'

                # Put the whole table where cell 00 was defined
                cpattern00 = re.compile(pattern00, re.DOTALL)
                #part = cpattern00.sub(tbl, part)  # does not preserve math \
                part = cpattern00.sub('XXXYYY@#$', part)  # some ID and then replace
                part = part.replace('XXXYYY@#$', tbl) # since replace handles \
                # Let the other cells be empty
                part = cpattern.sub('', part)
                #print 'part:'; pprint.pprint(part)
                part = [line + '\n' for line in part.splitlines()]
                parts[i] = part
            elif format.endswith('latex'):
                # typeset table in beamer latex
                tbl = ''
                for row in table:
                    tbl += r'\begin{columns}' + '\n'
                    for column, width in row:
                        if width is None:
                            raise ValueError('Bug: width is None')
                        tbl += r'\column{%g\textwidth}' % width + \
                               '\n%s\n' % column

                    tbl += r'\end{columns}' + '\n'
                tbl += '\n'

                # Put the whole table where cell 00 was defined
                cpattern00 = re.compile(pattern00, re.DOTALL)
                #part = cpattern00.sub(tbl, part)  # does not preserve math \
                part = cpattern00.sub('XXXYYY@#$', part)  # some ID and then replace
                part = part.replace('XXXYYY@#$', tbl) # since replace handles \
                # Let the other cells be empty
                part = cpattern.sub('', part)
                #print 'part:'; pprint.pprint(part)
                part = [line + '\n' for line in part.splitlines()]
                parts[i] = part
    return parts

def _format_comments(format='html'):
    if format == 'html':
        return '<!--', '-->'
    elif format == 'latex':
        return '%', ''
    elif format == 'rst' or format == 'sphinx':
        return '..', ''
    else:
        return None, None

def get_header_parts_footer(filename, format='html'):
    """Return list of lines for header, parts split by !split, and footer."""
    from doconce import main_content_char
    header = []
    footer = []
    parts = [[]]
    if format in ('latex', 'pdflatex', 'html'):
        loc = 'header'
    else:
        loc = 'body'  # no header
    begin_comment, end_comment = _format_comments(format)
    f = open(filename, 'r')
    for line in f:
        if re.search(r'^%s %s+ main content %s+ ?%s' %
                     (begin_comment, main_content_char,
                      main_content_char, end_comment), line):
            loc = 'body'
        if re.search(r'^%s !split.*?%s' % (begin_comment, end_comment), line):
            parts.append([])
        if re.search(r'^%s %s+ end of main content %s+ ?%s' %
                     (begin_comment, main_content_char,
                      main_content_char, end_comment), line):
            loc = 'footer'
        if loc == 'header':
            header.append(line)
        elif loc == 'body':
            parts[-1].append(line)
        elif loc == 'footer':
            footer.append(line)
    f.close()
    return header, parts, footer


def doconce_split_html(header, parts, footer, basename, filename, slides=False):
    """Native doconce style splitting of HTML file into parts."""
    import html
    header_str = '\n'.join(header)

    bootstrap = '<!-- Bootstrap style: ' in header_str or \
                bool(re.search(r'<link .*href=.+?boots(trap|watch).*\.css', header_str))

    if bootstrap:
        local_navigation_pics = False    # navigation is in the template

        def bootstrap_navigation(pn, prev_part_filename, next_part_filename):
            text = '<!-- navigation buttons at the bottom of the page -->'
            if '--pagination' in sys.argv:
                # Use Bootstrap pagination
                text += '\n<ul class="pagination">\n'
                if pn > 0:
                    text += '<li><a href="%s">&laquo;</a></li>\n' % prev_part_filename
                max_pagination_pages = 16
                #max_pagination_pages = 4 # for debugging
                if len(parts) <= max_pagination_pages/2:
                    # Show all pages
                    for i in range(len(parts)):
                        if i == pn:
                           text += '  <li class="active"><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                        else:
                           text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                else:
                    # Show first, last, and pages around the current one
                    if pn >= max_pagination_pages/2 + 2:
                        i = 0
                        text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                        text += '  <li><a href="">...</a></li>\n'
                    start = max(0, pn-(max_pagination_pages/2))
                    stop = min(len(parts), pn+max_pagination_pages/2+2)
                    if start == 1:
                        # Special case, add page 1
                        text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, 0) + '.html', 0+1)
                    for i in range(start, stop):
                        if i == pn:
                           text += '  <li class="active"><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                        else:
                           text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)
                    if pn <= (len(parts) - (max_pagination_pages/2 + 3)):
                        text += '  <li><a href="">...</a></li>\n'
                        i = len(parts)-1
                        text += '  <li><a href="%s">%d</a></li>\n' % (_part_filename % (basename, i) + '.html', i+1)

                if pn < len(parts)-1:
                    text += '  <li><a href="%s">&raquo;</a></li>\n' % next_part_filename
                text += '</ul>\n'
            else:
                # Use plain next and prev buttons with arrows, but
                # Bootstrap style
                text += '\n<ul class="pager">\n'
                if pn > 0:
                    text += """\
  <li class="previous">
    <a href="%s">&larr; Prev</a>
  </li>
""" % prev_part_filename
                if pn < len(parts)-1:
                    text += """\
  <li class="next">
    <a href="%s">Next &rarr;</a>
  </li>
""" % next_part_filename
                text += '</ul>\n'
            return text
    else:
        local_navigation_pics = False    # avoid copying images to subdir...

    nav_button = 'gray1'
    for arg in sys.argv:
        if arg.startswith('--nav_button='):
            nav_button = arg.split('=')[1]
            break
    if bootstrap:
        nav_button_pos = 'bottom'
        if nav_button in ('top', 'top+bottom'):
            nav_button_pos = nav_button
    else:
        nav_button_pos = 'top+bottom'
        if ',' in nav_button:
            nav_button, nav_button_pos = nav_button.split(',')
        # Values after comma: top, bottom, top+bottom

    # Map nav_button name to actual image file in bundled/html_images
    prev_button = next_button = ''
    if nav_button == 'gray1':
        prev_button = 'prev1'
        next_button = 'next1'
    elif nav_button == 'gray2':
        prev_button = 'prev2'
        next_button = 'next2'
    elif nav_button == 'bigblue':
        prev_button = 'prev3'
        next_button = 'next3'
    elif nav_button == 'blue':
        prev_button = 'prev4'
        next_button = 'next4'
    elif nav_button == 'green':
        prev_button = 'Knob_Left'
        next_button = 'Knob_Forward'
    elif nav_button in ('text', 'top', 'bottom', 'top+bottom'):
        pass
    else:
        print '*** warning: --nav_button=%s is illegal value, text,top+bottom is used' % nav_button
        nav_button == 'text'
        nav_button_pos = 'top+bottom'

    header_part_line = ''  # 'colorline'
    if local_navigation_pics:
        copy_datafiles(html_images)  # copy html_images subdir if needed
        if prev_button:
            prev_button_filename = html_imagefile(prev_button)
            next_button_filename = html_imagefile(next_button)
            html.add_to_file_collection(prev_button_filename, filename, 'a')
            html.add_to_file_collection(next_button_filename, filename, 'a')
    else:
        if prev_button:
            prev_button_filename = 'http://hplgit.github.io/doconce/bundled/html_images/%s.png' % prev_button
            next_button_filename = 'http://hplgit.github.io/doconce/bundled/html_images/%s.png' % next_button


    # Fix internal links to point to the right splitted file
    name_pattern = r' id="([^"]+?)">'
    parts_name = [re.findall(name_pattern, ''.join(part)) for part in parts]
    parts_name.append(re.findall(name_pattern, ''.join(header)))
    parts_name.append(re.findall(name_pattern, ''.join(footer)))
    href_pattern = r'<a href="#([^"]+?)"'
    parts_href = [re.findall(href_pattern, ''.join(part)) for part in parts]
    parts_href.append(re.findall(href_pattern, ''.join(header)))
    parts_href.append(re.findall(href_pattern, ''.join(footer)))

    # id="..." can also define anchors (e.g., in bootstrap styles)
    id_pattern = r' id="([^"]+?)"'
    all_ids = [re.findall(id_pattern, ''.join(part)) for part in parts] + \
              [re.findall(id_pattern, ''.join(header)),
               re.findall(id_pattern, ''.join(footer))]
    # Flatten
    ids = []
    for sublist in all_ids:
        for id in sublist:
            ids.append(id)

    parts_name2part = {}   # map a name to where it is defined
    for i in range(len(parts_name)):
        for name in parts_name[i]:
            parts_name2part[name] = i

    import pprint
    # Substitute hrefs in each part, plus header and footer
    for i in range(len(parts_href)):
        for name in parts_href[i]:
            n = parts_name2part.get(name, None) #part where this name is defined
            if n is None and name not in ids:
                print '*** error: <a href="#%s" has no corresponding anchor (<a name= or some id=)' % name
                print '    This is probably a bug in DocOnce.'
                _abort()
                continue  # go to next if abort is turned off
            if n is not None and n != i:
                # Reference to label in another part, except the header
                # and footer (which is included in all parts)
                name_def_filename = _part_filename % (basename, n) + '.html'
                if i < len(parts):
                    part = parts[i]
                elif i == len(parts):
                    part = header
                elif i == len(parts)+1:
                    part = footer
                text = ''.join(part).replace(
                    '<a href="#%s"' % name,
                    '<a href="%s#%s"' % (name_def_filename, name))
                # Side effect: will substitute in header and footer
                # when it should not. This is fixed when the whole
                # file is constructed.
                if i < len(parts):
                    parts[i] = text.splitlines(True)
                elif i == len(parts):
                    header = text.splitlines(True)
                elif i == len(parts)+1:
                    footer = text.splitlines(True)

    # Treat \eqref and labels: MathJax does not support references
    # to eq. labels in other files.
    # Also, skip equation references to external documents.
    label_pattern = r'\label\{(.+?)\}'  # label in latex equations
    parts_label = [re.findall(label_pattern, ''.join(part)) for part in parts]
    eqref_pattern = r'\eqref\{(.+?)\}'
    ref_pattern = r'ref(ch)?\[([^\]]*?)\]\[([^\]]*?)\]\[([^\]]*?)\]'
    parts_eqref = [re.findall(eqref_pattern,
                              re.sub(ref_pattern, '', ''.join(part)))
                   for part in parts]

    parts_label2part = {}   # map an eq. label to where it is defined
    for i in range(len(parts_label)):
        for label in parts_label[i]:
            parts_label2part[label] = i
    # Check if there are eqrefs to undefined labels
    if misc_option('labelcheck=', 'off') == 'on':
        undefined_labels = []
        for i in range(len(parts_eqref)):
            for label in parts_eqref[i]:
                if label not in parts_label2part:
                    undefined_labels.append(label)
        if undefined_labels:
            for label in undefined_labels:
                print '*** error: equation ref (ref{%s}) but no label{%s}' % (label, label)
            print '*** error: found references to undefined equation labels'
            print '    (use generalized references ref[][][] if labels are'
            print '    defined outside this doconce document)'
            _abort()
    # Substitute eqrefs in each part.
    # MathJax cannot refer to labels in other HTML files.
    # We generate tag number for each label, in the right numbering
    # and use tags to refer to equations.
    # Info on http://stackoverflow.com/questions/16339000/how-to-refer-to-an-equation-in-a-different-page-with-mathjax
    # Tags are numbered globally
    labels = []  # Hold all labels in a list (not list of list as parts_label)
    for i in parts_label:
        labels += i
    label2tag = {}
    for i in range(len(labels)):
        label2tag[labels[i]] = i+1
    # Go from AMS to non equationNumering in MathJax since we do not
    # want any equation without label to have numbers (instead we
    # control all numbers here by inserting \tag)
    for i in range(len(header)):
        if 'autoNumber: "AMS"' in header[i]:
            header[i] = header[i].replace('autoNumber: "AMS"', 'autoNumber: "none"')
            break
    # Insert tags in each part
    for i in range(len(parts)):
        text = ''.join(parts[i])
        if r'\label{' in text:
            labels = re.findall(label_pattern, text)
            for label in labels:
                text = text.replace(
                    r'\label{%s}' % label,
                    r'\tag{%s}' % (label2tag[label]))
        parts[i] = text.splitlines(True)
    # Substitute all \eqrefs (can only have tags, not labels for
    # right navigation to an equation)
    for i in range(len(parts_eqref)):
        for label in parts_eqref[i]:
            if not label in parts_label2part:
                continue
            n = parts_label2part[label]   # part where this label is defined
            if i < len(parts):
                part = parts[i]
                text = ''.join(part)
                if n != i:
                    # Reference to equation with label in another file
                    #print '*** warning: \\eqref{%s} to label in another HTML file will appear as (eq)' % (label)
                    label_def_filename = _part_filename % (basename, n) + '.html'
                    text = text.replace(
                        r'\eqref{%s}' % label,
                        '<a href="%s#mjx-eqn-%s">(%s)</a>' %
                        (label_def_filename, label2tag[label], label2tag[label]))
                else:
                    text = text.replace(
                        r'\eqref{%s}' % label,
                        '<a href="#mjx-eqn-%s">(%s)</a>' %
                        (label2tag[label], label2tag[label]))
                if i < len(parts):
                    parts[i] = text.splitlines(True)

    generated_files = []
    for pn, part in enumerate(parts):
        header_copy = header[:]
        if bootstrap:
            # Highligh first section in this part in the navigation in header
            m = re.search(r'<h(1|2|3).*?>(.+?)<', ''.join(part))
            if m:
                first_header = m.group(2).strip()
                for k in range(len(header_copy)):
                    if 'navigation toc:' in header[k]:
                        m2 = re.search(r'<li><a href="(.+?)">', header[k])
                        if m2:
                           if m2.group(1) == first_header:
                               header_copy[k] = header[k].replace(
                                   '<li>', '<li class="active">')
                        else:
                            print '*** error: doconce bug: wrong syntax in navigation toc for bootstrap styles'
                            _abort()

        lines = header_copy[:]
        lines.append('<a name="part%04d"></a>\n' % pn)

        # Decoration line?
        if header_part_line and not bootstrap:
            if local_navigation_pics:
                header_part_line_filename = html_imagefile(header_part_line)
            else:
                header_part_line_filename = 'http://hplgit.github.io/doconce/bundled/html_images/%s.png' % header_part_line
            lines.append("""
<p><br><img src="%s"><p><br><p>
""" % header_part_line_filename)

        part_filename = _part_filename % (basename, pn) + '.html'
        prev_part_filename = _part_filename % (basename, pn-1) + '.html'
        next_part_filename = _part_filename % (basename, pn+1) + '.html'
        generated_files.append(part_filename)

        if bootstrap:
            # Make navigation arrows
            prev_ = next_ = ''
            buttons = bootstrap_navigation(pn, prev_part_filename, next_part_filename)
            # Add jumbotron button reference on first page
            if pn == 0:
                for i in range(len(part)):
                    if part[i].startswith('<!-- potential-jumbotron-button -->'):
                        part[i] = part[i].replace(
                              '<!-- potential-jumbotron-button -->',
                              '\n\n<p><a href="%s" class="btn btn-primary btn-lg">Read &raquo;</a></p>\n\n' % next_part_filename)
                        break
            if 'top' in nav_button_pos:
                lines += buttons.splitlines(True)

        elif 'top' in nav_button_pos:
            # Simple navigation buttons at the top and bottom of the page
            # (only at bottom if the function argument slides is True)
            if not slides:
                lines.append('<p>\n<!-- begin top navigation -->\n') # for easy removal
                # Need a table for navigation pics, otherwise they cannot
                # be on the same line
                lines.append('<table style="width: 100%"><tr><td>\n')
                if pn > 0:
                    if nav_button == 'text':
                        lines.append("""\
<div style="text-align: left;"><a href="%s">&laquo; Previous</a></div>
""" % (prev_part_filename))
                    else:
                        lines.append("""\
<div style="text-align: left;"><a href="%s"><img src="%s" border=0 alt="&laquo; Previous"></a></div>
""" % (prev_part_filename, prev_button_filename))
                lines.append('</td><td>\n')
                if pn < len(parts)-1:
                    if nav_button == 'text':
                        lines.append("""\
<div style="text-align: right;"><a href="%s">Next &raquo;</a></div>
""" % (next_part_filename))
                    else:
                        lines.append("""\
<div style="text-align: right;"><a href="%s"><img src="%s" border=0 alt="Next &raquo;"></a></div>
""" % (next_part_filename, next_button_filename))
                lines.append('</td></tr></table>\n')
                lines.append('<!-- end top navigation -->\n</p>\n\n')
                lines.append('<p>\n')


        # Main body of text
        lines += part

        # Navigation in the bottom of the page
        lines.append('<p>\n')
        if bootstrap:
            if 'bottom' in nav_button_pos:
                lines += buttons.splitlines(True)
            lines += footer
        elif 'bottom' in nav_button_pos:
            lines.append('<!-- begin bottom navigation -->\n')
            lines.append('<table style="width: 100%"><tr><td>\n')
            if pn > 0:
                if nav_button == 'text':
                    lines.append("""\
<div style="text-align: left;"><a href="%s">&laquo; Previous</a></div>
""" % (prev_part_filename))
                else:
                    lines.append("""\
<div style="text-align: left;"><a href="%s"><img src="%s" border=0 alt="&laquo; Previous"></a></div>
""" % (prev_part_filename, prev_button_filename))
            lines.append('</td><td>\n')
            if pn < len(parts)-1:
                if nav_button == 'text':
                    lines.append("""\
<div style="text-align: right;"><a href="%s">Next &raquo;</a></div>
""" % (next_part_filename))
                else:
                    lines.append("""\
<div style="text-align: right;"><a href="%s"><img src="%s" border=0 alt="Next &raquo;"></a></div>
""" % (next_part_filename, next_button_filename))
            lines.append('</td></tr></table>\n')
            lines.append('<!-- end bottom navigation -->\n</p>\n\n')
            lines += footer

        html.add_to_file_collection(part_filename, filename, 'a')

        part_text = ''.join(lines)
        # Remove references with this file as prefix in href
        # (some Bootstrap functionality does not work without this fix,
        # and in general we should strip local references anyway)
        part_text = part_text.replace('<a href="%s#' % part_filename,
                                      '<a href="#')

        # Insert reference to published version of document?
        ackn = misc_option('reference=', None)
        if ackn is not None:
            ackn1 = '<p style="font-size:80%%">%s</p>' % ackn
            ackn2 = '<div style="font-size:80%%">%s</div>' % ackn
            ackn3 = '<center style="font-size:80%%">%s</center>' % ackn
            if pn >= 1:
                # Place the acknowledgment/reference at the top, right after
                # the (only) !split command in each file
                part_text = part_text.replace(
                    '<!-- !split -->', '<!-- !split -->\n%s' % ackn1)
            elif pn == 0:
                # Include in front page if jumbotron button
                pattern = r'<p><a href=".+?" class="btn btn-primary btn-lg">Read &raquo;</a></p>'
                m = re.search(pattern, part_text)
                if m:  # jumbotron button?
                    button = m.group()
                    part_text = part_text.replace(
                        button, '\n<p>' + ackn2 + '</p>\n' + button)
                else:
                    # Put text after navigation
                    part_text = part_text.replace(
                        '<!-- end bottom navigation -->\n</p>\n',
                        '<!-- end bottom navigation -->\n</p>%s\n' % ackn1)

        # Remove notes
        part_text = re.sub(r'^<!-- !bnotes.+?^<!-- !enotes -->', '',
                           part_text, flags=re.MULTILINE|re.DOTALL)
        # Fix font size for solarized slides
        if re.search(r'''<link href=["']http.+?solarized.*?\.css''', part_text):
            part_text = part_text.replace(r'<style type="text/css">',
                                          """<style type="text/css">
body, td {font-size: 140%;}
h1 {font-size: 200%;}
h2 {font-size: 180%;}
""")

        # Write part to ._*.html file
        f = open(part_filename, 'w')
        f.write(part_text)
        f.close()

        # Make sure main html file equals the first part
        if pn == 0:
            shutil.copy(part_filename, filename)
    return generated_files


def generate_html5_slides(header, parts, footer, basename, filename,
                          slide_tp='reveal'):
    if slide_tp not in ['dzslides', 'html5slides']:
        copy_datafiles(eval(slide_tp + '_files'))  # copy to subdir if needed

    slide_syntax = dict(
        reveal=dict(
            subdir='reveal.js',
            default_theme='beige',
            main_style='reveal',
            slide_envir_begin='<section>',
            slide_envir_end='</section>',
            pop=('fragment', 'li'),
            notes='<aside class="notes">\n<!-- click "s" to activate -->\n\\g<1>\n</aside>\n',
            head_header="""
<!-- reveal.js: http://lab.hakim.se/reveal-js/ -->

<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />

<link rel="stylesheet" href="reveal.js/css/%(main_style)s.css">
<link rel="stylesheet" href="reveal.js/css/theme/%(theme)s.css" id="theme">
<!--
<link rel="stylesheet" href="reveal.js/css/reveal.css">
<link rel="stylesheet" href="reveal.js/css/theme/beige.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/beigesmall.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/solarized.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/serif.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/night.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/moon.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/simple.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/sky.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/darkgray.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/default.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/cbc.css" id="theme">
<link rel="stylesheet" href="reveal.js/css/theme/simula.css" id="theme">
-->

<!-- For syntax highlighting -->
<link rel="stylesheet" href="reveal.js/lib/css/zenburn.css">

<!-- If the query includes 'print-pdf', use the PDF print sheet -->
<script>
document.write( '<link rel="stylesheet" href="reveal.js/css/print/' + ( window.location.search.match( /print-pdf/gi ) ? 'pdf' : 'paper' ) + '.css" type="text/css" media="print">' );
</script>

<style type="text/css">
    hr { border: 0; width: 80%%; border-bottom: 1px solid #aaa}
    p.caption { width: 80%%; font-size: 60%%; font-style: italic; text-align: left; }
    hr.figure { border: 0; width: 80%%; border-bottom: 1px solid #aaa}
    .reveal .alert-text-small   { font-size: 80%%;  }
    .reveal .alert-text-large   { font-size: 130%%; }
    .reveal .alert-text-normal  { font-size: 90%%;  }
    .reveal .alert {
             padding:8px 35px 8px 14px; margin-bottom:18px;
             text-shadow:0 1px 0 rgba(255,255,255,0.5);
             border:5px solid #bababa;
             -webkit-border-radius: 14px; -moz-border-radius: 14px;
             border-radius:14px
             background-position: 10px 10px;
             background-repeat: no-repeat;
             background-size: 38px;
             padding-left: 30px; /* 55px; if icon */
     }
     .reveal .alert-block {padding-top:14px; padding-bottom:14px}
     .reveal .alert-block > p, .alert-block > ul {margin-bottom:1em}
     /*.reveal .alert li {margin-top: 1em}*/
     .reveal .alert-block p+p {margin-top:5px}
     /*.reveal .alert-notice { background-image: url(http://hplgit.github.io/doconce/bundled/html_images/small_gray_notice.png); }
     .reveal .alert-summary  { background-image:url(http://hplgit.github.io/doconce/bundled/html_images/small_gray_summary.png); }
     .reveal .alert-warning { background-image: url(http://hplgit.github.io/doconce/bundled/html_images/small_gray_warning.png); }
     .reveal .alert-question {background-image:url(http://hplgit.github.io/doconce/bundled/html_images/small_gray_question.png); } */

</style>

""",
            body_header="""\
<body>
<div class="reveal">

<!-- Any section element inside the <div class="slides"> container
     is displayed as a slide -->

<div class="slides">
""",
            footer="""
</div> <!-- class="slides" -->
</div> <!-- class="reveal" -->

<script src="reveal.js/lib/js/head.min.js"></script>
<script src="reveal.js/js/reveal.min.js"></script>

<script>
// Full list of configuration options available here:
// https://github.com/hakimel/reveal.js#configuration
Reveal.initialize({

    // Display navigation controls in the bottom right corner
    controls: true,

    // Display progress bar (below the horiz. slider)
    progress: true,

    // Display the page number of the current slide
    slideNumber: true,

    // Push each slide change to the browser history
    history: false,

    // Enable keyboard shortcuts for navigation
    keyboard: true,

    // Enable the slide overview mode
    overview: true,

    // Vertical centering of slides
    //center: true,
    center: false,

    // Enables touch navigation on devices with touch input
    touch: true,

    // Loop the presentation
    loop: false,

    // Change the presentation direction to be RTL
    rtl: false,

    // Turns fragments on and off globally
    fragments: true,

    // Flags if the presentation is running in an embedded mode,
    // i.e. contained within a limited portion of the screen
    embedded: false,

    // Number of milliseconds between automatically proceeding to the
    // next slide, disabled when set to 0, this value can be overwritten
    // by using a data-autoslide attribute on your slides
    autoSlide: 0,

    // Stop auto-sliding after user input
    autoSlideStoppable: true,

    // Enable slide navigation via mouse wheel
    mouseWheel: false,

    // Hides the address bar on mobile devices
    hideAddressBar: true,

    // Opens links in an iframe preview overlay
    previewLinks: false,

    // Transition style
    transition: 'default', // default/cube/page/concave/zoom/linear/fade/none

    // Transition speed
    transitionSpeed: 'default', // default/fast/slow

    // Transition style for full page slide backgrounds
    backgroundTransition: 'default', // default/none/slide/concave/convex/zoom

    // Number of slides away from the current that are visible
    viewDistance: 3,

    // Parallax background image
    //parallaxBackgroundImage: '', // e.g. "'https://s3.amazonaws.com/hakim-static/reveal-js/reveal-parallax-1.jpg'"

    // Parallax background size
    //parallaxBackgroundSize: '' // CSS syntax, e.g. "2100px 900px"

    theme: Reveal.getQueryHash().theme, // available themes are in reveal.js/css/theme
    transition: Reveal.getQueryHash().transition || 'default', // default/cube/page/concave/zoom/linear/none

});

Reveal.initialize({
    dependencies: [
        // Cross-browser shim that fully implements classList - https://github.com/eligrey/classList.js/
        { src: 'reveal.js/lib/js/classList.js', condition: function() { return !document.body.classList; } },

        // Interpret Markdown in <section> elements
        { src: 'reveal.js/plugin/markdown/marked.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
        { src: 'reveal.js/plugin/markdown/markdown.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },

        // Syntax highlight for <code> elements
        { src: 'reveal.js/plugin/highlight/highlight.js', async: true, callback: function() { hljs.initHighlightingOnLoad(); } },

        // Zoom in and out with Alt+click
        { src: 'reveal.js/plugin/zoom-js/zoom.js', async: true, condition: function() { return !!document.body.classList; } },

        // Speaker notes
        { src: 'reveal.js/plugin/notes/notes.js', async: true, condition: function() { return !!document.body.classList; } },

        // Remote control your reveal.js presentation using a touch device
        //{ src: 'reveal.js/plugin/remotes/remotes.js', async: true, condition: function() { return !!document.body.classList; } },

        // MathJax
        //{ src: 'reveal.js/plugin/math/math.js', async: true }
    ]
});

Reveal.initialize({

    // The "normal" size of the presentation, aspect ratio will be preserved
    // when the presentation is scaled to fit different resolutions. Can be
    // specified using percentage units.
    width: 1170,  // original: 960,
    height: 700,

    // Factor of the display size that should remain empty around the content
    margin: 0.1,

    // Bounds for smallest/largest possible scale to apply to content
    minScale: 0.2,
    maxScale: 1.0

});
</script>

<!-- begin footer logo
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 0px">
<img src="somelogo.png">
</div>
     end footer logo -->

""",
            theme=None,
            title=None,
            ),
        csss=dict(
            subdir='csss',
            default_theme='csss_default',
            slide_envir_begin='<section class="slide">',
            slide_envir_end='</section>',
            pop=('delayed', 'li'),
            notes='<p class="presenter-notes">\n<!-- press "Ctrl+P" or "Shift+P" to activate -->\n\\g<1>\n</p>\n',
            head_header="""
<!-- CSSS: http://leaverou.github.com/CSSS/ -->

<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<link href="csss/slideshow.css" rel="stylesheet" />
<link href="csss/theme.css" rel="stylesheet" />
<link href="csss/talk.css" rel="stylesheet" />
<script src="csss/prefixfree.min.js"></script>
""",
            body_header="""\
<body data-duration="10">
""",
            footer="""
<script src="csss/slideshow.js"></script>
<script src="csss/plugins/css-edit.js"></script>
<script src="csss/plugins/css-snippets.js"></script>
<script src="csss/plugins/css-controls.js"></script>
<script src="csss/plugins/code-highlight.js"></script>
<script>
var slideshow = new SlideShow();

var snippets = document.querySelectorAll('.snippet');
for(var i=0; i<snippets.length; i++) {
	new CSSSnippet(snippets[i]);
}

var cssControls = document.querySelectorAll('.css-control');
for(var i=0; i<cssControls.length; i++) {
	new CSSControl(cssControls[i]);
}
</script>
""",
            theme=None,
            title=None,
            ),
        dzslides=dict(
            subdir=None,
            default_theme='dzslides_default',  # just one theme in dzslides
            slide_envir_begin='<section>',
            slide_envir_end='</section>',
            #notes='<div role="note">\n\g<1>\n</div>',
            pop=('incremental', 'ul', 'ol'),
            notes='<details>\n<!-- use onstage shell to activate: invoke http://hplgit.github.io/doconce/bundled/dzslides/shells/onstage.html -->\n\\g<1>\n</details>\n',
            #notes='<div role="note">\n<!-- use onstage shell to activate: invoke http://hplgit.github.io/doconce/bundled/dzslides/shells/onstage.html -->\n\\g<1>\n</div>\n',
            head_header="""
<!-- dzslides: http://paulrouget.com/dzslides/ -->

<!-- One section is one slide -->
""",
            body_header="""\
<body>
""",
            footer="""
<!-- Define the style of your presentation -->

<!--
Style by Hans Petter Langtangen hpl@simula.no:
a slight modification of the original dzslides style,
basically smaller fonts and left-adjusted titles.
-->

<!-- Maybe a font from http://www.google.com/webfonts ? -->
<link href='http://fonts.googleapis.com/css?family=Oswald' rel='stylesheet'>

<style>
  html, .view body { background-color: black; counter-reset: slideidx; }
  body, .view section { background-color: white; border-radius: 12px }
  /* A section is a slide. It's size is 800x600, and this will never change */
  section, .view head > title {
      /* The font from Google */
      font-family: 'Oswald', arial, serif;
      font-size: 30px;
  }

  .view section:after {
    counter-increment: slideidx;
    content: counter(slideidx, decimal-leading-zero);
    position: absolute; bottom: -80px; right: 100px;
    color: white;
  }

  .view head > title {
    color: white;
    text-align: center;
    margin: 1em 0 1em 0;
  }

  center {
    font-size: 20px;
  }
  h1 {
    margin-top: 100px;
    text-align: center;
    font-size: 50px;
  }
  h2 {
    margin-top: 10px;
    margin: 25px;
    text-align: left;
    font-size: 40px;
  }
  h3 {
    margin-top: 10px;
    margin: 25px;
    text-align: left;
    font-size: 30px;

  }

  ul {
    margin: 0px 60px;
    font-size: 20px;
  }

  ol {
    margin: 0px 60px;
    font-size: 20px;
  }

  p {
    margin: 25px;
    font-size: 20px;
  }

  pre {
    font-size: 50%;
    margin: 25px;
  }

  blockquote {
    height: 100%;
    background-color: black;
    color: white;
    font-size: 60px;
    padding: 50px;
  }
  blockquote:before {
    content: open-quote;
  }
  blockquote:after {
    content: close-quote;
  }

  /* Figures are displayed full-page, with the caption
     on top of the image/video */
  figure {
    background-color: black;
    width: 100%;
    height: 100%;
  }
  figure > * {
    position: absolute;
  }
  figure > img, figure > video {
    width: 100%; height: 100%;
  }
  figcaption {
    margin: 70px;
    font-size: 50px;
  }

  footer {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 40px;
    text-align: right;
    background-color: #F3F4F8;
    border-top: 1px solid #CCC;
  }

  /* Transition effect */
  /* Feel free to change the transition effect for original
     animations. See here:
     https://developer.mozilla.org/en/CSS/CSS_transitions
     How to use CSS3 Transitions: */
  section {
    -moz-transition: left 400ms linear 0s;
    -webkit-transition: left 400ms linear 0s;
    -ms-transition: left 400ms linear 0s;
    transition: left 400ms linear 0s;
  }
  .view section {
    -moz-transition: none;
    -webkit-transition: none;
    -ms-transition: none;
    transition: none;
  }

  .view section[aria-selected] {
    border: 5px red solid;
  }

  /* Before */
  section { left: -150%; }
  /* Now */
  section[aria-selected] { left: 0; }
  /* After */
  section[aria-selected] ~ section { left: +150%; }

  /* Incremental elements */

  /* By default, visible */
  .incremental > * { opacity: 1; }

  /* The current item */
  .incremental > *[aria-selected] { opacity: 1; }

  /* The items to-be-selected */
  .incremental > *[aria-selected] ~ * { opacity: 0; }

  /* The progressbar, at the bottom of the slides, show the global
     progress of the presentation. */
  #progress-bar {
    height: 2px;
    background: #AAA;
  }
</style>

<!-- {{{{ dzslides core
#
#
#     __  __  __       .  __   ___  __
#    |  \  / /__` |    | |  \ |__  /__`
#    |__/ /_ .__/ |___ | |__/ |___ .__/ core
#
#
# The following block of code is not supposed to be edited.
# But if you want to change the behavior of these slides,
# feel free to hack it!
#
-->

<div id="progress-bar"></div>

<!-- Default Style -->
<style>
  * { margin: 0; padding: 0; -moz-box-sizing: border-box; -webkit-box-sizing: border-box; box-sizing: border-box; }
  [role="note"] { display: none; }
  body {
    width: 800px; height: 600px;
    margin-left: -400px; margin-top: -300px;
    position: absolute; top: 50%; left: 50%;
    overflow: hidden;
    display: none;
  }
  .view body {
    position: static;
    margin: 0; padding: 0;
    width: 100%; height: 100%;
    display: inline-block;
    overflow: visible; overflow-x: hidden;
    /* undo Dz.onresize */
    transform: none !important;
    -moz-transform: none !important;
    -webkit-transform: none !important;
    -o-transform: none !important;
    -ms-transform: none !important;
  }
  .view head, .view head > title { display: block }
  section {
    position: absolute;
    pointer-events: none;
    width: 100%; height: 100%;
  }
  .view section {
    pointer-events: auto;
    position: static;
    width: 800px; height: 600px;
    margin: -150px -200px;
    float: left;

    transform: scale(.4);
    -moz-transform: scale(.4);
    -webkit-transform: scale(.4);
    -o-transform: scale(.4);
    -ms-transform: scale(.4);
  }
  .view section > * { pointer-events: none; }
  section[aria-selected] { pointer-events: auto; }
  html { overflow: hidden; }
  html.view { overflow: visible; }
  body.loaded { display: block; }
  .incremental {visibility: hidden; }
  .incremental[active] {visibility: visible; }
  #progress-bar{
    bottom: 0;
    position: absolute;
    -moz-transition: width 400ms linear 0s;
    -webkit-transition: width 400ms linear 0s;
    -ms-transition: width 400ms linear 0s;
    transition: width 400ms linear 0s;
  }
  .view #progress-bar {
    display: none;
  }
</style>

<script>
  var Dz = {
    remoteWindows: [],
    idx: -1,
    step: 0,
    html: null,
    slides: null,
    progressBar : null,
    params: {
      autoplay: "1"
    }
  };

  Dz.init = function() {
    document.body.className = "loaded";
    this.slides = Array.prototype.slice.call($$("body > section"));
    this.progressBar = $("#progress-bar");
    this.html = document.body.parentNode;
    this.setupParams();
    this.onhashchange();
    this.setupTouchEvents();
    this.onresize();
    this.setupView();
  }

  Dz.setupParams = function() {
    var p = window.location.search.substr(1).split('&');
    p.forEach(function(e, i, a) {
      var keyVal = e.split('=');
      Dz.params[keyVal[0]] = decodeURIComponent(keyVal[1]);
    });
  // Specific params handling
    if (!+this.params.autoplay)
      $$.forEach($$("video"), function(v){ v.controls = true });
  }

  Dz.onkeydown = function(aEvent) {
    // Don't intercept keyboard shortcuts
    if (aEvent.altKey
      || aEvent.ctrlKey
      || aEvent.metaKey
      || aEvent.shiftKey) {
      return;
    }
    if ( aEvent.keyCode == 37 // left arrow
      || aEvent.keyCode == 38 // up arrow
      || aEvent.keyCode == 33 // page up
    ) {
      aEvent.preventDefault();
      this.back();
    }
    if ( aEvent.keyCode == 39 // right arrow
      || aEvent.keyCode == 40 // down arrow
      || aEvent.keyCode == 34 // page down
    ) {
      aEvent.preventDefault();
      this.forward();
    }
    if (aEvent.keyCode == 35) { // end
      aEvent.preventDefault();
      this.goEnd();
    }
    if (aEvent.keyCode == 36) { // home
      aEvent.preventDefault();
      this.goStart();
    }
    if (aEvent.keyCode == 32) { // space
      aEvent.preventDefault();
      this.toggleContent();
    }
    if (aEvent.keyCode == 70) { // f
      aEvent.preventDefault();
      this.goFullscreen();
    }
    if (aEvent.keyCode == 79) { // o
      aEvent.preventDefault();
      this.toggleView();
    }
  }

  /* Touch Events */

  Dz.setupTouchEvents = function() {
    var orgX, newX;
    var tracking = false;

    var db = document.body;
    db.addEventListener("touchstart", start.bind(this), false);
    db.addEventListener("touchmove", move.bind(this), false);

    function start(aEvent) {
      aEvent.preventDefault();
      tracking = true;
      orgX = aEvent.changedTouches[0].pageX;
    }

    function move(aEvent) {
      if (!tracking) return;
      newX = aEvent.changedTouches[0].pageX;
      if (orgX - newX > 100) {
        tracking = false;
        this.forward();
      } else {
        if (orgX - newX < -100) {
          tracking = false;
          this.back();
        }
      }
    }
  }

  Dz.setupView = function() {
    document.body.addEventListener("click", function ( e ) {
      if (!Dz.html.classList.contains("view")) return;
      if (!e.target || e.target.nodeName != "SECTION") return;

      Dz.html.classList.remove("view");
      Dz.setCursor(Dz.slides.indexOf(e.target) + 1);
    }, false);
  }

  /* Adapt the size of the slides to the window */

  Dz.onresize = function() {
    var db = document.body;
    var sx = db.clientWidth / window.innerWidth;
    var sy = db.clientHeight / window.innerHeight;
    var transform = "scale(" + (1/Math.max(sx, sy)) + ")";

    db.style.MozTransform = transform;
    db.style.WebkitTransform = transform;
    db.style.OTransform = transform;
    db.style.msTransform = transform;
    db.style.transform = transform;
  }


  Dz.getNotes = function(aIdx) {
    var s = $("section:nth-of-type(" + aIdx + ")");
    var d = s.$("[role='note']");
    return d ? d.innerHTML : "";
  }

  Dz.onmessage = function(aEvent) {
    var argv = aEvent.data.split(" "), argc = argv.length;
    argv.forEach(function(e, i, a) { a[i] = decodeURIComponent(e) });
    var win = aEvent.source;
    if (argv[0] === "REGISTER" && argc === 1) {
      this.remoteWindows.push(win);
      this.postMsg(win, "REGISTERED", document.title, this.slides.length);
      this.postMsg(win, "CURSOR", this.idx + "." + this.step);
      return;
    }
    if (argv[0] === "BACK" && argc === 1)
      this.back();
    if (argv[0] === "FORWARD" && argc === 1)
      this.forward();
    if (argv[0] === "START" && argc === 1)
      this.goStart();
    if (argv[0] === "END" && argc === 1)
      this.goEnd();
    if (argv[0] === "TOGGLE_CONTENT" && argc === 1)
      this.toggleContent();
    if (argv[0] === "SET_CURSOR" && argc === 2)
      window.location.hash = "#" + argv[1];
    if (argv[0] === "GET_CURSOR" && argc === 1)
      this.postMsg(win, "CURSOR", this.idx + "." + this.step);
    if (argv[0] === "GET_NOTES" && argc === 1)
      this.postMsg(win, "NOTES", this.getNotes(this.idx));
  }

  Dz.toggleContent = function() {
    // If a Video is present in this new slide, play it.
    // If a Video is present in the previous slide, stop it.
    var s = $("section[aria-selected]");
    if (s) {
      var video = s.$("video");
      if (video) {
        if (video.ended || video.paused) {
          video.play();
        } else {
          video.pause();
        }
      }
    }
  }

  Dz.setCursor = function(aIdx, aStep) {
    // If the user change the slide number in the URL bar, jump
    // to this slide.
    aStep = (aStep != 0 && typeof aStep !== "undefined") ? "." + aStep : ".0";
    window.location.hash = "#" + aIdx + aStep;
  }

  Dz.onhashchange = function() {
    var cursor = window.location.hash.split("#"),
        newidx = 1,
        newstep = 0;
    if (cursor.length == 2) {
      newidx = ~~cursor[1].split(".")[0];
      newstep = ~~cursor[1].split(".")[1];
      if (newstep > Dz.slides[newidx - 1].$$('.incremental > *').length) {
        newstep = 0;
        newidx++;
      }
    }
    this.setProgress(newidx, newstep);
    if (newidx != this.idx) {
      this.setSlide(newidx);
    }
    if (newstep != this.step) {
      this.setIncremental(newstep);
    }
    for (var i = 0; i < this.remoteWindows.length; i++) {
      this.postMsg(this.remoteWindows[i], "CURSOR", this.idx + "." + this.step);
    }
  }

  Dz.back = function() {
    if (this.idx == 1 && this.step == 0) {
      return;
    }
    if (this.step == 0) {
      this.setCursor(this.idx - 1,
                     this.slides[this.idx - 2].$$('.incremental > *').length);
    } else {
      this.setCursor(this.idx, this.step - 1);
    }
  }

  Dz.forward = function() {
    if (this.idx >= this.slides.length &&
        this.step >= this.slides[this.idx - 1].$$('.incremental > *').length) {
        return;
    }
    if (this.step >= this.slides[this.idx - 1].$$('.incremental > *').length) {
      this.setCursor(this.idx + 1, 0);
    } else {
      this.setCursor(this.idx, this.step + 1);
    }
  }

  Dz.goStart = function() {
    this.setCursor(1, 0);
  }

  Dz.goEnd = function() {
    var lastIdx = this.slides.length;
    var lastStep = this.slides[lastIdx - 1].$$('.incremental > *').length;
    this.setCursor(lastIdx, lastStep);
  }

  Dz.toggleView = function() {
    this.html.classList.toggle("view");

    if (this.html.classList.contains("view")) {
      $("section[aria-selected]").scrollIntoView(true);
    }
  }

  Dz.setSlide = function(aIdx) {
    this.idx = aIdx;
    var old = $("section[aria-selected]");
    var next = $("section:nth-of-type("+ this.idx +")");
    if (old) {
      old.removeAttribute("aria-selected");
      var video = old.$("video");
      if (video) {
        video.pause();
      }
    }
    if (next) {
      next.setAttribute("aria-selected", "true");
      if (this.html.classList.contains("view")) {
        next.scrollIntoView();
      }
      var video = next.$("video");
      if (video && !!+this.params.autoplay) {
        video.play();
      }
    } else {
      // That should not happen
      this.idx = -1;
      // console.warn("Slide doesn't exist.");
    }
  }

  Dz.setIncremental = function(aStep) {
    this.step = aStep;
    var old = this.slides[this.idx - 1].$('.incremental > *[aria-selected]');
    if (old) {
      old.removeAttribute('aria-selected');
    }
    var incrementals = $$('.incremental');
    if (this.step <= 0) {
      $$.forEach(incrementals, function(aNode) {
        aNode.removeAttribute('active');
      });
      return;
    }
    var next = this.slides[this.idx - 1].$$('.incremental > *')[this.step - 1];
    if (next) {
      next.setAttribute('aria-selected', true);
      next.parentNode.setAttribute('active', true);
      var found = false;
      $$.forEach(incrementals, function(aNode) {
        if (aNode != next.parentNode)
          if (found)
            aNode.removeAttribute('active');
          else
            aNode.setAttribute('active', true);
        else
          found = true;
      });
    } else {
      setCursor(this.idx, 0);
    }
    return next;
  }

  Dz.goFullscreen = function() {
    var html = $('html'),
        requestFullscreen = html.requestFullscreen || html.requestFullScreen || html.mozRequestFullScreen || html.webkitRequestFullScreen;
    if (requestFullscreen) {
      requestFullscreen.apply(html);
    }
  }

  Dz.setProgress = function(aIdx, aStep) {
    var slide = $("section:nth-of-type("+ aIdx +")");
    if (!slide)
      return;
    var steps = slide.$$('.incremental > *').length + 1,
        slideSize = 100 / (this.slides.length - 1),
        stepSize = slideSize / steps;
    this.progressBar.style.width = ((aIdx - 1) * slideSize + aStep * stepSize) + '%';
  }

  Dz.postMsg = function(aWin, aMsg) { // [arg0, [arg1...]]
    aMsg = [aMsg];
    for (var i = 2; i < arguments.length; i++)
      aMsg.push(encodeURIComponent(arguments[i]));
    aWin.postMessage(aMsg.join(" "), "*");
  }

  function init() {
    Dz.init();
    window.onkeydown = Dz.onkeydown.bind(Dz);
    window.onresize = Dz.onresize.bind(Dz);
    window.onhashchange = Dz.onhashchange.bind(Dz);
    window.onmessage = Dz.onmessage.bind(Dz);
  }

  window.onload = init;
</script>


<script> // Helpers
  if (!Function.prototype.bind) {
    Function.prototype.bind = function (oThis) {

      // closest thing possible to the ECMAScript 5 internal IsCallable
      // function
      if (typeof this !== "function")
      throw new TypeError(
        "Function.prototype.bind - what is trying to be fBound is not callable"
      );

      var aArgs = Array.prototype.slice.call(arguments, 1),
          fToBind = this,
          fNOP = function () {},
          fBound = function () {
            return fToBind.apply( this instanceof fNOP ? this : oThis || window,
                   aArgs.concat(Array.prototype.slice.call(arguments)));
          };

      fNOP.prototype = this.prototype;
      fBound.prototype = new fNOP();

      return fBound;
    };
  }

  var $ = (HTMLElement.prototype.$ = function(aQuery) {
    return this.querySelector(aQuery);
  }).bind(document);

  var $$ = (HTMLElement.prototype.$$ = function(aQuery) {
    return this.querySelectorAll(aQuery);
  }).bind(document);

  $$.forEach = function(nodeList, fun) {
    Array.prototype.forEach.call(nodeList, fun);
  }

</script>
""",
            theme=None,
            title=None,
            ),
        deck=dict(
            subdir='deck.js',
            default_theme='web-2.0',
            slide_envir_begin='<section class="slide">',
            slide_envir_end='</section>',
            pop=('slide', 'li'),
            notes='<div class="notes">\n<!-- press "n" to activate -->\n\\g<1>\n</div>\n',
            head_header="""
<!-- deck.js: https://github.com/imakewebthings/deck.js -->

<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<meta name="viewport" content="width=1024, user-scalable=no">

<!-- Required stylesheet -->
<link rel="stylesheet" href="deck.js/core/deck.core.css">

<!-- Extension CSS files go here. Remove or add as needed.
deck.goto: Adds a shortcut key to jump to any slide number.
Hit g, type in the slide number, and hit enter.

deck.hash: Enables internal linking within slides, deep
linking to individual slides, and updates the address bar and
a permalink anchor with each slide change.

deck.menu: Adds a menu view, letting you see all slides in a grid.
Hit m to toggle to menu view, continue navigating your deck,
and hit m to return to normal view. Touch devices can double-tap
the deck to switch between views.

deck.navigation: Adds clickable left and right buttons for the
less keyboard inclined.

deck.status: Adds a page number indicator. (current/total).

deck.scale: Scales each slide to fit within the deck container
using CSS Transforms for those browsers that support them.

deck.pointer: Turn mouse into laser pointer (toggle with p).
(Requires https://github.com/mikeharris100/deck.pointer.js)
-->

<link rel="stylesheet" href="deck.js/extensions/menu/deck.menu.css">
<link rel="stylesheet" href="deck.js/extensions/navigation/deck.navigation.css">
<link rel="stylesheet" href="deck.js/extensions/scale/deck.scale.css">
<link rel="stylesheet" href="deck.js/extensions/pointer/deck.pointer.css">
<link rel="stylesheet" href="deck.js/extensions/notes/deck.notes.css">
<!--
<link rel="stylesheet" href="deck.js/extensions/goto/deck.goto.css">
<link rel="stylesheet" href="deck.js/extensions/hash/deck.hash.css">
<link rel="stylesheet" href="deck.js/extensions/status/deck.status.css">
-->

<!-- Style theme. More available in themes/style/ or create your own. -->
<link rel="stylesheet" href="deck.js/themes/style/%(theme)s.css">

<!--
<link rel="stylesheet" href="deck.js/themes/style/neon.css">
<link rel="stylesheet" href="deck.js/themes/style/swiss.css">
<link rel="stylesheet" href="deck.js/themes/style/web-2.0.css">

git clone git://github.com/duijf/mnml.git
<link rel="stylesheet" href="deck.js/themes/style/mnml.css">

git://github.com/groovecoder/deckjs-theme-mozilla.git
<link rel="stylesheet" href="deck.js/themes/style/sandstone.css">
<link rel="stylesheet" href="deck.js/themes/style/sandstone.aurora.css">
<link rel="stylesheet" href="deck.js/themes/style/sandstone.dark.css">
<link rel="stylesheet" href="deck.js/themes/style/sandstone.default.css">
<link rel="stylesheet" href="deck.js/themes/style/sandstone.firefox.css">
<link rel="stylesheet" href="deck.js/themes/style/sandstone.light.css">
<link rel="stylesheet" href="deck.js/themes/style/sandstone.mdn.css">
<link rel="stylesheet" href="deck.js/themes/style/sandstone.nightly.css">
<link rel="stylesheet" href="deck.js/themes/style/sandstone.cbc.css">

git://github.com/barraq/deck.ext.js.git
<link rel="stylesheet" href="deck.js/themes/style/beamer.css">
-->

<!--
Transition theme. More available in /themes/transition/ or create your own. -->
<!--
<link rel="stylesheet" href="deck.js/themes/transition/horizontal-slide.css">
<link rel="stylesheet" href="deck.js/themes/transition/fade.css">
<link rel="stylesheet" href="deck.js/themes/transition/vertical-slide.css">
<link rel="stylesheet" href="deck.js/themes/transition/horizontal-slide.css">
-->

<!-- Required Modernizr file -->
<script src="deck.js/modernizr.custom.js"></script>

<style type="text/css">
/* Override h1, h2, ... styles */
h1 { font-size: 2.8em; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.4em; }
h4 { font-size: 1.3em; }
h1, h2, h3, h4 { font-weight: bold; line-height: 1.2; }
body { overflow: auto; } /* vertical scrolling */

hr { border: 0; width: 80%%; border-bottom: 1px solid #aaa}
p.caption { width: 80%%; font-size: 60%%; font-style: italic; text-align: left; }
hr.figure { border: 0; width: 80%%; border-bottom: 1px solid #aaa}
.slide .alert-text-small   { font-size: 80%%;  }
.slide .alert-text-large   { font-size: 130%%; }
.slide .alert-text-normal  { font-size: 90%%;  }
.slide .alert {
     padding:8px 35px 8px 14px; margin-bottom:18px;
     text-shadow:0 1px 0 rgba(255,255,255,0.5);
     border:5px solid #bababa;
       -webkit-border-radius:14px; -moz-border-radius:14px;
     border-radius:14px
     background-position: 10px 10px;
     background-repeat: no-repeat;
     background-size: 38px;
     padding-left: 30px; /* 55px; if icon */
 }
 .slide .alert-block {padding-top:14px; padding-bottom:14px}
 .slide .alert-block > p, .alert-block > ul {margin-bottom:0}
 /*.slide .alert li {margin-top: 1em}*/
 .deck .alert-block p+p {margin-top:5px}
 /*.slide .alert-notice { background-image: url(http://hplgit.github.io/doconce/bundled/html_images//small_gray_notice.png); }
 .slide .alert-summary  { background-image:url(http://hplgit.github.io/doconce/bundled/html_images//small_gray_summary.png); }
 .slide .alert-warning { background-image: url(http://hplgit.github.io/doconce/bundled/html_images//small_gray_warning.png); }
 .slide .alert-question {background-image:url(http://hplgit.github.io/doconce/bundled/html_images/small_gray_question.png); } */

</style>

""",
            body_header="""\
<body class="deck-container">

<header>
<!-- Here goes a potential header -->
</header>

<!-- do not use the article tag - it gives strange sizings -->
""",
            footer="""

<footer>
<!-- Here goes a footer -->
</footer>

<!-- Begin extension snippets. Add or remove as needed. -->

<!-- deck.navigation snippet -->
<a href="#" class="deck-prev-link" title="Previous">&#8592;</a>
<a href="#" class="deck-next-link" title="Next">&#8594;</a>

<!-- deck.status snippet
<p class="deck-status">
	<span class="deck-status-current"></span>
	/
	<span class="deck-status-total"></span>
</p>
-->

<!-- deck.goto snippet
<form action="." method="get" class="goto-form">
	<label for="goto-slide">Go to slide:</label>
	<input type="text" name="slidenum" id="goto-slide" list="goto-datalist">
	<datalist id="goto-datalist"></datalist>
	<input type="submit" value="Go">
</form>
-->

<!-- deck.hash snippet
<a href="." title="Permalink to this slide" class="deck-permalink">#</a>
-->

<!-- End extension snippets. -->


<!-- Required JS files. -->
<script src="deck.js/jquery.min.js"></script>
<script src="deck.js/core/deck.core.js"></script>

<!-- Extension JS files. Add or remove as needed. -->
<script src="deck.js/core/deck.core.js"></script>
<script src="deck.js/extensions/hash/deck.hash.js"></script>
<script src="deck.js/extensions/menu/deck.menu.js"></script>
<script src="deck.js/extensions/goto/deck.goto.js"></script>
<script src="deck.js/extensions/status/deck.status.js"></script>
<script src="deck.js/extensions/navigation/deck.navigation.js"></script>
<script src="deck.js/extensions/scale/deck.scale.js"></script>
<script src="deck.js/extensions/notes/deck.notes.js"></script>

<!-- From https://github.com/mikeharris100/deck.pointer.js -->
<script src="deck.js/extensions/pointer/deck.pointer.js"></script>

<!-- From https://github.com/stvnwrgs/presenterview
<script type="text/javascript" src="deck.js/extensions/presenterview/deck.presenterview.js"></script> -->

<!-- From https://github.com/nemec/deck.annotate.js
<script type="text/javascript" src="deck.js/extensions/deck.annotate.js/deck.annotate.js"></script>
-->


<!-- Initialize the deck. You can put this in an external file if desired. -->
<script>
	$(function() {
		$.deck('.slide');
	});
</script>
""",
            theme=None,
            title=None,
            ),
        html5slides=dict(
            subdir=None,
            default_theme='template-default',  # template-io2011, should use template-io2012: https://code.google.com/p/io-2012-slides/
            slide_envir_begin='<article>',
            slide_envir_end='</article>',
            pop=('build', 'ul'),
            notes='<aside class="note">\n<!-- press "p" to activate -->\n\\g<1>\n</aside>\n',
            head_header="""
<!-- Google HTML5 Slides:
     http://code.google.com/p/html5slides/
-->

<meta charset='utf-8'>
<script
   src='http://html5slides.googlecode.com/svn/trunk/slides.js'>
</script>

</head>

<style>
/* Your individual styles here... */
</style>
""",
            body_header="""\
 <body style='display: none'>

<!-- See http://code.google.com/p/html5slides/source/browse/trunk/styles.css
     for definition of template-default and other styles -->

<section class='slides layout-regular %(theme)s'>
<!-- <section class='slides layout-regular template-io2011'> -->
<!-- <section class='slides layout-regular template-default'> -->

<!-- Slides are in <article> tags -->

""",
            footer="""
</section>
""",
            theme=None,
            title=None,
            ),
        )

    theme = misc_option('html_slide_theme=', default='default')

    # Check that the theme name is registered
    #from doconce.misc import recommended_html_styles_and_pygments_styles
    all_combinations = recommended_html_styles_and_pygments_styles()
    if not slide_tp in all_combinations:
        # This test will not be run since it is already tested that
        # the slide type is legal (before calling this function)
        print '*** error: slide type "%s" is not known - abort' % slide_tp
        print 'known slide types:', ', '.join(list(all_combinations.keys()))
        _abort()

    # We need the subdir with reveal.js, deck.js, or similar to show
    # the HTML slides so add the subdir to the registered file collection
    if slide_syntax[slide_tp]['subdir'] is not None:
        import html
        html.add_to_file_collection(
            slide_syntax[slide_tp]['subdir'], filename, 'a')

    if theme != 'default':
        if not theme in all_combinations[slide_tp]:
            print '*** error: %s theme "%s" is not known - abort' % \
                  (slide_tp, theme)
            print 'known themes:', ', '.join(list(all_combinations[slide_tp].keys()))
            _abort()

    #m = re.search(r'<title>(.*?)</title>', ''.join(parts[0]))
    #if m:
    #    title = m.group(1).strip()
    #else:
    #    title = ''
    #slide_syntax[slide_tp]['title'] = title
    slide_syntax[slide_tp]['theme'] = \
       slide_syntax[slide_tp]['default_theme'] if (theme == 'default' or theme.endswith('_default')) else theme

    # Fill in theme etc.
    slide_syntax[slide_tp]['head_header'] = \
           slide_syntax[slide_tp]['head_header'] % slide_syntax[slide_tp]
    slide_syntax[slide_tp]['body_header'] = \
           slide_syntax[slide_tp]['body_header'] % slide_syntax[slide_tp]

    footer_logo = misc_option('html_footer_logo=', default=None)

    # Handle short forms for cbc, simula, and uio logos
    if footer_logo == 'cbc':
        footer_logo = 'cbc_footer'
    elif footer_logo == 'simula':
        footer_logo = 'simula_footer'
    elif footer_logo == 'uio':
        footer_logo = 'uio_footer'

    # Default footer logo command
    repl = """
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 0px;">
<img src="%s/cbc_footer.png" width=110%%;></div>
""" % footer_logo

    # Override repl for cbc, simula, uio logos since these are specified
    # without full URLs

    # Path to cbc, simula, uio logo files
    footer_logo_path = dict(reveal='reveal.js/css/images',
                            deck='deck.js/themes/images')
    if footer_logo == 'cbc_footer':
        if slide_tp not in ('reveal', 'deck'):
            raise ValueError('slide type "%s" cannot have --html_footer_logo' ^ slide_tp)
        repl = """
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 0px;">
<img src="%s/cbc_footer.png" width=110%%;></div>
""" % footer_logo_path[slide_tp]
    elif footer_logo == 'cbc_symbol':
        repl = """
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 20px;">
<img src="%s/cbc_symbol.png" width="50"></div>
""" % footer_logo_path[slide_tp]
    elif footer_logo == 'simula_footer':
        repl = """
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 0px;">
<img src="%s/simula_footer.png" width=700></div>
""" % footer_logo_path[slide_tp]
    elif footer_logo == 'simula_symbol':
        repl = """
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 10px;">
<img src="%s/simula_symbol.png" width=200></div>
""" % footer_logo_path[slide_tp]
    elif footer_logo == 'uio_footer':
        repl = """
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 0px;">
<img src="%s/uio_footer.png" width=450></div>
""" % footer_logo_path[slide_tp]
    elif footer_logo == 'uio_symbol':
        repl = """
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 20px;">
<img src="%s/uio_symbol.png" width=100></div>
""" % footer_logo_path[slide_tp]
    elif footer_logo == 'uio_simula_symbol':
        repl = """
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 20px; margin-bottom: 0px;">
<img src="%s/uio_footer.png" width="180"></div>
<div style="position: absolute; bottom: 0px; left: 0; margin-left: 250px; margin-bottom: 0px;">
<img src="%s/simula_symbol.png" width="250"></div>
""" % (footer_logo_path[slide_tp], footer_logo_path[slide_tp])

    pattern = dict(
        reveal=r'<!-- begin footer logo\s+(.+?)\s+end footer logo -->',
        deck=r'<!-- Here goes a footer -->')

    if footer_logo is not None:
        slide_syntax[slide_tp]['footer'] = re.sub(
            pattern[slide_tp], repl,
            slide_syntax[slide_tp]['footer'], flags=re.DOTALL)

    # Grab the relevant lines in the <head> and <body> parts of
    # the original header
    head_lines = []
    body_lines = []
    inside_style = False
    inside_head = False
    inside_body = False
    for line in header:
        if '<head>' in line:
            inside_head = True
            continue
        elif '</head>' in line:
            inside_head = False
            continue
        elif line.strip().startswith('<body'):
            inside_body = True
            continue
        elif '</body>' in line:
            inside_body = False
            continue
        elif line.strip().startswith('<style'):
            inside_style = True
            continue
        elif '</style>' in line:
            inside_style = False
            continue
        if inside_style:
            continue  # skip style lines
        elif inside_body:
            body_lines.append(line)
        elif inside_head:
            head_lines.append(line)
    slide_syntax[slide_tp]['head_lines'] = ''.join(head_lines)
    slide_syntax[slide_tp]['body_lines'] = ''.join(body_lines)

    #<title>%(title)s</title>
    slides = """\
<!DOCTYPE html>

%(head_lines)s

%(head_header)s

<!-- Styles for table layout of slides -->
<style type="text/css">
td.padding {
  padding-top:20px;
  padding-bottom:20px;
  padding-right:50px;
  padding-left:50px;
}
</style>

</head>

%(body_header)s

%(body_lines)s

""" % slide_syntax[slide_tp]

    # Avoid too many numbered equations: use \tag for all equations
    # with labels (these get numbers) and turn all other numbers off
    # by autoNumber: "none"
    slides = slides.replace('autoNumber: "AMS"', 'autoNumber: "none"')

    for part_no, part in enumerate(parts):
        part = ''.join(part)

        if '<!-- begin inline comment' in part:
            pattern = r'<!-- begin inline comment -->\s*\[<b>.+?</b>:\s*<em>(.+?)</em>]\s*<!-- end inline comment -->'
            part = re.sub(pattern,
                          slide_syntax[slide_tp]['notes'], part,
                          flags=re.DOTALL)

        if '<!-- !bnotes' in part:
            pattern = r'<!-- !bnotes .*?-->(.+?)<!-- !enotes.*?-->'
            part = re.sub(pattern,
                          slide_syntax[slide_tp]['notes'], part,
                          flags=re.DOTALL)

        if slide_tp == 'deck':
            if '<!-- document title -->' in part:
                # h1 title should be h2 to fix problems with
                # .csstransforms h1, .csstransforms .vcenter in css files
                pattern = r'<center><h1>(.+?)</h1></center>'
                part = re.sub(pattern,
                              r'<h2 style="text-align: center;">\g<1></h2>',
                              part)
                # Date should use b rather than h4 (which is too big)
                pattern = '<center><h4>(.+?)</h4></center>'
                part = re.sub(pattern, r'<center><b>\g<1></b></center>', part)

            # <b> does not work, so we must turn on bold manually
            part = part.replace('<b>', '<b style="font-weight: bold">')

        if slide_tp in ('deck', 'reveal'):
            # Add more space around equations
            part = re.sub(r'\$\$([^$]+)\$\$',
                          #r'<p>&nbsp;<br>&nbsp;<br>\n$$\g<1>$$\n&nbsp;<br>',
                          r'<p>&nbsp;<br>\n$$\g<1>$$\n<p>&nbsp;<br>',
                          part)

        if slide_tp == 'reveal' and part_no == 0:
            # Add space after names and after institutions
            part = re.sub(r'<p>\s+<!-- institution\(s\)',
                          r'<p>&nbsp;<br>\n<!-- institution(s)', part)
            part = re.sub(r'<p>\s+<center><h4>(.+?)</h4></center>\s+<!-- date -->',
                          r'<p>&nbsp;<br>\n<center><h4>\g<1></h4></center> <!-- date -->',
                          part)

        #if '!bpop' not in part:
        #if slide_tp in ['reveal']:
        part = part.replace('<li>', '<p><li>')  # more space between bullets
        # else: the <p> destroys proper handling of incremental pop up
        # Try this for all and see if any problem appears
        part = part.replace('<li ', '<p><li ')  # more space between bullets

        # Find pygments style
        m = re.search(r'typeset with pygments style "(.+?)"', part)
        pygm_style = m.group(1) if m else 'plain <pre>'
        html_style = slide_syntax[slide_tp]['theme']
        recommended_combinations = all_combinations[slide_tp]
        if html_style in recommended_combinations:
            if pygm_style != 'plain <pre>' and \
               not pygm_style in recommended_combinations[html_style]:
                print '*** warning: pygments style "%s" is not '\
                      'recommended for "%s"!' % (pygm_style, html_style)
                print 'recommended styles are %s' % \
                (', '.join(['"%s"' % combination
                            for combination in
                            recommended_combinations[html_style]]))

        # Fix styles: native should have black background for dark themes
        if slide_syntax[slide_tp]['theme'] in ['neon', 'night', 'moon', 'blood']:
            if pygm_style == 'native':
                # Change to black background
                part = part.replace('background: #202020',
                                    'background: #000000')

        # Make h1 section headings centered
        part = part.replace('<h1>', '<h1 style="text-align: center;">')

        # Pieces to pop up item by item as the user is clicking
        if '<!-- !bpop' in part:
            pattern = r'<!-- !bpop (.*?)-->(.+?)<!-- !epop.*?-->'
            cpattern = re.compile(pattern, re.DOTALL)
            #import pprint;pprint.pprint(cpattern.findall(part))
            def subst(m):  # m is match object
                arg = m.group(1).strip()
                if arg:
                    arg = ' ' + arg

                inserted_pop_up = False
                class_tp = slide_syntax[slide_tp]['pop'][0]
                placements = slide_syntax[slide_tp]['pop'][1:]
                body = m.group(2)

                # Insert special pop-up tags for lists, admons, and
                # pygments code blocks first.
                # If none of these are found (inserted_pop_up = False)
                # mark the whole paragraph as pop-up element

                if '<ol>' in body or '<ul>' in body:
                    for tag in placements:
                        tag = '<%s>' % tag.lower()
                        if tag in body:
                            body = body.replace(tag, '%s class="%s%s">' % (tag[:-1], class_tp, arg))
                            inserted_pop_up = True
                if '<div class="alert' in body:
                    # Augment admonitions with pop-up syntax
                    body = body.replace('div class="alert',
                                        'div class="%s alert' % class_tp)
                    inserted_pop_up = True
                if '<div class="highlight' in body:
                    # Augment pygments blocks with pop-up syntax
                    body = body.replace('<div class="highlight',
                                        '<div class="%s" class="highlight' % class_tp)
                    inserted_pop_up = True
                if not inserted_pop_up:
                    # Treat whole block as pop-up paragraph

                    # Hack to preserve spacings before equation (see above),
                    # when <p> is removed (as we must do below)
                    body = body.replace('<p>&nbsp;<br>', '&nbsp;<br>&nbsp;<br>')
                    body = body.replace('<p>', '')  # can make strange behavior
                    # Add a <p class="fragments"> to the whole body
                    # (but only if not code or admon content?)
                    body2 = '\n<p class="%s">\n' % class_tp

                    # Add arguments specified after !bpop?
                    if slide_tp == 'reveal' and arg:  # reveal specific
                        args = arg.split()
                        for arg in args:
                            if arg:
                                body2 += '\n<span class="%s %s">\n' % (class_tp, arg)
                        body2 += body
                        for arg in args:
                            if arg:
                                body2 += '\n</span>\n'
                    else:
                        body2 += body
                    body2 += '\n</p>\n'
                    body = body2
                return body

            part = cpattern.sub(subst, part)

        # Special treatment of the text for some slide tools
        if slide_tp == 'deck':
            part = re.sub(r'<pre>(.+?)</pre>',
                          r'<pre><code>\g<1></code></pre>',
                          part, flags=re.DOTALL)
        if slide_tp == 'reveal':
            part = re.sub(r'<pre><code>(.+?)</code></pre>',
                          r'<pre><code data-trim contenteditable>\g<1></code></pre>',
                          part,
                          flags=re.DOTALL)

        # Add space after list, except in admons (ended by </div>)
        part = re.sub(r'</ul>(?!\s*</div>)', r'</ul>\n<p>', part)
        part = re.sub(r'</ol>(?!\s*</div>)', r'</ol>\n<p>', part)

        slides += """
%s
%s
%s

""" % (slide_syntax[slide_tp]['slide_envir_begin'],
       part,
       slide_syntax[slide_tp]['slide_envir_end'])
    slides += """
%s

</body>
</html>
""" % (slide_syntax[slide_tp]['footer'])
    slides = re.sub(r'<!-- !split .*-->\n', '', slides)

    eq_no = 1  # counter for equations
    # Insert \tag for each \label (\label only in equations in HTML)
    labels = re.findall(r'\\label\{(.+?)\}', slides)
    for label in labels:
        slides = slides.replace(r'\label{%s}' % label,
                                r'\tag{%s}' % eq_no)
        slides = slides.replace(r'\eqref{%s}' % label,
                                '<a href="#mjx-eqn-%s">(%s)</a>' %
                                (eq_no, eq_no))
        eq_no += 1

    if slide_tp == 'reveal':
        # Adjust font size in code
        slides = slides.replace('<pre style="', '<pre style="font-size: 80%; ')

    return slides


def _usage_slides_beamer():
    print """Usage: doconce slides_beamer mydoc --beamer_slide_theme=themename --beamer_slide_navigation=off --beamer_block_style=mdbox [--handout]

themename can be
red_plain, blue_plain, red_shadow, blue_shadow, dark, dark_gradient, vintage

--beamer_slide_navigation=on turns on navigation links in the header
and footer. The links are defined by sections (only), i.e., headings
with 7 = in the source file.

--beamer_block_style=X controls how beamer blocks are typeset.
X=native gives the standard beamer blocks.
X=mdbox gives a mdframed box around the content. This is preferable
for simple slide styles.

--handout is used for generating PDF that can be printed as handouts
(usually after using pdfnup to put multiple slides per sheet).
"""

def slides_beamer():
    """
    Split latex file into slides and typeset slides using
    various tools. Use !split command as slide separator.
    """

    if len(sys.argv) <= 1:
        _usage_slides_beamer()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.tex'):
        filename += '.tex'
    if not os.path.isfile(filename):
        print 'doconce file in latex format, %s, does not exist - abort' % filename
        _abort()
    basename = os.path.basename(filename)
    filestem = os.path.splitext(basename)[0]

    header, parts, footer = get_header_parts_footer(filename, "latex")
    parts = tablify(parts, "latex")

    filestr = generate_beamer_slides(header, parts, footer,
                                     basename, filename)

    if filestr is not None:
        f = open(filename, 'w')
        f.write(filestr)
        f.close()
        print 'slides written to', filename
        if misc_option('handout', False):
            print 'printing for handout:\npdfnup --nup 2x3 --frame true --delta "1cm 1cm" --scale 0.9 --outfile %s.pdf %s.pdf' % (filestem, filestem)


def _usage_slides_markdown():
    print """
Usage: doconce slides_markdown mydoc slide_type --slide_theme=dark

slide_type: remark (the only implemented so far)
--slide_theme: light (default) or dark

Output: mydoc.html
"""

def slides_markdown():
    """
    Transform markdown file to remark slides.
    Must have been generated by doconce format pandoc mydoc.html --github_md
    """

    if len(sys.argv) <= 2:
        _usage_slides_markdown()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.md'):
        filename += '.md'
    if not os.path.isfile(filename):
        print 'doconce file in html format, %s, does not exist' % filename
        _abort()

    f = open(filename, 'r')
    filestr = f.read()
    f.close()

    slide_type = sys.argv[2]
    if slide_type != 'remark':
        print '*** error: only remark slides are allowed, not %s' % slide_type

    template = """
<!DOCTYPE html>
<html>
<head>
<title>%(title)s</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<style type="text/css">
   @import url(http://fonts.googleapis.com/css?family=Yanone+Kaffeesatz);
   @import url(http://fonts.googleapis.com/css?family=Droid+Serif:400,700,400italic);
   @import url(http://fonts.googleapis.com/css?family=Ubuntu+Mono:400,700,400italic);

body { font-family: 'Droid Serif'; }
h1, h2, h3 {
  font-family: 'Yanone Kaffeesatz';
  font-weight: normal;
}
.remark-code, .remark-inline-code { font-family: 'Ubuntu Mono'; }
%(additional_styling)s
</style>
</head>

<body>
%(mathjax)s
<textarea id="source">

%(class_)s

%(main)s

</textarea>
<script src="http://gnab.github.io/remark/downloads/remark-latest.min.js" type="text/javascript">
</script>
<script type="text/javascript">
  var slideshow = remark.create();
</script>
</body>
</html>
"""

    theme = misc_option('slide_theme=', default='light')
    class_ = 'class: center, middle'
    additional_styling = ''
    if theme == 'dark':
        class_ = 'class: center, middle, inverse'
        additional_styling = """

/* Style taken from the official remark demo */
body { font-family: 'Droid Serif'; }
h1, h2, h3 {
  font-family: 'Yanone Kaffeesatz';
  font-weight: 400;
  margin-bottom: 0;
}
.remark-slide-content h1 { font-size: 3em; }
.remark-slide-content h2 { font-size: 2em; }
.remark-slide-content h3 { font-size: 1.6em; }
.footnote { position: absolute; bottom: 3em; }
li p { line-height: 1.25em; }
.red { color: #fa0000; }
.large { font-size: 2em; }
a, a > code { color: rgb(249, 38, 114); text-decoration: none; }
code {
  -moz-border-radius: 5px;
  -web-border-radius: 5px;
  background: #e7e8e2;
  border-radius: 5px;
}
.remark-code, .remark-inline-code { font-family: 'Ubuntu Mono'; }
.remark-code-line-highlighted { background-color: #373832; }
.pull-left { float: left; width: 47%; }
.pull-right { float: right; width: 47%; }
.pull-right ~ p { clear: both; }
#slideshow .slide .content code { font-size: 0.8em; }
#slideshow .slide .content pre code { font-size: 0.9em; padding: 15px; }
.inverse { background: #272822; color: #777872; text-shadow: 0 0 20px #333; }
.inverse h1, .inverse h2 {color: #f3f3f3; line-height: 0.8em; }
"""

    # MathJax?
    mathjax = ''
    if '$' in filestr:
        # Fix inline math $...$ to \\( ... \\)
        filestr = re.sub(r'([^$])\$([^$]+)\$([^$])',
                         r'\g<1>\\\\( \g<2> \\\\)\g<3>', filestr,
                         flags=re.DOTALL)
        # Remove newlines before and after equations inside $$--$$
        def subst(m):
            eq = m.group(1).strip()
            return '$$\n%s\n$$\n\n' % eq

        filestr = re.sub(r'^\$\$\n+(.+?)\$\$\n+', subst,
                         filestr, flags=re.MULTILINE|re.DOTALL)
        # Insert MathJax script and newcommands
        from html import mathjax_header
        mathjax = mathjax_header(filestr)

    # Fixes
    filestr = re.sub(r'^## ', '# ', filestr, flags=re.MULTILINE)
    filestr = re.sub(r'^### ', '## ', filestr, flags=re.MULTILINE)
    # Turn figures to HTML
    filestr = re.sub(r'^<!-- (<img.+?>.*) -->\n!\[.+$', r'.center[\g<1>]',
                     filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'^!\[(.*?)\]\((.+?)\)',
    #                 '.center[<img src="\g<2>" width=80%/>]',
    #                 filestr, flags=re.MULTILINE)

    # Remove notes
    filestr = re.sub(r'^<!-- !bnotes.+?^<!-- !enotes -->', '',
                     filestr, flags=re.MULTILINE|re.DOTALL)
    lines = filestr.splitlines()
    # Find title, author and date
    title = ''
    percentage_counter = 0
    for i in range(len(lines)):
        if lines[i].startswith('%'):
            percentage_counter += 1
        if percentage_counter == 1:
            # Title
            lines[i] = lines[i].replace('% ', '# ')
            title = lines[i][1:].lstrip()
        elif percentage_counter == 2:
            # Authors
            lines[i] = '\n\n###' + '\n\n###'.join(lines[i][1:].lstrip().split(';'))
        elif percentage_counter == 3:
            # Date
            lines[i] = lines[i].replace('% ', '\n\n### ')
            break

    filestr = '\n'.join(lines)

    # Drop pop ups and other constructions
    filestr = re.sub(r'^<!-- ![be]pop -->\s+', '', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'^<!-- ![be]slidecell.*\s*', '', filestr,
                     flags=re.MULTILINE)

    if '<!-- !bslidecell' in filestr:
        print '*** warning: !bslidecell-!eslidecell does not work with remark slides'
        print '    (all cells will be placed in their own row...)'

    if theme == 'dark':
        filestr = filestr.replace('<!-- !split -->', '---\nclass: inverse\n')
    else:
        filestr = filestr.replace('<!-- !split -->', '---\n')
    main = filestr
    template = template % vars()
    filename = filename.replace('.md', '.html')
    f = open(filename, 'w')
    f.write(template)
    f.close()
    print '%s slides in %s' % (slide_type, filename)

def generate_beamer_slides(header, parts, footer, basename, filename):
    # Styles: red/blue_plain/shadow, dark, dark_gradient, vintage
    header = ''.join(header)
    theme = misc_option('beamer_slide_theme=', default='default')
    if theme != 'default':
        beamerstyle = 'beamertheme' + theme
        packages = [beamerstyle]
        if theme == 'vintage':
            packages.append('vintage_background.png')
        copy_latex_packages(packages)
    handout = '[handout]' if misc_option('handout', False) else ''

    if misc_option('beamer_slide_navigation=', 'off') == 'on':
        frame_options = '[fragile]'
    else:
        # plain signifies no navigation
        frame_options = '[plain,fragile]'

    block_style = misc_option('beamer_block_style=', 'native')
    parskip = 0 if theme.endswith('_plain') else 7

    slides = r"""
%% LaTeX Beamer file automatically generated from DocOnce
%% https://github.com/hplgit/doconce

%%-------------------- begin beamer-specific preamble ----------------------

\documentclass%(handout)s{beamer}

\usetheme{%(theme)s}
\usecolortheme{default}

%% turn off the almost invisible, yet disturbing, navigation symbols:
\setbeamertemplate{navigation symbols}{}

%% Examples on customization:
%%\usecolortheme[named=RawSienna]{structure}
%%\usetheme[height=7mm]{Rochester}
%%\setbeamerfont{frametitle}{family=\rmfamily,shape=\itshape}
%%\setbeamertemplate{items}[ball]
%%\setbeamertemplate{blocks}[rounded][shadow=true]
%%\useoutertheme{infolines}
%%
%%\usefonttheme{}
%%\useinntertheme{}
%%
%%\setbeameroption{show notes}
%%\setbeameroption{show notes on second screen=right}

%% fine for B/W printing:
%%\usecolortheme{seahorse}

\usepackage{pgf,pgfarrows,pgfnodes,pgfautomata,pgfheaps,pgfshade}
\usepackage{graphicx}
\usepackage{epsfig}
\usepackage{relsize}

\usepackage{fancybox}  %% make sure fancybox is loaded before fancyvrb

\usepackage{fancyvrb}
%%\usepackage{minted} %% requires pygments and latex -shell-escape filename
%%\usepackage{anslistings}
%%\usepackage{listingsutf8}

\usepackage{amsmath,amssymb,bm}
%%\usepackage[latin1]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{colortbl}
\usepackage[english]{babel}
\usepackage{tikz}
\usepackage{framed}
%% Use some nice templates
\beamertemplatetransparentcovereddynamic

%% --- begin table of contents based on sections ---
%% Delete this, if you do not want the table of contents to pop up at
%% the beginning of each section:
%% (Only section headings can enter the table of contents in Beamer
%% slides generated from DocOnce source, while subsections are used
%% for the title in ordinary slides.)
\AtBeginSection[]
{
  \begin{frame}<beamer>[plain]
  \frametitle{}
  %%\frametitle{Outline}
  \tableofcontents[currentsection]
  \end{frame}
}
%% --- end table of contents based on sections ---

%% If you wish to uncover everything in a step-wise fashion, uncomment
%% the following command:

%%\beamerdefaultoverlayspecification{<+->}

\newcommand{\shortinlinecomment}[3]{\note{\textbf{#1}: #2}}
\newcommand{\longinlinecomment}[3]{\shortinlinecomment{#1}{#2}{#3}}

\definecolor{linkcolor}{rgb}{0,0,0.4}
\hypersetup{
    colorlinks=true,
    linkcolor=linkcolor,
    urlcolor=linkcolor,
    pdfmenubar=true,
    pdftoolbar=true,
    bookmarksdepth=3
    }
\setlength{\parskip}{%(parskip)spt}  %% {1em}

\newenvironment{doconceexercise}{}{}
\newcounter{doconceexercisecounter}
\newenvironment{doconce:movie}{}{}
\newcounter{doconce:movie:counter}

\newcommand{\subex}[1]{\noindent\textbf{#1}}  %% for subexercises: a), b), etc
""" % vars()

    # Check if we need minted or anslistings:
    if re.search('\\usepackage.+minted', header):
        slides = slides.replace(
            r'%\usepackage{minted}', r'\usepackage{minted}')
    if re.search('\\usepackage.+listings', header):
        m = re.search(r'^% Define colors.+?^% end of custom lstdefinestyles', header, flags=re.DOTALL|re.MULTILINE)
        lststyles = m.group() if m else ''
        slides = slides.replace(
            r'%\usepackage{listingsutf8}', r'\usepackage{listingsutf8}' + '\n\n' + lststyles)
    if re.search('\\usepackage.+anslistings', header):
        slides = slides.replace(
            r'%\usepackage{anslistings}', r'\usepackage{anslistings}')

    if block_style.startswith('mdbox'):
        # Add defnition of an appropriate mdframe
        slides += r"""
\usepackage[framemethod=TikZ]{mdframed}
\newcommand{\frametitlecolor}{gray!65!black}
%\usetikzlibrary{shadows}
%\usetikzlibrary{shadows.blur}
% block with title
\newenvironment{mdboxt}[1]{%
    \begin{mdframed}[%
        frametitle={#1\vphantom{\frametitlecolor}},
        skipabove=0.5\baselineskip,
        skipbelow=0.5\baselineskip,
        outerlinewidth=0.5pt,
        frametitlerule=true,
        frametitlebackgroundcolor=gray!15,
        frametitlefont=\normalfont,
        frametitleaboveskip=3pt,
        frametitlebelowskip=2pt,
        frametitlerulewidth=0.5pt,
        roundcorner=2pt,
        %shadow=true,
        %shadowcolor=green!10!black!40,
        %shadowsize=5pt
        %apptotikzsetting={\tikzset{mdfshadow/.style=blur shadow={shadow blur steps=5,shadow blur extra rounding=1.3pt,xshift=3pt,yshift=-3pt}}}
    ]%
}{\end{mdframed}}

% block without title
\newenvironment{mdbox}{%
    \begin{mdframed}[%
        roundcorner=2pt,
        %shadow=true,
        %shadowcolor=green!10!black!40,
        %shadowsize=5pt
        %apptotikzsetting={\tikzset{mdfshadow/.style=blur shadow={shadow blur steps=5,shadow blur extra rounding=1.3pt,xshift=3pt,yshift=-3pt}}}
    ]%
}{\end{mdframed}}

"""

    slides += r"""
%-------------------- end beamer-specific preamble ----------------------

% Add user's preamble

"""

    # Add possible user customization from the original latex file,
    # plus the newcommands and \begin{document}
    preamble_divider_line = '% --- end of standard preamble for documents ---'
    if preamble_divider_line not in header:
        print '*** error: generated latex document has missing'
        print '    title, author, and date - add TITLE:, AUTHOR:, DATE:'
        _abort()
    slides += header.split(preamble_divider_line)[1]

    for part in parts:
        part = ''.join(part)
        code_free_part = remove_verbatim_blocks(part, 'latex')

        if 'inlinecomment{' in part:
            # Inline comments are typeset as notes in this beamer preamble
            pass
        if '% !bnotes' in part:
            pattern = r'% !bnotes(.+?)% !enotes\s'
            part = re.sub(pattern,
                          r'\\note{\g<1>}', part,
                          flags=re.DOTALL)

        # Keep blocks or make mdbox
        if block_style.startswith('mdbox'):
            def subst(m):
                title = m.group(1).strip()
                text = m.group(2)
                b = 'mdboxt' if title else 'mdbox'
                s = r'\begin{%s}{%s}%s\end{%s}' % (b, title, text, b)
                return s

            pattern = r'\\begin\{block\}\{(.*?)\}(.+)?\\end\{block\}'
            part = re.sub(pattern, subst, part, flags=re.DOTALL)
            # remove margins becomes boxes are not that big
            part = part.replace('leftmargin=7mm', 'leftmargin=0mm')

        # Use smaller margin in slides
        part = part.replace('leftmargin=7mm', 'leftmargin=2mm')

        # Pieces to pop up item by item as the user is clicking
        if '% !bpop' in part:
            num_pops = part.count('% !bpop')
            pattern = r'% !bpop *(.*?)\s+(.+?)\s+% !epop'
            cpattern = re.compile(pattern, re.DOTALL)
            #import pprint;pprint.pprint(cpattern.findall(part))
            def subst(m):  # m is match object
                arg = m.group(1).strip()
                body = m.group(2)

                startswith_block = startswith_list = has_list = False
                pattern_block = r'(\\begin\{block|\\begin\{mdbox|\\summarybox\{|\\begin\{[A-Za-z0-9_]+admon\})'
                pattern_list = r'\\begin\{(enumerate|itemize|description)\}'
                if re.match(pattern_block, body.lstrip()):
                    startswith_block = True
                if re.match(pattern_list, body.lstrip()):
                    startswith_list = True
                if r'\item' in body:
                    has_list = True

                if startswith_block:
                    # Pop up the whole block at once
                    body = '\\pause\n' + body
                elif startswith_list:
                    # Pop up each list item
                    body = re.sub(r'^( *\\item)', r'\pause\n\g<1>', body,
                                  flags=re.MULTILINE)
                else:
                    # Just pause before what's coming
                    body = '\\pause\n' + body

                '''
                # OLD:
                # Individual pop up of list items if there is only
                # one pop block on this slide, otherwise pause the
                # whole list (in else branch)
                if r'\item' in body: # and num_pops == 1:
                    marker = '[[[[['
                    body = body.replace('\item ', r'\item%s ' % marker)
                    n = body.count('item%s' % marker)
                    for i in range(n):
                        body = body.replace('item%s' % marker,
                                            'item<%d->' % (i+2), 1)
                else:
                    # treat whole part as a block
                    pattern = r'(\\begin\{block|\\begin\{mdbox|\\summarybox\{|\\begin\{[A-Za-z0-9_]+admon\})'
                    m = re.match(pattern, body.lstrip())
                    if m:
                        # body has a construction that is already a block
                        body = r"""
\pause
%s
""" % body
                    else:
                        # wrap body in a block (does not work well if
                        # bpop-epop is already within another block
                        body = r"""
\pause
\begin{block}{}
%s
\end{block}
""" % body
                '''
                return body

            part = cpattern.sub(subst, part)

        # Check that we do not have multiple subsections (i.e., multiple
        # slides) on this split - if so, it is a forgotten !split
        subsections = re.findall(r'\\subsection\{', code_free_part)
        if len(subsections) > 1:
            print '*** error: more than one subsection in a slide:'
            print part
            _abort()

        # Add text for this slide

        # Grab slide title as *first* subsection in part
        pattern = r'subsection\{(.+)\}'  # greedy so it goes to the end
        m = re.search(pattern, code_free_part)
        if m:
            title = m.group(1).strip()
            title = r'\frametitle{%s}' % title + '\n'
            part = re.sub('\\\\.*' + pattern, '', part, count=1)
        elif r'\title{' in code_free_part:
            title = ''
        else:
            title = '% No title on this slide\n'

        # Beamer does not support chapter, paragraph,
        # while section is here used for the toc and subsection
        # for the title
        if r'\chapter{' in code_free_part:
            part = part.replace(r'\chapter{', r'\noindent\textbf{\huge ')
        if r'\paragraph{' in code_free_part:
            part = part.replace(r'\paragraph{', r'\noindent\textbf{')

        section_slide = False
        # \section{} should be \section[short title]{long title}
        # This is signified in a comment
        if r'\section{' in code_free_part:
            section_slide = True

            # Empty section is fine, but if there are more here than
            # labels and comments, we embed that in a separate slide
            # with the same title (otherwise it will come out as garbage)
            section_title = re.search(r'\\section\{(.+)\}', part).group(1)
            remove_patterns = [r'\\section\{.+\}', r'\\label\{.+\}', '^%.*',]
            stripped_part = part
            for pattern in remove_patterns:
                stripped_part = re.sub(pattern, '', stripped_part,
                                       flags=re.MULTILINE)
            stripped_part = stripped_part.strip()
            if stripped_part:
                # Embed everything after section in a new slide
                part = re.sub(r'(\\section\{.+\})', r"""\g<1>

\\begin{frame}%(frame_options)s
\\frametitle{%(section_title)s}
""" % vars(), part)
                part += '\n\\end{frame}\n'

            # Add short title? (\section[short title]{ordinary title})
            short_title = '' # signifies ordinary slide
            m = re.search(r'^% +short +title: +(.+)', code_free_part,
                          flags=re.MULTILINE|re.IGNORECASE)
            if m:
                short_title = m.group(1).strip()
                part = re.sub(r'\\section\{', r'\\section[%s]{' % short_title,
                              part)
                part = part.replace(m.group(), '')  # remove short title comment
            # --- end of section slide treatment ---

        part = part.rstrip()

        # Check if slide is empty
        empty_slide = True
        for line in part.splitlines():
            if line.startswith('%'):
                continue
            if line.strip() != '':
                empty_slide = False

        if r'\title{' in code_free_part:
            # Titlepage needs special treatment
            # Find figure (no caption or figure envir, just includegraphics)
            m = re.search(r'(\\centerline\{\\includegraphics.+\}\})', part)
            if m:
                titlepage_figure = m.group(1)
                # Move titlepage figure to \date{}
                part = part.replace('% <optional titlepage figure>', r'\\ \ \\ ' + '\n' + titlepage_figure)
                # Remove original titlepage figure
                part = re.sub(r'% inline figure\n\\centerline.+', '', part)
            slides += r"""
%(part)s

\begin{frame}%(frame_options)s
\titlepage
\end{frame}
""" % vars()
        elif section_slide:
            # Special section slide, not frame environment
            slides += r"""
%(part)s
""" % vars()
        elif not empty_slide:
            # Ordinary slide
            slides += r"""
\begin{frame}%(frame_options)s
%(title)s
%(part)s
\end{frame}
""" % vars()
    slides += """
\end{document}
"""
    slides = re.sub(r'% !split\s+', '', slides)
    return slides

def _usage_split_rst0():
    print 'Usage: doconce split_rst complete_file.rst'

def split_rst0():
    """
    Split a large .rst file into smaller files corresponding
    to each main section (7= in headings).

    The large complete doconce file typically looks like this::

        #>>>>>>> part: header >>>>>
        # #include "header.do.txt"

        #>>>>>>> part: fundamentals >>>>>
        # #include "fundamentals.do.txt"

        #>>>>>>> part: nonlinear >>>>>
        # #include "nonlinear.do.txt"

        #>>>>>>> part: timedep >>>>>
        # #include "timedep.do.txt"

    Note that the comment lines ``#>>>...`` *must* appear right above
    the include directives. The includes are replaced by text, while
    the ``#>>>...`` are still left as markers in the complete document
    for the various sections. These markers are used to split the
    text into parts. For Sphinx to treat section headings right,
    each part should start with a main section (7=).

    The ``split_rst`` command will in this example take the complete
    ``.rst`` file and make files ``header.rst``, ``fundamentals.rst``,
    ``nonlinear.rst``, etc.  The ``doconce sphinx_dir`` command takes
    all these ``.rst`` files as arguments and creates the
    corresponding index file etc. The names of the various ``.rst``
    files are specified in the ``#>>>... Part: ...`` markers. Normally,
    a part name corresponding to the included filename is used.

    CAVEAT: Nested includes in doconce files and doconce files in subdirs.
    SOLUTION: Use #>>> Part: mypart >>> for an include mypart/mypart.do.txt.
    All parts are then split into files in the top directory.

    fig dirs must be copied, but that can be easily done automatically
    if the fig dir name is of the right form.
    """

    if len(sys.argv) <= 1:
        _usage_split_rst0()
        sys.exit(0)

    complete_file = sys.argv[1]
    f = open(complete_file, 'r')
    filestr = f.read()
    f.close()

    # Determine parts
    part_pattern = r'\.\.\s*>>+\s*[Pp]art:\s*%s\s*>>+'
    parts = re.findall(part_pattern % '([^ ]+?)', filestr)

    # Split file
    for i in range(len(parts)):
        if i < len(parts)-1:  # not the last part?
            this_part = part_pattern % parts[i]
            next_part = part_pattern % parts[i+1]
        else:
            this_part = part_pattern % parts[i]
            next_part = '$'  # end of string
        pattern = '%s(.+?)%s' % (this_part, next_part)
        cpattern = re.compile(pattern, re.DOTALL)
        m = cpattern.search(filestr)
        text = m.group(1)
        filename = parts[i] + '.rst'
        f = open(filename, 'w')
        f.write(text)
        f.close()
        #print 'Extracted part', parts[i], 'in', filename
    print ' '.join(parts)

def _usage_split_rst():
    print 'Usage: doconce split_rst mydoc'
    print """Example:
doconce sphinx_dir author="Kaare Dump" title="Short title" dirname=mydir mydoc
doconce format sphinx mydoc
doconce split_rst mydoc
python automake_sphinx.py
"""


def split_rst():
    """
    Split rst file into parts. Use !split command as separator between
    parts.
    """
    if len(sys.argv) <= 1:
        _usage_split_rst()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.rst'):
        basename = filename
        filename += '.rst'
    else:
        basename = filename[:-4]

    header, parts, footer = get_header_parts_footer(filename, "rst")
    import pprint
    files = doconce_rst_split(parts, basename, filename)
    #print ' '.join([name[:-4] for name in files])
    print basename, 'split into'
    print ' '.join(files)


def doconce_rst_split(parts, basename, filename):
    """Native doconce style splitting of rst file into parts."""
    # Write the parts to file and fix references to equations.

    label_pattern = r'.. math::\s+:label: (.+?)$'
    parts_label = [re.findall(label_pattern, ''.join(part), flags=re.MULTILINE)
                   for part in parts]
    parts_label2part = {}   # map an eq. label to where it is defined
    for i in range(len(parts_label)):
        for label in parts_label[i]:  # assume all labels are unique
            parts_label2part[label] = i
    label2tag = {}
    for pn, part_label in enumerate(parts_label):
        local_eq_no = 1
        for label in part_label:
            label2tag[label] = '%d.%d' % (pn+1, local_eq_no)
            local_eq_no += 1

    # The definition of |nbsp| must be repeated in each part, except the first.
    # The definition is inserted in the beginning of the document, i.e.,
    # in parts[0].
    nbsp = '.. |nbsp| unicode:: 0xA0' in ''.join(parts[0])

    generated_files = []
    for pn, part in enumerate(parts):
        text = ''.join(part)

        # Check if headings are consistent: the first heading must be
        # the highest one
        m = re.search(r'^(%%+|==+|--+|~~+)$', text, flags=re.MULTILINE)
        if m:
            first_heading = m.group(1)
            if first_heading.startswith('='):
                if re.search(r'^(%%+)$', text, flags=re.MULTILINE):
                    print """
*** error: first heading in part %d is a section, but the part
    also contains a chapter.
    !split must be moved to avoid such inconsistent reST headings""" % pn
                    _abort()
            elif first_heading.startswith('-'):
                if re.search(r'^(%%+|==+)$', text, flags=re.MULTILINE):
                    print """
*** error: first heading in part %d is a subsection, but the part
    also contains a chapter or section.
    !split must be moved to avoid such inconsistent reST headings""" % pn
                    _abort()
            elif first_heading.startswith('~'):
                if re.search(r'^(%%+|==+|--+)$', text, flags=re.MULTILINE):
                    print """
*** error: first heading in part %d is a subsubsection, but the part
    also contains a chapter, section, or subsection.
    !split must be moved to avoid such inconsistent reST headings""" % pn
                    _abort()

        part_filename = _part_filename % (basename, pn) + '.rst'
        generated_files.append(part_filename)

        if nbsp and pn > 0:
            text = """

.. |nbsp| unicode:: 0xA0
   :trim:

""" + text

        for label in parts_label[pn]:
            # All math labels get an anchor above for equation refs
            # from other parts. The anchor is Eq:label
            text = re.sub(r'.. math::\s+:label: %s$' % label,
                          r".. _Eq:%s:\n\n.. math::\n   :label: %s" %
                          (label, label), text, flags=re.MULTILINE)
        local_eqrefs = re.findall(r':eq:`(.+?)`', text)
        for label in local_eqrefs:
            # (Ignore non-existent labels - sphinx.py removes labels
            # in non-align math environments anyway)
            if parts_label2part.get(label, None) == pn:
                # References to local labels in this part apply the
                # standard syntax
                pass
            else:
                text = text.replace(
                    r':eq:`%s`' % label,
                    ':ref:`(%s) <Eq:%s>`' %
                    (label2tag.get(label, 'label:removed'), label))
        f = open(part_filename, 'w')
        f.write(text)
        f.close()
    return generated_files

def _usage_list_labels():
    print 'Usage: doconce list_labels doconcefile.do.txt | latexfile.tex'

def list_labels():
    """
    List all labels used in a doconce or latex file.
    Since labels often are logically connected to headings in
    a document, the headings are printed in between in the
    output from this function, with a comment sign # in
    front so that such lines can easily be skipped when
    processing the output.

    The purpose of the function is to enable clean-up of labels
    in a document. For example, one can add to the output a
    second column of improved labels and then make replacements.
    """
    if len(sys.argv) <= 1:
        _usage_list_labels()
        sys.exit(0)
    filename = sys.argv[1]

    # doconce or latex file
    dofile = True if filename.endswith('.do.txt') else False
    lines = open(filename, 'r').readlines()
    labels = []  # not yet used, but nice to collect all labels
    for line in lines:
        # Identify heading and print out
        heading = ''
        if dofile:
            m = re.search(r'={3,7}\s*(.+?)\s*={3,7}', line)
            if m:
                heading = m.group(1).strip()
        else:
            m = re.search(r'section\{(.+)\}', line) # make .+ greedy
            if m:
                heading = m.group(1).strip()
        if heading:
            print '#', heading

        # Identify label
        if 'label{' in line:
            m = re.search(r'label\{(.+?)\}', line)
            if m:
                label = m.group(1).strip()
            else:
                print 'Syntax error in line'
                print line
                _abort()
            print label
            labels.append(label)


def _usage_teamod():
    print 'Usage: doconce teamod name'

def teamod():
    if len(sys.argv) < 2:
        _usage_teamod()
        sys.exit(0)

    name = sys.argv[1]
    if os.path.isdir(name):
        os.rename(name, name + '.old~~')
        print 'directory %s exists, renamed to %s.old~~' % (name, name)
    os.mkdir(name)
    os.chdir(name)
    os.mkdir('fig-%s' % name)
    os.mkdir('src-%s' % name)
    os.mkdir('slides-%s' % name)
    f = open('main_%s.do.txt' % name, 'w')
    f.write("""# Main file for teaching module "%s"

TITLE: Here Goes The Title ...
AUTHOR: name1 email:..@.. at institution1, institution2, ...
AUTHOR: name2 at institution3
DATE: today

# #include "%s.do.txt"
""" % name)
    f.close()
    f = open('%s.do.txt' % name, 'w')
    f.write("""# Teaching module: %s
======= Section =======

===== Subsection =====
idx{example}
label{mysubsec}

__Paragraph.__ Running text...

Some mathematics:

!bt
\begin{align}
a &= b,  label{eq1}\\
a &= b,  label{eq2}
\end{align}
!et
or

!bt
\[ a = b, \quad c=d \]
!et

Some code:
!bc pycod
def f(x):
    return x + 1
!ec

A list with

 * item1
 * item2
   * subitem2
 * item3
   continued on a second line

""")
    f.close()


def _usage_assemble():
    print 'Usage: doconce assemble master.do.txt'

def assemble():
    # See 2DO and teamod.do.txt

    # Assume some master.do.txt including other .do.txt recursively.
    # search for all @@@CODE, FIGURE, MOVIE and archive in list/dict.
    # search for all #include ".+\.do\.txt", call recursively
    # for each of these with dirname and dotxtname as arguments.
    # Build local links to all src- and figs- directories, make
    # sure all teamod names are unique too.

    # analyzer: old comments on how to implement this. Try the
    # description above first.
    if len(sys.argv) < 2:
        _usage_assemble()
        sys.exit(0)

    master = sys.argv[2]

    # Run analyzer...

def _usage_analyzer():
    print 'Usage: doconce analyzer complete_file.do.txt'

def analyzer():
    """
    For a doconce file, possibly composed of many other doconce
    files, in a nested fashion, this function returns a tree
    data structure with the various parts, included files,
    involved source code, figures, movies, etc.

    Method:
    Go through all #include's in a doconce file, find subdirectories
    used in @@@CODE, FIGURE, and MOVIE commands, and make links
    in the present directory to these subdirectories such that
    @@@CODE, FIGURE, and MOVIE works from the present directory.
    This is very important functionality when a doconce document
    is made up of many distributed documents, in different
    directories, included in a (big) document.

    Make recursive calls.
    """
    # 2DO:
    # - start with an example (some Cython intro examples? in a tree?)
    # - make doconce nested_include
    #   which makes a tree of all the dirs that are involved in a
    #   complete document
    # - simply copy all subnits and the complete doc to a new _build dir
    # - simply copy all figs-*, movies-*, src-* to _build
    # - compile

    # IDEA: Have a convention of src-poisson, figs-poisson etc
    # naming and use a simple script here to link from one dir to
    # all src-* and figs-* movies-* found in a series of dir trees. YES!!
    # Maybe use code below to issue warnings if FIGURE etc applies other
    # directories (could extend with eps-*, ps-*, pdf-*, png-*, jpeg-*,
    # gif-*, flv-*, avi-*, ...) and/or do this also in std doconce
    # translation (no, simple stand-alone thing must be fine with
    # figs/, it's the big distributed projects that need this
    # naming convention).  YES! Should be figs-basename(os.getcwd())

    # Can play with fenics tut: put each section in sep dirs,
    # stationary/poisson, transient/diffusion etc.,
    # with local src and figs
    # Need a script that can pack all local src dirs into a separate tree
    # for distribution (doconce pack_src): create new tree, walk a set
    # of trees, for each subdir with name src-*, strip off src-, copy
    # subdir to right level in new tree

    # Support for latex files too (includegraphics, movie15, psfig,
    # input, include), starting point is a .tex file with includes/inputs

    if len(sys.argv) <= 1:
        _usage_analyzer()
        sys.exit(0)

    # Must have this in a function since we need to do this recursively
    filename = sys.argv[1]
    alltext = open(filename, 'r').read()
    # preprocess parts and includes
    part_pattern = r'\.\.\s*>>+\s*[Pp]art:\s*%s\s*>>+'
    parts = re.findall(part_pattern % '([^ ]+?)', alltext)

    include_files = re.findall(r"""[#%]\s+\#include\s*["']([A-Za-z0-9_-., ~]+?)["']""", alltext)
    include_files = [filename for dummy, filename in include_files]

    figure = re.compile(r'^FIGURE:\s*\[(?P<filename>[^,\]]+),?(?P<options>[^\]]*)\]\s*?(?P<caption>.*)$', re.MULTILINE)
    movie = re.compile(r'^MOVIE:\s*\[(?P<filename>[^,\]]+),?(?P<options>[^\]]*)\]\s*?(?P<caption>.*)$', re.MULTILINE)
    code = re.compile(r'^\s*@@@CODE\s+([^ ]+?) ')

    for filename in include_files:
        f = open(filename, 'r')
        directory = os.path.dirname(f)
        fstr = f.read()
        f.close()
        # What about figs/myfig/1stver/t.png? Just link to figs...
        # but it's perhaps ok with links at different levels too?
        figure_files = [filename for filename, options, captions in \
                        figure.findall(fstr)]
        movie_files = [filename for filename, options, captions in \
                       movie.findall(fstr)]
        code_files = code.findall(fstr)
        print figure_files
        figure_dirs = [os.path.dirname(f) for f in figure_files] # no dir??
        print figure_dirs
        dirs = [os.path.join(directory, figure_dir) \
                for figure_dir in figure_dirs]




def old2new_format():
    if len(sys.argv) == 1:
        print 'Usage: %s file1.do.txt file2.do.txt ...' % sys.argv[0]
        sys.exit(1)

    for filename in sys.argv[1:]:
        print 'Converting', filename
        _old2new(filename)

def _old2new(filename):
    """
    Read file with name filename and make substitutions of
    ___headings___ to === headings ===, etc.
    A backup of the old file is made (filename + '.old').
    """
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    os.rename(filename, filename + '.old')

    # perform substitutions:
    nchanges = 0
    for i in range(len(lines)):
        oldline = lines[i]
        # change from ___headings___ to === headings ===:
        lines[i] = re.sub(r'(^\s*)_{7}\s*(?P<title>[^ ].*?)\s*_+\s*$',
                          r'\g<1>======= \g<title> =======' + '\n', lines[i])
        lines[i] = re.sub(r'(^\s*)_{5}\s*(?P<title>[^ ].*?)\s*_+\s*$',
                          r'\g<1>===== \g<title> =====' + '\n', lines[i])
        lines[i] = re.sub(r'(^\s*)_{3}\s*(?P<title>[^ ].*?)\s*_+\s*$',
                          r'\g<1>=== \g<title> ===' + '\n', lines[i])
        if lines[i].startswith('AUTHOR:'):
            # swith to "name at institution":
            if not ' at ' in lines[i]:
                print 'Warning, file "%s": AUTHOR line needs "name at institution" syntax' % filename

        if oldline != lines[i]:
            nchanges += 1
            print 'Changing\n  ', oldline, 'to\n  ', lines[i]

    print 'Performed %d changes in "%s"' % (nchanges, filename)
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()

def latex_header():
    from doconce.doconce import INTRO
    print INTRO['latex']

def latex_footer():
    from doconce.doconce import OUTRO
    print OUTRO['latex']


# -------------------- functions for spell checking ---------------------

_environments = [
    # DocOnce: use regex instead, it is safer (!bc at beginning of line etc.)
    # Mako: use regex
    # hpl tex stuff
    ("\\beq",               "\\eeq"),
    ("\\beqa",              "\\eeqa"),
    ("\\beqan",             "\\eeqan"),
    # Wait until the end with removing comment lines
    ]

# These are relevant if doconce spellcheck is applied to latex or ptex2tex files
_latex_environments = [
   ("\\begin{equation}",   "\\end{equation}"),
    ("\\begin{equation*}",  "\\end{equation*}"),
    ("\\begin{align}",      "\\end{align}"),
    ("\\begin{align*}",     "\\end{align*}"),
    ("\\begin{eqnarray}",   "\\end{eqnarray}"),
    ("\\begin{eqnarray*}",  "\\end{eqnarray*}"),
    ("\\begin{figure}[",    "]"),
    ("\\begin{figure*}[",   "]"),
    ("\\begin{multline}",   "\\end{multiline}"),
    ("\\begin{tabbing}",   "\\end{tabbing}"),
    # ptex2tex environments
    ("\\bccq",              "\\eccq"),
    ("\\bcc",               "\\ecc"),
    ("\\bcod",              "\\ecod"),
    ("\\bpycod",            "\\epycod"),
    ("\\bpro",              "\\epro"),
    ("\\bpypro",            "\\epypro"),
    ("\\brpy",              "\\erpy"),
    ("\\bipy",              "\\eipy"),
    ("\\bfcod",             "\\efcod"),
    ("\\bfpro",             "\\efpro"),
    ("\\bccod",             "\\epcod"),
    ("\\bcpro",             "\\epcro"),
    ("\\bcppcod",           "\\ecppcod"),
    ("\\bcpppro",           "\\ecpppro"),
    ("\\bhtmlcod",          "\\ehtmlcod"),
    ("\\bhtmlpro",          "\\ehtmlpro"),
    ("\\brcod",             "\\ercod"),
    ("\\brpro",             "\\eprro"),
    ("\\bjscod",            "\\ejscod"),
    ("\\bjspro",            "\\ejspro"),
    ("\\blatexcod",         "\\elatexcod"),
    ("\\blatexpro",         "\\elatexpro"),
    ("\\bshcod",            "\\eshcod"),
    ("\\bshpro",            "\\eshpro"),
    ("\\bsys",              "\\esys"),
    ("\\bdat",              "\\edat"),
    ("\\bsni",              "\\esni"),
    ("\\bdsni",             "\\edsni"),
    ("\\bpyshell",          "\\epyshell"),
    ("\\bpy",               "\\epy"),
    ]

_replacements = [
    # General
    (r'cf.', ''),
    # DocOnce
    (r'^<%.+^%>', '', re.MULTILINE|re.DOTALL),  # Mako Python code
    (r'^<%doc.+^</%doc>', '', re.MULTILINE|re.DOTALL),  # Mako comments
    (r'"([^"]*?)":\s*"[^"]+?"', r'\g<1>'),  # links ("`file.py`" -> "": "...")
    (r"^#.*$", "", re.MULTILINE),
    (r"(idx|label|ref|cite)\{.*?\}", ""),
    (r"cite\[.+?\]\{.+?\}", ""),
    (r"refch\[.*?\]\[.*?\]\[.*?\]", "", re.DOTALL),
    (r'^ *\|[\-rlc]+?\|', '', re.MULTILINE),
    (r' +\| +', ' '),
    ('<linebreak>', ''),
    (r"={3,}",  ""),  # section
    (r"^__(.+?)__", r"\g<1>\n", re.MULTILINE),  # paragraph
    (r"\[\^.+?\]", ""), # footnote
    (r'`[^ ][^`]*?`', ""),
    (r"`[A-Za-z0-9_.]+?`", ""),
    (r"^#.*$",          "", re.MULTILINE),
    (r'"https?://.*?"', ""),
    (r'"ftp://.*?"', ""),
    (r"\b[A-Za-z_0-9/.:]+\.(com|org|net|edu|)\b", ""),  # net name
    (r'\[[A-Za-z]+:\s+[^\]]*?\]', ''),  # inline comment
    (r'''^\s*files?=[${}()"'A-Za-z_0-9.,*= ]+\s*$''', '', re.MULTILINE),
    (r"^@@@CODE.*$", "", re.MULTILINE),
    (r"^@@@OSCMD.*$", "", re.MULTILINE),
    (r"^\s*(FIGURE|MOVIE):\s*\[.+?\]",    "", re.MULTILINE),
    (r"^\s*BIBFILE:.+$",    "", re.MULTILINE),
    (r"^\s*TOC:\s+(on|off)", "", re.MULTILINE),
    (r"\$[^{].*?\$", "", re.DOTALL),  # inline math
    (r"\$\{[A-Za-z_].+?\}", "", re.DOTALL),   # mako substitutions (note that ${\cal O}..$ math is not allowed)
    ('!split', ''),
    (r'![be]slidecell', ''),
    (r'![be]ans', ''),
    (r'![be]sol', ''),
    (r'![be]subex', ''),
    (r'![be]hint', ''),
    (r'![be]notes', ''),
    (r'![be]pop', ''),
    (r'![be]warning', ''),
    (r'![be]summary', ''),
    (r'![be]question', ''),
    (r'![be]notice', ''),
    (r'![be]quote', ''),
    (r'![be]box', ''),
    (r'![be]block', ''),
    (r'![be]remarks', ''),
    (r'![be]quiz', ''),
    (r'![be]u-[^ ]+', ''),  # user-def envirs
    # Preprocess
    (r"^#.*ifn?def.*$", "", re.MULTILINE),
    (r"^#.*else.*$", "", re.MULTILINE),
    (r"^#.*endif.*$", "", re.MULTILINE),
    (r"^#include.*$", "", re.MULTILINE),
    # Mako
    (r'^<%.+?^%>', '', re.MULTILINE|re.DOTALL),
    (r"^% .*$", "", re.MULTILINE),
    (r"^<%.*$", "", re.MULTILINE),
    ]

_latex_replacements = [
    (r"%.*$", "", re.MULTILINE),  # comments
    (r"\\.*section\{(.+)\}", "\g<1>"),
    (r"^\\\[[^@]+\\\]",    ""),  # (@ is "unlikely" character)
    (r"\\includegraphics.*?(\.pdf|\.png|\.eps|\.ps|\.jpg)", ""),
    (r"\\(pageref|eqref|ref|label|url|emp)\{.*?\}", ""),
    (r"\\(emph|texttt)\{(.*?)\}", "\g<2>"),
    (r"\\footnote\{", " "),  # leaves an extra trailing } (ok)
    #(r"\\[Vv]erb(.)(.+?)\1", "\g<2>"),
    (r"\\[Vv]erb(.)(.+?)\1", ""),
    (r"\\index\{.*?\}", ""),
    (r"\$.+?\$", "", re.DOTALL),
    (r"([A-Za-z])~", "\g<1> "),
    (r"``(.+?)''", "\g<1>"),  # very important, otherwise doconce verb eats the text
    (r' \.', '.'),
    ('\n\\.', '.\n'),
    (r':\s*\.', '.'),
    (r' ,', ','),
    ('\n\,', ',\n'),
    (',{2,}', ','),
    # ptex2tex
    (r"^@@@DATA.*$",    "", re.MULTILINE),
    (r"^@@@CMD.*$",    "", re.MULTILINE),
    # hpl's idx latex commands
    (r"\\idx\{.*?\}", ""),
    (r"\\idx(font|f|m|p|st|s|c|e|numpyr|numpy)\{.*?\}", ""),
    (r"\\codett\{.*?\}", ""),
    (r"\\code\{.*?\}", ""),
    ]

_common_typos = [
    '!bsubsex',
    '!esubsex',
    'hiearchy',
    'hieararchy',
    'statment',
    ' imples',
    'imples ',
    'execption',
    'excercise',
    'exersice',
    'eletric',
    'everyting',
    'progam',
    'technqiues',
    'incrased',
    'similarily',
    'occurence',
    'persue',
    'becase',
    'frequence',
    'noticable',
    'peform',
    'paramter',
    'intial',
    'inital',
    'condtion',
    'expontential',
    'differentation',
    'recieved',
    'cateogry',
    'occured',
    '!bc pydoc',
    '!bc pycodc',
    ]


def _grep_common_typos(text, filename, common_typos):
    """Search for common typos and abort program if any is found."""
    found = False
    for i, line in enumerate(text.splitlines()):
        for typo in common_typos:
            if re.search(typo, line):
                print '\ntypo "%s" in line %d in file %s:\n' % \
                      (typo, i+1, filename), line
                found = True
    if found:
        sys.exit(1)

def _strip_environments(text, environments, verbose=0):
    """Remove environments in the ``environments`` list from the text."""
    # Note: this stripping does not work well for !bc and !bt envirs,
    # because a phrase like `!bc pycod` in running text gives a split...
    for item in environments:
        if len(item) != 2:
            raise ValueError(
                '%s in environments to be stripped is wrong' % (str(item)))
        begin, end = item
        if not begin in text:
            continue
        parts = text.split(begin)
        text = parts[0]
        for part in parts[1:]:
            subparts = part.split(end)
            text += end.join(subparts[1:])
            if verbose > 1:
                print '\n============ split %s <-> %s\ntext so far:' % (begin, end)
                print text
                print '\n============\nSkipped:'
                print subparts[0]
        if verbose > 0:
            print 'split away environments: %s %s\nnew text:\n' % (begin, end)
            print text
            print '\n=================='
    return text

def _do_regex_replacements(text, replacements, verbose=0):
    """Substitute according to the `replacement` list."""
    for item in replacements:
        if len(item) == 2:
            from_, to_ = item
            text = re.sub(from_, to_, text)
        elif len(item) == 3:
            from_, to_, flags = item
            text = re.sub(from_, to_, text, flags=flags)
        if verbose > 0:
            print '=================='
            print 'regex substitution: %s -> %s\nnew text:' % (from_, to_)
            print text
    return text

def _do_fixes_4MSWord(text):
    t = text  # short cut
    # Deal with special strange left-overs from removing ref, cite, etc.
    # , , ,
    t = re.sub(r',\s+,', ' ', t)
    # .  period at the beginning of a line
    t = re.sub(r'^\. +', '', t, flags=re.MULTILINE)
    #,   comma at the beginning of a line
    t = re.sub(r'^\, +', '', t, flags=re.MULTILINE)
    # text like   .,
    t = re.sub(r' +,\.', '.', t)
    # or   -.
    t = re.sub(r' +-\.', '.', t)
    # and ( ,  ,   , , )
    t = re.sub(r'\([, ]*\)', ' ', t)
    # initial spaces on a line
    t = re.sub(r'^ +([A-Z])', r'\1', t, flags=re.MULTILINE)
    # too complicated to remove emphasize: t = re.sub(r'(^| +)\*(.+?)\*[, \n.]', r' \2 ', t, flags=re.DOTALL|re.MULTILINE)
    t = re.sub(r'^\s+\*\s+', '', t, flags=re.MULTILINE)
    t = re.sub(r' +\)', ')', t)
    t = t.replace(':)', ')')
    t = re.sub(r'^ +', '', t, flags=re.MULTILINE)
    t = re.sub(r'^\.\n', '\n', t, flags=re.MULTILINE)
    t = re.sub(r'  +', ' ', t)
    t = re.sub(r'\\begin\{.+?\}', '', t)
    t = re.sub(r'\\end\{.+?\}', '', t)
    # Remove space above paragraphs starting with lower case
    t = re.sub(r'\n\n+([a-z])', r' \1', t)
    # Remove newlines at the end of text (to help word)
    # (this might not be desired for grepping in the stripped file)
    if not '--dont_remove_newlines' in sys.argv:
        t = re.sub(r'([A-Za-z0-9,.:!?)])\n(?=[^\n])', '\g<1> ', t)
    # Do these after we have joined lines
    # spaces before comma
    t = re.sub(r'([A-Za-z])[:;?.]?\s+, +', r'\1, ', t)
    # spaces before period
    t = re.sub(r'([A-Za-z])[:;?.]? +\. +', r'\1. ', t)
    # spaces before period
    t = re.sub(r'([A-Za-z])[:;?.]? +\.', r'\1.', t)
    # spaces before colon
    t = re.sub(r'([A-Za-z])[:;?.]? +:', r'\1:', t)

    t = t.replace(', g.,', '')
    t = t.replace('ref[', '')
    t = t.replace('][', '')
    t = t.replace(']', '')
    t = t.replace('[', '')
    t = t.replace(']', '')
    t = t.replace('*', '')
    t = t.replace('|', '')
    t = t.replace('()', '')
    t = t.replace('(-)', '')
    t = t.replace(r'\noindent', '')

    return t


def _spellcheck(filename, dictionaries=['.dict4spell.txt'], newdict=None,
                remove_multiplicity=False, strip_file='.strip', verbose=False):
    """
    Spellcheck `filename` and list misspellings in the file misspellings.txt~.
    The `dictionaries` list contains filenames for dictionaries to be
    used with ispell.
    `newdict` is an optional filename for creating a new, updated
    dictionary containing all given dictionaries and all misspellings
    found (assuming they are correct and approved in previous runs).
    `remove_multiplicity` removes multiple occurrences of the same
    misspelling in the misspellings.txt~ (output) file.
    `strip_file` holds the filename of a file with definitions of
    environments to be stripped off in the source file, replacements
    to be performed, and a list of typical misspellings that are first
    check before ispell is run.
    """

    try:
        f = open(filename, 'r')
    except IOError:
        print '\nfile %s does not exist!' % filename
        _abort()

    text = f.read()
    f.close()

    # Standardize newlines
    text = re.sub(r'(\r\n|\r|\n)', '\n', text)

    # Remove all !bc and !bt blocks
    text = re.sub(r'^!bc(.*?)\n(.*?)^!ec', '',
                  text, flags=re.DOTALL|re.MULTILINE)
    text = re.sub(r'^!bt *\n(.*?)^!et', '', text,
                  flags=re.DOTALL|re.MULTILINE)

    # Check for double words (before removing verbatim)

    pattern = r"\b([\w'\-]+)(\s+\1)+\b"
    found = False
    offset = 30  # no of chars before and after double word to be printed
    start = 0
    while start < len(text)-1:
        m = re.search(pattern, text[start:])
        if m:
            # Words only
            word = m.group(0)
            try:
                [float(w) for w in word.split()]
                is_word = False
            except ValueError:
                # Drop words with underscore, ...
                #drop = ['_', '--',
                is_word = '_' not in word

            if is_word:
                print "\ndouble words detected in %s (marked inside [...]):\n------------------------" % filename
                print "%s[%s]%s\n------------------------" % \
                      (text[max(0,start+m.start()-offset):start+m.start()],
                       word,
                       text[start+m.end():min(start+m.end()+offset,
                                               len(text)-1)])
                found = True
            start += m.end()
        else:
            break
    if found:
        pass
        #print '\nAbort because of double words.'
        #sys.exit(1)

    # Remove inline quotes before inline verbatim
    pattern = "``([A-Za-z][A-Za-z0-9\s,.;?!/:'() -]*?)''"
    text = re.sub(pattern, r'\g<1>', text)
    # Remove inline verbatim
    text = re.sub(r'`[^ ][^`]*?`', '', text)  # remove inline verbatim
    if verbose > 0:
        print 'removal of quotes, inline verbatim, code and tex blocks\nnew text:\n'
        print text
        print '==================\n'

    # Continue with spell checking

    if os.path.isfile(strip_file):
        execfile(strip_file)
    else:
        environments = []
        replacements = []
        common_typos = []
    # Add standard definitions (above)
    environments += _environments
    replacements += _replacements
    common_typos += _common_typos

    # Add standard latex definitions when spellchecking latex
    if os.path.splitext(filename)[1] == '.tex':
        # Make sure to do latex first (\label{} before label{})
        environments = _latex_environments + environments
        replacements = _latex_replacements + replacements


    _grep_common_typos(text, filename, common_typos)

    text = _strip_environments(text, environments, verbose)
    #print 'Text after environment strip:\n', text

    text = _do_regex_replacements(text, replacements, verbose)
    #print 'Text after regex replacements:\n', text

    text = _do_fixes_4MSWord(text)

    # Write modified text to scratch file and run ispell
    scratchfile = 'tmp_stripped_%s' % filename
    f = open(scratchfile, 'w')
    f.write(text)
    f.close()
    personal_dictionaries = []
    p_opt = ''  # personal dictionary specification for ispell
    for dictionary in dictionaries:
        if os.path.isfile(dictionary):
            p_opt += " -p`pwd`/%s" % dictionary
            f = open(dictionary, 'r')
            personal_dictionaries += f.readlines()
            f.close()
        else:
            print 'Dictionary file %s does not exist.' % dictionary

    personal_dictionaries = list(sets.Set(personal_dictionaries))
    misspellings = 'tmp_misspelled_' + filename + '~'
    cmd = 'cat %s | ispell -l -t -d american %s > %s' % \
          (scratchfile, p_opt, misspellings)
    #cmd = 'cat %s | aspell -t -d american list %s > %s'
    system(cmd)

    # Load misspellings, remove duplicates
    f = open(misspellings, 'r')
    words = f.readlines()
    f.close()
    words2 = list(sets.Set(words))  # remove multiple words
    if len(words2) > 0:             # do we have misspellings?
        print '%d misspellings in %s' % (len(words2), filename)
        if remove_multiplicity:
            f = open(misspellings, 'w')
            f.write(words2)
            f.close()
    else:
        os.remove(misspellings)

    # Make convenient updates of personal dictionaries
    if newdict is not None:
        accepted_words = words2 + personal_dictionaries
        if os.path.isfile(newdict):
            f = open(newdict, 'r')
            newdict_words = f.readlines()
            f.close()
            newdict_add = words2 + newdict_words
            newdict_add = sorted(list(sets.Set(newdict_add)))
            union = accepted_words + newdict_words
            union = sorted(list(sets.Set(union)))
            #print '%s %d: %d misspellings (%d from personal dicts) -> %d' % (newdict, len(newdict_words), len(words2), len(personal_dictionaries), len(union))
        else:
            union = accepted_words
            newdict_add = words2
        # union is the potentially new personal dictionary
        #
        f = open(newdict, 'w')
        f.writelines(newdict_add)
        f.close()
        f = open('new_dictionary.txt~', 'w')
        f.writelines(union)
        f.close()
        #if len(newdict_add) > 0:
        #    print '%s: %d, %s: %d items' % (newdict, len(newdict_add), 'new_dictionary.txt~', len(union))


def _spellcheck_all(**kwargs):
    for filename in glob.glob('tmp_misspelled*~') + glob.glob('misspellings.txt~*'):
        os.remove(filename)
    for filename in ['__tmp.do.txt']:
        if filename in sys.argv[1:]:  # iterate over copy
            os.remove(filename)
            del sys.argv[sys.argv.index(filename)]
    for filename in sys.argv[1:]:
        if not filename.startswith('tmp_stripped_'):
            _spellcheck(filename, **kwargs)
    tmp_misspelled = glob.glob('tmp_misspelled*~')
    if len(tmp_misspelled) > 0:
        print
        if len(sys.argv[1:]) == 1:
            print 'See misspellings.txt~ for all misspelled words found.'
        else:
            for name in tmp_misspelled:
                print 'See', name, 'for misspellings in', name.replace('tmp_misspelled_', '')[:-1]
        dictfile = kwargs.get('dictionary', '.dict4spell.txt')
        print 'When all misspellings are acceptable, cp new_dictionary.txt~',\
              dictfile, '\n'
        sys.exit(1)
    else:
        sys.exit(0)

def _usage_spellcheck():
    print """
doconce spellcheck file1.do.txt file2.do.txt ...  # use .dict4spell.txt
doconce spellcheck -d .mydict.txt file1.do.txt file2.do.txt ...

Spellcheck of files via ispell (but problematic parts are removed from the
files first).

Output:

misspellings.txt~: dictionary of potentially new accepted words, based on all
the current misspellings.

new_dictionary.txt~: suggested new dictionary, consisting of the old and
all new misspellings (if they can be accepted).

tmp_stripped_file1.do.txt: the original files are stripped off for
various constructs that cause trouble in spelling and the stripped
text is found in files with a filename prefix tmp_stripped_ (this file
can be checked for spelling and grammar mistakes in MS Word, for
instance, but a better method might be to translate the entire
DocOnce document to HTML and import that HTML code into Word.)

Usage
-----

For a new project, do the points below for initializating a new accepted
personal dictionary for this project. Thereafter, the process is
automated: misspellings.txt~ should be empty if there are no new misspellings.
tmp_misspelled*~ are made for each file tested with the file's misspelled
words.

For each file:

  * Run spellcheck.py without a dictionary or with a previous dictionary:
    doconce spellcheck file or doconce spellcheck -d .mydict.txt file
    (default dictionary file is .dict4spell.txt)
  * Check misspelled.txt~ for misspelled words. Change wrong words.
  * Rerun. If all words in misspelled.txt are acceptable,
    copy new_dictionary.txt to .dict4spell.txt (or another name)
  * Optional: import tmp_stripped_text.txt into MS Word for grammar check.
  * Remove tmp_* and *~ files

The next time one can run::

  spellcheck.py file*                   # use .dict4spell.txt
  spellcheck.py -d .mydict.txt file*

misspellings.txt~ should ideally be empty if there are no (new)
spelling errors. One can check that the file is empty or check
the $? variable on Unix since this prorgram exits with 1
when spelling errors are found in any of the tested files::

  # Run spellcheck
  doconce spellcheck *.do.txt
  if [ $? -ne 0 ]; then exit; fi


How to correct misspellings
---------------------------

Some misspellings can be hard to find if the word is strange
(like "emp", for instance). Then invoke ``tmp_stripped_text.txt``,
which is the stripped version of the text file being spellchecked.
All references, labels, code segments, etc., are removed in this
stripped file. Run ispell on the file::

  ispell -l -p.dict4spell.txt tmp_stripped_text.txt

Now, ispell will prompt you for the misspellings and show the context.
A common error in latex is to forget a ``\ref`` or ``\label`` in front
of a label so that the label gets spellchecked.  This may give rise to
strange words flagged as misspelled.

How to control what is stripped
-------------------------------

The spellcheck function loads a file .strip, if present, with
possibly three lists that defines what is being stripped away
in ``tmp_stripped_*`` files:

  * ``environments``, holding begin-end pairs of environments that
    should be entirely removed from the text.
  * ``replacements``, holding (from, to) pairs or (from, to, regex-flags)
    triplets for substituting text.
  * ``common_typos``, holding typical wrong spellings of words.

execfile is applied to .strip to execute the definition of the lists.

"""


def spellcheck():
    if len(sys.argv) == 1:
        _usage_spellcheck()
        sys.exit(0)
    if sys.argv[1] == '-d':
        dictionary = [sys.argv[2]]
        del sys.argv[1:3]
    else:
        if os.path.isfile('.dict4spell.txt'):
            dictionary = ['.dict4spell.txt']
        else:
            dictionary = []
    verbose = False
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == '--debug':
            del sys.argv[i]
            verbose = True
    if len(sys.argv) < 2:
        _usage_spellcheck()
        sys.exit(0)

    _spellcheck_all(newdict='misspellings.txt~', remove_multiplicity=False,
                    dictionaries=dictionary, verbose=verbose)

def _usage_ref_external():
    print 'doconce ref_external dofile [pubfile --skip_chapter]'
    print 'Must give pubfile if no BIBFILE in dofile.do.txt'
    print '--skip_chapter avoids substitution of Chapter ref{} -> refch[Chapter ...][][].'

def ref_external():
    """
    Examine "# Externaldocuments: ..." in doconce file and publish
    file to suggest a substitution script for transforming
    references to external labels to the ref[][][] generalized
    reference form.
    """
    if len(sys.argv) < 2:
        _usage_ref_external()
        sys.exit(0)

    filename = sys.argv[1]
    if filename.endswith('.do.txt'):
        basename = filename[:-7]
    else:
        basename = filename
    # Analyze the topfile for external documents and publish file
    f = open(basename + '.do.txt', 'r')
    topfilestr = f.read()
    f.close()
    m = re.search('^#\s*[Ee]xternaldocuments:\s*(.+)$', topfilestr,
                  flags=re.MULTILINE)
    if m:
        external_docs = [s.strip() for s in m.group(1).split(',')]
    else:
        print '*** error: no # Externaldocuments: file1, file2, ... in', basename + '.do.txt'
        print '    cannot get info about external documents and their labels!'
        _abort()
    m = re.search('^BIBFILE:\s*(.+)', topfilestr, re.MULTILINE)
    if m:
        pubfile = m.group(1).strip()
    else:
        if len(sys.argv) >= 3:
            pubfile = sys.argv[2]
        else:
            print '*** error: no BIBFILE: file.pub, missing publish file on the command line!'
            _abort()
    print '    working with publish file', pubfile
    import publish
    # Note: we have to operate publish in the directory
    # where pubfile resides
    pubdir, pubname = os.path.split(pubfile)
    if not pubdir:
        pubdir = os.curdir
    this_dir = os.getcwd()
    os.chdir(pubdir)
    pubdata = publish.database.read_database(pubname)
    os.chdir(this_dir)

    def process_external_doc(extdoc_basename):
        topfile = extdoc_basename + '.do.txt'
        if not os.path.isfile(topfile):
            print '*** error: external document "%s" does not exist' % topfile
            _abort()
        f = open(topfile, 'r')
        text = f.read()
        m = re.search('^TITLE:\s*(.+)', text, flags=re.MULTILINE)
        if m:
            title = m.group(1).strip()
        else:
            print '*** error: no TITLE: ... in "%s"' % topfile
            _abort()
        found = False
        key = None
        url = None
        for pub in pubdata:
            if pub['title'].lower() == title.lower():
                key = pub.get('key', None)
                url = pub.get('url', None)
                print '       title:', title
                print '       url:', url
                print '       key:', key
                found = True
                break
        if not found and extdoc_basename != basename:
            print '*** warning: could not find the document'
            print '   ', title
            print '    in the publish database %s' % pubfile

        # Try to load the full doconce file as the result of mako,
        # or as the result of preprocess, or just extdoc_basename.do.txt
        dname, bname = os.path.split(extdoc_basename)
        dofile = os.path.join(dname, 'tmp_mako__' + bname + '.do.txt')
        if os.path.isfile(dofile):
            fullfile = dofile
        else:
            dofile = os.path.join(dname, 'tmp_preprocess__' + bname + '.do.txt')
            if os.path.isfile(dofile):
                fullfile = dofile
            else:
                fullfile = topfile
                # Check that there are no includes:
                m = re.search(r'^#\s+#include', text, flags=re.MULTILINE)
                if m:
                    print '*** error: doconce format is not run on %s' % topfile
                    print '    cannot proceed...'
                    _abort()

        print '    ...processing', fullfile
        f = open(fullfile, 'r')
        text = f.read()
        f.close()
        # Analyze the full text of the external doconce document
        labels = re.findall(r'label\{(.+?)\}', text)
        return title, key, url, labels, text

    import sets
    # Find labels and references in this doconce document
    dummy, dummy, dummy, mylabels, mytext = process_external_doc(basename)
    refs = [(prefix, ref) for dummy, prefix, ref in
            re.findall(r'(^|\(|\s+)([A-Za-z]+?)\s+ref\{(.+?)\}', mytext,
                       flags=re.MULTILINE)]
    refs = [(prefix.strip(), ref.strip()) for prefix, ref in refs]
    refs = list(sets.Set(refs))
    pattern = r'\(ref\{(.+?)\}\)-\(ref\{(.+?)\}\)'
    eqrefs2 = list(sets.Set(re.findall(pattern, mytext)))
    mytext2 = re.sub(pattern, 'XXX', mytext)
    # Now all pairs of equation references are removed, search for triplets
    pattern = r'\(ref\{(.+?)\}\),\s+\(ref\{(.+?)\}\),?\s+and\s+\(ref\{(.+?)\}\)'
    eqrefs3 = list(sets.Set(re.findall(pattern, mytext2)))
    mytext3 = re.sub(pattern, 'XXX', mytext2)
    # Now all pairs and triplets are removed and we can collect the remaining
    # single equation references
    eqrefs1 = re.findall(r'\(ref\{(.+?)\}\)', mytext3)

    extdocs_info = {}
    refs2extdoc = {}
    for external_doc in external_docs:
        title, key, url, labels, text = process_external_doc(external_doc)
        extdocs_info[external_doc] = dict(title=title, key=key,
                                          url=url, labels=labels)
        for prefix, ref in refs:
            if ref not in mylabels:
                if ref in labels:
                    refs2extdoc[ref] = (external_doc, prefix)
        for ref in eqrefs1:
            if ref not in mylabels:
                if ref in labels:
                    refs2extdoc[ref] = (external_doc, 1)
        for ref1, ref2 in eqrefs2:
            if ref1 not in mylabels:
                if ref1 in labels:
                    refs2extdoc[ref1] = (external_doc, 2)
            if ref2 not in mylabels:
                if ref2 in labels:
                    refs2extdoc[ref2] = (external_doc, 2)
        for ref1, ref2, ref3 in eqrefs3:
            if ref1 not in mylabels:
                if ref1 in labels:
                    refs2extdoc[ref1] = (external_doc, 3)
            if ref2 not in mylabels:
                if ref2 in labels:
                    refs2extdoc[ref2] = (external_doc, 3)
            if ref3 not in mylabels:
                if ref3 in labels:
                    refs2extdoc[ref3] = (external_doc, 3)

    # We now have all references in refs2extdoc and can via extdocs_info
    # get additional info about all references
    for label in mylabels:
        if label in refs2extdoc:
            print '*** error: ref{%s} in %s was found as' % (label, basename)
            print '    label{%s} in %s and %s' % \
                  (label, basename, refs2extdoc[label][0])
            _abort()

    # Substitute all external references by ref[][][]
    scriptname = 'tmp_subst_references.sh'
    scriptname2 = 'tmp_grep_references.sh'
    f = open(scriptname, 'w')
    f2 = open(scriptname2, 'w')
    print 'substitution script:', scriptname
    print 'grep script (for context of each substitution):', scriptname2
    dofiles = basename[5:] + '.do.txt' if basename.startswith('main_') else basename + '.do.txt'
    f.write('files="%s"  # files to which substitutions apply\n\n' % dofiles)
    f2.write('files="%s"  # files to which substitutions apply\n\nnlines=6  # no of context lines for each matched line' % dofiles)
    skip_chapter = '--skip_chapter' in sys.argv
    skip_eqs = '--skip_eqs' in sys.argv
    for prefix, ref in refs:
        if skip_chapter and prefix.lower in ('chapter', 'appendix'):
            continue
        if ref not in mylabels:
            f.write(r"doconce subst '%(prefix)s\s+ref\{%(ref)s\}'  " % vars())
            f2.write(r"grep --context=$nlines --line-number -E '%(prefix)s\s+ref\{%(ref)s\}' $files" % vars() + '\n\n')
            ch = 'ch' if prefix.lower() in ('chapter', 'appendix') else ''
            f.write("'ref%(ch)s[%(prefix)s ref{%(ref)s}]" % vars())
            if ref in refs2extdoc:
                if ch:
                    f.write('[ cite{%s}][' %
                            extdocs_info[refs2extdoc[ref][0]]['key'])
                else:
                    f.write('[ in cite{%s}][' %
                            extdocs_info[refs2extdoc[ref][0]]['key'])
                f.write('the document "%s"' %
                        extdocs_info[refs2extdoc[ref][0]]['title'])
                if extdocs_info[refs2extdoc[ref][0]]['url'] is not None:
                    f.write(': "%s"' %
                            extdocs_info[refs2extdoc[ref][0]]['url'])
                if extdocs_info[refs2extdoc[ref][0]]['key'] is not None:
                    f.write(' cite{%s}' %
                            extdocs_info[refs2extdoc[ref][0]]['key'])
                f.write("]'")
            else:
                f.write("[no cite info][no doc info]'")
            f.write(' $files\n\n')
    if skip_eqs:
        f.close()
        return

    if eqrefs1 or eqrefs2 or eqrefs3:
        f.write('\n# Equations:\n')
    for ref in eqrefs1:
        if ref not in mylabels:
            f.write(r"doconce replace '(ref{%(ref)s})'  " % vars())
            f2.write(r"grep --context=$nlines --line-number '(ref{%(ref)s})' $files" % vars() + '\n\n')
            f.write("'ref[(ref{%(ref)s})]" % vars())
            if ref in refs2extdoc:
                f.write('[ in cite{%s}]' %
                        extdocs_info[refs2extdoc[ref][0]]['key'])
                f.write('[reference to specific _equation_ (label %s) in external document "%s": "%s" cite{%s} is not recommended]' %
                        (ref,
                         extdocs_info[refs2extdoc[ref][0]]['title'],
                         extdocs_info[refs2extdoc[ref][0]]['url'],
                         extdocs_info[refs2extdoc[ref][0]]['key']))
            else:
                f.write('[no cite info][no doc info]')
            f.write("' $files\n\n")
    for ref1, ref2 in eqrefs2:
        if ref1 not in mylabels and ref2 not in mylabels:
            f.write(r"doconce replace '(ref{%(ref1)s})-(ref{%(ref2)s})'  " % vars())
            f2.write(r"grep --context=$nlines --line-number '(ref{%(ref1)s})-(ref{%(ref2)s})' $files" % vars() + '\n\n')
            f.write("'ref[(ref{%(ref1)s})-(ref{%(ref2)s})]" % vars())
            if ref1 in refs2extdoc and ref2 in refs2extdoc:
                f.write('[ in cite{%s}]' %
                        extdocs_info[refs2extdoc[ref1][0]]['key'])
                f.write('[reference to specific _equations_ (label %s and %s) in external document "%s": "%s" cite{%s} is not recommended]' %
                        (ref1, ref2,
                         extdocs_info[refs2extdoc[ref1][0]]['title'],
                         extdocs_info[refs2extdoc[ref1][0]]['url'],
                         extdocs_info[refs2extdoc[ref1][0]]['key']))
            else:
                f.write('[no cite info][no doc info]')
            f.write("' $files\n\n")
    for ref1, ref2, ref3 in eqrefs3:
        if ref1 not in mylabels and ref2 not in mylabels \
               and ref3 not in mylabels:
            f.write(r"doconce subst '\(ref\{%(ref1)s\}\),\s+\(ref\{%(ref2)s\}\),?\s+and\s+\(ref{%(ref3)s\}\)'  " % vars())
            f2.write(r"grep --context=$nlines --line-number -E '\(ref\{%(ref1)s\}\),\s+\(ref\{%(ref2)s\}\),?\s+and\s+\(ref{%(ref3)s\}\)' $files" % vars() + '\n\n')
            f.write("'ref[(ref{%(ref1)s}), (ref{%(ref2)s}), and (ref{%(ref3)s})]" % vars())
            if ref1 in refs2extdoc and ref2 in refs2extdoc \
                   and ref3 in refs2extdoc:
                if refs2extdoc[ref1][0] == refs2extdoc[ref2][0] and \
                   refs2extdoc[ref2][0] == refs2extdoc[ref3][0]:
                    f.write('[ in cite{%s}]' %
                            extdocs_info[refs2extdoc[ref1][0]]['key'])
                else:
                    # the equations come from different external docs
                    s = sets.Set([extdocs_info[refs2extdoc[ref1][0]]['key'],
                                  extdocs_info[refs2extdoc[ref2][0]]['key'],
                                  extdocs_info[refs2extdoc[ref3][0]]['key']])
                    f.write('[ cite{%s}]' % ','.join(list(s)))

                f.write('[reference to specific _equations_ (label %s, %s, and %s) in external document "%s": "%s" cite{%s} is not recommended]' %
                        (ref1, ref2, ref3,
                         extdocs_info[refs2extdoc[ref][0]]['title'],
                         extdocs_info[refs2extdoc[ref][0]]['url'],
                         extdocs_info[refs2extdoc[ref][0]]['key']))
            else:
                f.write('[no cite info][no doc info]')
            f.write("' $files\n\n")
    f.close()

def _usage_latex_problems():
    print 'doconce latex_problems mydoc.log [overfull-hbox-limit --texcode]'
    print """
Interpret the .log file and write out latex problems related to
undefined references, multiply defined labels, and overfull hboxes.
The lower limit for overfull hboxes can be specified as an integer.
--texcode causes the problematic lines in overfull hboxes to be printed.
"""

def latex_problems():
    if len(sys.argv) < 2:
        _usage_latex_problems()
        sys.exit(0)

    try:
        overfull_hbox_limit = float(sys.argv[2])
    except IndexError:
        overfull_hbox_limit = 20

    filename = sys.argv[1]
    if not filename.endswith('.log'):
        filename += '.log'
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    ok_overfull_hboxes = []
    # Springer T2 will have some overfull hboxes for chapter headings,
    # remove these from the report 120.1 and 30.8
    t2 = 't2do.sty' in ''.join(lines)
    if t2:
        ok_overfull_hboxes += ['120.1', '30.8']

    multiply_defined_labels = []
    multiply_defined_labels_pattern = r"LaTeX Warning: Label `(.+?)' multiply defined"
    undefined_references = []
    undefined_references_pattern = r"LaTeX Warning: Reference `(.+?)' on page (.+?) undefined"
    overfull_hboxes = []
    overfull_hboxes_pattern = r"Overfull \\hbox \((.+)pt too wide\) .+lines (.+)"
    for line in lines:
        m = re.search(multiply_defined_labels_pattern, line)
        if m:
            multiply_defined_labels.append(m.group(1))
        m = re.search(undefined_references_pattern, line)
        if m:
            undefined_references.append((m.group(1), m.group(2)))
        m = re.search(overfull_hboxes_pattern, line)
        if m:
            overfull_hboxes.append(
                ('%.1f' % float(m.group(1)), m.group(2).strip()))
    problems = False
    if multiply_defined_labels:
        problems = True
        print '\nMultiply defined labels:'
        for label in multiply_defined_labels:
            print '    ', label
    if undefined_references:
        problems = True
        print '\nUndefined references:'
        for ref, page in undefined_references:
            print '    ', ref, 'on page', page
    if overfull_hboxes:
        texcode = '--texcode' in sys.argv
        if texcode:
            # Load .tex file
            f = open(filename[:-4] + '.tex', 'r')
            texfile = f.readlines()
            f.close()
        problems = True
        print "\nOverfull hbox'es:"
        for npt, at_lines in overfull_hboxes:
            if float(npt) > overfull_hbox_limit and npt not in ok_overfull_hboxes:
                print '    ', npt, 'lines', at_lines
                if texcode:
                    line_range = [int(line)-1 for line in at_lines.split('--')]
                    if line_range[1] - line_range[0] < 4 and r'\end' in texfile[line_range[1]]:
                        # Print more surroundings above
                        print '\n*** printing 6 lines above problem line:'
                        print ''.join(texfile[line_range[0]-6:line_range[1]+1])
                    else:
                        print '\n', ''.join(texfile[line_range[0]:line_range[1]+1])

    if not problems:
        print 'no serious LaTeX problems found in %s!' % filename


def _usage_grep():
    print 'doconce grep FIGURE|MOVIE|CODE doconce-file'

def grep():
    if len(sys.argv) < 3:
        _usage_grep()
        sys.exit(0)

    file_tp = sys.argv[1]
    filenames = []
    for filename in sys.argv[2:]:
        if not filename.endswith('.do.txt'):
            filename += '.do.txt'
        if not os.path.isfile(filename):
            continue  # just drop non-existing files to avoid corrupt output
        f = open(filename, 'r')
        filestr = f.read()
        f.close()

        if file_tp == 'FIGURE':
            pattern = r'^FIGURE:\s*\[(?P<filename>[^,\]]+),?(?P<options>[^\]]*)\]'
            filenames += [filename for filename, dummy in
                          re.findall(pattern, filestr, re.MULTILINE)]
        elif file_tp == 'MOVIE':
            pattern = r'^MOVIE:\s*\[(?P<filename>[^,\]]+),?(?P<options>[^\]]*)\]'
            filenames += [filename for filename, dummy in
                          re.findall(pattern, filestr, re.MULTILINE)]
        elif file_tp == 'CODE':
            pattern = '^@@@CODE +(.+?)\s+'
            filenames += re.findall(pattern, filestr, re.MULTILINE)
        else:
            print '*** error: cannot grep', file_tp, '(not implemented)'
    import sets
    filenames = list(sets.Set(filenames))  # remove multiple filenames
    print ' '.join(filenames)

def _usage_capitalize():
    print 'doconce capitalize [-d file_with_cap_words] doconce-file'
    print 'list of capitalized words can also be in .dict4cap.txt'
    print '(typically, Python, Unix, etc. must be capitalized)'

def capitalize():
    if len(sys.argv) >= 2 and sys.argv[1] == '-d':
        dictionary = [sys.argv[2]]
        del sys.argv[1:3]
    else:
        if os.path.isfile('.dict4cap.txt'):
            dictionary = '.dict4cap.txt'
        else:
            dictionary = ''

    if len(sys.argv) < 2:
        _usage_capitalize()
        sys.exit(0)

    filename = sys.argv[1]

    cap_words = [
        'Celsius', 'Fahrenheit', 'Kelvin',
        'Fahrenheit-Celsius',
        'Newton', 'Gauss', "Gauss'",
        'Legendre', 'Lagrange', 'Markov',
        'Laguerre', 'Taylor', 'Einstein',
        'Maxwell', 'Euler', 'Gaussian', 'Eulerian', 'Lagrangian',
        'Poisson',
        'Heaviside', 'MATLAB', 'Matlab',
        'Trapezoidal', "Simpson's", 'Monte', 'Carlo',
        'ODE', 'PDE', 'Adams-Bashforth', 'Runge-Kutta', 'SIR', 'SIZR', 'SIRV',
        'Python', 'IPython', 'Cython', 'Idle', 'NumPy', 'SciPy', 'SymPy',
        'Matplotlib', 'None', '$N$',
        'Fortran', 'MATLAB', 'SWIG', 'Perl', 'Ruby', 'CPU',
        'DNA', 'British', 'American', 'Internet', # 'Web',
        'HTML', 'MSWord', 'OpenOffice',
        'StringFunction', 'Vec2D', 'Vec3D', 'SciTools', 'Easyviz',
        'Pysketcher',
        ]
    # This functionality is not well implemented so instead of finding
    # a perfect solution we fix well-known special cases.
    # A better software solution would be to read a user-made file
    # with fixes. The fixes below are special for a book project...
    cap_words_fix = [
        ('exer. ref{', 'Exer. ref{'),
        ('exer. (_', 'Exer. (_'),  # latex2doconce external reference
        ('subsection. ref{', 'Subsection. ref{'),
        ('section. ref{', 'Section. ref{'),
        ('chapter. ref{', 'Chapter ref{'),
        ('Python library reference', 'Python Library Reference'),
        # Cannot have C and C++ as a special word since an equation with c
        # will then get capital C...try to repair these cases:
        (' c code', ' C code'),
        (' c program', ' C program'),
        (' c++ ', ' C++ '),
        (' 1d ', ' 1D '),
        (' 2d ', ' 2D '),
        (' 3d ', ' 3D '),
        ('vec2d', 'Vec2D'),
        ('vec3d', 'Vec3D'),
        ('hello, world!', 'Hello, World!'),
        ('hello world', 'Hello World'),
        ('mac os x', 'Mac OS X'),
        ('midpoint integration', 'Midpoint integration'),
        ('midpoint rule', 'Midpoint rule'),
        ('trapozoidal integration', 'Trapozoidal integration'),
        ('trapozoidal rule', 'Trapozoidal rule'),
        ('world wide web', 'World Wide Web'),
        ('cODE', 'code'),
        ('on windows', 'on Windows'),
        ('in windows', 'in Windows'),
        ('under windows', 'under Windows'),
        ('on mac', 'on Mac'),
        ('in mac', 'in Mac'),
        ('under mac', 'under Mac'),
        ('a mac', 'a Mac'),
        ("python's", "Python's"),
        ("forward Euler", "Forward Euler"),
        ("backward Euler", "Backward Euler"),
        ("crank-nicolson", "Crank-Nicolson"),
        ("adams-bashforth", "Adams-Bashforth"),
        ('runge-kutta', 'Runge-Kutta'),
        ]
    for name in 'Newton', 'Lagrange', 'Einstein', 'Poisson', 'Taylor', 'Gibb', \
            'Heun', :
        genetive = "'s"
        cap_words_fix.append((name.lower()+genetive, name+genetive))

    if dictionary:
        f = open(dictionary, 'a')
        cap_words += f.read().split()

    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    shutil.copy(filename, filename + '.old~~')

    filestr, old2new = _capitalize(filestr, cap_words, cap_words_fix)

    f = open(filename, 'w')
    f.write(filestr)
    f.close()
    for old, new in old2new:
        if old != new:
            print old
            print new
            print

def _capitalize(filestr, cap_words, cap_words_fix):
    pattern1 = r'^\s*(={3,9})(.+?)(={3,9})'  # sections
    pattern2 = r'^__(.+?[.:?;!])__'       # paragraphs

    sections   = re.findall(pattern1, filestr, flags=re.MULTILINE)
    paragraphs = re.findall(pattern2, filestr, flags=re.MULTILINE)
    orig_titles1 = [t.strip() for s1, t, s2 in sections]
    orig_equals1 = [s1 for s1, t, s2 in sections]
    orig_titles2 = [t.strip() for t in paragraphs]
    orig_headings1 = [s1 + t + s2 for s1, t, s2 in sections]
    orig_headings2 = ['__' + t + '__' for t
                      in re.findall(pattern2, filestr, flags=re.MULTILINE)]

    #print orig_titles1
    #print orig_titles2

    def capitalize_titles(orig_titles, cap_words):
        cap_words_lower = [s.lower() for s in cap_words]
        new_titles = []
        for title in orig_titles:
            #print '*', title

            # Exercises, problems, are exceptions (view title as what
            # comes after the initial word)
            word0 = title.split()[0]
            if word0 in ['Exercise:', 'Problem:', 'Project:', 'Example:',
                         '[Exercise}:', '{Problem}:', '{Project}:', '{Example}:',]:
                title = title.replace(word0, '').strip()
                new_title = word0 + ' ' + title.capitalize()
            else:
                new_title = title.capitalize()

            words = new_title.split()
            # Handle hyphens
            old_words = words[:]
            for word in old_words:
                if '-' in word:
                    words.remove(word)
                    words += word.split('-')
                if word[0] == '`' and word[-1] == '`':
                    if word in words:
                        words.remove(word)

            for word in words:
                #print '    ', word
                # Strip away non-alphabetic characters
                word_stripped = ''.join([w for w in list(word)
                                         if w.isalpha()])
                #if word != word_stripped:
                    #print '        ', word_stripped
                if word_stripped.lower() in cap_words_lower:
                    #print '        found',
                    try:
                        i = cap_words_lower.index(word_stripped.lower())
                        new_word = word.replace(word_stripped, cap_words[i])
                        new_title = new_title.replace(word, new_word)
                        #print 'as', cap_words[i]
                    except ValueError:
                        pass
                        #print 'Did not find', word_stripped.lower(), 'in', cap_words_lower
                        pass
            #print '>', new_title
            for wrong_words, fixed_words in cap_words_fix:
                if wrong_words in new_title:
                    new_title = new_title.replace(wrong_words, fixed_words)
            new_titles.append(new_title)
        return new_titles

    new_titles1 = capitalize_titles(orig_titles1, cap_words)
    new_titles2 = capitalize_titles(orig_titles2, cap_words)

    old2new = []
    for new_title, orig_title, orig_heading, s1 in \
            zip(new_titles1, orig_titles1, orig_headings1, orig_equals1):
        new_heading = '%s %s %s' % (s1, new_title, s1)
        filestr = filestr.replace(orig_heading, new_heading)
        old2new.append((orig_title, new_title))
    for new_title, orig_title, orig_heading in \
            zip(new_titles2, orig_titles2, orig_headings2):
        new_heading = '__%s__' % new_title
        filestr = filestr.replace(orig_heading, new_heading)
        old2new.append((orig_title, new_title))
    return filestr, old2new


def _usage_md2html():
    print 'Usage: doconce md2html doconce-file'
    print 'Make HTML from pandoc-exteded Markdown'
    print '(.html file from .md pandoc file)'
    print 'The purpose is to fix the HTML code with full MathJax support.'

def md2html():
    """
    Translate a .md file to .html that the HTML code gets full LaTeX
    math support.
    The .md file is fixed, then ``pandoc -f markdown -t html`` is run
    to create HTML from Markdown, then the HTML code is fixed.
    """
    if len(sys.argv) < 2:
        _usage_md2html()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.md'):
        if os.path.isfile(filename + '.md'):
            filename += '.md'
        else:
            raise IOError('no file %s.md' % filename)
    # First make sure \eqref survives the pandoc translation
    f = open(filename ,'r'); text = f.read(); f.close()
    text = text.replace('\\eqref{', 'EQREF{')
    f = open(filename ,'w'); f.write(text); f.close()

    # Translate to HTML and fix the MathJax things
    basename = filename[:-3]
    cmd = 'pandoc -f markdown -t html --mathjax -s -o %s.html %s.md' % \
          (basename, basename)
    print cmd
    failure = os.system(cmd)
    if failure:
        print 'could not run\n', cmd
        sys.exit(1)
    f = open('%s.html' % basename, 'r')
    text = f.read()
    f.close()
    # Add extra info
    pattern = r'(<script src=".+?MathJax\.js)'
    replacement = r"""
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  TeX: {
     equationNumbers: {  autoNumber: "AMS"  },
     extensions: ["AMSmath.js", "AMSsymbols.js", "autobold.js", "color.js"]
  }
});
</script>
\g<1>"""
    text = re.sub(pattern, replacement, text)
    text = text.replace('EQREF{', '\\eqref{')

    f = open('%s.html' % basename, 'w')
    f.write(text)
    f.close()
    print 'output in %s.html' % basename


def _usage_md2latex():
    print 'Usage: doconce md2latex doconce-file'
    print 'Make LaTeX from pandoc-exteded Markdown'
    print '(.tex file from .md file).'
    print 'The purpose is to fix the LaTeX code so it compiles.'

def md2latex():
    """
    Read the .md file and fix equation syntax such that LaTeX
    generated from Markdown (via pandoc) compiles.
    """
    if len(sys.argv) < 2:
        _usage_md2latex()
        sys.exit(0)

    filename = sys.argv[1]
    if not filename.endswith('.md'):
        if os.path.isfile(filename + '.md'):
            filename += '.md'
        else:
            raise IOError('no file %s.md' % filename)

    # Remove $$ around begin-end structures
    basename = filename[:-3]
    cmd = 'pandoc -f markdown -t latex -s -o %s.tex %s.md' % \
          (basename, basename)
    print cmd
    failure = os.system(cmd)
    if failure:
        print 'could not run\n', cmd
        sys.exit(1)
    f = open('%s.tex' % basename, 'r')
    text = f.read()
    f.close()
    pattern = r'\$\$(\s*\\begin\{.+?\\end\{.+?)\$\$'
    text = re.sub(pattern, r'\g<1>', text)
    f = open('%s.tex' % basename, 'w')
    f.write(text)
    f.close()
    print 'output in %s.tex' % basename


# ----------------------- functions for insertdocstr -----------------------

def insertdocstr():
    """
    This scripts first finds all .do.txt (DocOnce source code) files in a
    directory tree and transforms these to a format given as command-line
    argument to the present script. The transformed file has the extension
    .dst.txt (dst for Doc STring), regardless of the format.

    In the next phase, all .p.py files (Python files that need preprocessing)
    are visited, and for each file the C-like preprocessor (preprocess.py)
    is run on the file to include .dst.txt files into doc strings.
    The result is an ordinary .py file.

    Example:
    A file basename.p.py has a module doc string which looks like
    '''
    # #include "docstrings/doc1.dst.txt"
    '''

    In the subdirectory docstrings we have the file doc1.do.txt, which
    contains the documentation in DocOnce format. The current script
    detects this file, transforms it to be desired format, say Epytext.
    That action results in doc1.epytext. This file is then renamed to
    doc1.dst.txt.

    In the next step, files of the form basename.p.py is visisted, the
    preprocess program is run, and the docstrings/doc1.dst.txt file is
    inserted in the doc string. One can run with Epytext format, which is
    suitable for running Epydoc on the files afterwards, then run with
    Sphinx, and finally re-run with "plain" format such that only quite
    raw plain text appears in the final basename.py file (this is suitable
    for Pydoc, for instance).

    Usage: doconce insertdocstr format root [preprocessor options]
    """

    try:
        format = sys.argv[1]
        root = sys.argv[2]
    except:
        print 'Usage: doconce insertdocstr format root [preprocessor options]'
        sys.exit(1)

    global doconce_program
    if os.path.isfile(os.path.join('bin', 'doconce')):
        doconce_program = 'python ' + os.path.join(os.getcwd(), 'bin', 'doconce')
    else:
        doconce_program = 'doconce'  # must be found somewhere in PATH
    # alternative: use sys.argv[3] argument to tell where to find doconce
    # can then run "bin/doconce insertdocstr bin" from setup.py

    print '\n----- doconce insertdocstr %s %s\nFind and transform doconce files (.do.txt) ...' % (format, root)
    arg = format
    os.path.walk(root, _walker_doconce, arg)

    print 'Find and preprocess .p.py files (insert doc strings etc.)...'
    arg = ' '.join(sys.argv[3:])  # options for preprocessor
    os.path.walk(root, _walker_include, arg)
    print '----- end of doconce insertdocstr -----\n'



# not used:
def _preprocess_all_files(rootdir, options=''):
    """
    Run preprocess on all files of the form basename.p.ext
    in the directory with root rootdir. The output of each
    preprocess run is directed to basename.ext.
    """
    def _treat_a_dir(arg, d, files):
        for f in files:
            path = os.path.join(d, f)
            if '.p.' in f and not '.svn' in f:
                basename_dotp, ext = os.path.splitext(f)
                basename, dotp = os.path.splitext(basename_dotp)
                outfilename = basename + ext
                outpath = os.path.join(d, outfilename)
                cmd = 'preprocess %s %s > %s' % (options, path, outpath)
                system(cmd)

    os.path.walk(rootdir, _treat_a_dir, None)

def _run_doconce(filename_doconce, format):
    """
    Run doconce format filename_doconce.
    The result is a file with extension .dst.txt (same basename
    as filename_doconce).
    """
    if filename_doconce.startswith('__'):
        # old preprocessed file from aborted doconce execution
        print 'skipped', filename_doconce
        return

    global doconce_program # set elsewhere
    cmd = '%s format %s %s' % (doconce_program, format, filename_doconce)
    print 'run', cmd
    failure, outtext = commands.getstatusoutput(cmd)
    if failure:
        raise OSError, 'Could not run\n%s\nin %s\n%s\n\n\n' % \
              (cmd, os.getcwd(), outtext)
    out_filename = outtext.split()[-1]
    root, ext = os.path.splitext(out_filename)
    new_filename = root + '.dst.txt'
    os.rename(out_filename, new_filename)
    print '(renamed %s to %s for possible inclusion in doc strings)\n' % (out_filename, new_filename)

def _walker_doconce(arg, dir, files):
    format = arg
    # we move to the dir:
    origdir = os.getcwd()
    os.chdir(dir)
    for f in files:
        if f[-7:] == '.do.txt':
            _run_doconce(f, format)
    os.chdir(origdir)

def _run_preprocess4includes(filename_dotp_py, options=''):
    pyfile = filename_dotp_py[:-5] + '.py'
    cmd = 'preprocess %s %s > %s' % (options, filename_dotp_py, pyfile)
    print 'run', cmd
    failure, outtext = commands.getstatusoutput(cmd)
    #os.remove(tmp_filename)
    if failure:
        raise OSError, 'Could not run\n%s\nin %s\n%s\n\n\n' % \
              (cmd, os.getcwd(), outtext)

def _walker_include(arg, dir, files):
    options = arg
    # we move to the dir:
    origdir = os.getcwd()
    os.chdir(dir)
    for f in files:
        if f[-5:] == '.p.py':
            _run_preprocess4includes(f, options)
    os.chdir(origdir)

# ----------------------------------------------------------------------


def which(program):
    """
    Mimic the Unix ``which`` command and return the full path of
    a program whose name is in the `program` argument.
    Return None if the program is not found in any of the
    directories in the user's ``PATH`` variable.
    """
    pathdirs = os.environ['PATH'].split(os.pathsep)
    program_path = None
    for d in pathdirs:
        if os.path.isdir(d):
            if os.path.isfile(os.path.join(d, program)):
                program_path = d
                break
    return program_path


# subst_* below must be global because local functions in _latex2doconce
# disable the use of the important exec(f.read()) statement.

def subst_author_latex2doconce(m):
    author_str = m.group('subst')
    authors = author_str.split(r'\and')
    institutions = ['']*len(authors)
    # footnotes with institutions?
    if r'\footnote{' in author_str:
        for i, author in enumerate(authors):
            if r'\footnote{' in author:
                pattern = r'\footnote\{(.+?\}'
                m2 = re.search(pattern, author)
                if m2:
                    institutions[i] = m2.group(1).strip()
                    authors[i] = re.sub(pattern, '', authors[i])
    authors = ['AUTHOR: %s' % a.strip() for a in authors]
    for i in range(len(authors)):
        if institutions[i] != '':
            authors[i] += ' at ' + institutions[i]
    return '\n'.join(authors)

def subst_minted_latex2doconce(m):
    lang = m.group(1)
    if lang in minted2bc:
        return '!bc ' + minted2bc[lang]
    else:
        return '!bc'

def subst_paragraph_latex2doconce(m):
    title = m.group(1)
    ending = m.group(2)
    if ending != '.':
        title += ending
    return '=== %s ===\n' % title


def _latex2doconce(filestr):
    """Run latex to doconce transformations on filestr."""
    user_subst = []
    user_replace = []
    fixfile = 'latex2doconce_fix.py'
    if os.path.isfile(fixfile):
        # fixfile must contain subst and replace, to be
        # applied _after_ the general subst and replace below
        f = open(fixfile)
        exec(f.read())
        f.close()
        try:
            user_subst = subst
            user_replace = replace
        except NameError, e:
            print fixfile, 'does not contain subst and replace lists'
            print e
            sys.exit(1)
        except Exception, e:
            print fixfile, 'has errors'
            print e
            sys.exit(1)

    # cf. doconce.latex.fix_latex_command_regex to see how important
    # it is to quote the backslash correctly for matching, substitution
    # and output strings when using re.sub for latex text!


    subst = [
        # hpl specific things:
        # \ep is difficult to replace automatically...
        #(r'\\ep(\\|\s+|\n)', r'\thinspace . \g<1>*'), # gives tab hinspace .
        #(r'^\ep\n', r'\\thinspace .\n', re.MULTILINE),
        #(r'\ep\n', r' \\thinspace .\n'),
        #(r'\ep\s*\\\]', r' \\thinspace . \]'),
        #(r'\ep\s*\\e', r' \\thinspace . \e'),
        #(r'\\thinspace', 'thinspace'),
        (r'\\code\{(?P<subst>[^}]+)\}', r'`\g<subst>`'),
        (r'\\emp\{(?P<subst>[^}]+)\}', r'`\g<subst>`'),
        (r'\\codett\{(?P<subst>[^}]+)\}', r'`\g<subst>`'),
        (r'\{\\rm\\texttt\{(?P<subst>[^}]+)\}\}', r'`\g<subst>`'),
        (r'\\idx\{(?P<subst>.+?)\}', r'idx{`\g<subst>`}'),
        (r'\\idxf\{(?P<subst>.+?)\}', r'idx{`\g<subst>` function}'),
        (r'\\idxs\{(?P<subst>.+?)\}', r'idx{`\g<subst>` script}'),
        (r'\\idxp\{(?P<subst>.+?)\}', r'idx{`\g<subst>` program}'),
        (r'\\idxc\{(?P<subst>.+?)\}', r'idx{`\g<subst>` class}'),
        (r'\\idxm\{(?P<subst>.+?)\}', r'idx{`\g<subst>` module}'),
        (r'\\idxnumpy\{(?P<subst>.+?)\}', r'idx{`\g<subst>` (from `numpy`)}'),
        (r'\\idxnumpyr\{(?P<subst>.+?)\}', r'idx{`\g<subst>` (from `numpy.random`)}'),
        (r'\\idxst\{(?P<subst>.+?)\}', r'idx{`\g<subst>` (from `scitools`)}'),
        (r'\\idxfn\{(?P<subst>.+?)\}', r'idx{`\g<subst>` (FEniCS)}'),
        (r'\\idxe\{(?P<attr>.+?)\}\{(?P<obj>.+?)\}', r'idx{`\g<attr>` \g<obj>}'),
        (r'\\refeq\{(?P<subst>.+?)\}', r'(ref{\g<subst>})'),
        (r'^\bpy\s+', r'\bipy' + '\n', re.MULTILINE),
        (r'^\epy\s+', r'\eipy' + '\n', re.MULTILINE),
        # general latex constructions
        # (comments are removed line by line below)
        (r'\\author\{(?P<subst>.+)\}', subst_author_latex2doconce),
        (r'\\title\{(?P<subst>.+)\}', r'TITLE: \g<subst>'),
        (r'\\chapter\*?\{(?P<subst>.+)\}', r'========= \g<subst> ========='),
        (r'\\section\*?\{(?P<subst>.+)\}', r'======= \g<subst> ======='),
        (r'\\subsection\*?\{(?P<subst>.+)\}', r'===== \g<subst> ====='),
        (r'\\subsubsection\*?\{(?P<subst>.+)\}', r'=== \g<subst> ==='),
        (r'\\paragraph\{(?P<subst>.+?)\}', r'__\g<subst>__'),  # modified later
        (r'\\chapter\*?\[.+\]\{(?P<subst>.+)\}', r'========= \g<subst> ========='),
        (r'\\section\*?\[.+\]\{(?P<subst>.+)\}', r'======= \g<subst> ======='),
        (r'\\subsection\*?\[.+\]\{(?P<subst>.+)\}', r'===== \g<subst> ====='),
        (r'\\subsubsection\*?\[.+\]\{(?P<subst>.+)\}', r'=== \g<subst> ==='),
        (r'\\emph\{(?P<subst>.+?)\}', r'*\g<subst>*'),
        (r'\\texttt\{(?P<subst>[^}]+)\}', r'`\g<subst>`'),
        (r'\{\\em\s+(?P<subst>.+?)\}', r'*\g<subst>*'),
        (r'\{\\bf\s+(?P<subst>.+?)\}', r'_\g<subst>_'),
        (r'\{\\it\s+(?P<subst>.+?)\}', r'*\g<subst>*'),
        (r'\\textbf\{(?P<subst>.+?)\}', r'_\g<subst>_'),
        (r'\\eqref\{(?P<subst>.+?)\}', r'(ref{\g<subst>})'),
        (r'(\S)\\label\{', r'\g<1> \\label{'),
        (r'(\S)\\idx(.?)\{', r'\g<1> \\idx\g<2>{'),
        (r'(\S)\\index\{', r'\g<1> \\index{'),
        (r'\\idxfont\{(.+?)\}', r'`\g<1>`'),
        (r'\\index\{(?P<sortkey>.+?)@(?P<index>.+?)\}', r'idx{\g<index>}'),
        (r'\\index\{(?P<subst>.+?)\}', r'idx{\g<subst>}'),
        (r'\\href\{(?P<url>.+?)\}\{(?P<text>.+?)\}', r'"\g<2>": "\g<1>"'),
        (r'\\input\{(?P<subst>.+?)\}', r'# #include "\g<subst>.do.txt"'),
        ] + user_subst
    try:
        for item in subst:
            if len(item) == 2:
                pattern, replacement = item
                cpattern = re.compile(pattern)
            elif len(item) == 3:
                pattern, replacement, flags = item
                cpattern = re.compile(pattern, flags)
            if cpattern.search(filestr):
                #print 'substituting', item, item[0]
                filestr = cpattern.sub(replacement, filestr)
            else:
                #print 'no occurence of', item, item[0]
                pass
    except Exception, e:
        print 'pattern: %s, replacement: %s' % (pattern, replacement)
        raise e

    replace = [
        # make sure \beqan comes before \beqa and \beq in replacements...
        (r'\begin{document}', ''),
        (r'\end{document}', ''),
        (r'\maketitle', ''),
        (r'\[', r'\begin{equation*}'),
        (r'\]', r'\end{equation*}'),
        (r'\beqan', r'\begin{eqnarray*}'),
        (r'\eeqan', r'\end{eqnarray*}'),
        (r'\beqa', r'\begin{eqnarray}'),
        (r'\eeqa', r'\end{eqnarray}'),
        (r'\beq', r'\begin{equation}'),
        (r'\eeq', r'\end{equation}'),
        (r'\ben', r'\begin{enumerate}'),
        (r'\een', r'\end{enumerate}'),
        (r'\bit', r'\begin{itemize}'),
        (r'\eit', r'\end{itemize}'),
        (r'\para{', r'\paragraph{'),
        (r'\refeq', r'\eqref'),
        # dangerous double derivative: ("''", '"'),
        # should be corrected manually ("``", '"'),
        ("Chapter~", "Chapter "),
        ("Section~", "Section "),
        ("Appendix~", "Appendix "),
        ("Appendices~", "Appendices "),
        ("Figure~", "Figure "),
        ("Table~", "Table "),
        ("Chapters~", "Chapters "),
        ("Sections~", "Sections "),
        ("Figures~", "Figures "),
        ("Tables~", "Tables "),
        ("Chap.~", "Chapter "),
        ("Sec.~", "Section "),
        ("App.~", "Appendix "),
        ("Fig.~", "Figure "),
        ("Tab.~", "Table "),
        (".~", ". "),
        ('@@@CMD ', '@@@OSCMD '),

        ] + user_replace

    # Pure string replacements:
    for from_, to_ in replace:
        if from_ in filestr:
            if filestr != filestr.replace(from_, to_):
                filestr = filestr.replace(from_, to_)
                #print '   ....replacing', from_

    # Add extra line after label after section
    filestr = re.sub(r'(==={3,9}\n\\label\{.+?\}) *\n(\w)',
                     r'\g<1>\n\n\g<2>', filestr)

    # problems (cannot understand this old code...):
    """
    problems = [
        r'\Sindex\{',
        r'\Sidx.?\{',
        r'\Slabel\{',
        ]
    for problem in problems:
        p = re.findall(problem, filestr)
        if len(p) > 0:
            print 'PROBLEM:', problem, '\n', p
    """

    math_envirs = 'equation', 'eqnarray', 'eqnarray*', 'align', 'align*', 'equation*'
    math_starters = [r'\begin{%s}' % envir for envir in math_envirs]
    math_starters.append(r'\[')
    math_enders = [r'\end{%s}' % envir for envir in math_envirs]
    math_enders.append(r'\]')

    # add !bt before and !et after math environments:
    for e in math_starters:
        filestr = filestr.replace(e, '\n!bt\n' + e)
    for e in math_enders:
        filestr = filestr.replace(e, e + '\n!et')

    # Make sure there is a line after heading (and label)
    filestr = re.sub(r'(===[A-Za-z0-9 ]+?={3,9})\s+(\\label\{.+?\})\s+([A-Za-z ])', r'\g<1>\n\g<2>\n\n\g<3>', filestr)
    filestr = re.sub('(===[A-Za-z0-9 ]+?={3,9})\s+([A-Za-z ])', r'\g<1>\n\n\g<2>', filestr)

    # minted
    pattern = r'\\begin\{minted}\[?.*\]?{(.+?)\}'
    minted2bc = dict(python='py', cython='cy', fortran='f',
                     c='c', bash='sh', rst='rst',
                     matlab='m', perl='pl',
                     latex='latex', html='html', js='js',
                     xml='xml', ruby='rb')
    minted2bc['c++'] = 'cpp'
    filestr = re.sub(pattern, subst_minted_latex2doconce, filestr)
    filestr = filestr.replace('\\end{minted}', '!ec')
    pattern = r'\\begin\{Verbatim}\[?.*\]?{(.+?)\}'
    filestr = re.sub(pattern, '!bc', filestr)
    filestr = filestr.replace('\\end{Verbatim}', '!ec')
    filestr = filestr.replace('\\begin{verbatim}', '!bc')
    filestr = filestr.replace('\\end{verbatim}', '!ec')
    for lang in minted2bc:
        begin_pattern = r'\begin{%s}' % lang
        end_pattern = r'\end{%s}' % lang
        filestr = filestr.replace(begin_pattern, '!bc ' + minted2bc[lang])
        filestr = filestr.replace(end_pattern, '!ec')

    # ptex2tex code environments:
    code_envirs = ['ccq', 'cod', 'pro', 'ccl', 'cc', 'sys',
                   'dsni', 'sni', 'slin', 'ipy', 'rpy',
                   'pyshell', 'plin', 'ver', 'warn', 'rule', 'summ',
                   'dat', 'txt'] # sequence important for replace!
    for language in 'py', 'f', 'c', 'cpp', 'sh', 'pl', 'm':
        for tp in 'cod', 'pro':
            code_envirs.append(language + tp)

    for e in code_envirs:
        s = r'\b%s' % e
        filestr = filestr.replace(s, '\n!bc ' + e)
        s = r'\e%s' % e
        filestr = filestr.replace(s, '!ec')

    filestr = filestr.replace('bc rpy', 'bc sys')

    # eqnarray -> align
    filestr = filestr.replace(r'{eqnarray', '{align')
    filestr = re.sub(r'&(\s*)=(\s*)&', '&\g<1>=\g<2>', filestr)
    filestr = re.sub(r'&(\s*)\\approx(\s*)&', '&\g<1>\\\\approx\g<2>', filestr)

    # \item alone on line: join with next line (indentation is fixed later)
    filestr = re.sub(r'\\item\s+(\w)', r'\item \g<1>', filestr)

    # Make sure all items in lists are on one line so we do not run
    # into indentation problems (lookahead pattern makes this easy)
    pattern = r'(\\item\s+.+?)(?=\\item|\\end\{)'
    list_items = re.findall(pattern, filestr, flags=re.DOTALL)
    for item in list_items:
        filestr = filestr.replace(item, ' '.join(item.splitlines()) + '\n\n')

    # Find subfigures (problems)
    if filestr.count('\\subfigure{') > 0:
        print '\nPROBLEM: found \\subfigure{...} - should be changed (combine individual'
        print '      figure files into a single file; now subfigures are just ignored!)\n'

    # Figures: assumptions are that subfigure is not used and that the label
    # sits inside the caption. Also, width should be a fraction of
    # \linewidth.

    # figures with width spec: psfig, group1: filename, group2: width, group3: caption
    pattern = re.compile(r'\\begin{figure}.*?\psfig\{.*?=([^,]+?),\s*width=(.+?)\\linewidth.*?\caption\{(.*?)\}\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'FIGURE: [\g<1>, width=\g<2>] {{{{\g<3>}}}}', filestr)
    # note: cannot treat width=10cm, only width=0.8\linewidth
    # figures: psfig, group1: filename, group2: caption
    pattern = re.compile(r'\\begin{figure}.*?\psfig\{.*?=([^,]+).*?\caption\{(.*?)\}\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'FIGURE: [\g<1>, width=400] {{{{\g<2>}}}}', filestr)
    # figures: includegraphics, group1: width, group2: filename, group3: caption
    pattern = re.compile(r'\\begin{figure}.*?\includegraphics\[width=(.+?)\\linewidth\]\{(.+?)\}.*?\caption\{(.*?)\}\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'FIGURE: [\g<2>, width=400 frac=\g<1>] {{{{\g<3>}}}}', filestr)
    # includegraphics with other measures of width and caption after fig
    pattern = re.compile(r'\\begin{figure}.*?\includegraphics\[(.+?)]\{(.+?)\}.*?\caption\{(.*?)\}\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'# original latex figure with \g<1>\n\nFIGURE: [\g<2>, width=400 frac=1.0] {{{{\g<3>}}}}', filestr)
    # includegraphics with other measures of width and caption before fig
    pattern = re.compile(r'\\begin{figure}.*?\caption\{(.*?)\}\includegraphics\[(.+?)]\{(.+?)\}.*?\s*\\end{figure}', re.DOTALL)
    filestr = pattern.sub(r'# original latex figure with \g<2>\n\nFIGURE: [\g<3>, width=400 frac=1.0] {{{{\g<1>}}}}', filestr)

    # Better method: grab all begin and end figures and analyze the complete
    # text between begin and end. That can handle comment lines in figures,
    # which now destroy the regex'es above since they will grab the
    # first image anyway.

    captions = re.findall(r'\{\{\{\{(.*?)\}\}\}\}', filestr, flags=re.DOTALL)
    for caption in captions:
        orig_caption = caption
        # Add label to end of caption
        pattern = r'(\\label\{.*?\})'
        m = re.search(pattern, caption)
        if m:
            label = m.group(1)
            caption = caption.replace(label, '')
            caption = caption.strip() + ' ' + label
        # Strip off comments
        lines = caption.splitlines()
        for i in range(len(lines)):
            if '%' in lines[i] and not r'\%' in lines[i]:
                lines[i] = lines[i].split('%')[0]
        # Make one line
        caption = ' '.join(lines)
        filestr = filestr.replace('{{{{%s}}}}' % orig_caption, caption)


    # Process lists, comment lines, @@@CODE lines, and other stuff
    inside_enumerate = False
    inside_itemize = False
    inside_code = False
    appendix = False
    lines = filestr.splitlines()
    for i in range(len(lines)):
        if lines[i].startswith('!bc'):
            inside_code = True
        if lines[i].startswith('!ec'):
            inside_code = False
        if (not inside_code) and lines[i].lstrip().startswith('%'):
            lines[i] = '# ' + lines[i].lstrip()[1:]
        if lines[i].startswith('@@@CODE'):
            # Translate ptex2tex CODE envir to doconce w/regex
            words = lines[i].split(' ')  # preserve whitespace!
            new_line = ' '.join(words[:2])  # command filename, no space in name
            if len(words) > 2:
                restline = ' '.join(words[2:])
                new_line += ' fromto: '
                if '@' in restline:
                    from_, to_ = restline.split('@')[:2]
                    new_line += re.escape(from_)  # regex in doconce
                    new_line += '@' + re.escape(to_)
                else:
                    new_line += re.escape(restline) + '@'
                new_line = new_line.replace(r'\ ', ' ').replace(r'\,', ',').replace(r'\:', ':')
            lines[i] = new_line

        # two types of lists (but not nested lists):
        if r'\begin{enumerate}' in lines[i] or r'\ben' in lines[i]:
            inside_enumerate = True
            lines[i] = ''
        if r'\begin{itemize}' in lines[i] or r'\bit' in lines[i]:
            inside_itemize = True
            lines[i] = ''
        if inside_enumerate or inside_itemize:
            if lines[i].lstrip().startswith(r'\item'):
                l = re.sub(r'\s*\\item\s*', '', lines[i]).strip()
                lines[i] = '  * ' + l
        if r'\end{enumerate}' in lines[i] or r'\een' in lines[i]:
            inside_enumerate = False
            lines[i] = ''
        if r'\end{itemize}' in lines[i] or r'\eit' in lines[i]:
            inside_itemize = False
            lines[i] = ''
        if re.search(r'^\s*\appendix', lines[i]):
            appendix = True
        if appendix and 'section{' in lines[i] or 'section*{' in lines[i]:
            lines[i] = re.sub(r'section\*?\{(.+?)\}',
                              'section{Appendix: \g<1>}', lines[i])
        if r'\bibliography' in lines[i]:
            lines[i] = re.sub(r'\\bibliography\{(.+?)\}',
                              r'\n_Must run publish import on BibTeX file \g<1>!_\nBIBFILE: papers.pub\n',
                              lines[i])
            lines[i] = re.sub(r'\\bibliographystyle\{.+?\}', '', lines[i])



    # put all newcommands in a file (note: newcommands must occupy only one line!)
    newlines = []
    newcommands = []
    for line in lines:
        l = line.lstrip()
        if l.startswith('\\newcommand{'):
            newcommands.append(l)
        else:
            newlines.append(line)

    filestr = '\n'.join(newlines)
    if newcommands:
        newcommands_file = 'newcommands_keep.tex'
        nf = open(newcommands_file, 'w')
        nf.writelines(newcommands)
        nf.close()

    # Exercises of the following particular format
    pattern = re.compile(r'\\begin\{exercise\}\s*\\label\{(.*?)\}\s*\\exerentry\{(.*?)\}\s*$\s*(.+?)\\hfill\s*\$\\diamond\$\s*\\end\{exercise\}', re.DOTALL|re.MULTILINE)
    filestr = pattern.sub(r'===== Exercise: \g<2> =====\n\label{\g<1>}\nfile=\n\n\g<3>\n', filestr)

    # Fix "Name of program file:" construction in exercises
    lines = filestr.splitlines()
    program_file = None
    for i in range(len(lines)-1, -1, -1):
        if 'Name of program file' in lines[i]:
            m = re.search(r'Name of program file:\s*`([^`]+?)`', lines[i])
            if m:
                program_file = m.group(1)
                lines[i] = ''
        if lines[i] == 'file=':
            if program_file is not None:
                lines[i] = 'file=' + program_file
                program_file = None
            else:
                # No "Name of program file" was found after last file=.
                # This exercise does not have a program file specified.
                lines[i] = ''
    filestr = '\n'.join(lines)

    # Check idx{} inside paragraphs
    lines = filestr.splitlines()
    last_blank_line = -1
    pattern = r'idx\{.+?\}'
    inside_code_or_math = False
    for i in range(len(lines)):
        if lines[i].startswith('!bc') or lines[i].startswith('!bt'):
            inside_code_or_math = True
        if lines[i].startswith('!ec') or lines[i].startswith('!et'):
            inside_code_or_math = False
        if lines[i].strip() == '' and not inside_code_or_math:
            last_blank_line = i
        if 'idx{' in lines[i] and i < len(lines)-1 \
               and lines[i+1].strip() != '':
            # idx on a line and next line is text
            line = re.sub(pattern, '', lines[i]).strip()
            idx = re.findall(pattern, lines[i])
            if line != '':
                # We have idx{} in the middle of a paragraph, try move
                lines[i] = line
            else:
                lines[i] = '# REMOVE (there was just a single idx{...} on this line)'
            lines[last_blank_line] = '\n' + ' '.join(idx) + \
                                     ' ' + lines[last_blank_line]

    # Tables are difficult: require manual editing?
    inside_table = False
    new_lines = []
    headings = []
    nhlines = 0
    align_headings = []
    for i in range(len(lines)):
        if 'begin{table}' in lines[i] or 'begin{tabular}' in lines[i]:
            inside_table = True
            table_lines = []
            if '{tabular}{' in lines[i]:
                align = lines[i].split('{tabular}{')[-1].split('}')[0]
                align = align.replace('|', '')
            else:
                align = None
        if inside_table:
            if '&' in lines[i]:
                line = lines[i].replace('\\\\', '').strip()
                if '\\hline' in line:
                    line = line.replace('\\hline', '')
                    nhlines += 1
                if '\\multicolumn{' in line:
                    m = re.findall(r'\\multicolumn\{\d+\}\{(.)\}\{(.+?)\}',
                                   line)
                    if m:
                        headings = [heading for align_char, heading in m]
                        align_headings = [align_char for align_char, heading in m]
                        line = line.split('&')
                        # Fill headings from right
                        for j in range(len(line)):
                            line[j] = ''
                        for j, h in enumerate(reversed(headings)):
                            line[len(line)-1-j] = h
                        line = '&'.join(line)
                table_lines.append(line)
            else:
                # \hline, end{table, caption
                pass
        else:
            new_lines.append(lines[i])

        if inside_table and ('end{table}' in lines[i] or 'end{tabular}' in lines[i]):
            inside_table = False
            if table_lines:
                max_column_width = 0
                num_columns = 0
                for j in range(len(table_lines)):
                    columns = [s.strip()
                               for s in table_lines[j].split('&')]
                    max_column_width = max([max_column_width] + \
                                           [len(c) for c in columns])
                    num_columns = max(num_columns, len(columns))
                    table_lines[j] = columns
                max_column_width += 2   # add space before/after widest column
                # Construct doconce table
                # (if the formatting gets wrong, see csv2table, that
                # formatting works well)
                width = max_column_width*num_columns + num_columns+1
                separator0 = '|' + '-'*(width-2) + '|'
                separator1 = separator0
                separator2 = separator0
                if align_headings:
                    # Insert align chars for header from the right
                    # (sometimes 1st column may have no header)
                    s = list(separator1)
                    for j in range(len(align_headings)):
                        s[len(s)-1-max_column_width/2 - j*max_column_width] = align_headings[len(align_headings)-1-j]
                    separator1 = ''.join(s)
                if align is not None:
                    # As many chars in align as there are columns
                    s = list(separator2)
                    for j in range(len(align)):
                        s[max_column_width/2 + j*max_column_width] = align[j]
                    separator2 = ''.join(s)
                column_format = ' %%-%ds ' % (max_column_width-2)
                for j in range(len(table_lines)):
                    table_lines[j] = [column_format % c for c in table_lines[j]]
                    table_lines[j] = '|' + '|'.join(table_lines[j]) + '|'
                table = '\n\n' + separator1 + '\n' + table_lines[0] + '\n' + \
                        separator2 + '\n' + '\n'.join(table_lines[1:]) + \
                        '\n' + separator0 + '\n\n'
                if new_lines:
                    new_lines[-1] += table
                else:
                    new_lines.append(table)

    filestr = '\n'.join(new_lines)
    filestr = re.sub(r'^# REMOVE \(there was.+$\s*', '', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'(idx\{.+?\})\s+([^i\n ])', r'\g<1>\n\n\g<2>', filestr)

    # Let paragraphs be subsubsections === ... ===
    pattern = r'__([A-Z].+?)([.?!:])__'
    filestr = re.sub(pattern, subst_paragraph_latex2doconce, filestr)

    # Find all labels and refs and notify about refs to external
    # labels
    problems = False
    labels = re.findall(r'label\{(.+?)\}', filestr)  # figs have label, not \label
    refs = re.findall(r'\\ref\{(.+?)\}', filestr)
    eqrefs = re.findall(r'\\eqref\{(.+?)\}', filestr)
    pagerefs = re.findall(r'\\pageref\{(.+?)\}', filestr)
    refs = refs + eqrefs + pagerefs
    '''
    for ref in refs:
        if ref not in labels:
            print 'found reference but no label{%s}' % ref
            problems = True
            # Attempt to do a generalized reference
            # (Make table of chapters, stand-alone docs and their labels - quite easy if associated chapters and their URLs are in a file!!!)
            filestr = filestr.replace(r'\ref{%s}' % ref,
                      r'(_PROBLEM: external ref_) ref{%s}' % ref)
            #print r'FIX external ref: ref[%(ref)s]["section where %(ref)s is": "http URL with %(ref)s" cite{doc_with_%(ref)s}]["section where %(ref)s is": "http URL with %(ref)s" cite{doc_with_%(ref)s}]' % vars()
    '''
    for ref in pagerefs:
        print 'pageref{%s} should be rewritten' % ref
        filestr = filestr.replace(r'\pageref{%s}' % ref,
            r'(_PROBLEM: pageref_) \pageref{%s}' % ref)
        problems = True

    print '\n## search for CHECK to see if auto editing was correct\n'
    if problems:
        print '\n## search for PROBLEM: to see need for manual adjustments\n\n\n'
    filestr = filestr.replace(r'\label{', 'label{')  # done above
    filestr = filestr.replace(r'\ref{', 'ref{')
    filestr = filestr.replace(r'\cite{', 'cite{')
    filestr = filestr.replace(r'\cite[', 'cite[')
    filestr = filestr.replace(r'\noindent', r"""# #if FORMAT in ("latex", "pdflatex")
\noindent
# #endif""")
    filestr = re.sub(r'\\vspace\{(.+?)\}', r"""# #if FORMAT in ("latex", "pdflatex")
\\vspace{\g<1>}
# #endif""", filestr)
    filestr = filestr.replace(r'\_', '_')
    filestr = filestr.replace(r' -- ', ' - ')
    filestr = filestr.replace(r'}--ref', '}-ref')
    filestr = filestr.replace(r'})--(ref', '})-(ref')
    filestr = filestr.replace(r'~', ' ')
    filestr = filestr.replace(r'\end{table}', '')

    # Treat footnotes
    # Footnote at the end of a sentence: enclose in parenthesis
    # (regex is not perfect so
    pattern = r'\\footnote\{([^}]+)\}\.'
    filestr = re.sub(pattern, '.( _CHECK: footnote_ at end of sentence placed in parenthesis) (\g<1>) ', filestr)
    # Without final . means footnote in the middle of a sentence
    pattern = r'\\footnote\{([^}]+)\}'
    filestr = re.sub(pattern, '( _PROBLEM: footnote_ in the middle of a sentence must be rewritten) (\g<1>)', filestr)

    # Check that !bc, !ec, !bt, !ec are at the beginning of the line
    for envir in 'c', 't':
        for tag in '!b', '!e':
            command = tag + envir
            pattern = r'^ +' + command
            filestr = re.sub(pattern, command, filestr, flags=re.MULTILINE)
    # Ensure a blank line before !bt and !bc for nicer layout
    # (easier with lookahead! - se below)
    #filestr = re.sub(r'([A-Za-z0-9,:?!; ])\n^!bt', r'\g<1>\n\n!bt',
    #                 filestr, flags=re.MULTILINE)
    #filestr = re.sub(r'([A-Za-z0-9,:?!; ])\n^!bc', r'\g<1>\n\n!bc',
    #                 filestr, flags=re.MULTILINE)
    filestr = re.sub(r'\s+(?=^!bt|^!bc)', '\n\n', filestr, flags=re.MULTILINE)

    # Inline equations cause trouble
    filestr = re.sub(r'!et +([^\n])', '!et\n\g<1>', filestr)

    return filestr

def latex2doconce():
    """
    Apply transformations to a latex file to help translate the
    document into DocOnce format.

    Suggestions for preparations: avoid pageref, replace subfigures
    by files combined to a single file, avoid footnotes, index inside
    paragraphs, do not start code blocks with indentation, ...
    """
    print '# #ifdef LATEX2DOCONCE'
    print 'This is the result of the doconce latex2doconce program.'
    print 'The translation from LaTeX is just a helper. The text must'
    print 'be carefully examined! (Be prepared that some text might also'
    print 'be lost in the translation - in seldom cases.)\n'

    filename = sys.argv[1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    filestr = _latex2doconce(filestr)

    print '# #endif'   # end of intro with warnings etc.

    print filestr  # final output


def html2doconce():
    """
    Apply transformations to an html file to help translate the
    document into DocOnce format.
    """
    print '# #ifdef HTML2DOCONCE'
    print 'This is the result of the doconce htmldoconce program.'
    print 'The translation from HTML is just a helper. The text must'
    print 'be carefully examined! (Be prepared that some text might also'
    print 'be lost in the translation - in seldom cases.)\n'

    filename = sys.argv[1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    filestr = _html2doconce(filestr)

    print '# #endif'   # end of intro with warnings etc.

    print filestr  # final output to stdout


def _html2doconce(filestr):
    # All headings
    headings = {1: 7, 2: 5, 3: 3}
    def subst(m):
        border = '='*headings[int(m.group(1))]
        return border + ' ' + m.group(2) + ' ' + border + '\n'

    filestr = re.sub(r'<h(\d)>(.+?)</h\d>', subst, filestr)

    # Paragraphs
    filestr = re.sub(r'<p>\s*', '\n', filestr)
    # Various tags
    filestr = re.sub(r'<em>(.+?)</em>', '*\g<1>*', filestr, flags=re.DOTALL)
    filestr = re.sub(r'<b>(.+?)</b>', '_\g<1>_', filestr, flags=re.DOTALL)
    filestr = re.sub(r'<tt>(.+?)</tt>', '`\g<1>`', filestr, flags=re.DOTALL)
    filestr = re.sub(r'^\s*<title>(.+?)</title>', 'TITLE: \g<1>', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'<!--(.+?)-->', '#\g<1>', filestr, flags=re.DOTALL)
    filestr = re.sub(r'<a href="(.+?)">(.+?)</a>', '"\g<2>": "\g<1>"', filestr,
                     flags=re.DOTALL)
    filestr = re.sub(r'<img.*? src="(.+?)".*?>',
                     '\nFIGURE: [\g<1>, width=600 frac=1]\n', filestr,
                     flags=re.DOTALL)
    filestr = re.sub(r'\s*^<pre>\s*', '\n\n!bc cod\n', filestr,
                     flags=re.MULTILINE)
    filestr = re.sub(r'</pre>\s*', '!ec\n', filestr,
                     flags=re.MULTILINE)
    # <code>?
    filestr = re.sub(r'<ul>', '\n', filestr)
    filestr = re.sub(r'</ul>', '\n', filestr)
    # All lists become bullet lists, read line by line and use a stack
    # to improve this
    if '<ol>' in filestr:
        print '*** warning: enumerated lists become bullet lists'
    filestr = re.sub(r'<ol>', '\n', filestr)
    filestr = re.sub(r'</ol>', '\n', filestr)
    filestr = re.sub(r'<li>', '  * ', filestr)

    if '<table' in filestr:
        print '*** warning: html2doconce cannot handle tables.'
        print '    Recommendation: edit manually to CSV format and run'
        print '    doconce csv2table command to create table.'

    return filestr

def latex_dislikes():
    """
    Report constructions in latex that will not translate to doconce
    format by latex2dococe and constructions that are not recommended
    for common other formats.

    Rules:

      * Collect all newcommands in a separate file, one definition
        per line (i.e., multi-line definitions are not allowed).
      * Do not use environments for algorithms.
      * Do not use environments for computer code in floating figures.
      * Tables will not be floating. Computer code, tables, algorithms,
        anything but figures, will be inline at the position where they
        are defined.
      * Do not use `description` lists.
    """
    filename = sys.argv[1]
    f = open(filename, 'r')
    filestr = f.read()
    f.close()
    # Should we first run through latex2doconce? Many fixes there
    # simplifies things here...
    filestr = _latex2doconce(filestr)

    lines = filestr.splitlines()
    # Add line numbers
    for i in range(len(lines)):
        lines[i] = '%4d: ' % (i+1) + lines[i]
    lines = '\n'.join(lines).splitlines()

    # add line numbers to each line in the latex file
    # list matches (begin, commands) that are problematic
    # and report them for every line
    begin_likes = [
        'equation',
        'equation*',
        'align',
        'align*',
        'itemize',
        'enumerate',
        ]
    begin_ok = [
        'eqnarray',
        'eqnarray*',
        ]

    # dislikes: list of (regex, explanation)
    dislikes = [(r'%s~?\s*\\ref\{(.+?)\}' % tp,
                 r'use %s in \g<1>' % (tp[0].upper() + tp[1:]))
                for tp in
                ('section', 'chapter', 'appendix',
                 'sec.', 'chap.', 'app.')]
    dislikes += [
        (r'\\subfigure', 'Avoid \\subfigure, combine images to a single new image.'),
        (r'\\pageref', 'Avoid \\pageref entirely (page numbers do not make sense in most electronic formats).'),
        #(r'\\psfig\{', 'Avoid \\psfig, use \\includegraphics.'),
        (r'\\begin\{table\}', 'Tables are handled, but can easily become problematic. Test outcome of latex2doconce for this table, make it inline (only tabular) and of a form that easily translates to doconce.'),
        (r'\\begin\{tabular\}', 'Tables are handled, but can easily become problematic. Test outcome of latex2doconce for this tabular environment and adjust if necessary/possible.'),
        ]
    likes_commands = []

    for line in lines:
        if r'\begin{' in line:
            m = re.search(r'\begin\{(.+?)\}', line)
            if m:
                envir = m.group(1)
                if envir in begin_likes:
                    pass # fine!
                elif envir in begin_ok:
                    print """
Found \\begin{%s}, which can be handled, but it is
recommended to avoid this construction.""" % envir
                else:
                    print """
Found \\begin{%s}, which will not carry over to DocOnce
and other formats.""" % envir
                    # Could have message here (begin_messages) that
                    # guide rewrites, e.g., lstlisting etc.
                print line + '\n'

        for regex, message in dislikes:
            if re.search(regex, line):
                print message
                print line + '\n'


# ---- Attempt to make a pygments syntax highlighter for DocOnce ----
try:
    import pygments as pygm
    from pygments.lexer import RegexLexer, \
         bygroups, include, using, this, do_insertions
    from pygments.token import Punctuation, Text, Comment, Keyword, \
         Name, String, Generic, Operator, Number, Whitespace, Literal
    from pygments.formatters import HtmlFormatter
    from pygments import highlight
    from pygments.styles import get_all_styles
except ImportError:
    pygm = None
    print 'pygments is not installed'
    _abort()

class DocOnceLexer(RegexLexer):
    """
    Lexer for DocOnce files.
    """

    name = 'DocOnce'
    aliases = ['doconce']
    filenames = ['*.do.txt']
    mimetypes = ['text/x-doconce']

    tokens = {
        'general': [
            (r'\#.*\n', Comment),
            (r'[{}]', Name.Builtin),
        ],
        'root': [
            (r' .*\n', Text),
            (r'\#.*\n', Comment),
            (r'idx', Name.Builtin),
            (r'label\{.+?\}', Name.Builtin),
            (r'TITLE:', Generic.Heading),
            (r'AUTHOR:', Generic.Heading),
            (r'DATE:', Generic.Heading),
            (r'TOC:', Generic.Heading),
            (r'FIGURE:', Name.Builtin),
            (r'MOVIE:', Name.Builtin),
            #(r'!.+\n', Generic.Strong),
            (r'!.+\n', Name.Builtin),
            (r'@@@CODE .*\n', Generic.Subheading),
            (r'=== .*\n', Generic.Subheading),
            (r'__.+?__\n', Generic.Subheading),
            (r'={3,9} .*\n', Generic.Heading),
            (r'\\\[', String.Backtick, 'displaymath'),
            (r'\\\(', String, 'inlinemath'),
            (r'\$\$', String.Backtick, 'displaymath'),
            (r'\$', String, 'inlinemath'),
            (r'\\([a-zA-Z]+|.)', Keyword, 'command'),
            (r'.*\n', Text),
        ],
        'math': [
            (r'\\([a-zA-Z]+|.)', Name.Variable),
            include('general'),
            (r'[0-9]+', Number),
            (r'[-=!+*/()\[\]]', Operator),
            (r'[^=!+*/()\[\]\\$%&_^{}0-9-]+', Name.Builtin),
        ],
        'inlinemath': [
            (r'\\\)', String, '#pop'),
            (r'\$', String, '#pop'),
            include('math'),
        ],
        'displaymath': [
            (r'\\\]', String, '#pop'),
            (r'\$\$', String, '#pop'),
            (r'\$', Name.Builtin),
            include('math'),
        ],
        'command': [
            (r'\[.*?\]', Name.Attribute),
            (r'\*', Keyword),
            (r'', Text, '#pop'),
        ],
    }

    def analyse_text(text):
        if text[:7] == 'Index: ':
            return True
        if text[:5] == 'diff ':
            return True
        if text[:4] == '--- ':
            return 0.9

class DocOnceLexer(RegexLexer):
    """
    Lexer for DocOnce files.

    Built this one from TexLexer and extended with DocOnce stuff.
    Difficult to get both to work
    """

    name = 'DocOnce'
    aliases = ['doconce']
    filenames = ['*.do.txt']
    mimetypes = ['text/x-doconce']

    tokens = {
        'general': [
            (r'#.*?\n', Comment),
            (r'[{}]', Name.Builtin),
            (r'[&_^]', Name.Builtin),
        ],
        'root': [
            (r'\\\[', String.Backtick, 'displaymath'),
            (r'\\\(', String, 'inlinemath'),
            (r'\$\$', String.Backtick, 'displaymath'),
            (r'\$', String, 'inlinemath'),
            (r'\\([a-zA-Z]+|.)', Keyword, 'command'),
            (r'!.+\n', Name.Builtin),
            (r'@@@CODE .*\n', Generic.Subheading),
            (r'=== .*\n', Generic.Subheading),
            (r'__.+?__\n', Generic.Subheading),
            (r'={3,9} .+? ={3,9}\n', Generic.Heading),
            (r'idx', Name.Builtin),
            (r'label\{.+?\}', Name.Builtin),
            (r'TITLE:', Generic.Heading),
            (r'AUTHOR:', Generic.Heading),
            (r'DATE:', Generic.Heading),
            (r'TOC:', Generic.Heading),
            (r'FIGURE:', Name.Builtin),
            (r'MOVIE:', Name.Builtin),
            include('general'),
            # these two are crucial - no 2 turns on latex math everywhere
            # but not doconce, no 1 does the other way around
            #(r'.*\n', Text),
            (r'[A-Za-z0-9 ]?\n', Text),  # makes latex stuff correct
            (r'[^\\$%&_^{}]+', Text),
            (r'.*\n', Text),
        ],
        'math': [
            (r'\\([a-zA-Z]+|.)', Name.Variable),
            include('general'),
            (r'[0-9]+', Number),
            (r'[-=!+*/()\[\]]', Operator),
            (r'[^=!+*/()\[\]\\$%&_^{}0-9-]+', Name.Builtin),
        ],
        'inlinemath': [
            (r'\\\)', String, '#pop'),
            (r'\$', String, '#pop'),
            include('math'),
        ],
        'displaymath': [
            (r'\\\]', String, '#pop'),
            (r'\$\$', String, '#pop'),
            (r'\$', Name.Builtin),
            include('math'),
        ],
        'command': [
            (r'\[.*?\]', Name.Attribute),
            (r'\*', Keyword),
            (r'', Text, '#pop'),
        ],
    }
    """
    tokens = {
        'general': [
            (r'\#.*\n', Comment),
            (r'[{}]', Name.Builtin),
        ],
        'root': [
            (r' .*\n', Text),
            #(r'!.+\n', Generic.Strong),
            (r'\\\[', String.Backtick, 'displaymath'),
            (r'\\\(', String, 'inlinemath'),
            (r'\$\$', String.Backtick, 'displaymath'),
            (r'\$', String, 'inlinemath'),
            (r'\\([a-zA-Z]+|.)', Keyword, 'command'),
        ],
        'math': [
            (r'\\([a-zA-Z]+|.)', Name.Variable),
            include('general'),
            (r'[0-9]+', Number),
            (r'[-=!+*/()\[\]]', Operator),
            (r'[^=!+*/()\[\]\\$%&_^{}0-9-]+', Name.Builtin),
        ],
        'inlinemath': [
            (r'\\\)', String, '#pop'),
            (r'\$', String, '#pop'),
            include('math'),
        ],
        'displaymath': [
            (r'\\\]', String, '#pop'),
            (r'\$\$', String, '#pop'),
            (r'\$', Name.Builtin),
            include('math'),
        ],
        'command': [
            (r'\[.*?\]', Name.Attribute),
            (r'\*', Keyword),
            (r'', Text, '#pop'),
        ],
    }
    """

    def analyse_text(text):
        return True

# The version below is the best one so far (still far from complete, not
# everything works as intended, so much experimentation is needed to
# extend it, but the result with doconce pygmentize mydoc perldoc looks
# fine). Need to understand more of how the lexers work to make
# further progress: look at DiffLexer, TexLexer, RstLexer, and other text
# lexers in /usr/local/lib/python2.7/dist-packages/Pygments-1.6dev_20131113-py2.7.egg/pygments/lexers/text.py.
# It seems that there is no markdown lexer on the net.

class DocOnceLexer(RegexLexer):
    """
    Lexer for DocOnce files.
    """

    name = 'DocOnce'
    aliases = ['doconce']
    filenames = ['*.do.txt']
    mimetypes = ['text/x-doconce']
    #flags = re.MULTILINE | re.DOTALL  # did not work

    tokens = {
        'root': [
            (r' .*\n', Text),
            (r'\#.*\n', Comment),
            (r'(label|ref|idx)\{.+?\}', Name.Builtin),
            (r'\\(begin|end)\{.+?\}', Name.Builtin),
            #(r'\$.+?\$', String),  # works only occasionally
            #(r'label\{.+?\}', Name.Builtin),
            #('idx', Keyword),
            (r'TITLE:.+\n', Generic.Heading),
            (r'AUTHOR:', Generic.Heading),
            (r'DATE:', Generic.Heading),
            (r'TOC:', Generic.Heading),
            (r'FIGURE:.*\n', Name.Builtin),
            (r'MOVIE:.*\n', Name.Builtin),
            (r'![a-z]+', Keyword),
            (r'@@@CODE .*\n', Generic.Subheading),
            (r'__.+?__', Generic.Subheading),
            (r'\|.+\|\n', String),  # tables
            (r'`.+?`', String.Backtick),  # does not work
            (r'".+?"', String),  # does not work
            (r'={3,9} .* ={3,9}\n', Generic.Heading),
            (r'.*\n', Text),
        ],
    }

    def analyse_text(text):
        True

def _usage_pygmentize():
    print 'Usage: doconce pygmentize doconce-file [pygments style]'

def pygmentize():
    """
    Typeset a DocOnce file with pygmentize, using the DocOnceLexer
    class above.

    An alternative is to register the DocOnceLexer with Pygments.
    """
    if len(sys.argv) < 2:
        _usage_pygmentize()
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith('.do.txt'):
        filename += '.do.txt'
    try:
        pygm_style = sys.argv[2]
    except IndexError:
        pygm_style = 'default'

    f = open(filename, 'r');  text = f.read();  f.close()
    lexer = DocOnceLexer()
    formatter = HtmlFormatter(noclasses=True, style=pygm_style)
    text = highlight(text, lexer, formatter)
    f = open(filename + '.html', 'w');  f.write(text);  f.close()
    print 'pygmentized doconce code written to %s.html' % filename

def _usage_makefile():
    print 'Usage:   doconce makefile doconce-file [html pdflatex latex sphinx gwiki pandoc ipynb deck reveal beamer ...]'
    print 'Example: doconce makefile mydoc.do.txt html sphinx'
    print """
A script make.py is generated with the basic steps for running a
spellcheck on .do.txt files followed by commands for producing
output in various formats (in the sequence specified on the command
line). If no formats are specified, html, pdflatex, and sphinx are
produced.

make.py is a template: edit to set the desired options for compiling
to the various formats.

make.py autogenerates a unix shell script with all commands: you may
use this shell script instead of make.py.
"""

def makefile():
    """Generate a generic (Python) makefile for compiling doconce files."""
    if len(sys.argv) < 3:
        _usage_makefile()
        sys.exit(0)

    dofile = sys.argv[1]
    if dofile.endswith('.do.txt'):
        dofile = dofile[:-7]

    formats = sys.argv[2:]

    # make.py with lots of functions for creating everything you can
    # create, easy to use in ipython
    # make.py mydoc sphinx pdflatex beamer

    if not formats:
        formats = ['pdflatex', 'html', 'sphinx', 'deck', 'reveal', 'beamer']

    make = open('make.py', 'w')
    make.write('''\
#!/usr/bin/env python
"""
Automatically generated file for compiling doconce documents.
"""
import sys, glob, os, shutil, subprocess

logfile = 'tmp_output.log'  # store all output of all operating system commands
f = open(logfile, 'w'); f.close()  # touch logfile so it can be appended

unix_command_recorder = []

def system(cmd):
    """Run system command cmd using the simple os.system command."""
    print cmd
    failure = os.system(cmd)
    if failure:
        print """Command
  %s
failed""" % cmd
        sys.exit(1)
    unix_command_recorder.append(cmd)  # record command for bash script

def system(cmd):
    """Run system command cmd using subprocess module."""
    print cmd
    try:
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print """Command
  %s
failed""" % cmd
        print 'Return code:', e.returncode
        print e.output
        sys.exit(1)
    print output
    f = open(logfile, 'a'); f.write(output); f.close()
    unix_command_recorder.append(cmd)  # record command for bash script

def spellcheck():
    for filename in glob.glob('*.do.txt'):
        if not filename.startswith('tmp'):
            cmd = 'doconce spellcheck -d .dict4spell.txt %(filename)s' % vars()
            system(cmd)

def latex(name,
          latex_program='pdflatex',    # or 'latex'
          options='--latex_code_style=vrb',
          ptex2tex='',
          version='paper',             # or 'screen', '2up', 'A4', 'A4-2up'
          postfix='',                  # or 'auto'
          ):
    """
    Make latex/pdflatex (according to latex_program) PDF file from
    the doconce file name (without any .do.txt extension).

    version can take the following values:
      * paper: normal page size, --device=paper
      * 2up: normal page size, --device=paper, 2 pages per sheet
      * A4: A4 page size, --device=paper
      * A4-2up: A4 page size, --device=paper, 2 pages per sheet
      * screen: normal pages size, --device=screen

    If a separate ptex2tex step is wanted, fill in all necessary
    commands in the ptex2tex string.
    """
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')
    system('rm -f %(name)s.aux' % vars())

    if version in ('paper', 'A4', '2up', 'A4-2up'):
        if not '--device=paper' in options:
            options += ' --device=paper'
    elif version == 'screen' and '--device=paper' in options:
        options = options.replace('--device=paper', '')
    if version in ('A4', 'A4-2up'):
        if not '--latex_papersize=a4' in options:
            options += ' --latex_papersize=a4'
    if postfix == 'auto':
        if version == 'paper':
            postfix = '4print'
        elif version == 'screen':
            postfix = '4screen'
        else:
            postfix = version

    # Compile source
    cmd = 'doconce format %(latex_program)s %(name)s %(options)s ' % vars()
    system(cmd)

    # Transform .p.tex to .tex?
    if ptex2tex:
        cmd = ptex2tex
        system(cmd)

    # Load latex file into string for examination
    dofile = open(name + '.tex', 'r')
    text = dofile.read()
    dofile.close()

    latex_options = ''
    if latex_program == 'pdflatex':
        latex_options = '-file-line-error -interaction nonstopmode'

    # Run latex
    shell_escape = ' -shell-escape' if 'begin{minted}' in text else ''
    cmd_latex = '%(latex_program)s%(shell_escape)s %(latex_options)s %(name)s' % vars()
    system(cmd_latex)

    if 'idx{' in text:
        cmd = 'makeindex %(name)s' % vars()
        system(cmd)
    if 'BIBFILE:' in text:
        cmd = 'bibtex %(name)s' % vars()
        system(cmd)
    system(cmd_latex)
    system(cmd_latex)
    if latex_program == 'latex':
        cmd = 'dvipdf %(name)s' % vars()
        system(cmd)
        # Could instead of dvipdf run the old-fashioned dvips and ps2pdf

    if version in ('2up', 'A4-2up'):
        # Use pdfnup to make two pages per sheet
        cmd = 'pdfnup --frame true --outfile %(name)s.pdf %(name)s.pdf' % vars()
        system(cmd)
    if postfix:
        shutil.copy(name + '.pdf', name + '-' + postfix + '.pdf')


def html(name, options='', split=False):
    """
    Make HTML file from the doconce file `name`
    (without any .do.txt extension).
    """
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    cmd = 'doconce format html %(name)s %(options)s ' % vars()
    system(cmd)

    if split:
        cmd = 'doconce split_html %(name)s' % vars()


def reveal_slides(name, options='', postfix='reveal', theme='darkgray'):
    """Make reveal.js HTML5 slides from the doconce file `name`."""
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    if '--pygments_html_style=' not in options:
        from doconce.misc import recommended_html_styles_and_pygment_styles
        combinations = recommended_html_styles_and_pygment_styles()
        options += ' --pygments_html_style=%s' % combinations['reveal'][theme][0]
    if '--keep_pygments_html_bg' not in options:
        options += ' --keep_pygments_html_bg'
    options += ' --html_output="%(name)s-%(postfi)s'

    cmd = 'doconce format html %(name)s %(options)s ' % vars()
    system(cmd)

    cmd = 'doconce slides_html %(name)s-%(postfi)s reveal --html_slide_theme=%(theme)s'
    system(cmd)

def deck_slides(name, options='', postfix='deck', theme='sandstone.default'):
    """Make deck.js HTML5 slides from the doconce file `name`."""
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    if '--pygments_html_style=' not in options:
        from doconce.misc import recommended_html_styles_and_pygment_styles
        combinations = recommended_html_styles_and_pygment_styles()
        options += ' --pygments_html_style=%s' % combinations['deck'][theme][0]
    if '--keep_pygments_html_bg' not in options:
        options += ' --keep_pygments_html_bg'
    options += ' --html_output="%(name)s-%(postfi)s'

    cmd = 'doconce format html %(name)s %(options)s ' % vars()
    system(cmd)

    cmd = 'doconce slides_html %(name)s-%(postfi)s deck --html_slide_theme=%(theme)s'
    system(cmd)

def beamer_slides(name, options='', postfix='beamer', theme='red_shadow',
                  ptex2tex_envir='minted'):
    """Make latex beamer slides from the doconce file `name`."""
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')
    system('rm -f %(name)s.aux' % vars())

    # Compile source
    shell_escape = '-shell-escape' if ptex2tex_envir == 'minted' else ''
    cmd = 'doconce format pdflatex %(name)s %(options)s ' % vars()
    system(cmd)
    # Run latex
    cmd = 'doconce ptex2tex %(name)s envir=%(ptex2tex_envir)s' % vars()
    system(cmd)
    cmd = 'doconce slides_beamer %(name)s --beamer_slide_theme=%(theme)s' % vars()
    system(cmd)
    cmd = 'pdflatex %(shell_escape)s %(name)s'
    system(cmd)
    system(cmd)
    system('cp %(name)s.pdf %(name)s-%(postfi).pdf' % vars())

    cmd = 'doconce slides_html %(name)s-%(postfi)s deck --html_slide_theme=%(theme)s'
    system(cmd)


def sphinx(name, options='', dirname='sphinx-rootdir',
           theme='pyramid', automake_sphinx_options='',
           split=False):
    """
    Make Sphinx HTML subdirectory from the doconce file `name`
    (without any .do.txt extension).
    """
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    cmd = 'doconce format sphinx %(name)s %(options)s ' % vars()
    system(cmd)

    if split:
        cmd = 'doconce split_rst %(name)s' % vars()

    # Create sphinx directory
    cmd = 'doconce sphinx_dir theme=%(theme)s %(options)s %(name)s' % vars()
    system(cmd)

    # Compile sphinx
    cmd = 'python automake_sphinx.py %(automake_sphinx_options)s' % vars()
    system(cmd)

def doconce2format(name, format, options=''):
    """Make given format from the doconce file `name`."""
    if name.endswith('.do.txt'):
        name = name.replace('.do.txt', '')

    # Compile source
    cmd = 'doconce format %(format)s %(name)s %(options)s ' % vars()
    system(cmd)

def plain(name, options=''):
    doconce2format(name, 'plain', options)

def pandoc(name, options=''):
    doconce2format(name, 'pandoc', options)

def ipynb(name, options=''):
    doconce2format(name, 'ipynb', options)

def cwiki(name, options=''):
    doconce2format(name, 'cwiki', options)

def mwiki(name, options=''):
    doconce2format(name, 'mwiki', options)

def gwiki(name, options=''):
    doconce2format(name, 'gwiki', options)

def main():
    """
    Produce various formats from the doconce source.
    """
''')
    make.write('''
    dofile = "%(dofile)s"

    spellcheck()

    common_options = ''
''' % vars())

    for format in formats:
        if format.endswith('latex'):
            make.write("""
    # --- latex ---

    common_latex_options = ' --latex_code_style=vrb'

    for version in 'paper', 'screen':  # , 'A4', '2up', 'A4-2up':
        latex(
          dofile,
          latex_program='pdflatex',
          options=common_options + common_latex_options,
          version=version,
          postfix='auto')
""")
        elif format == 'html':
            make.write("""
    # --- HTML ---

    common_html_options = ''

    # HTML Bootstrap
    bootstrap_options = ' --html_style=bootswatch_readable --html_code_style=inherit --html_pre_style=inherit --html_toc_depth=2 --pygments_html_style=default'

    html(
      dofile,
      options=common_options + common_html_options + bootstrap_options,
      split=True)

    # One long HTML file
    #html(dofile, options=common_options + common_html_options + ' --html_style=bloodish --html_output=%s-1' % dofile, split=False)

    # Solarized HTML
    #html(dofile, options=common_options + common_html_options + ' --html_style=solarized3 --html_output=%s-solarized' % dofile, split=True)
""")
        elif format == 'sphinx':
            make.write("""
    # --- Sphinx ---

    sphinx_themes = ['pyramid',]
    for theme in sphinx_themes:
        dirname = 'sphinx-rootdir' if len(sphinx_themes) == 1 else 'sphinx-rootdir-%s' % theme
        sphinx(
          dofile,
          options=common_options + '',
          dirname=dirname,
          theme=theme,
          automake_sphinx_options='',
          split=False)
""")
        elif format == 'reveal':
            make.write("""

    # --- reveal.js slides ---

    reveal_slides(
      dofile,
      options=common_options + '',
      postfix='reveal',
      theme='darkgray')
""")
        elif format == 'deck':
            make.write("""
    # --- deck.js slides ---

    deck_slides(
      dofile,
      options=common_options + '',
      postfix='deck',
      theme='sandstone.default')
""")
        elif format == 'beamer':
            make.write("""
    # --- latex beamer slides ---

    beamer_slides(
      dofile,
      options=common_options + '',
      postfix='beamer',
      theme='red_shadow',
      ptex2tex_envir='minted')  # 'ans:nt'
""")
        elif format.endswith('wiki') or format in ('pandoc', 'plain', 'ipynb'):
            make.write("""
    doconce2format(dofile, format, options=common_options + '')

""")
    # Are there slides documents in addition?
    dofile_slides = glob.glob('slides_*.do.txt')
    for dofile in dofile_slides:
        # Is the TOC surrounded by a WITH_TOC test directive?
        f = open(dofile, 'r'); text = f.read(); f.close()
        with_toc = ' -DWITH_TOC' if 'WITH_TOC' in text else ''

        dofile = dofile[:-7]
        make.write("""
    # Slides file %(dofile)s
    dofile = "%(dofile)s"
""" % vars())
        for format in formats:
            if format == 'html':
                make.write("""
    html_style = 'bloodish'
    # One long HTML file
    html(
      dofile,
      options=common_options + ' --html_output=%(dofile)s-1 --html_style=%(html_style)s' % vars() + with_toc,
      split=False)
    system('doconce replace "<li>" "<p><li>" %(dofile)s-1.html' % vars())

    # Splitted HTML file
    html(
      dofile,
      options=common_options + ' --html_style=%(html_style)s' % vars() + with_toc,
      split=True)
    system('doconce replace "<li>" "<p><li>" %(dofile)s.html' % vars())

    # One long solarized file
    html(
      dofile,
      options=common_options + ' --html_style=solarized --html_output=%(dofile)s-solarized --pygments_html_style=perldoc --pygments_html_linenos' % vars() + with_toc,
      split=False)
    system('doconce replace "<li>" "<p><li>" %(dofile)s-solarized.html' % vars())
    reveal_slides(
      dofile,
      options=common_options + '',
      postfix='reveal',
      theme='darkgray')

    deck_slides(
      dofile,
      options=common_options + '',
      postfix='deck',
      theme='sandstone.default')
""")
            elif format.endswith('latex'):
                make.write("""
    beamer_slides(
      dofile,
      options=common_options + ' --latex_code_style=pyg',
      postfix='beamer',
      theme='red_shadow')

    # Ordinary latex document (for printing)
    latex(
      dofile,
      latex_program='pdflatex',
      options=common_options + ' --device=paper' + with_toc,
      )
""")
    make.write("""
    # Dump all Unix commands run above as a Bash script
    bash = open('tmp_make.sh', 'w')
    print 'see tmp_make.sh for an equivalent auto-generated unix script'
    bash.write('''\
#!/bin/bash
set -x  # display all commands in output

# Safe execution of a Unix command: exit if failure
function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}
''')
    for cmd in unix_command_recorder:
        if cmd.startswith('doconce format') or cmd.startswith('rm '):
            bash.write('\\n')  # delimiter line in script
        bash.write('system ' + cmd + '\\n')
    bash.close()

    print 'see tmp_output.log for the output of all the commands'
""")
    make.write("""

if __name__ == '__main__':
    main()
""")
    make.close()
    print 'generated make.py for compiling %s.do.txt' % dofile
    print 'make.py is basically a template: edit to set the desired options'
    print '\n*** warning: the generated make.py script is experimental\n    and tested to a very little extent! (latex, html, sphinx are tested)'


def _usage_fix_bibtex4publish():
    print 'Usage: doconce fix_bibtex4publish fil1e.bib file2.bib ...'
    print """
Fix a bibtex file so that the values are enclosed by braces (only)
and publish can import the data.
"""

def fix_bibtex4publish():
    """Edit BibTeX files so that publish can import them."""
    if len(sys.argv) < 1:
        _usage_fix_bibtex4publish()
        sys.exit(0)

    bibfiles = sys.argv[1:]
    for bibfile in bibfiles:
        if not bibfile.endswith('.bib'):
            print bibfile, 'is not a BibTeX file'
            _abort()
        shutil.copy(bibfile, bibfile + '.old~~')
        f = open(bibfile, 'r')
        lines = f.readlines()
        f.close()
        print '\n*** working with', bibfile, '\n'

        for line in lines:
            print line
        keys = []
        for i in range(len(lines)):
            # Classification line? Fix to lower case publication type
            if lines[i].lstrip().startswith('@'):
                m = re.search(r'^\s*@(.+?)\{(.+), *$', lines[i])
                if m:
                    pub_type = m.group(1)
                    key = m.group(2)
                    print '\n--- found %s (key %s)\n' % (pub_type, key)
                    pub_type = pub_type.lower()
                    if pub_type == 'incollection':
                        pub_type = 'inproceedings'
                    keys.append(key)
                    lines[i] = '@%s{%s,\n' % (pub_type, key)
            # Data line? Enclose value in {}, lower case variable, etc.
            elif re.search(r'^\s*[A-Za-z ]+=', lines[i]):
                words = lines[i].split('=')
                old_variable = words[0]
                variable = old_variable.lower().strip()
                if len(words) > 2:
                    # A = in the value..
                    print words
                    value = '='.join(words[1:]).strip()
                else:
                    value = words[1].strip()
                if value[-1] == ',':
                    value = value[:-1]
                old_value = value
                fixed = False
                if value.startswith('"'):
                    value = '{' + value[1:-1].lstrip()
                    fixed = True
                if value.endswith('"'):
                    value = value[:-1].rstrip() + '}'
                    fixed = True
                if value[0] != '{':
                    value = '{' + value.lstrip()
                    fixed = True
                if value[-1] != '}':
                    value = value.rstrip() + '}'
                    fixed = True
                lines[i] = '%-15s = %s,\n' % (variable, value)
                if fixed:
                    print '%s = %s' % (old_variable, old_value)
                    print '...fixed to...'
                    print '%-15s = %s\n' % (variable, value)
            elif lines[i].strip() == '':
                pass # ok
            elif lines[i].strip() == '}':
                pass # ok
            elif lines[i].lstrip().startswith('%'):
                pass # ok
            else:
                # Loose sentence, this one should be glued with the
                # former one
                # NOT IMPLEMENTED
                print '*** error: broken line'
                print lines[i]
                print 'Glue with previous line!'
                _abort()

        f = open(bibfile, 'w')
        f.writelines(lines)
        f.close()

def _usage_list_fig_src_files():
    print 'Usage: doconce list_fig_src_files *.do.txt'

def list_fig_src_files():
    """
    List all figure, movie, and source code files needed in a
    set of .do.txt files. Useful when splitting a document into
    new chapters and directories.
    """
    if len(sys.argv) < 2:
        _usage_list_fig_src_files()
        sys.exit(0)

    from common import INLINE_TAGS
    code_pattern = '^@@@CODE +([^ ]+)'
    figs = []
    movs = []
    cods = []
    for filename in sys.argv[1:]:
        f = open(filename, 'r');  text = f.read();  f.close()
        figs += [figfile for figfile, options, caption in
                 re.findall(INLINE_TAGS['figure'], text, flags=re.MULTILINE)]
        movs += [movfile for movfile, options, caption in
                 re.findall(INLINE_TAGS['movie'], text, flags=re.MULTILINE)]
        cods += re.findall(code_pattern, text, flags=re.MULTILINE)
    if figs:
        print '\n'.join(figs)
    if movs:
        print '\n'.join(movs)
    if cods:
        print '\n'.join(cods)


def _usage_csv2table():
    print 'Usage: doconce csv2table somefile.csv [--headings=clr --columns=rrl --delimiter=;] > outfile'

def csv2table():
    """Convert a csv file to a DocOnce table."""
    if len(sys.argv) < 2:
        _usage_csv2table()
        sys.exit(0)

    delimiter = ','
    for arg in sys.argv[1:]:
        if arg.startswith('--delimiter='):
            delimiter = arg.split('=')[1]

    import csv
    filename = sys.argv[1]
    csvfile = open(filename, 'r')
    table = []
    for row in csv.reader(csvfile, delimiter=delimiter):
        if row:
            table.append(row)
    csvfile.close()
    # Now, table is list of lists
    for i in range(len(table)):
        for j in range(len(table[i])):
            table[i][j] = table[i][j].strip()

    #import pprint;pprint.pprint(table)
    num_columns = 0
    max_column_width = 0
    for row in table:
        num_columns = max(num_columns, len(row))
        for column in row:
            max_column_width = max(max_column_width, len(column))
    # Add empty cells
    for i in range(len(table)):
        table[i] = table[i] + ['']*(num_columns-len(table[i]))

    align_headings = align_columns = 'c'*num_columns
    for arg in sys.argv[1:]:
        if arg.startswith('--headings='):
            align_headings = list(arg.split('=')[1])
            if len(align_headings) != num_columns:
                print '*** error: %s has wrong no of columns (should be %d)' % \
                      (arg, num_columns)
        if arg.startswith('--columns='):
            align_columns = list(arg.split('=')[1])
            if len(align_columns) != num_columns:
                print '*** error: %s has wrong no of columns (should be %d)' % \
                      (arg, num_columns)


    # Construct doconce table
    width = (max_column_width+2)*num_columns + num_columns+1
    separator0 = '|' + '-'*(width-2) + '|'
    separator1 = separator0
    separator2 = separator0

    s = list(separator1)
    for j in range(num_columns):
        s[max_column_width/2 + 1 + j*(max_column_width+3)] = align_headings[j]
    separator1 = ''.join(s)

    s = list(separator2)
    for j in range(num_columns):
        s[max_column_width/2 + 1 + j*(max_column_width+3)] = align_columns[j]
    separator2 = ''.join(s)

    column_format = ' %%-%ds ' % max_column_width
    for j in range(len(table)):
        table[j] = [column_format % c for c in table[j]]
        table[j] = '|' + '|'.join(table[j]) + '|'
    text = '\n\n' + separator1 + '\n' + table[0] + '\n' + \
           separator2 + '\n' + '\n'.join(table[1:]) + \
           '\n' + separator0 + '\n\n'
    print text


# ------------ diff two files ----------------
_diff_programs = {
    'latexdiff': ('http://www.ctan.org/pkg/latexdiff', 'latexdiff'),
    'pdiff': ('http://www.gnu.org/software/a2ps/ http://www.gnu.org/software/wdiff/', 'a2ps wdiff texlive-latex-extra texlive-latex-recommended'),
    'kdiff3': ('http://www.gnu.org/software/wdiff/', 'kdiff3'),
    'diffuse': ('http://diffuse.sourceforge.net/', 'diffuse'),
    'xxdiff': ('http://xxdiff.sourceforge.net/local/', 'fldiff'),
    'fldiff': ('http://packages.debian.org/sid/fldiff', 'fldiff'),
    'meld': ('http://meldmerge.org/', 'meld'),
    'tkdiff.tcl': ('https://sourceforge.net/projects/tkdiff/', 'not in Debian')
    }

def _missing_diff_program(program_name):
    print program_name, 'is not installed.'
    print 'see', _diff_programs[program_name][0]
    if not _diff_programs[program_name][1].startswith('not in'):
        print 'Ubuntu/Debian Linux: sudo apt-get install', \
              _diff_programs[program_name][1]
    sys.exit(1)

def _usage_diff():
    print 'Usage: doconce diff oldfile newfile [diffprog]'
    print 'diffprogram may be difflib (default),'
    print 'pdiff, diff, diffuse, kdiff3, xxdiff, meld, latexdiff'
    print 'Output in diff.*'

def diff():
    """Find differences between two files."""
    if len(sys.argv) < 3:
        _usage_diff()
        sys.exit(0)
    system('rm -f _diff.*')

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    try:
        diffprog = sys.argv[3]
    except:
        diffprog = 'difflib'

    if diffprog == 'difflib':
        diffing_files = pydiff(file1, file2)
        if diffing_files:
            print 'differences found, see ', \
                  ','.join([name + '.html|.txt' for name in diffing_files])

    elif diffprog == 'latexdiff':
        if which('latexdiff'):
            latexdiff(file1, file2)
        else:
            _missing_diff_program('latexdiff')

    else:
        diff_files(file1, file2, diffprog)

def pydiff(files1, files2, n=3, prefix_diff_files='tmp_diff_'):
    """
    Use Python's difflib to compute the difference between
    files1 and files2 (can be corresponding lists of files
    or just two strings if only one set of files is to be
    compared).
    Produce text and html diff.
    """
    import difflib, time, os
    if isinstance(files1, str):
        files1 = [files1]
    if isinstance(files2, str):
        files2 = [files2]

    sizes = []  # measure diffs in bytes
    diff_files = []  # filestem of non-empty diff files generated
    for fromfile, tofile in zip(files1, files2):

        if not os.path.isfile(fromfile):
            print fromfile, 'does not exist'
            _abort()
        if not os.path.isfile(tofile):
            print tofile, 'does not exist'
            _abort()

        fromdate = time.ctime(os.stat(fromfile).st_mtime)
        todate = time.ctime(os.stat(tofile).st_mtime)

        fromlines = open(fromfile, 'U').readlines()
        tolines = open(tofile, 'U').readlines()

        diff_html = difflib.HtmlDiff().make_file(
            fromlines, tolines, fromfile, tofile, context=True, numlines=n)
        diff_plain = difflib.unified_diff(
            fromlines, tolines, fromfile, tofile, fromdate, todate, n=n)
        filename_plain = prefix_diff_files + tofile + '.txt'
        filename_html  = prefix_diff_files + tofile + '.html'

        f = open(filename_plain, 'w')
        # Need to add newlines despite doc saying that trailing newlines are
        # inserted...
        diff_plain = [line + '\n' for line in diff_plain]
        f.writelines(diff_plain)
        f.close()

        f = open(filename_html, 'w')
        f.writelines(diff_html)
        f.close()
        size = os.path.getsize(filename_plain)
        # Any diff? (Could also just test if the file strings are different)
        if size > 4:
            sizes.append(size)
            diff_files.append(prefix_diff_files + tofile)
        else:
            os.remove(filename_plain)
            os.remove(filename_html)
    return diff_files  # empty if no differences

def check_diff(diff_file):
    size = os.path.getsize(diff_file)
    if size > 4:
        print 'diff in', diff_file
    else:
        os.remove(diff_file)


def latexdiff(files1, files2):
    """Highlight file differences with latexdiff."""
    if not which('latexdiff'):
        _missing_diff_program('latexdiff')

    if isinstance(files1, str):
        files1 = [files1]
    if isinstance(files2, str):
        files2 = [files2]

    for fromfile, tofile in zip(files1, files2):

        # Must convert to latex if doconce files
        if fromfile.endswith('.do.txt'):
            basename = fromfile[:-7]
            failure1 = os.system('doconce format pdflatex %s' % basename)
            failure2 = os.system('doconce ptex2tex %s' % basename)
            fromfile = basename + '.tex'

        if tofile.endswith('.do.txt'):
            basename = tofile[:-7]
            failure1 = os.system('doconce format pdflatex %s' % basename)
            failure2 = os.system('doconce ptex2tex %s' % basename)
            tofile = basename + '.tex'

        diff_file = 'tmp_diff_%s.tex' % os.path.basename(tofile)
        failure = os.system('latexdiff %s %s > %s' %
                            (fromfile, tofile, diff_file))
        failure = os.system('pdflatex %s' % diff_file)
        size = os.path.getsize(diff_file)
        if size > 4:
            print 'output in', diff_file[:-3] + 'pdf'


def diff_files(files1, files2, program='diff'):
    """
    Run some diff program:

          diffprog file1 file2 > tmp_diff_*.txt/.pdf/.html

    for file1, file2 in zip(files1, files2).
    """
    if isinstance(files1, str):
        files1 = [files1]
    if isinstance(files2, str):
        files2 = [files2]

    for fromfile, tofile in zip(files1, files2):
        cmd = '%s %s %s' % (program, fromfile, tofile)
        if program in ['diffuse', 'kdiff3', 'xxdiff', 'fldiff', 'meld', 'tkdiff.tcl']:
            # GUI program
            if which(program):
                system(cmd, verbose=True)
            else:
                _missing_diff_program(program)
        elif program == 'diff':
            diff_file = 'tmp_diff_%s.txt' % os.path.basename(tofile)
            system(cmd + ' > ' + diff_file, verbose=True)
            check_diff(diff_file)
        elif program == 'pdiff':
            diff_file = 'tmp_diff_%s' % os.path.basename(tofile)
            if which('pdiff'):
                system(cmd + ' -- -1 -o %s.ps' % diff_file)
                system('ps2pdf -sPAPERSIZE=a4 %s.ps; rm -f %s.ps' %
                       (diff_file, diff_file))
            else:
                _missing_diff_program(program)
            print 'diff in %s.pdf' % diff_file
        else:
            print program, 'not supported'
            _abort()

def _usage_diffgit():
    #print 'Usage: doconce gitdiff diffprog file1 file2 file3'
    print 'Usage: doconce gitdiff file1 file2 file3'

def gitdiff():
    """Make diff of newest and previous version of files (under Git)."""
    if len(sys.argv) < 2:
        _usage_diffgit()
        sys.exit(0)

    #diffprog = sys.argv[1]
    filenames = sys.argv[1:]
    old_files = []
    for filename in filenames:
        failure, output = commands.getstatusoutput('git log %s' % filename)
        if not failure:
            commits = re.findall(r'^commit\s+(.+)$', output,
                                 flags=re.MULTILINE)
            dates = re.findall(r'^Date:\s+(.+)\d\d:\d\d:\d\d .+$', output,
                               flags=re.MULTILINE)
            system('git checkout %s %s' % (commits[1], filename))
            old_filename = '__' + dates[1].replace(' ', '_') + filename
            shutil.copy(filename, old_filename)
            system('git checkout %s %s' % (commits[0], filename))
            old_files.append(old_filename)
            print 'doconce diff', old_filename, filename
            #pydiff(filenames, old_files)
