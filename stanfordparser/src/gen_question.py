'''
Created on Mar 11, 2016

@author: zhongzhu
'''

from sys import stdin

from nltk.parse.stanford import StanfordParser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree

import tree_util


aux_map = {"VBD": "did", "VB": "do", "VBZ": "does", "VBP": "do"}

lemmatizer = WordNetLemmatizer()
def insert_aux(node, mainvb, aux):
    for c in node:
        if isinstance(c, Tree):
            if c.label() == "INSERT":
                c.set_label(mainvb.label())
                c.remove("insert")
                c.append(aux)
            if c == mainvb:
                ori = c[0]
                c.remove(ori)
                c.insert(0, lemmatizer.lemmatize_verb(ori, 'v'))
            if c.height() > 2:
                insert_aux(c, mainvb, aux)


s = stdin.readline()
# parse the sentence
parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
initial_tree = parser.raw_parse(s).next()

check_aux = tree_util.has_aux(initial_tree)
if check_aux:
    qtree = Tree.fromstring(tree_util.inverse_aux(initial_tree))
else:
    # decompose verb
    aux_marked_treestr = tree_util.insert_aux_node(initial_tree)
    mainvb = Tree.fromstring(tree_util.get_main_verb(aux_marked_treestr))
    tree_with_aux_node = Tree.fromstring(aux_marked_treestr)
    insert_aux(tree_with_aux_node, mainvb, aux_map[mainvb.label()])
    qtree = Tree.fromstring(tree_util.inverse_aux(tree_with_aux_node))

print("\nQuestion:")
print(" ".join(qtree.leaves()))


# for w in s.split():
#     print("===================")
#     synsets = wordnet.synsets(w.lower())  # @UndefinedVariable
#     print(w, len(synsets))
#     for synset in synsets:
#         print "-" * 10
#         print "Name:", synset.name()
#         print "Lexical Type:", synset.lexname()
#         print "Lemmas:", synset.lemma_names()
#         print "Definition:", synset.definition()
#         for example in synset.examples():
#             print "Example:", example
