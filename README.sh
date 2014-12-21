#!/bin/sh
# Transform README.do.txt to README.md in GitHub flavored Markdown format
doconce format pandoc README --github_md

# The Highlights section of the README file is also featured on the
# main web page in doc/web/index.html, so every update of that section
# in README.do.txt should be propagated manually to the index.html page.
doconce format html README
doconce replace '<li>' '<p><li>' README.html
cp README.html tmp.html
rm -f README.html .*_html_file_collection
echo Copy the source manually from tmp.html into index.html
