'''
Created on Mar 11, 2016

@author: zhongzhu
'''
from subprocess import check_output
import sys

import nltk
from nltk.parse.stanford import StanfordParser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree


tag_aux_map = {"VBD": "did", "VB": "do", "VBZ": "does", "VBP": "do"}
init_tree_file = "__inittree"
marked_tree_file = "__auxmarkedtree"
decom_tree_file = "__decomptree"

lemmatizer = WordNetLemmatizer()
def insert_aux(node, mainvb, aux):
    for c in node:
        if isinstance(c, nltk.Tree):
            if c.label() == "INSERT":
                c.set_label(mainvb.label())
                c.remove("insert")
                c.append(aux)
            if c == mainvb:
                ori = c[0]
                c.remove(ori)
                c.insert(0, lemmatizer.lemmatize(ori, 'v'))
            if c.height() > 2:
                insert_aux(c, mainvb, aux)


s = "We will work on the final project."
inputstr = sys.stdin.readline()
if inputstr:
    s = inputstr
# parse the sentence
parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
# t = treebank.parsed_sents("wsj_0015.mrg")[0]  # @UndefinedVariable
initial_tree = parser.raw_parse(s).next()
with open(init_tree_file, "w+") as f:
    f.write(str(initial_tree))
check_aux = check_output(['../lib/stanford-tregex-2015-12-09/tregex.sh',
                    '-s',
                    'ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))',
                    init_tree_file])

print("check_aux", check_aux)

# decompose verb
if check_aux:
    print("The sentence already has an auxiliary verb.")
    with open(decom_tree_file, "w+") as f:
        f.write(str(initial_tree))
else:
    print("The sentence doesn't have an auxiliary verb.")
    print("Decompose verb...")
    aux_marked_treestr = check_output(['../lib/stanford-tregex-2015-12-09/tsurgeon.sh',
                                '-treeFile',
                                init_tree_file,
                                '-s',
                                '../scripts/insert_aux'])
    aux_inserted_tree = Tree.fromstring(aux_marked_treestr)
    with open(marked_tree_file, "w+") as f:
        f.write(str(aux_marked_treestr))
    tregex_str = check_output(['../lib/stanford-tregex-2015-12-09/tregex.sh',
                         '-s', '/VB.?/ > (VP $ INSERT)', marked_tree_file])
    mainvb = Tree.fromstring(tregex_str)
    insert_aux(aux_inserted_tree, mainvb, tag_aux_map[mainvb.label()])
    with open(decom_tree_file, "w+") as f:
        f.write(str(aux_inserted_tree))

inversed_tree = check_output(['../lib/stanford-tregex-2015-12-09/tsurgeon.sh',
      '-treeFile',
      decom_tree_file,
      '-s',
      '-po',
      'ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))',
      'move aux $+ clause'])
qtree = Tree.fromstring(inversed_tree)
# qtree.draw()
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
