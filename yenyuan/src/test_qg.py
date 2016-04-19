'''
Created on Apr 8, 2016

@author: zhongzhu
'''
import traceback

from article import Article
from gen_question import question
from simplify import simplify_sen


with open("../temp/questions.txt", "w+") as qf:
    with open("../data/set1/a1.txt") as f:
        article = Article(f.read())
        sents = article.sentences()
        for sent in sents[:20]:
            print(sent)
        for ori_sentence in article.sentences():
            try:
                for s in simplify_sen(ori_sentence):
                    if s:
                        print(s)
                        for q in question(s):
                            print(q)
                            qf.write(q + "\n")
                            qf.flush()
            except Exception as e:
                continue
                '''
                print("[Error]" + str(e))
                traceback.print_exc()
                '''
            print("")