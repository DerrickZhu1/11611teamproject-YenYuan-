'''
Created on Apr 9, 2016

@author: zhongzhu
'''

import traceback

from answer import yes_or_no
from article import Article
from gen_question import question
from simplify import simplify_sen
from extract_answer import extract_answer


with open("../data/set3/a9.txt") as f:
    article = Article(f.read())
    question = "Does universal bytecode make porting easier?"
    ranked_answers = extract_answer(question, article)
    extractions = []
    print("\nQuestion: " + question + "\n")
    print("Top 5 answer sources:\n")
    for i in range(5):
        (sim, sent) = ranked_answers[i]
        print(str(i+1) + ": " + sent)
        print("Cosine similarity: " + str(1-sim) + "\n")
        


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