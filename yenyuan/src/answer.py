'''
Created on April 18, 2016

@author: bsennish
'''

import sys
from article import Article
from extract_answer import extract_answer
from util import timer_log
import time




def answer():
    article_file, question_file = sys.argv[1:]
    questions = []
    article = None
    with open(question_file, 'r') as f:
        for question in f.readlines():
            questions.append(question.strip())
        f.close()
    with open(article_file, 'r') as f:
        article = Article(f.read())
        f.close()
    for question in questions:
        print(extract_answer(question, article))
        timer_log()


if __name__ == "__main__":
    start = time.time()
    answer()
    print("Completed 20 questions: " + str(time.time() - start))