'''
Created on Apr 14, 2016

@author: zhongzhu
'''

from nltk.corpus import wordnet as wn

for synset in wn.synsets("Jamaica"):
    print(synset.hypernym_paths())