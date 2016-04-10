'''
Created on April 9, 2016
@author: Brock Sennish

ISSUES:
Extraction from appositives is buggy - don't want to insert in the whole
preceding NP.
'''

import nltk
from nltk.parse.stanford import StanfordParser
from nltk.tree import Tree

import script_wrapper as stanford_parser
import script_wrapper as tsurgeon

import string

parser = StanfordParser(path_to_jar=stanford_parser.stanford_parser_jar, path_to_models_jar=stanford_parser.stanford_model_jar)


# # MAIN ALGORITHM ##


def extractSimplifiedSentences(tree):
    result = []
    extracted = [tree] + getExtractions(tree)  # <- a list of extractions
    for t in extracted:
        if isinstance(t, str):
            t = parser.raw_parse(t).next()
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
    elif tsurgeon.hasSubjFMV(tree):
        result.append(tree)
    return result
        
    
# # EXTRACTION FUNCTIONS ##


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
    part_mod = tsurgeon.hasParticipleMod(tree)
    if part_mod != '':
        subject = tsurgeon.findSubject(tree)
        subject_words = Tree.fromstring(subject).leaves()
        part_tree = Tree.fromstring(part_mod)
        part_words = part_tree.leaves()
        # Ignoring inflection
        result_words = subject_words + ['is'] + part_words[1:]
        sentence = ' '.join(result_words).strip() + '.'
        return sentence
    pass


def extractConjuncts(tree):
    pass


# # REMOVAL FUNCTIONS ##


def removeNounMods(tree):
    tree_str = tsurgeon.remove_internal_mods(tree)
    if tree_str != '':
        tree = Tree.fromstring(tree_str)
    tree_str = tsurgeon.remove_participle_mods(tree)
    if tree_str != '':
        tree = Tree.fromstring(tree_str)
    return tree
    

def removeVerbMods(tree):
    return tree


def removeLeadingMods(tree):
    tree_str = tsurgeon.remove_leading_mods(tree)
    if tree_str != '':
        new = Tree.fromstring(tree_str)
        if new != tree:
            return removeLeadingMods(Tree.fromstring(tree_str))
    return tree
    


# # TREE PROPERTY FUNCTIONS ##


def hasConjuncts(tree):
    pass
    


# # OTHERS ##


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


def simplify_sen(sent):
    results = []
    tree = parser.raw_parse(sent).next()
    result = extractSimplifiedSentences(tree)
    punct = string.punctuation
    for tree in result:
        # TEMPORARY POSTPROCESSING
        tokens = [tok for tok in tree.leaves() if tok not in punct]
        results.append(' '.join(tokens) + '.')
    return results


def main():
    sent = "John, a man, killed Mary, a woman."
    tree = parser.raw_parse(sent).next()
    result = extractSimplifiedSentences(tree)
    punct = string.punctuation
    for tree in result:
        # TEMPORARY POSTPROCESSING
        tokens = [tok for tok in tree.leaves() if tok not in punct]
        print(' '.join(tokens) + '.')


if __name__ == "__main__":
    main()
