import itertools
from invoke import format_html
import os

def read_options(subdir):
    default = ()
    infile = os.path.join(subdir, 'OPTIONS')
    if not os.path.isfile(infile):
        return default
    with open(infile, 'r') as f:
        OPTIONS = tuple(l.strip() for l in f.readlines())
        return OPTIONS

def error_msg(args, out, err):
    s = "COMMAND:\n{}\n".format(' '.join(args))
    s += "STDOUT:\n{}\n\nSTDERR:\n{}\n".format(out, err)
    return s

SUBDIRS = ('header')

def _test_subdir(subdir):
    cwd = os.path.abspath(os.curdir)
    OPTIONS = read_options(subdir)
    n = len(OPTIONS)
    try:
        os.chdir(subdir)
        for comb in itertools.product((False, True), repeat=n):
            opts = []
            outfile = subdir
            for i, c in enumerate(comb):
                if c:
                    opts.append('-D%s' % OPTIONS[i])
                    outfile += '__'+OPTIONS[i]

            opts.append('--html_output='+outfile)
            retval, out, err, args = format_html('generic', opts)
            msg = error_msg(args, out, err)
            assert retval == 0, msg
    finally:
        os.chdir(cwd)

def test_header():
    _test_subdir('header')


if __name__ == '__main__':
    test_header()
