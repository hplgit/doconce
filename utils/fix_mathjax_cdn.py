#! /usr/bin/env python
import re, sys

def replace(s):
    # handle siunitx first
    siunitx1_old = '\nMathJax.Ajax.config.path["Contrib"] = "https://cdn.mathjax.org/mathjax/contrib";'
    siunitx2_old = '\nMathJax.Ajax.config.path["Contrib"] = "https://cdn.mathjax.org/mathjax/contrib";'
    siunitx1_new = ', "[Contrib]/siunitx/unpacked/siunitx.js"'
    siunitx2_new = ', "[Contrib]/siunitx/unpacked/siunitx.js"'

    if 'siunitx' in s:
        s = s.replace(siunitx1_old, siunitx1_new)
        s = s.replace(siunitx2_old, siunitx2_new)

    # may be two lines and URL may be http or https
    pattern = '<script type=\"text/javascript\"(\n?) src=\"(https?)://cdn\.mathjax\.org/mathjax/latest/MathJax\.js\?config=TeX-AMS-MML_HTMLorMML\">'
    replacement = '<script type="text/javascript" async\\1 src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML">'
    s = re.sub(pattern, replacement, s)
    return s

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("ERROR: No file name provided")
        print("Usage: %s <html file>" % (sys.argv[0]))
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        old = f.read()
    new = replace(old)
    if new != old:
        with open(filename, 'w') as f:
            f.write(new)
