'''
Created on Apr 9, 2016

@author: zhongzhu
'''

import traceback

from article import Article
from simplify import simplify_sen


with open("../data/set1/a2.txt") as f:
    article = Article(f.read())
    for s in article.sentences():
        try:
            if s:
                print("ORIGINAL:\n" + s)
                for sen in simplify_sen(s):
                    print("DERIVED:\n" + sen)
        except Exception as e:
            print("[Error]" + str(e))
            traceback.print_exc()
        print("")