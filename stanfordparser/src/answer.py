'''
Created on Mar 15, 2016

@author: zhongzhu
'''

from re import match
from sys import stdin

from nltk.parse.stanford import StanfordParser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree

from article import Article
import tree_util


lemmatizer = WordNetLemmatizer()
parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

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

def clean(s):
    s = s.replace('?', '.')
    s = s[0].upper() + s[1:]
    return s

sentences = []
with open("../temp/a1.txt") as t:
    article = Article(t.read())
    for s in article.sentences():
        try:
            t = parser.raw_parse(s).next()
            lemmatize_verb(t)
            sentences.append(" ".join(t.leaves()).encode('ascii', errors='backslashreplace'))
        except StopIteration:
            pass

s = stdin.readline()
initial_tree = parser.raw_parse(s).next()
stmt_tree_1 = tree_util.remove_aux(initial_tree)
stmt_tree_2 = tree_util.revert_aux(initial_tree)
stmt1 = clean(" ".join(lemmatize_verb(Tree.fromstring(stmt_tree_1)).leaves()))
stmt2 = clean(" ".join(lemmatize_verb(Tree.fromstring(stmt_tree_2)).leaves()))

print(stmt1, stmt2)
for s in sentences:
    print(s)
print(stmt1 in sentences or stmt2 in sentences)

# is Dempsey of Irish descent on his father's side?
