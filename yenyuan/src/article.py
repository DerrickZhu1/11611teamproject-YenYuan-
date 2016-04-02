'''
Created on Mar 16, 2016

@author: zhongzhu
'''


import stanford_parser


class Article(object):
    def __init__(self, r):
        self.raw_content = r
    
    def paragraphs(self):
        return self.raw_content.replace("\n\n", "\n").split("\n")
    
    def sentences(self):
        sentences = []
        for line in self.raw_content.split("\n"):
            if line:
                r = stanford_parser.preprocess(line)
                sentences.extend(r.split('\n'))
        return sentences