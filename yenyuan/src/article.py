'''
Created on Mar 16, 2016

@author: zhongzhu
'''

import string

from nltk.tokenize import sent_tokenize


class Article(object):
    def __init__(self, r):
        self.raw_content = r
    
    def paragraphs(self):
        return self.raw_content.split("\n")
    
    def sentences(self):
        sentences = []
        for line in self.paragraphs():
            if line and line.endswith('.'):
                printable = set(string.printable)
                line = filter(lambda x: x in printable, line)
                cleaned = sent_tokenize(line)
                sentences.extend(cleaned)
        return sentences
    
    
def test():
    with open("../temp/all.sen", "w+") as t:
        for i in range(1, 10):
            file_name = "../data/set1/a" + str(i) + ".txt"
            with open(file_name) as f:
                article = Article(f.read())
                t.write("\n".join(article.sentences()))