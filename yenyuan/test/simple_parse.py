'''
Created on Apr 12, 2016

@author: zhongzhu
'''
from nltk.parse.stanford import StanfordParser
from nltk.tag.stanford import StanfordNERTagger
from nltk.tokenize import word_tokenize

import script_wrapper as stanford_parser 


sentence = "Dempsey was drafted by Major League Soccer club New England Revolution."
st = StanfordNERTagger(model_filename='../lib/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz', path_to_jar="../lib/stanford-ner-2015-12-09/stanford-ner-3.6.0.jar")
tags = st.tag(word_tokenize(sentence))
print(tags)

prev_tag_name = tags[0][1]
cur_entity = tags[0][0]
entities = {}
for i in range(1, len(tags)):
    cur_tag = tags[i]
    cur_token = cur_tag[0]
    cur_tag_name = cur_tag[1]
    if cur_tag_name == prev_tag_name:
        cur_entity = cur_entity + " " + cur_token
    else:
        if not prev_tag_name in entities:
            entities[prev_tag_name] = []
        entities[prev_tag_name].append(cur_entity)
        cur_entity = cur_token
    prev_tag_name = cur_tag_name
del entities['O']
print(entities)

parser = StanfordParser(path_to_jar=stanford_parser.stanford_parser_jar, path_to_models_jar=stanford_parser.stanford_model_jar)
print(parser.raw_parse("Dempsey was drafted by Major League Soccer club New England Revolution.").next())