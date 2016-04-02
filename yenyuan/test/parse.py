'''
Created on Mar 12, 2016

@author: zhongzhu
'''
from nltk.parse.stanford import StanfordParser
from nltk.tree import Tree


productions = {}
lexicons = {}

def collect_productions(node):
    for p in node.productions():
        p = str(p)
        if '\'' in p:
            p = p.replace('\'', '')
            if not p in lexicons:
                lexicons[p] = 0
            lexicons[p] += 1
        else:
            if not p in productions:
                productions[p] = 0
            productions[p] += 1
#         print("[" + p + "]")
#     for c in node:
#         if isinstance(c, Tree):
#             for p in c.productions():
#                 p = str(p)
#                 if '\'' in p:
#                     p = p.replace('\'', '')
#                     if not p in lexicons:
#                         lexicons[p] = 0
#                     lexicons[p] += 1
#                     print("[%s]", p)
#                 else:
#                     if not p in productions:
#                         productions[p] = 0
#                     productions[p] += 1
#                     print("[%s]", p)
#             if c.height() > 2:
#                 collect_productions(c)

parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
with open("../temp/examples.sen") as f:
    trees = parser.raw_parse_sents(f.read().split("\n"))  # @UndefinedVariable
    for t in trees:
        t = t.next()
#         print("_".join(t.leaves()))
        collect_productions(t)

for k in sorted(productions):
    print(k + " " + str(productions[k]))
for k in sorted(lexicons):
    print(k + " " + str(lexicons[k]))
