'''
Created on Apr 14, 2016

@author: zhongzhu
'''

import inspect

from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset


# methods = inspect.getmembers(Synset, predicate=inspect.ismethod)
# for synset in wordnet.synsets("small"):
#     for m in methods:
#         try:
#             print(m[0] + ":\t" + getattr(synset, m[0])())
#         except:
#             print(m[0])
#             pass
#     print("==============")

for synset in wn.synsets("earn"):
    for hypernym in synset.instance_hypernyms():
#     print(synset.definition(), hypernym.instance_hyponyms())
#     print(synset.similar_tos())
        print(synset.hypernyms())
#     print(synset.instance_hypernyms())
#     print(synset.hyponyms())
#     print(synset.instance_hyponyms())
#     print(synset.member_holonyms())
#     print(synset.substance_holonyms())
#     print(synset.part_holonyms())
#     print(synset.member_meronyms())
#     print(synset.substance_meronyms())
#     print(synset.part_meronyms())
#     print(synset.topic_domains())