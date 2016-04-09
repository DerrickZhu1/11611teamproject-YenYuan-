'''
Created on Apr 8, 2016

@author: zhongzhu
'''
from article import Article
from gen_question import question


with open("../temp/questions.txt", "w+") as qf:
    with open("../data/set1/a1.txt") as f:
        article = Article(f.read())
        for s in article.sentences():
            try:
                if s:
                    print(s)
                    q = question(s)
                    print(q)
                    qf.write(q + "\n")
                    qf.flush()
            except Exception as e:
                print("[Error]" + str(e))
            print("")