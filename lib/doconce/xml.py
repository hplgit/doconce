"""
Start with html.py, let output be begin and end tags surrounding
all constructs. Lists, environments, math, code, exercises can
easily be wrapped in tags.
Paragraphs ends are more challenging but can be treated at the
end: if there is an ordinary text without a closing tag and then
space until <p>, the previous text must be an ordinary paragraph
that should have an </p> at the end.

Sections can be done at the beginning (first native format function
called): just push the occurence of ===+ on to a stack ('chapter',
'section', ...) and empty the stack down the current heading level
when encountering a new heading.

With a doconce to XML translator it is possible to use XML
tools to translate to any desired output since all constructs
are wrapped in tags.
"""
