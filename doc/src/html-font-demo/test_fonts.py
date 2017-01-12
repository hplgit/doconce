from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import subprocess, os, shutil

failure, output = subprocess.getstatusoutput('doconce format html report --html-body-font=?')
fonts = output.splitlines()[-1].split()

for font in fonts:
    print(font)
    font2 = font.replace('+', ' ')
    os.system('doconce format html report --html-body-font=%s --html-heading-font=%s --html-style=bloodish BODY_FONT="%s" HEADING_FONT="%s"' % (font, font, font2, font2))
    shutil.copy('report.html', 'report_%s_%s.html' % (font, font))
    os.system('doconce format html report --html-heading-font=%s --html-style=bloodish BODY_FONT="default" HEADING_FONT="%s"' % (font, font2))
    shutil.copy('report.html', 'report_%s.html' % (font))
