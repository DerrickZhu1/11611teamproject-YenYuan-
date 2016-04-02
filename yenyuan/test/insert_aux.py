'''
Created on Mar 12, 2016

@author: zhongzhu
'''
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree


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

tree = Tree.fromstring("(ROOT (S (NP (PRP We)) (VP (INSERT insert) (VBD worked) (PP (IN on) (NP (DT the) (JJ final) (NN project)))) (. .)))")
insert_aux(tree, Tree.fromstring("(VBD worked)"), "did")
print(tree)