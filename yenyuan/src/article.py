'''
Created on Mar 16, 2016

@author: zhongzhu
'''

import util
import script_wrapper as stanford_parser


class Article(object):
    def __init__(self, r):
        self.raw_content = r
    
    def paragraphs(self):
        return self.raw_content.split("\n")
    
    def sentences(self):
        sentences = []
        for line in self.raw_content.split("\n"):
            if line:
                r = stanford_parser.preprocess(line)
                sentences.extend(r.split('\n'))
        return sentences
    
    
with open("../temp/a_.txt") as f:
    article = Article(f.read())
    print("\n".join(article.sentences()))
    util.timer_log("preprocesss")
