'''
Created on Mar 11, 2016

@author: zhongzhu
'''
import os

from nltk.parse.stanford import StanfordDependencyParser
from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from nltk.tag.stanford import StanfordPOSTagger


st = StanfordPOSTagger('english-bidirectional-distsim.tagger')
st.tag('What is the airspeed of an unladen swallow ?'.split())

st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz') 
st.tag('Rami Eid is studying at Stony Brook University in NY'.split())

parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
list(parser.raw_parse("the quick brown fox jumps over the lazy dog"))

dep_parser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
print [parse.tree() for parse in dep_parser.raw_parse("The quick brown fox jumps over the lazy dog.")]
