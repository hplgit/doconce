"""Minimalistic set of unit tests for DocOnce."""
from __future__ import print_function
from builtins import range
# Note: test.verify is a full test, but requires *a lot* of dependencies.
# This test can be run with an install of plain DocOnce code (even not
# preprocess and mako are used).

import os, shutil

def pydiff(text1, text2, text1_name='text1', text2_name='text2',
           prefix_diff_files='tmp_diff', n=3):
    """
    Use Python's ``difflib`` module to compute the difference
    between strings `text1` and `text2`.
    Produce text and html diff in files with `prefix_diff_files`
    as prefix. The `text1_name` and `text2_name` arguments can
    be used to label the two texts in the diff output files.
    No files are produced if the texts are equal.
    """
    if text1 == text2:
        return False

    # Else:
    import difflib, time, os

    text1_lines = text1.splitlines()
    text2_lines = text2.splitlines()

    diff_html = difflib.HtmlDiff().make_file(
        text1_lines, text2_lines, text1_name, text2_name,
        context=True, numlines=n)
    diff_plain = difflib.unified_diff(
        text1_lines, text2_lines, text1_name, text2_name, n=n)
    filename_plain = prefix_diff_files + '.txt'
    filename_html  = prefix_diff_files + '.html'

    f = open(filename_plain, 'w')
    # Need to add newlines despite doc saying that trailing newlines are
    # inserted...
    diff_plain = [line + '\n' for line in diff_plain]
    f.writelines(diff_plain)
    f.close()

    f = open(filename_html, 'w')
    f.writelines(diff_html)
    f.close()
    return True


def assert_equal_text(text1, text2,
                      text1_name='text1', text2_name='text2',
                      prefix_diff_files='tmp_diff',
                      msg=''):
    if msg != '' and msg[-1] not in ('.', '?', ':', ';', '!'):
        msg += '.'
    if msg != '':
        msg += '\n'
    msg += 'Load tmp_diff.html into a browser to see differences.'
    assert not pydiff(text1, text2, text1_name, text2_name,
                      prefix_diff_files, n=3), msg

def assert_equal_files(file1, file2,
                      text1_name='text1', text2_name='text2',
                      prefix_diff_files='tmp_diff',
                      msg=''):
    text1 = open(file1, 'r').read()
    text2 = open(file2, 'r').read()
    assert_equal_text(text1, text2,
                      text1_name=file1, text2_name=file2,
                      prefix_diff_files=prefix_diff_files,
                      msg=msg)

# ---- Here goes the tests -----

def test_mintest_html():
    filename = '_ref_mintest_bluegray'
    shutil.copy('mintest.do.txt', filename + '.do.txt')
    cmd = 'doconce format html %s --html_style=bootstrap_bluegray --html_output=%s' % (filename, filename)
    failure = os.system(cmd)
    if failure:
        assert False, 'Could not run %s' % cmd
    cmd = 'doconce split_html %s.html' % filename
    failure = os.system(cmd)
    if failure:
        assert False, 'Could not run %s' % cmd

    filenames = [filename+'.html'] + ['._%s%03d.html' % (filename, i)
                                      for i in range(4)]
    for filename in filenames:
        assert_equal_files(filename,
                           os.path.join('mintest', filename))
    print('------- end of html test ------------')

def test_mintest_latex():
    filename = '_ref_mintest'
    shutil.copy('mintest.do.txt', filename + '.do.txt')
    cmd = 'doconce format pdflatex %s --latex_code_style=vrb' % filename
    failure = os.system(cmd)
    if failure:
        assert False, 'Could not run %s' % cmd
    filenames = [filename+'.tex']
    for filename in filenames:
        assert_equal_files(filename, os.path.join('mintest', filename))
    print('------- end of latex test ------------')

def test_mintest_plain():
    filename = '_ref_mintest'
    shutil.copy('mintest.do.txt', filename + '.do.txt')
    cmd = 'doconce format plain %s' % filename
    failure = os.system(cmd)
    if failure:
        assert False, 'Could not run %s' % cmd
    filenames = [filename+'.txt']
    for filename in filenames:
        assert_equal_files(filename, os.path.join('mintest', filename))
    print('------- end of plain text test ------------')

def test_mintest_ipynb():
    filename = '_ref_mintest'
    shutil.copy('mintest.do.txt', filename + '.do.txt')
    cmd = 'doconce format ipynb %s' % filename
    failure = os.system(cmd)
    if failure:
        assert False, 'Could not run %s' % cmd
    filenames = [filename+'.ipynb']
    for filename in filenames:
        assert_equal_files(filename, os.path.join('mintest', filename))
    print('------- end of plain text test ------------')

if __name__ == '__main__':
    test_mintest_html()
    test_mintest_latex()
    test_mintest_plain()
    test_mintest_ipynb()
