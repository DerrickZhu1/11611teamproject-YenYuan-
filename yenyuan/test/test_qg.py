'''
Created on Apr 8, 2016

@author: zhongzhu
'''
from article import Article
from gen_question import question


with open("../data/set1/a1.txt") as f:
    article = Article(f.read())
    for s in article.sentences():
        try:
            if s:
                print(s)
                print(question(s))
        except:
            print("[Error]")
        print("")