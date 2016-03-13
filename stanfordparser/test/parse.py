'''
Created on Mar 12, 2016

@author: zhongzhu
'''
from nltk.parse.stanford import StanfordParser


parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
# t = treebank.parsed_sents("wsj_0015.mrg")[0]  # @UndefinedVariable
initial_tree = parser.raw_parse("Do we know?").next()
initial_tree.draw()