'''
Created on Apr 9, 2016

@author: zhongzhu
'''
import traceback

from answer import yes_or_no
from article import Article
from gen_question import question


with open("../data/set1/a1.txt") as f:
    article = Article(f.read())
    for s in article.sentences():
        try:
            if s:
                print(s)
                q = question(s)
                print(q)
                print(yes_or_no(s, q))
        except Exception as e:
            print("[Error]" + str(e))
#             traceback.print_exc()
        print("")