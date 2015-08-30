#!/bin/sh
pygmentize -l text -f html -O full,style=default -o demo.do.txt.html demo.do.txt

# wordpress.com
doconce format html demo -DBLOG=wordpress --wordpress
cp demo.html demo_wordpress.html
doconce subst 'defined in <b>.+' '' demo_wordpress.html  # refs don't work
pygmentize -l html -f html -O full,style=default -o demo_wordpress.html.html demo_wordpress.html
# fix

# Google Blogger
doconce format html demo -DBLOG=google
pygmentize -l html -f html -O full,style=default -o demo.html.html demo.html

doconce format mwiki demo

# need to update doconce.blogspot.no with new text
# and doconce.wordpress.com
# and http://doconcedemo.jumpwiki.com/wiki/First_demo
# and http://doconcedemo.shoutwiki.com/wiki/Doconce_demo_page
# (recall that new shout wikis require files to be uploaded)
# and test in http://en.wikibooks.org/wiki/Sandbox

doconce sphinx_dir copyright=hpl title=demo demo
python automake_sphinx.py
# check out sphinx-rootdir/_build/html/demo.html
