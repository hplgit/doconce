doconce format html quiz --html_style=bootstrap_bloodish
doconce split_html quiz.html
scp quiz.html ._quiz*.html $fb2:www_docs/tmp/