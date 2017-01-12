#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import
from builtins import range
from past.builtins import basestring
import shutil, re, sys, os

# NOTE: all newcommands can only span *one line*!
# (necessary requirement since a findall with re.DOTALL will
# not catch the final } of a command, real parsing is then neeeded)

def process_newcommand(line):
    line = line.replace('renewcommand', 'newcommand') # make syntax uniform
    # newcommand without arguments:
    pattern1 = r'\\newcommand\{(.+?)\}\s*\{(.*)\}'
    found = False
    m = re.search(pattern1, line)
    if m:
        # for a newcommand \x we can have many appearances:
        # \x |{\x}|\x{}|(\x)|\x, and replacing \x in \xpoint must
        # but avoided - the idea is to use the regex (\x)([^A-Za-z])
        end_pattern = r'([^A-Za-z])'
        pattern = m.group(1) + end_pattern
        text = m.group(2)
        if not text.endswith('}'):
            # Do not encapsulate plain words in {}
            if not re.search(r'[A-Za-z ,.]{%d}' % len(text), text):
                text = '{' + text + '}'
        replacement = text + r'\g<1>'  # \g<1> is the end_pattern
        # could also use a lookahead pattern: (?=[^A-Za-z]), not tested
        #pattern = m.group(1) + r'(?=[^A-Za-z])'
        #replacement = m.group(2)
        found = True

    # newcommand with arguments:
    pattern2 = r'\\newcommand\{(.+)\}\[(\d)\]\{(.*)\}'
    m = re.search(pattern2, line)
    if m:
        nargs = int(m.group(2))
        args = r'\{(.+?)\}'*nargs
        pattern = m.group(1) + args
        replacement = m.group(3)
        if not replacement.endswith('}'):
            # Do not encapsulate plain words in {}
            if not re.search(r'[A-Za-z ,.]{%d}' % len(replacement), replacement):
                replacement = '{' + replacement + '}'
        for i in range(1, nargs+1):
            replacement = replacement.replace('#%d' % i, r'\g<%d>' % i)
        found = True

    if found:
        # fix \x, \b, \r... etc in strings
        from .latex import fix_latex_command_regex as fix
        pattern = fix(pattern, 'match')
        replacement = fix(replacement, 'replacement')
        return pattern, replacement

def parse_newcommands(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    newcommands = []

    for line in lines:
        line = line.strip()
        if line.startswith('%') or line == '':
            continue
        elif line.startswith(r'\newcommand') or \
             line.startswith(r'\renewcommand'):
            pattern, replacement = process_newcommand(line)
            newcommands.append((pattern, replacement))
        else:
            raise SyntaxError(
                '*** error: illegal line\n  %s\n    line' % line +
                'must start with %% or ' + r'\newcommand')
    return newcommands

def substitute(source, newcommands):
    """
    Expand all newcommands in the list 'newcommands' of
    (pattern, replacement) pairs. source can be a filename
    or just a string with text. If source is a filename, a backup
    file with extension .old~ is first made and then the original
    file is overwritten by the new text with expanded commands.
    """
    if os.path.isfile(source):
        shutil.copy(source, source + '.old~')
        f = open(source, 'r')
        text = f.read()
        f.close()
    else:
        text = source

    from .doconce import debugpr
    for pattern, replacement in newcommands:
        text, n = re.subn(pattern, replacement, text)
        if n:
            debugpr('newcommand replacement: %s -> %s (%d times)'
                    % (pattern, replacement, n))

    # newcommands can be nested, let's repeat
    depth = 2
    for i in range(depth):
        for pattern, replacement in newcommands:
            m = re.search(pattern, text)
            text, n = re.subn(pattern, replacement, text)
            if n:
                debugpr('newcommand replacement: %s -> %s (%d times)'
                        % (pattern, replacement, n))

    if os.path.isfile(source):
        f = open(source, 'w')
        f.write(text)
        f.close()
    else:
        return text

def expand_newcommands(newcommands_files, source):
    if isinstance(newcommands_files, basestring):
        newcommands_files = [newcommands_files]  # always list
    newcommands = []
    for filename in newcommands_files:
        if os.path.isfile(filename):
            newcommands.extend(parse_newcommands(filename))
    #import pprint; pprint.pprint(newcommands)
    return substitute(source, newcommands)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: expand_newcommands.py newcommands_file source_file1 source_file2 ...')
        sys.exit(1)
    newcommands_file = sys.argv[1]
    for source_file in sys.argv[2:]:
        print('expanding newcommands in', source_file)
        expand_newcommands(newcommands_file, source_file)
