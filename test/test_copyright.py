from __future__ import print_function
import os, shutil, sys, re, glob
shutil.copy('copyright.do.txt', 'tmp_copyright.do.txt')
name = 'tmp_copyright'  # DocOnce file

def system(cmd):
    print(cmd)
    failure = os.system(cmd)
    if failure:
        sys.exit(1)

def grep(pattern, filenames):
    if isinstance(filenames, str):
        filenames = [filenames]
    results = []
    for filename in filenames:
        results.append('------------------- File: ' + filename + '\n')
        with open(filename, 'r') as f:
            text = f.read()
            results.append('\n'.join(re.findall(pattern, text, flags=re.MULTILINE)))
    return '\n'.join(results)

book = 'True'
years = ['', 'present', '2000-2010', '2000-present', '2000-2100']
licenses = ['', 'CC BY', 'CC BY-NC', 'Released under the MIT license.']
results = []

for format in 'pdflatex', 'sphinx', 'html':
    counter = 0
    for year in years[:1]:
        for license_ in licenses:
            copyright_ = '{copyright'
            if year:
                copyright_ += ', ' + year
            if license_:
                copyright_ += '|' + license_
            copyright_ += '}'
            counter += 1
            cmd = 'doconce format %s %s COPYRIGHT="%s" BOOK=%s --cite_doconce' % (format, name, copyright_, book)
            if format == 'pdflatex':
                cmd += ' --latex_code_style=vrb'
            elif format == 'html':
                cmd += ' --html_output=%s%d' % (name, counter)
            print(cmd)
            system(cmd)
            if format == 'html':
                cmd = 'doconce split_html %s%d.html' % (name, counter)
                system(cmd)
                results.append(grep('&copy;.+', ['%s%d.html' % (name, counter)] + glob.glob('._%s%d*.html' % (name, counter))))
            elif format == 'sphinx':
                cmd = 'doconce split_rst %s.rst' % name
                system(cmd)
                cmd = 'doconce sphinx_dir theme=alabaster dirname=tmp_sphinx-rootdir%d %s' % (counter, name)
                system(cmd)
                cmd = 'python automake_sphinx.py'
                system(cmd)
                results.append(grep('^.*copyright =.+', 'tmp_sphinx-rootdir%d/conf.py' % counter))
            elif format == 'pdflatex':
                # The long copyright footer looks nicer with a controlled linebreak
                system(r'doconce replace "Released under" "\\\\ Released under" %s.tex' % name)
                cmd = 'pdflatex %s' % name
                system(cmd)
                cmd = 'pdflatex %s' % name
                system(cmd)
                shutil.copy('%s.pdf' % name, '%s%d.pdf' % (name, counter))
                results.append(grep(r'\\fancyfoot\[C\]\{\{\\footnotesize .+', name + '.tex'))
results = '\n'.join(results)

with open('test_copyright.out', 'w') as f:
    f.write(results)
