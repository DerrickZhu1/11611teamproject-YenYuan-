'''
Created on April 9, 2016
@author: Brock Sennish
'''

import nltk
from nltk.parse.stanford import StanfordParser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree

import script_wrapper as stanford_parser
import script_wrapper as tsurgeon

parser = StanfordParser(path_to_jar=stanford_parser.stanford_parser_jar, path_to_models_jar=stanford_parser.stanford_model_jar)


# Main algorithm
def extractSimplifiedSentences(tree):
    result = []
    extracted = [tree] + getExtractions(tree) # <- a list of extractions
    print(extracted)
    for t in extracted:
        for new in extractHelper(t):
            result.append(new)
    return result
    

def extractHelper(tree):
    result = []
    tree = movePP(tree)
    removalFunctions = [removeNounMods, removeVerbMods, removeLeadingMods]
    for remove in removalFunctions:
        tree = remove(tree)
    if hasConjuncts(tree):
        conjuncts = extractConjuncts(tree)
        for t in conjuncts:
            result.append(t)
    elif hasSubjFMV(tree):
        result.append(tree)
    return result
        
    
## EXTRACTION FUNCTIONS ##


# Returns all extracted sentences from main sentence.
def getExtractions(tree):
    result = []
    extractFunctions = [extractNonResMod, extractSubClause, extractParticiple]
    for f in extractFunctions:
        extraction = f(tree)
        if extraction != None:
            result.append(extraction)
    return result


# Extracts sentences for non-restrictive appositives and relative clauses
# that modify the subject. (generating sentences from other modifiers leads to
# problem cases. 
def extractNonResMod(tree):
    subject = tsurgeon.findSubject(tree)
    print(subject)
    sub_tree = Tree.fromstring(subject)
    tokens = sub_tree.leaves()
    parts = ' '.join(tokens).split(',')
    main_subject = parts[0]
    if len(parts) > 1 and parts[1] != '':
        phrase_type = getTag(parts[1].strip(), sub_tree)
        # check if it is an appositive
        if phrase_type == 'NP':
            # adding 'is' temporarily - might be able to get inflection correct
            # by examining main verb.
            sentence = main_subject + 'is' + parts[1].rstrip() + '.'
            return sentence
        # check if it is a relative clause
        elif phrase_type == 'SBAR':
            # CONSTRAINTS:
            # fails for relative clauses with adjunct gaps
            # assumes we don't have a subordinate clause - need case for this
            substitution = [main_subject.rstrip()] + parts[1].split()[1:]
            sentence = ' '.join(substitution).rstrip() + '.'
            return sentence
    pass
    

# Extracts a sentence from a subordinate clause.
def extractSubClause(tree):
    sub_clause = tsurgeon.hasSubordinateClause(tree)
    if sub_clause != '':
        sub_tree = Tree.fromstring(sub_clause)
        words = sub_tree.leaves()
        if words[0].lower() != 'if':
            sentence = ' '.join(words[1:]).strip() + '.'
            return sentence
    pass
    

def extractParticiple(tree):
    pass


def extractConjuncts(tree):
    pass


## REMOVAL FUNCTIONS ##


def removeNounMods(tree):
    pass
    

def removeVerbMods(tree):
    pass


def removeLeadingMods(tree):
    pass


## TREE PROPERTY FUNCTIONS ##


def hasConjuncts(tree):
    pass
    
    
def hasSubjFMV(tree):
    pass    


## OTHERS ##


def movePP(tree):
    # Temporary condition
    if type(tree) == str:
        pass
    moved_pp_treestr = tsurgeon.moveLeadingPP(tree)
    if moved_pp_treestr != '':
        return Tree.fromstring(moved_pp_treestr)
    pass


def getTag(string, tree):
    for sub in tree.subtrees():
        if ' '.join(sub.leaves()) == string:
            return sub.label()
    return None


def main():
    sent = "In 2000, Bush, the governor of Texas, won the election."
    tree = parser.raw_parse(sent).next()
    extractSimplifiedSentences(tree)


if __name__ == "__main__":
    main()
