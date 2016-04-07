'''
Created on April 2, 2016

@author: Brock Sennish
'''

'''
from subprocess import check_output
import sys
import string
from os.path import devnull
'''
import time

start = time.time()

from subprocess import check_output
from os.path import devnull
import re
import nltk
import string
import copy
from nltk.parse.stanford import StanfordParser, StanfordDependencyParser
from nltk.tree import Tree

tree_file = "__tree"
parser_path = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
tsurgeon_path = '../lib/stanford-tregex-2015-12-09/tsurgeon.sh'
tregex_path = '../lib/stanford-tregex-2015-12-09/tregex.sh'
parser = StanfordParser(model_path=parser_path)
dep_parser=StanfordDependencyParser(model_path=parser_path)
DEVNULL = open(devnull, 'wb')

# Removes parentheticals from a sentence.
def removeParentheticals(sent):
    # DO THIS WITH REGEX...STOP BEING STUPID
    new = sent
    start = 0
    for i in range(len(sent)):
        if sent[i] == '(':
            start = i
        elif sent[i] == ')':
            new = sent[:start] + sent[i+1:]
            break
    if '(' in new:
        return removeParentheticals(new)
    else:
        return new


# NAIVE
def findSubject(tree):
    with open(tree_file, "w+") as f:
        f.write(str(tree))
    f.close()
    pattern = 'NP=subj > S' #> ROOT)'
    subject =  check_output([tregex_path,
                        '-s',
                        pattern,
                        tree_file], stderr=DEVNULL)
    return ' '.join(Tree.fromstring(subject).leaves()).split(',')


def getPOS(string, tree):
    for sub in tree.subtrees():
        if ' '.join(sub.leaves()) == string:
            return sub.label()
    return None


def extractSubjMods(sent, tree):
    new_tree = tree
    found = False
    for sub in tree.subtrees():
        if ' '.join(sub.leaves()) == sent:
            tree = sub
            found = True
            break
    if not found:
        sent += "."
        new_tree = parser.raw_parse(sent).next()
    segments = ' '.join(new_tree.leaves()).split(',')
    subject = ""
    try: subject = findSubject(tree)
    except: return ""
    extractions = []
    if len(subject) > 1:
        if subject[1][:4] == " who":
            extractions.append(subject[0] + subject[1][5:])
        else:
            extractions.append(subject[0] + 'is' + subject[1])
    return extractions



# Extracts simplified sentences.
def extractSimplifiedSentences(tree):
    conjuncts = splitSententialConj(tree)
    result = [conjunct for conjunct in conjuncts]
    extracted = [removeGlobalModifiers(sent, tree) for sent in result]
    extraction_functions = [extractSubjMods] #[nonResApp, nonResRel, subClause, partPhrase]
    for f in extraction_functions:
        for sent in extracted:
            for extract in f(sent, tree):
                extracted.append(extract)
    for s in extracted:
        for extract in extractHelper(s, tree):
            if extract not in result:
                result.append(extract)
    return result


def splitSententialConj(tree):
    conjuncts = []
    words = tree.leaves()
    pos_dict = dict()
    for (word, part) in tree.pos():
        pos_dict[word] = part
    for i in range(len(words)):
        if pos_dict[words[i]] == "CC":
            sent1 = copy.copy(words[:i])
            sent2 = copy.copy(words[i+1:])
            if sent1[-1] in string.punctuation:
                sent1 = sent1[:-1]
            if sent2[-1] in string.punctuation:
                sent2 = sent2[:-1]
            if getPOS(' '.join(sent1), tree) == getPOS(' '.join(sent2), tree) == "S":
                conjuncts.append(' '.join(sent1))
                conjuncts.append(' '.join(sent2))
                return conjuncts
    return [' '.join(words)]
    


def removeGlobalModifiers(sent, tree):
    first_comma = 0
    words = sent.split()
    for i in range(len(words)):
        if words[i] == ',':
            first_comma = i
            break
    pos = getPOS(' '.join(words[:i]), tree)
    if pos == "ADVP":  # Probably will want to change this condition
        return ' '.join(words[first_comma+1:])
    return ' '.join(words)
    
    
def removeAppositives(sent, tree):
    words = sent.split()
    start = 0
    new = sent
    segment = ''
    if words.count(',') > 1:
        for i in range(len(words)):
            if words[i] == ',' and start == 0:
                start = i
            elif words[i] == ',':
                segment = ' '.join(words[start+1:i])
                new = ' '.join(words[:start] + words[i+1:])
        if getPOS(segment, tree) == 'NP':
            return removeAppositives(new, tree)
    return new
                
    


# Helper function for extractSimplifiedSentences...DESCRIBE WHAT IT DOES
def extractHelper(sent, tree):
    result = []
    # MOVE leading prep phrases & quotations to be the last children of the
    # main verb phrase (OPTIONAL)
    # movePrepQuot(tree)
    
    # REMOVE noun modifiers offset by commas, 
    # verb modifiers offset by commas, 
    # leading modifiers of the main clause
    result.append(removeAppositives(sent, tree))
    
    # SPLIT conjunctions
    # IF tree has S,SBAR, or VP nodes conjoined with c not in {or, nor}, THEN
        # Tconjuncts <-- EXTRACT new sentence trees for each conjunct in the 
        # leftmost, topmost set of conjoined S, SBAR, or VP nodes in tree
        # FORALL t in Tconjuncts DO
            # Tresult <-- Tresult U extractHelper(t)
    # ELIF tree has a subject and finite main verb THEN
        # Tresult <-- Tresult U {t}
        
    return result


# Function to return the input tree with non-restrictive appositives removed.


def main():
    sentence = "John, a sailor, went to the store, and Mary, who is a woman, went shopping."
    sentence = removeParentheticals(sentence)
    parse = parser.raw_parse(sentence).next()
    for extraction in extractSimplifiedSentences(parse):
        print(extraction)
    
    
if __name__ == "__main__":
    main()


print(time.time() - start)