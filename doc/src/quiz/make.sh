#!/bin/sh
doconce format html quiz --html_style=bootstrap --html_code_style=inherit -DDOCONCE --quiz_horizontal_rule=off
doconce split_html quiz.html

# publish
cp -r quiz.html ._quiz*.html fig ../../pub/quiz