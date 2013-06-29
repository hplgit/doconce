"""
A simple, rough, and very incomplete translation from latex to doconce.
This is a help script, and manual editing is required, yet much
boring editing is automated.
"""

print """
What is not handled:

  - footnotes
  - tables (can be nice to have pure latex (#ifdef) and doconce version)
  - idx{} inside paragraphs

Such elements must be manually edited.
"""

from doconce.misc import latex2doconce
latex2doconce()
