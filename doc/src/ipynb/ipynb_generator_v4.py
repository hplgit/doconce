import sys, os, re

# Mapping of shortnames like py to full language
# name like python used by markdown/pandoc
shortname2language = dict(
    py='Python', ipy='Python', pyshell='Python', cy='Python',
    c='C', cpp='Cpp', f='Fortran', f95='Fortran95',
    rb='Ruby', pl='Perl', sh='Shell', js='JavaScript', html='HTML',
    tex='Tex', sys='Bash',
    )

def read(text, argv=sys.argv[2:]):
    lines = text.splitlines()
    # First read all include statements
    for i in range(len(lines)):
        if lines[i].startswith('#include "'):
            filename = lines[i].split('"')[1]
            with open(filename, 'r') as f:
                include_text = f.read()
            lines[i] = include_text
    text = '\n'.join(lines)

    # Run Mako
    mako_kwargs = {}
    for arg in argv:
        key, value = arg.split('=')
        mako_kwargs[key] = value

    encoding = 'utf-8'
    try:
        import mako
        has_mako = True
    except ImportError:
        print 'Cannot import mako - mako is not run'
        has_mako = False

    if has_mako:
        from mako.template import Template
        from mako.lookup import TemplateLookup
        lookup = TemplateLookup(directories=[os.curdir])

        text = unicode(text, encoding)
        temp = Template(text=text, lookup=lookup,
                        strict_undefined=True)
        text = temp.render(**mako_kwargs)

    # Parse the cells
    lines = text.splitlines()
    cells = []
    inside = None    # indicates which type of cell we are inside
    fullname = None  # full language name in code cells
    for line in lines:
        if line.startswith('-----'):
            # New cell, what type?
            m = re.search(r'-----([a-z0-9-]+)?', line)
            if m:
                shortname = m.group(1)
                if shortname:
                    # Check if code is to be typeset as static
                    # Markdown code (e.g., shortname=py-t)
                    astext = shortname[-2:] == '-t'
                    if astext:
                        # Markdown
                        shortname = shortname[:-2]
                        inside = 'markdown'
                        cells.append(['markdown', 'code', ['\n']])
                        cells[-1][2].append('```%s\n' % fullname)
                    else:
                        # Code cell
                        if shortname in shortname2language:
                            fullname = shortname2language[shortname]
                        inside = 'codecell'
                        cells.append(['codecell', fullname, []])
                else:
                    # Markdown cell
                    inside = 'markdown'
                    cells.append(['markdown', 'text', ['\n']])
            else:
                raise SyntaxError(
                    'Wrong syntax of cell delimiter:\n%s'
                    % repr(line))
        else:
            # Ordinary line in a cell
            if inside in ('markdown', 'codecell'):
                cells[-1][2].append(line)
            else:
                raise SyntaxError(
                    'line\n  %s\nhas not beginning cell delimiter'
                    % line)
    # Merge the lines in each cell to a string
    for i in range(len(cells)):
        if cells[i][0] == 'markdown' and cells[i][1] == 'code':
            # Add an ending ``` of code
            cells[i][2].append('```\n')
        cells[i][2] = '\n'.join(cells[i][2])
    import pprint
    return cells

def write(cells):
    """Turn cells list into valid IPython notebook code."""
    # Use IPython.nbformat functionality for writing the notebook
    from IPython.nbformat.v4 import (
        new_code_cell, new_markdown_cell, new_notebook)
    nb_cells = []

    for cell_tp, language, block in cells:
        if cell_tp == 'markdown':
            nb_cells.append(new_markdown_cell(source=block))
        elif cell_tp == 'codecell':
            nb_cells.append(new_code_cell(source=block))

    nb = new_notebook(cells=nb_cells)
    from IPython.nbformat import writes
    filestr = writes(nb, version=4)
    return filestr

def driver():
    """Compile a document and its variables."""
    try:
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            text = f.read()
    except (IndexError, IOError) as e:
        print 'Usage: %s filename' % (sys.argv[0])
        print e
        sys.exit(1)
    cells = read(text, argv=sys.argv[2:])
    filestr = write(cells, 3)
    filename = filename[-5:] + '.ipynb'
    with open(filename, 'w') as f:
        f.write(filestr)

def test_notebook_generator():
    """Unit test for nosetests or py.test."""
    argv = ['NAME=Core Dump',
            'ADDRESS=Seg. Fault Ltd and Univ. of C. Space',
            'IC=2']
    with open('.test1.aipynb', 'r') as f:
        text = f.read()
    cells = read(text, argv=argv)
    computed = write(cells, 3).strip()
    print computed

    with open('.test1.ipynb', 'r') as f:
        expected = f.read().strip()

    for c1, c2, n in zip(computed, expected, range(len(expected))):
        if c1 != c2:
            print 'character no.%d differ: %s vs %s' % (n, c1, c2)
    assert computed == expected

if __name__ == '__main__':
    logfile = 'tmp.log'
    if os.path.isfile:
        os.remove(logfile)
    driver()
