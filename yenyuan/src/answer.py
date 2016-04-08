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
from util import timer_log


lemmatizer = WordNetLemmatizer()
parser = StanfordParser(path_to_jar=script_wrapper.stanford_parser_jar, )
stemmer = EnglishStemmer()

def lemmatize_verb(node):
    for c in node:
        if isinstance(c, Tree):
            # assuming the verb is the only child of a VB* node. 
            # Remove the only child, lemmatize the verb itself, then append it back
            if match("VB.*", c.label()):
                c.set_label("VB")
                ori = c[0]
                c.remove(ori)
                c.append(lemmatizer.lemmatize(ori, 'v'))
            if c.height() > 2:
                lemmatize_verb(c)
    return node

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

def clean(s):
    s = s.replace('?', '.')
    s = s[0].upper() + s[1:]
    return s

# porter stemmer
def yes_or_no(statement, question):
    qtree = parser.raw_parse(question).next()
    stree = parser.raw_parse(statement).next()
    timer_log("parsing")
    qtree = Tree.fromstring(script_wrapper.remove_aux(qtree))
    qtokens = extract_words(qtree.leaves())
    stokens = extract_words(stree.leaves())
    for t in qtokens:
        if t not in stokens:
            print("Found missing word: " + t)
            return False
    return True

# sentences = []
# with open("../temp/a1.txt") as t:
#     article = Article(t.read())
#     for s in article.sentences():
#         try:
#             t = parser.raw_parse(s).next()
#             lemmatize_verb(t)
#             sentences.append(" ".join(t.leaves()).encode('ascii', errors='backslashreplace'))
#         except StopIteration:
#             pass

# s = stdin.readline()
# initial_tree = parser.raw_parse(s).next()
# stmt_tree_1 = script_wrapper.remove_aux(initial_tree)
# stmt_tree_2 = script_wrapper.revert_aux(initial_tree)
# stmt1 = clean(" ".join(lemmatize_verb(Tree.fromstring(stmt_tree_1)).leaves()))
# stmt2 = clean(" ".join(lemmatize_verb(Tree.fromstring(stmt_tree_2)).leaves()))

# print(stmt1, stmt2)
# for s in sentences:
#     print(s)
# print(stmt1 in sentences or stmt2 in sentences)

question = "Did he start 23 of 24 matches scoring seven goals?"
print("\nThe question is: \n\t" + question)
print("Our answer is: ")
if yes_or_no("In his rookie season, he started 23 of 24 matches scoring seven goals.", question):
    print("yes")
else: 
    print("no")

# is Dempsey ^ of Irish ^ descent on his father's side?
