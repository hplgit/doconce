import re

# !bmchoice or !bquiz !equiz, better with quiz?

_QUIZ_BLOCK = '<<<!!QUIZ_BLOCK'

def mchoice2data(filestr):
    """
    Find all multiple choice questions in the string (file) filestr.
    and create a data structure of all contents of each question.
    """
    pattern = '^!bmchoice.+?^!echoice'
    quiztexts = re.findall(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
    filestr = re.sub(pattern, _QUIZ_BLOCK, filestr,
                     flags=re.DOTALL|re.MULTILINE)
    quizzes = []
    for text in quiztexts:
        quizzes.append(interpret_quiz_text(text))

