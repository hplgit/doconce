"""Extract all quiz environments from quiz.do.txt to a separate document."""
import re
pattern = r'^!bquiz.+?^!equiz\n'
f = open('quiz.do.txt')
text = f.read()
f.close()
quizzes = re.findall(pattern, text, flags=re.MULTILINE|re.DOTALL)
f = open('pure_quiz.do.txt', 'w')
f.write("""\
TITLE: Demo of quizzes
AUTHOR: HPL
DATE: today

This quiz collection is automatically extracted from the documentation
of the "quiz specification format":
"http://hplgit.github.io/doconce/doc/pub/quiz/quiz.html". All syntax
is explained in that document.

""")
for i, quiz in enumerate(quizzes):
    f.write('\n# Quiz %d\n\n' % (i+1) + quiz + '\n\n')
f.close()
