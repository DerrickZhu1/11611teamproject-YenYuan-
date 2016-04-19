'''
Created on Apr 9, 2016

@author: zhongzhu
'''

import traceback

from extract_answer import extract_answer
from article import Article
from gen_question import question
from simplify import simplify_sen



with open("../data/set3/a9.txt") as f:
    article = Article(f.read())
    question = "Who created Java?"
    print(extract_answer(question, article))
        


'''
with open("../data/set1/a1.txt") as f:
    article = Article(f.read())
    for s in article.sentences():
        try:
            if s:
                for sen in simplify_sen(s):
                    print(sen)
                    q = question(sen)
                    print(q)
                    print(yes_or_no(sen, q))
        except Exception as e:
            print("[Error]" + str(e))
            traceback.print_exc()
        print("")
'''