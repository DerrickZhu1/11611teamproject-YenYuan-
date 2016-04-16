'''
Created on April 14, 2016.

@author: bsennish
''' 

import time

from nltk.parse.stanford import StanfordParser
#from nltk.stem.snowball import EnglishStemmer
from nltk.tag.stanford import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk.tree import Tree

import script_wrapper as stanford_parser
parser = StanfordParser(path_to_jar=stanford_parser.stanford_parser_jar, path_to_models_jar=stanford_parser.stanford_model_jar)




def collect_named_entities(sentence):
    st = StanfordNERTagger(model_filename='../lib/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz', path_to_jar="../lib/stanford-ner-2015-12-09/stanford-ner-3.6.0.jar")
    tags = st.tag(word_tokenize(sentence))
    print(tags)
    # clean up the result from the tagger
    prev_tag_name = str(tags[0][1])
    cur_entity = str(tags[0][0])
    entities = {}  
    for i in range(1, len(tags)):
        cur_tag = tags[i]
        cur_token = str(cur_tag[0])
        cur_tag_name = str(cur_tag[1])
        if cur_tag_name == prev_tag_name:
            cur_entity = cur_entity + " " + cur_token
        else:
            if not prev_tag_name in entities:
                entities[prev_tag_name] = []
            # change encoding, another way is to .encode('ascii','ignore')
            entities[prev_tag_name].append(str(cur_entity))
            cur_entity = cur_token
        prev_tag_name = cur_tag_name
    if 'O' in entities:
        del entities['O']  # not needed, 'O' means not a named entity
    return entities
    
    
def process_question(question):
    type = question_type(question)
    parse = parser.raw_parse(question).next()
    tags = parse.pos()
    keywords = []
    ignore = ['DT', '.', 'WP', 'PRP', 'PRP$', 'WDT', 'WRB']
    for (word, tag) in tags:
        if tag not in ignore and word.lower() not in ["did", "do", "does"]:
            print(word, tag)
            keywords.append(word.lower())
    #keywords = word_tokenize(question)[:-1]
    '''
    if type == "YN":
        # process yes/no question
        pass
    else:
        # process wh-question
        pass
    '''
    return type, keywords


def question_type(question):
    pass


def process_yn(question):
    # extract keywords
    pass
    

def process_wh(question):
    # extract keywords
    pass

