import os
import sys
import nltk
from nltk.parse.stanford import StanfordParser


f = open(sys.argv[1])

text = f.read()
text = text.decode('utf-8')


sents = nltk.sent_tokenize(text)

print sents

modelPath = 'edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz'

parser = StanfordParser(model_path = modelPath)


for s in sents:
	print list(parser.raw_parse(s))




