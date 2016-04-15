'''
Created on Mar 15, 2016

@author: zhongzhu
'''

from re import match

from nltk.parse.stanford import StanfordParser
from nltk.stem.snowball import EnglishStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree

import script_wrapper
import process_question
from extract_answer import extract_answer
from util import timer_log


lemmatizer = WordNetLemmatizer()
parser = StanfordParser(path_to_jar=script_wrapper.stanford_parser_jar, path_to_models_jar=script_wrapper.stanford_model_jar)
stemmer = EnglishStemmer()

'''
Use Porter Stemming algorithm to clean the words.
'''

def extract_words(words):
    result = []
    for w in words:
        cleaned = stemmer.stem(w).lower()
        if not match(r"[^a-zA-Z\d\s:]", cleaned):
            result.append(cleaned)
    return result

# porter stemmer
def yes_or_no(statement, question):
    qtree = parser.raw_parse(question).next()
    stree = parser.raw_parse(statement).next()
    qtree = Tree.fromstring(script_wrapper.remove_aux(qtree))
    qtokens = extract_words(qtree.leaves())
    stokens = extract_words(stree.leaves())
    for t in qtokens:
        if t not in stokens:
            print("Found missing word: " + t)
            return False
    return True


def answer(question, filename):
    with open(filename, 'r') as f:
        article = Article(f.read())
        f.close()
    print(extract_answer(question, article))
    


# question = "Has he also played for New England Revolution Fulham and Tottenham Hotspur?"
# sentence = "He has also played for New England Revolution Fulham and Tottenham Hotspur"
# print("\nThe question is: \n\t" + question)
# print("Our answer is: ")
# if yes_or_no(sentence, question):
#     print("yes")
# else: 
#     print("no")