"""
Add space(s) at the beginning of all lines in a file to allow
the html code not to be interpreted as quizes inside !bc/!ec tags.
"""
import sys
f = open(sys.argv[1], 'r')
try:
    spaces = int(sys.argv[2])
except IndexError:
    spaces = 1
for line in f.read().splitlines():
    print ' '*spaces, line

